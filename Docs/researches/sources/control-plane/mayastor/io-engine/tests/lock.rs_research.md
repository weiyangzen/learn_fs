# sources/control-plane/mayastor/io-engine/tests/lock.rs

Purpose: unit/integration tests for the async `ResourceLockManager` at global, subsystem, and resource granularity, including try-lock and timeout behavior.

Important APIs/types/functions: `LockLevel` selects global/subsystem/resource locks. `get_lock_manager` initializes manager config with subsystem `items`. `test_lock_level` runs two tasks contending for the same lock and verifies try-lock fails while held. `test_lock_timed_level` verifies timeout returns no guard.

Control flow: first task acquires lock, attempts nonblocking double-lock, signals second task, sleeps while protected counter should remain unchanged, then drops guard. Second task waits for signal and then acquires after release. Timed variant uses a 1 second timeout while the holder sleeps 2 seconds.

State and persistence: process-global `ResourceLockManager` singleton. Atomic `STEP_COUNT` is reset per non-timed helper invocation.

Dependencies and integration points: Tokio task scheduling, oneshot channels, lock manager config/subsystem/resource APIs.

Risks and edge cases: timing sleeps make the tests sensitive to very slow runtimes. Singleton initialization means config changes in other tests could matter if run in same process.

Test signals: covers serialization, nonblocking acquisition, and timeout semantics for all lock levels.
