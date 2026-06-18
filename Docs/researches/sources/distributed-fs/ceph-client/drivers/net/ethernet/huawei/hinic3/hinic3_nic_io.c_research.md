
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_nic_io.c

## Purpose
`hinic3_nic_io.c` owns the hinic3 NIC data-path queue-pair lifecycle below the netdev TX/RX queues. It allocates per-function NIC I/O state, reserves doorbells and a coherent TX consumer-index table, creates SQ/RQ work queues, attaches them to `hinic3_nic_io`, and programs queue context/root context into firmware through command queues.

## Important APIs, Types, And Functions
- `struct hinic3_sq_ctxt`, `struct hinic3_rq_ctxt`, `struct hinic3_qp_ctxt_hdr`, `struct hinic3_sq_ctxt_block`, `struct hinic3_rq_ctxt_block`, and `struct hinic3_clean_queue_ctxt` describe the firmware queue-context payloads sent to `L2NIC_UCODE_CMD_MODIFY_QUEUE_CTX` and `L2NIC_UCODE_CMD_CLEAN_QUEUE_CTX`.
- `hinic3_init_nic_io()` allocates `struct hinic3_nic_io`, marks NIC service in use, initializes the function table, stores RX buffer length, fetches feature capability, and masks it to supported/default feature bits.
- `hinic3_free_nic_io()` clears the function service-used state and frees the NIC I/O object.
- `hinic3_init_nicio_res()` reads the hardware maximum queue count, allocates SQ/RQ doorbell addresses, and allocates the coherent CI table sized by `HINIC3_CI_TABLE_SIZE(max_qps)`.
- `hinic3_alloc_qps()`/`hinic3_free_qps()` allocate and destroy arrays of `struct hinic3_io_queue` for SQs and RQs, using `hinic3_wq_create()` with SQ/RQ WQEBB sizes.
- `hinic3_init_qps()` publishes the queue arrays into `nic_io`, initializes each SQ CI pointer to a 64-byte CI slot, clears hardware-visible CI, and installs common SQ/RQ doorbell bases.
- `hinic3_init_qp_ctxts()` prepares SQ and RQ context batches, cleans offload context, sets root context, and configures each SQ CI table entry.
- `hinic3_free_qp_ctxts()` cleans the root context.

## Control Flow
Initialization is layered. `hinic3_init_nic_io()` creates software state and enables the NIC service. `hinic3_init_nicio_res()` reserves PCI/device resources shared by all queues. A dynamic queue-parameter caller then invokes `hinic3_alloc_qps()` to allocate SQ/RQ WQs, followed by `hinic3_init_qps()` to publish queues into the live `nic_io`. `hinic3_init_qp_ctxts()` then sends SQ contexts in batches of at most `HINIC3_Q_CTXT_MAX` entries, sends RQ contexts the same way, cleans prior LRO/TSO context, programs the root context, and arms the SQ CI table for every queue.

SQ context preparation reads local PI/CI, records first WQ page PFN and WQ block PFN, enables owner bit, sets VLAN insertion mode, and applies prefetch thresholds. RQ context preparation computes hardware indices shifted for normal RQ WQE format, records MSI-X entry, sets 16-byte WQE/CQE format, and supplies the PI DMA address and WQ block PFNs. Cleanup sends `L2NIC_UCODE_CMD_CLEAN_QUEUE_CTX` for both SQ and RQ queue types.

## State And Persistence Behavior
State is runtime-only. Persistent state is limited to device/firmware contexts and coherent DMA memory while the driver is loaded and interface resources are active. `nic_io->ci_vaddr_base` is a coherent table where hardware updates SQ consumer indices; each queue gets a 64-byte slot. `nic_io->sq`, `nic_io->rq`, `num_qps`, `max_qps`, doorbell bases, `rx_buf_len`, and `feature_cap` are held in memory and released on teardown. Queue owner bits and WQ producer/consumer indices are transient protocol state shared with hardware.

## Dependencies And Integration Points
This file depends on `hinic3_hwdev`, `hinic3_hwif`, `hinic3_hw_comm`, `hinic3_cmdq`, `hinic3_nic_cfg`, `hinic3_nic_dev`, and `hinic3_wq`. It integrates with TX/RX files through `struct hinic3_io_queue` arrays, with firmware through `hinic3_cmdq_direct_resp()`, with device configuration through `hinic3_set_root_ctxt()`, `hinic3_clean_root_ctxt()`, and `hinic3_set_ci_table()`, and with PCI/DMA through doorbell allocation and coherent memory.

## Risks And Edge Cases
- Queue counts are rejected when zero or above `max_qps`, but callers must still keep SQ/RQ depths power-of-two so lower WQ allocation succeeds.
- Firmware command payloads are endian-swabbed before submission; field changes must preserve hardware layout exactly.
- `clean_qp_offload_ctxt()` uses logical OR between two cleanup calls, returning boolean-like failure rather than the first negative errno.
- On `hinic3_init_qp_ctxts()` failure after some CI table entries are set, cleanup is limited to root context cleanup, so callers must sequence broader teardown.
- Hardware-visible CI table slots are cleared on queue initialization; stale coherent memory would affect completion accounting.

## Test Signals
Useful validation signals include successful `hinic3_init_qp_ctxts()` on multi-queue devices, no firmware errors from `MODIFY_QUEUE_CTX`/`CLEAN_QUEUE_CTX`, correct TX completion advancement from the CI table, RX/TX traffic on all queues, queue count boundary tests, and teardown/reopen cycles that leave no leaked doorbells, WQs, or coherent allocations.
