# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_queue.c

## Purpose
`iris_hfi_queue.c` implements the shared host-firmware queue transport. It allocates queue/SFR DMA memory, initializes command/message/debug queue headers, writes command packets with wraparound handling, reads firmware packets, raises hardware interrupts, and frees queue resources.

## Important APIs, Types, And Functions
Private helpers are `iris_hfi_queue_write()`, `iris_hfi_queue_read()`, queue header setup/init/deinit functions. Public functions are `iris_hfi_queues_init()`, `iris_hfi_queues_deinit()`, `iris_hfi_queue_cmd_write_locked()`, `iris_hfi_queue_cmd_write()`, `iris_hfi_queue_msg_read()`, and `iris_hfi_queue_dbg_read()`.

## Control Flow
Queue writes calculate empty space from read/write indices in bytes, reject insufficient space, copy the packet linearly or with wraparound, issue memory barriers before and after updating `write_idx`, then command writes raise a VPU interrupt. Unlocked command writes wrap runtime PM resume/get, `core->lock`, locked write, and autosuspend. Queue reads detect empty queues, set `rx_req`, validate read pointer and packet size, copy linearly or with wraparound if the packet fits `IFACEQ_CORE_PKT_SIZE`, update `read_idx`, and return `-EBADMSG` for oversized packets. Queue init allocates one aligned DMA block for table plus three 800 KiB queues and a separate 4 KiB SFR block.

## State And Persistence Behavior
Shared DMA memory persists while the core is initialized. Queue headers hold firmware-visible `read_idx`, `write_idx`, request bits, watermarks, status, and queue metadata. `core->iface_q_table_vaddr/daddr`, `sfr_vaddr/daddr`, and per-queue descriptors are valid until deinit.

## Dependencies And Integration Points
It depends on runtime PM, VPU interrupt helpers, DMA allocation, `iris_core`, and queue structs. All HFI command implementations write through this file, and all response handlers read message/debug queues through it.

## Risks And Test Signals
Queue-full handling converts any write failure to `-ENODATA`, losing the original reason. Pointer arithmetic uses `void *` extensions in read paths and should be compiler-checked. Tests should cover wraparound writes/reads, empty queue rx request behavior, oversized packet handling, command write in error/deinit core states, DMA allocation failure cleanup, runtime-PM balance, and debug queue draining.
