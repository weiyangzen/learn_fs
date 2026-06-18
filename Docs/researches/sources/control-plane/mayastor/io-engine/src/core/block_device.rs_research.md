<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/block_device.rs -->
## sources/control-plane/mayastor/io-engine/src/core/block_device.rs

### Purpose
`block_device.rs` defines the core block-device abstraction traits and shared I/O statistics types. It is a boundary between high-level nexus/replica code and concrete SPDK-backed devices.

### Important APIs, Types, And Functions
`BlockDeviceIoStats` is a mergeable counter/latency struct. `BlockDeviceIoErrorStats` aliases SPDK error stats. `BlockDevice` describes device metadata, open, stats, I/O controller, and event-listener operations. `BlockDeviceDescriptor` models an opened descriptor. `BlockDeviceHandle` defines DMA allocation, read/write/compare/reset/unmap/write-zeroes/flush, NVMe admin and reservation operations, snapshot creation, passthrough, host ID, and controller-failure checks. `ReadOptions`, callback type aliases, `DeviceTimeoutAction`, and `DeviceIoController` complete the API.

### Control Flow
The trait supplies async convenience wrappers around callback-style I/O methods. Each wrapper creates a oneshot channel, submits the callback operation with `block_device_io_completion`, awaits completion, and converts non-success status into the corresponding `CoreError` with offset and length context. Default NVMe reservation and passthrough methods return not-supported errors unless an implementation overrides them.

### State, Persistence, And Dependencies
This file stores no concrete state but defines how implementations expose state. `BlockDeviceIoStats` uses saturating merge strategies, allowing aggregation. Dependencies include `spdk_rs` DMA buffers and I/O vectors, futures oneshot channels, `nix::errno`, `uuid`, `merge`, and core error/status types.

### Risks And Test Signals
The async wrappers `expect` successful oneshot receipt; dropped callbacks panic. Caller comments require I/O vector lengths to match block counts but the trait cannot enforce it. `ticks_to_time` users elsewhere depend on nonzero tick rate from stats. Tests should cover success and failure completion mapping for read/write/compare, callback drop behavior, unsupported NVMe default methods, merge saturation, and implementation conformance for block sizing and alignment.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/block_device.rs -->
