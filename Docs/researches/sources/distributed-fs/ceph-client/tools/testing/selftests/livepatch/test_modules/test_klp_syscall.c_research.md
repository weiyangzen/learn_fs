# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_syscall.c

## Purpose

`test_klp_syscall.c` livepatches the architecture-specific `sys_getpid` wrapper and tracks a configured set of PIDs until each has executed the patched function.

## Important APIs, Types, and Functions

It defines architecture-dependent `FN_PREFIX`, mutex `kpid_mutex`, module parameter array `klp_pids`, sysfs read-only attribute `npids`, replacement `lp_sys_getpid()`, `klp_func` for `sys_getpid`, and init/exit functions that create/remove a kobject.

## Control Flow and State

On load, it creates `/sys/kernel/test_klp_syscall/npids`, records the initial PID count, and enables the patch. Each patched `getpid` call locks the mutex, checks whether the current PID is pending, clears its slot, decrements `npids_pending`, and returns `task_tgid_vnr(current)`. Exit drops the kobject.

## Dependencies and Integration Points

It depends on livepatch syscall symbol naming, sysfs, module parameter arrays, and `test-syscall.sh`.

## Risks and Test Signals

Risks include wrong symbol prefix for an architecture, `NR_CPUS` limiting parameter count, mutex contention, or sysfs lifetime bugs on load failure. Signals are `npids` reaching 0 and helpers continuing to receive valid getpid results.
