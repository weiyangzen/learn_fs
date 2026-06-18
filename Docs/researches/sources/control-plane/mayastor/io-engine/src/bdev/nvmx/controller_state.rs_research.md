## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/controller_state.rs

### Purpose
`controller_state.rs` defines the NVMe controller lifecycle state machine and an exclusive flag mechanism used for reset serialization.

### Important APIs, Types, And Functions
`NvmeControllerState` has `New`, `Initializing`, `Running`, `Faulted(reason)`, `Unconfiguring`, and `Unconfigured`. `ControllerFailureReason` distinguishes reset, shutdown, and namespace initialization failures. `ControllerFlag` currently contains `ResetActive`. `ControllerStateMachine` exposes `transition()`, `transition_checked()`, `current_state()`, `set_flag_exclusively()`, and `clear_flag_exclusively()`.

### Control Flow
`check_transition()` enforces allowed state changes: new to initializing, initializing to running or faulted, running to unconfiguring or faulted, unconfiguring to unconfigured or faulted, faulted to running/unconfiguring/faulted, and no transitions out of unconfigured. Flag updates use atomic compare-exchange against the single stored boolean.

### State, Persistence, And Dependencies
State is in-memory only. The state machine stores a controller name for logs, the current enum value, and one atomic flag. Dependencies are `crossbeam::atomic::AtomicCell`, `snafu`, and `strum` display derivation.

### Integration Points
`controller.rs` uses state transitions to gate attach, namespace faulting, reset, shutdown, and drop safety. Reset code uses `ResetActive` to reject concurrent resets and assert that the reset owner clears the flag.

### Risks
Only one boolean flag is implemented, so adding more `ControllerFlag` values without changing `lookup_flag()` would alias them. `transition_checked()` reports the expected state as `current_state` in its error rather than the actual current state, which can make diagnostics confusing. Recovering from `Faulted` directly to `Running` is allowed and should remain deliberate.

### Test Signals
Tests should enumerate valid and invalid transitions, display strings, transition_checked mismatch behavior, exclusive flag set/clear success and failure, final-state immutability, and future multiple-flag expansion.
