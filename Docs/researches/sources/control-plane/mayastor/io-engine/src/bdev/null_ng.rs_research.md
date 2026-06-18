## sources/control-plane/mayastor/io-engine/src/bdev/null_ng.rs

### Purpose
`null_ng.rs` is a newer SPDK Rust-module example for a null bdev. It demonstrates `spdk_rs` module, bdev, I/O device, channel, and poller abstractions rather than the older C null bdev FFI path.

### Important APIs, Types, And Functions
`NullIoPollerData` queues pending `BdevIo` objects behind a mutex. `NullIoChannelData` owns a poller that drains queued I/O every millisecond and completes each as success. `NullIoDevice` implements `IoDevice` and `BdevOps`. `NullBdevModule` implements module registration via `WithModuleInit` and `BdevModuleBuild`; `register()` registers the module named `NullNg`.

### Control Flow
`submit_request()` pushes read and write I/O into the channel poller queue and fails unsupported I/O. The poller drains all queued I/O and calls `ok()` on each completion. `destruct()` unregisters the I/O device. The example `create()` builder is present but not called by module init; `module_init()` currently returns success without creating a device.

### State, Persistence, And Dependencies
All state is runtime-only. Per-channel state tracks a poller and synthetic channel id; per-device state tracks a next channel id in a `RefCell`. Dependencies are `spdk_rs` traits and wrappers, `parking_lot::Mutex`, `RefCell`, and SPDK bdev module registration.

### Integration Points
The file registers a module but does not expose a URI adapter in this source. It is likely experimental or demonstrative infrastructure for future Rust-native bdev modules.

### Risks
`unsafe impl Send` is used because `BdevIo` contains `NonNull`; correctness relies on the poller/channel execution model. The builder sets required alignment to 12, which is unusual and should be validated if activated. The create log typo is harmless, but the inactive `create()` path means registering this module alone creates no usable device.

### Test Signals
Tests or examples should verify module registration, manual `NullIoDevice::create()`, read/write completion through the poller, unsupported I/O failure, channel create/destroy behavior, destruct unregistering the I/O device, and thread-safety assumptions around queued `BdevIo`.
