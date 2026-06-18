# sources/distributed-fs/ceph-client/drivers/scsi/aacraid/comminit.c

## Purpose

`comminit.c` initializes and tears down the host-to-adapter communication interface for AACRAID adapters. It negotiates firmware communication capabilities, allocates the coherent DMA region containing adapter FIB space, host response queues, the adapter init structure, command/response queues, and the firmware printf buffer, initializes queue headers, selects interrupt mode, drains active I/O during shutdown, and sends the firmware close-all request.

This file is the bridge between early adapter-specific probe code and the runtime FIB/SCSI paths. It produces the `struct aac_dev` communication state consumed by `aachba.c`, `commctrl.c`, and lower-level transport files.

## Important APIs, Types, and Functions

Externally visible functions:

- `struct aac_common aac_config`: global communication configuration, defaulting interrupt moderation on.
- `aac_send_shutdown(struct aac_dev *dev)`: drains firmware-owned SCSI commands, sends `VM_CloseAll`, frees the shutdown FIB, and reverts SRC MSI-X adapters to INTx.
- `aac_define_int_mode(struct aac_dev *dev)`: chooses MSI-X vector count and per-vector capacity for SRC adapters.
- `aac_init_adapter(struct aac_dev *dev)`: negotiates firmware capabilities, initializes locks and limits, allocates communication queues and FIBs, and returns initialized adapter state or `NULL`.

Important internal functions:

- `aac_is_msix_mode()` and `aac_change_to_intx()`: detect and force interrupt mode on SRC hardware before initialization.
- `aac_alloc_comm()`: performs the main coherent DMA allocation and fills `dev->init`, `dev->host_rrq`, `dev->comm_addr`, `dev->printfbuf`, and related physical addresses.
- `aac_queue_init()`: initializes one firmware queue's producer/consumer pointers, wait queues, lock, command list, and entry count.
- `wait_for_io_iter()` and `aac_wait_for_io_completion()`: count and wait for SCSI commands still owned by firmware.
- `aac_comm_init()`: lays out and initializes the eight communication queues in the shared communication area.

## Control Flow

`aac_init_adapter()` starts by initializing management and sync locks, defaulting FIB and SG limits for the old 512-byte FIB format, selecting producer communication, and clearing raw I/O flags. If an SRC adapter is already in MSI-X mode, it switches firmware back to INTx before capability negotiation.

It then sends `GET_ADAPTER_PROPERTIES` through `aac_adapter_sync_cmd()`. A successful response can enable newer communication interfaces, raw I/O, 64-bit raw I/O, SA firmware mode, and soft-reset support. If firmware reports a larger mapping requirement for message communication, the function remaps the adapter MMIO footprint and falls back to producer mode on failure.

Next it sends `GET_COMM_PREFERRED_SETTINGS`, which supplies maximum command size, max FIB size, SG limits, outstanding FIB counts, and max AIF count. These values update `host->max_sectors`, `dev->max_fib_size`, `host->sg_tablesize`, `dev->sg_tablesize`, `host->can_queue`, and `dev->max_num_aif`. The `numacb` module parameter can further reduce `host->can_queue`. SRC adapters call `aac_define_int_mode()` to determine MSI-X use and response-queue partitioning.

After negotiation, `aac_init_adapter()` allocates `dev->queues`, calls `aac_comm_init()` to allocate and initialize the coherent communication area, calls `aac_fib_setup()` to initialize the FIB pool, and initializes `dev->fib_list` and `dev->sync_fib_list`.

`aac_alloc_comm()` computes the allocation size based on `max_fib_size`, init-structure revision, queue area size, alignment, printf buffer size, and host RRQ needs. For type1/type2/type3 communication it reserves host RRQ memory. Type3 with SA firmware reserves an r8 init structure with per-vector RRQ descriptors. Older interfaces fill the r7 init structure with adapter FIB physical address, host memory pages, max I/O commands, max I/O size, max FIB size, max AIFs, host RRQ address, and feature flags. It then aligns the queue header region, stores the communication header physical address when applicable, and places the printf buffer after the queues.

