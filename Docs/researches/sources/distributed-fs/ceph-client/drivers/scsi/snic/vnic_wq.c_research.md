## sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_wq.c

### Purpose
Implements Cisco vNIC work queue allocation, initialization, enable/disable, and cleanup for SNIC. Work queues are descriptor rings backed by DMA memory with parallel software buffer metadata, used for host-to-firmware requests and device-command queueing.

### Important APIs and Functions
- `vnic_wq_get_ctrl()` obtains the MMIO control block for a resource type and index using `svnic_dev_get_res()`.
- `vnic_wq_alloc_ring()` delegates descriptor-ring DMA allocation to `svnic_dev_alloc_desc_ring()`.
- `vnic_wq_alloc_bufs()` allocates `struct vnic_wq_buf` metadata blocks, links them into a circular list, and maps each software buffer to its descriptor address.
- `svnic_wq_alloc()` initializes normal `RES_TYPE_WQ` queues, disables hardware first, allocates ring memory, then allocates software buffers.
- `vnic_wq_devcmd2_alloc()` initializes the special `RES_TYPE_DEVCMD2` queue without software buffer metadata allocation.
- `vnic_wq_init_start()` writes ring base, ring size, fetch/posted indices, completion queue index, interrupt error settings, and resets software cursors.
- `svnic_wq_enable()`, `svnic_wq_disable()`, `svnic_wq_error_status()`, `svnic_wq_clean()`, and `svnic_wq_free()` manage runtime state and teardown.

### Control Flow and State
Allocation begins by binding a work queue to a device, acquiring MMIO control registers, disabling the queue, allocating the descriptor ring, and building circular software buffer metadata. Initialization programs the hardware ring with `VNIC_PADDR_TARGET` ORed into the physical base address and aligns `to_use`/`to_clean` with the fetch index. Disable writes `enable = 0` and polls `running` up to 100 microseconds. Cleanup requires the queue to be disabled, walks used descriptors through a caller-provided cleanup callback, resets indices and error status, and clears descriptor memory.

### Dependencies and Integration Points
The implementation depends on `vnic_dev` ring/resource helpers, Linux allocation and MMIO APIs, and `vnic_wq.h` register definitions. SNIC I/O code uses the queue to post firmware request descriptors and completion handlers use queue service helpers to release buffers.

### Risks and Test Signals
Risks include allocation failure leaks, incorrect circular buffer linking, off-by-one descriptor availability, and hardware disable timeout. The special devcmd2 path does not allocate `vnic_wq_buf` entries, so callers must not use normal post/service paths on it. Tests should cover queue allocation failure injection, disable timeout handling, descriptor post/complete wraparound, cleanup with outstanding descriptors, and probe/remove cycles.
