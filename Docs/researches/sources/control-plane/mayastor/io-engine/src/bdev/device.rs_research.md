<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/device.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/device.rs

Purpose: Implements the generic `BlockDevice`, descriptor, and I/O handle traits for native SPDK bdevs.

Important APIs/types: `SpdkBlockDevice` wraps `UntypedBdev` and exposes size, block length, UUID, product/driver/name, alignment, I/O type support, stats, open, and event listener registration. `SpdkBlockDeviceDescriptor` wraps `UntypedDescriptorGuard` and creates I/O handles. `SpdkBlockDeviceHandle` wraps `UntypedBdevHandle` and implements DMA allocation plus read/write/compare/reset/unmap/write-zeroes/flush/NVMe admin/snapshot methods. `bdev_io_ctx_pool_init()` initializes a global memory pool for `IoCtx`. `bdev_event_callback()` translates SPDK remove/resize/media events into io-engine device events.

Control flow: vector I/O methods allocate `IoCtx`, optionally inject faults, submit SPDK bdev calls, and complete through `bdev_io_completion`, which maps status, invokes caller callback, returns context to the pool, and frees SPDK I/O.

State and dependencies: global event-dispatcher map and I/O context pool. Depends on SPDK bdev functions, io-engine core traits, fault injection feature, and replica snapshot factory.

Risks and test signals: I/O before pool initialization panics. Some dispatch errors map all negative reset/unmap/write-zeroes/flush failures to `ENOMEM`. Event listeners are keyed by device name and protected by a mutex. Tests should cover pool exhaustion, callback status mapping, event forwarding, and fault-injection feature behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/device.rs -->
