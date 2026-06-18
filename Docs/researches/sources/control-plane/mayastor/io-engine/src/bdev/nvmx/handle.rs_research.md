## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/handle.rs

### Purpose
`nvmx/handle.rs` is the NVMe block-device I/O submission layer. It owns per-handle SPDK I/O channels, DMA allocation, read/write/compare/flush/unmap/write-zeroes dispatch, NVMe admin/I/O passthrough, reservations, snapshots, reset dispatch, completion translation, and I/O-context pooling.

### Important APIs, Types, And Functions
`NvmeDeviceHandle` implements `BlockDeviceHandle`. `NvmeIoCtx` is the pooled callback context for BIO-style I/O. `nvme_io_ctx_pool_init()`, `alloc_nvme_io_ctx()`, and `free_nvme_io_ctx()` manage the pool. Completion functions include `complete_nvme_command()`, `nvme_io_done()`, `nvme_writev_done()`, `nvme_unmap_completion()`, and `nvme_flush_completion()`. Helper functions validate I/O, map errors, walk SGLs, and check channel readiness.

### Control Flow
Handle creation gets an SPDK I/O channel by controller id, stores controller/namespace/protection flags, and connects the qpair synchronously or asynchronously. Deprecated async `read_at()`/`write_at()` validate byte alignment, submit a single-buffer SPDK command, await a oneshot completion, update stats, and decrement pending I/O. Callback-based vector operations allocate `NvmeIoCtx`, optionally inject faults, choose single-buffer or vectored SPDK calls, and account pending I/O. Completions update stats, translate NVMe status, invoke the caller callback with the block device, and free the context. Reset delegates to the controller. Flush and unmap use SPDK flush and dataset management commands. Admin and I/O passthrough build raw NVMe commands and await oneshot completions; reservation helpers and snapshot creation are layered on passthrough/admin.

### State, Persistence, And Dependencies
Per-handle state includes `ManuallyDrop<NvmeControllerIoChannel>`, controller wrapper, namespace `Arc`, protection flags, cached block size, and a block-device view. Per-I/O state is pooled in `NVME_IOCTX_POOL`; callbacks hold raw pointers to this state and the SPDK channel. Snapshot creation serializes `NvmeSnapshotMessage` into a DMA payload, but persistence happens on the target side. Dependencies include SPDK namespace/controller command APIs, `DmaBuf`, `IoVec`, `NvmeStatus`, `MemoryPool`, `Reactors`, `SnapshotParams`, and optional fault injection.

### Integration Points
`device.rs` constructs these handles from descriptors. `channel.rs` provides qpair and stats access. `controller.rs` services reset and timeout operations. Initiator and nexus paths rely on this implementation for actual NVMe I/O and management commands.

### Risks
On dispatch failure after allocating `NvmeIoCtx`, several paths return an error without freeing the context, unless the pool or caller handles it elsewhere. `unmap_blocks()` manually allocates a DSM range array and does not visibly free it on success or failure. Flush allocates a context but does not call `account_io()`, while completion skips pending decrement for flush; this is intentional for accounting but differs from other operations. Raw callback pointers require channel and handle lifetimes to remain valid. Some admin/reservation helpers unwrap DMA allocation.

### Test Signals
Exercise alignment validation, empty/uninitialized iovs, pool exhaustion, single and vectored read/write/compare, pending-I/O accounting on success/error, PI error detection, dispatch failure cleanup, unmap range splitting and limits, write-zeroes, flush accounting, reset callback translation, admin passthrough status handling, identify controller, reservation register/acquire/release/report, snapshot payload encoding, and fault-injection behavior.
