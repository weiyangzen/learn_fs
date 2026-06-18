# sources/distributed-fs/ceph-client/lib/locking-selftest.c

Purpose: boot-time/selftest-style lockdep test suite for spinlocks, rwlocks, mutexes, rwsems, ww_mutexes, rtmutexes, local locks, wait contexts, fs reclaim, IRQ safety, and nested lock classes.

Important APIs/types/functions: `locking_selftest()`, `dotest()`, `reset_locks()`, generated testcase macros, lock operation shortcuts `L/WL/RL/ML/WSL/RSL/RTL`, IRQ simulation macros, `ww_tests()`, `queued_read_lock_tests()`, `fs_reclaim_tests()`, `wait_context_tests()`, `local_lock_tests()`, and `lockdep_set_subclass_name_test()`.

Control flow: the file defines generic event bodies, repeatedly includes tiny adapter headers to bind `LOCK`/`UNLOCK`/IRQ macros, and generates many permutations. `locking_selftest()` initializes shared lock classes, marks the current task as selftest, runs expected-success and expected-failure matrices, resets lockdep state after each case, and summarizes unexpected failures. `dotest()` silences or prints lockdep output, runs a case, compares `debug_locks` to the expected result, restores preempt/RT/RCU/IRQ accounting, then calls `reset_locks()`.

State/persistence: uses many static lock objects, ww acquire contexts, counters for total/success/expected/unexpected failures, `debug_locks`, `debug_locks_silent`, `force_read_lock_recursive`, lockdep class keys, and per-cpu local lock state.

Dependencies/integration: deeply tied to lockdep, irqflags tracing, PREEMPT_RT behavior, ww_mutex internals, fs reclaim annotations, local locks, and raw lock nesting options.

Risks: tests intentionally trigger invalid locking and must repair corrupted preempt/RCU state. Config-specific behavior is complex. A real locking failure before the suite disables it. Incorrect expected matrices can either hide regressions or disable debug locks.

Test signals: kernel log table output, expected-failure counts, and absence of unexpected failures. The suite sets `debug_locks` back to 1 only when results match expectations.
