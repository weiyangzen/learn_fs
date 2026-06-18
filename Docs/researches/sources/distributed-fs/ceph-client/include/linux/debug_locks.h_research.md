# sources/distributed-fs/ceph-client/include/linux/debug_locks.h

Purpose: Declares global lock-debugging controls and wrappers used by lockdep and related debug code to report locking bugs once and then disable further lock debugging.

Important APIs, types, and functions: Exposes `debug_locks`, `debug_locks_silent`, `__debug_locks_off()`, `debug_locks_off()`, `DEBUG_LOCKS_WARN_ON()`, `SMP_DEBUG_LOCKS_WARN_ON()`, optional `locking_selftest()`, and lockdep helpers `debug_show_all_locks()`, `debug_show_held_locks()`, `debug_check_no_locks_freed()`, and `debug_check_no_locks_held()`.

Control flow: A debug check calls `DEBUG_LOCKS_WARN_ON(condition)`. If the system is not already in an oops and the condition is true, instrumentation is bracketed, `debug_locks_off()` atomically disables further lock debugging, and a warning is emitted unless silenced. SMP and lockdep-specific helpers compile to no-ops when unavailable.

State and persistence: Global in-memory state records whether lock debugging remains active and whether warnings should be silent. No persistence exists beyond logs.

Dependencies and integration points: Depends on atomic exchange, cacheline read-mostly storage, instrumentation guards, `oops_in_progress`, WARN infrastructure, SMP config, lockdep, and locking selftests.

Risks and test signals: Risks include disabling diagnostics too early, warning from unsafe instrumentation contexts, missing no-op coverage on non-lockdep builds, and false positives from freed-lock memory. Test lockdep selftests, SMP-only warnings, non-SMP builds, lock-free checks during object freeing, and repeated failure suppression.
