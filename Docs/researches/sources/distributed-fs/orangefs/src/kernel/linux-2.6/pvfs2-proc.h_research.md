# sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-proc.h

## Purpose
`pvfs2-proc.h` declares the proc/sysctl lifecycle hooks for the OrangeFS kernel module.

## Important APIs
`pvfs2_proc_initialize(void)` registers `/proc/sys/pvfs2` controls when `CONFIG_SYSCTL` support is compiled in. `pvfs2_proc_finalize(void)` unregisters that table. Both are implemented in `pvfs2-proc.c` and called by `pvfs2-mod.c` during module load/unload and error unwinding.

## Control flow, state, and integration
The header carries no state. It lets module initialization remain independent of the internal sysctl table definitions. The implementation internally tracks registration with a `struct ctl_table_header *`, making initialize/finalize idempotent around a non-NULL header.

## Dependencies and risks
There are no direct includes beyond the guard, so this header has a narrow dependency surface. The main risk is lifecycle ordering: callers must initialize operation caches and device request infrastructure before registering handlers that can issue client upcalls, and must unregister before destroying those dependencies.

## Test signals
Tests should verify successful registration on module load, cleanup on load failure after registration, cleanup on normal unload, and no exported proc entries when `CONFIG_SYSCTL` is disabled.
