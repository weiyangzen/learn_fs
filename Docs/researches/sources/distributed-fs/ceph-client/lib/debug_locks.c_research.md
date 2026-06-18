# sources/distributed-fs/ceph-client/lib/debug_locks.c

## Purpose
Provides shared global controls for kernel lock debugging facilities so lockdep and related lock validators can disable noisy follow-on reports after the first detected problem.

## APIs, Types, and Functions
Exports `int debug_locks`, initially enabled, and `int debug_locks_silent`, used by tests to suppress console output. `debug_locks_off()` calls `__debug_locks_off()`, optionally raises console verbosity, and returns whether it performed the first transition to disabled state.

## Control Flow
Callers detect a lock debugging failure and invoke `debug_locks_off()`. If debugging is still enabled and the lower-level atomic off operation succeeds, the function may call `console_verbose()` unless silent mode is set, then returns `1`. Later calls return `0`.

## State and Persistence
`debug_locks` and `debug_locks_silent` are global `__read_mostly` state. Once `debug_locks` is turned off, it remains off for the running kernel unless explicitly reset by test code or reinitialization paths.

## Dependencies and Integration Points
Depends on rwsem, mutex, spinlock, export, and debug-lock headers. It is shared by spinlock, mutex, rwsem, and lockdep debugging code and by the lock test suite.

## Risks and Test Signals
Risks include races in global disable handling, losing first-failure diagnostics if silent mode is misused, and excessive console verbosity if repeated failures are not suppressed. Test signals include lockdep selftests, intentional lock misuse tests, exported-symbol users, and checks that only the first failure toggles the global state.
