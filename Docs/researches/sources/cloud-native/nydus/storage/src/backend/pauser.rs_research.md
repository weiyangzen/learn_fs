# sources/cloud-native/nydus/storage/src/backend/pauser.rs

## Purpose
This utility module implements a process-local pauser that can block participating threads until a configured pause deadline expires or is cleared.

## Important APIs, Types, and Functions
`Pauser` is a cloneable wrapper around `Arc<Mutex<PauserInner>>` and `Arc<Condvar>`. `set_pause` sets or replaces the pause deadline. `clear_pause` removes it. `wait` blocks until no pause is active and returns the time spent waiting. `is_paused` and `status` expose non-blocking state checks. `Default` delegates to `new`.

## Control Flow
Callers invoke `wait` at participation points. It locks state, compares `pause_until` with `Instant::now`, clears expired pauses, or waits on the condition variable for the remaining duration. `set_pause` and `clear_pause` notify all waiters after updating state.

## State and Persistence Behavior
All state is in-memory. There is no durable pause state across process restarts. A new pause replaces any existing deadline regardless of whether it is shorter or longer.

## Dependencies and Integration Points
The global `BACKEND_PAUSER` in `mod.rs` exposes this mechanism to backend users. The module only depends on standard library synchronization and time primitives.

## Risks
Callers must explicitly call `wait`; the pauser does not intercept backend operations automatically. `is_paused` and `status` do not clear expired pause state, so they can report not paused while leaving `pause_until` set until a later `wait` or replacement. Mutex poisoning is unhandled via `unwrap`.

## Test Signals
Tests cover creation, setting, clearing, immediate waits, timed waits, concurrent wait release, repeated pauses, pause replacement, concurrent setters, non-blocking status, and late pause behavior after waiters have already passed.
