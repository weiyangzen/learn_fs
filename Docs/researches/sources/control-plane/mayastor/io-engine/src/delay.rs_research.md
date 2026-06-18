# sources/control-plane/mayastor/io-engine/src/delay.rs

## Purpose
Registers an SPDK poller that sleeps periodically to reduce CPU usage in non-performance contexts such as unit tests.

## Important APIs, Types, and Functions
- `register()` registers a poller that calls `sleep` every 1000 us and records the poller pointer in thread-local state.
- `unregister()` unregisters the saved poller if present.
- `sleep` sleeps the current thread for 1 ms and returns success.

## Control Flow and State
Each thread has a `DELAY_POLLER` `RefCell<Option<*mut spdk_poller>>`. Registering warns, calls `spdk_poller_register`, and panics on double registration for that thread. Unregistering takes the pointer and passes it to `spdk_poller_unregister`.

State is thread-local SPDK poller registration. There is no persistence.

## Dependencies and Integration Points
Depends on SPDK poller APIs. Related to developer delay mode in reactor/environment options, though reactor-level delay is also implemented directly in `reactor.rs`.

## Risks and Test Signals
Register does not check for null poller return. Double registration panics. The sleep blocks the reactor thread and intentionally degrades responsiveness. Tests should cover register/unregister lifecycle, double register panic, and no warning about leaked pollers at shutdown.
