# sources/distributed-fs/ceph-client/kernel/locking/test-ww_mutex.c

## Purpose
Provides a loadable kernel selftest for the wound/wait mutex API. It validates basic mutual exclusion, recursive/self acquisition rejection, ABBA deadlock detection, slowpath recovery, cyclic dependency recovery, and stress behavior for both wound-wait and wait-die ww classes.

## Important APIs, Types, And Functions
The module defines `wd_class` and `ww_class`, a global unbound workqueue, and sysfs attribute `run_tests`. Core tests are `test_mutex`, `test_aa`, `test_abba`, `test_cycle`, and `stress`. Worker helpers include `test_mutex_work`, `test_abba_work`, `test_cycle_work`, `stress_inorder_work`, `stress_reorder_work`, and `stress_one_work`. It exercises `ww_mutex_lock`, `ww_mutex_trylock`, `ww_mutex_lock_slow`, `ww_mutex_unlock`, `ww_acquire_init`, and `ww_acquire_fini`.

## Control Flow
`test_ww_mutex_init` seeds the random state, creates the workqueue and `/sys/kernel/test_ww_mutex/run_tests`, then runs all test classes once. A sysfs write reruns the same suite under `run_lock`. The suite first checks ordinary mutual exclusion, then self-acquire behavior, then ABBA and multi-thread cycles with and without slowpath resolution, followed by timed stress loops over randomized lock orders.

## State And Persistence
State is transient: stack-allocated test structures, allocated stress arrays, random order arrays, completions, and the workqueue. The only persistent runtime interface is the sysfs kobject/attribute until module unload.

## Dependencies And Integration Points
Depends on kernel workqueues, completions, random state, sysfs kobjects, module init/exit, and `linux/ww_mutex.h`. It integrates with debug ww mutex deadlock injection by disabling injection in deterministic deadlock tests when `CONFIG_DEBUG_WW_MUTEX_SLOWPATH` is set.

## Risks And Edge Cases
The tests are timing-sensitive because they use short completion timeouts and concurrent workqueue scheduling. Stress coverage may miss rare races because failures are logged with `pr_err_once`. The ABBA and cycle tests rely on completions ordering worker progress correctly. Memory allocation failures are handled, but a failed stress helper allocation can silently reduce coverage.

## Test Signals
Useful signals are module load success, `All ww mutex selftests passed`, no WARNs from `READ_ONCE(mutex.ctx)` checks, and clean sysfs reruns. Failures log specific scenarios such as mutual exclusion failure, missed ABBA deadlock, unresolved cyclic deadlock, or stress worker errors.
