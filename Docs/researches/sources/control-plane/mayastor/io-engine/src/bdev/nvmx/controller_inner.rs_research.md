## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/controller_inner.rs

### Purpose
`nvmx/controller_inner.rs` provides low-level controller wrappers and timeout handling for the Rust-native NVMe path. It translates configured timeout actions into abort, reset, hot-remove, or ignore behavior and wraps raw SPDK controller pointers.

### Important APIs, Types, And Functions
`DeviceTimeoutAction::try_from(u32)` maps SPDK config values plus hot-remove value `4`. `TimeoutConfig` holds atomically accessed timeout action, reset flags, SPDK controller wrapper, reset cooldown state, destroy/failure-report flags, and adminq-broken tracking. `SpdkNvmeController` wraps `NonNull<spdk_nvme_ctrlr>`. `DeviceIoController for NvmeController` exposes timeout action get/set. `NvmeController::configure_timeout()` registers SPDK timeout callbacks.

### Control Flow
Timeout callbacks call `io_timeout_handler()`, inspect the configured action and qpair, optionally escalate abort to reset, and either issue an abort command, reset the controller, hot-remove it, or ignore the timeout. `reset_controller()` is intended to serialize reset attempts, apply a cooldown after failures, and invoke `NvmeController::reset()` with `TimeoutConfig::reset_cb`. Admin queue polling uses `process_adminq()` and helper flags to report controller failure or adminq broken events only once. Hot-remove calls the controller hot-remove path, which fails the SPDK controller and resets channels.

### State, Persistence, And Dependencies
Timeout state is in-memory and uses `AtomicCell` for callback-path access without locking. The wrapped SPDK controller pointer is installed after attach. Dependencies include global `NVME_CONTROLLERS`, configured `nvme_bdev_opts`, SPDK timeout/admin/abort/fail APIs, `DeviceIoController`, and `DeviceTimeoutAction`.

### Integration Points
`controller.rs` owns allocation/drop of `TimeoutConfig` and passes its pointer to the adminq poller and SPDK timeout callback. `device.rs` lets users adjust timeout action through the block-device I/O controller.

### Risks
`reset_controller()` returns immediately when `compare_exchange(false, true).is_ok()`, which appears inverted for initiating an exclusive reset and may prevent resets from starting when the flag was successfully acquired. Raw pointer lifetime is critical because SPDK callbacks hold `TimeoutConfig` pointers. `SpdkNvmeController` exposes deref to mutable SPDK internals and is marked copyable, so use-after-detach must be prevented by lifecycle state.

### Test Signals
Cover timeout-action parsing, configure with zero timeout, abort success and abort failure escalation, reset cooldown, concurrent timeout callbacks, hot-remove path, adminq broken timeout threshold, one-shot failure reporting, `SpdkNvmeController` null handling, and the reset flag compare-exchange behavior.