`aac_comm_init()` lays out the eight queues in firmware-defined order: host normal/high command, adapter normal/high command, host normal/high response, adapter normal/high response. It also shares locks between opposite-direction queues that must serialize access to the same firmware-facing side.

`aac_send_shutdown()` checks adapter health, sets `adapter_shutdown` under the ioctl mutex, waits up to roughly 60 seconds for firmware-owned SCSI commands to complete, sends a synchronous `VM_CloseAll` container command, completes/frees the FIB, and changes SRC MSI-enabled adapters back to INTx mode.

## State and Persistence Behavior

The file creates and updates key per-adapter runtime state:

- `dev->comm_addr`, `comm_phys`, and `comm_size` track the coherent DMA communication allocation.
- `dev->init` and `init_pa` point at the firmware initialization structure inside that DMA allocation.
- `dev->host_rrq` and `host_rrq_pa` hold response queue memory for newer communication interfaces.
- `dev->printfbuf` points at the firmware printf buffer.
- `dev->queues` holds the software representation of the eight firmware queues.
- `dev->max_fib_size`, `max_num_aif`, `max_cmd_size`, `sg_tablesize`, `comm_interface`, `raw_io_interface`, `raw_io_64`, `sync_mode`, `sa_firmware`, `soft_reset_support`, `max_msix`, `vector_cap`, and `msi_enabled` are negotiated state.
- `dev->adapter_shutdown` is set during shutdown/reset coordination.

The state is volatile and per adapter. It is made firmware-visible through coherent DMA rather than persisted to storage.

## Dependencies and Integration Points

`comminit.c` depends on adapter-specific sync commands and MMIO operations through `aac_adapter_sync_cmd()`, `aac_adapter_ioremap()`, `aac_src_access_devreg()`, and SRC register macros from `aacraid.h`. It depends on Linux DMA coherent allocation, PCI MSI-X allocation, CPU count, SCSI host limits, delayed sleeps, and `scsi_host_busy_iter()`.

It integrates directly with FIB lifecycle setup through `aac_fib_setup()`, shutdown FIB sending through `aac_fib_send()`, and SCSI command ownership through `aac_priv(cmd)->owner`. Its output state is consumed by all runtime FIB senders, including the SCSI paths in `aachba.c` and management ioctls in `commctrl.c`.

## Risks and Edge Cases

- Firmware-reported limits drive allocation sizes and queue depths. Bad negotiation or insufficient validation can cause undersized DMA regions, SG overflows, or queue starvation.
- Type3/SA firmware uses multi-vector host RRQs and a larger r8 init structure. Off-by-one or vector-capacity errors can break completion delivery under MSI-X.
- `aac_alloc_comm()` returns `0` on allocation failure and `1` on success, while callers translate failure to `-ENOMEM`; this convention should stay consistent.
- Interrupt-mode transitions from MSI-X to INTx occur before init and during shutdown for SRC devices. Failure to transition cleanly could strand firmware interrupts.
- `aac_wait_for_io_completion()` only waits for commands whose private owner is `AAC_OWNER_FIRMWARE`. Incorrect owner transitions elsewhere can make shutdown either wait too little or report false outstanding I/O.
- Cleanup on partial `aac_init_adapter()` failure frees `dev->queues` but relies on other teardown paths for DMA/FIB allocations if later stages fail. Failure-injection tests should verify no coherent-memory leak.
- `numacb` can reduce queue depth. Very small or firmware-limited queues need testing for management FIB reservation (`AAC_NUM_MGT_FIB`) interactions.

## Test Signals

Useful signals include probe logs for communication interface type, successful fallback from unsupported message/MMIO sizing to producer mode, valid `host->can_queue`, SG table, max sectors, and max FIB values after negotiation, MSI-X vector allocation and vector-cap partitioning, coherent DMA allocation/free leak checks, queue producer/consumer initialization matching firmware expectations, FIB setup success, shutdown drain logs with active command counts, successful `VM_CloseAll`, INTx fallback after shutdown on SRC MSI adapters, and fault injection for failed sync commands, failed DMA allocation, failed queue allocation, failed FIB setup, and firmware-reported edge limits.
