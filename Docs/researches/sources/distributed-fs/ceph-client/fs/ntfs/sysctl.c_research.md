# sources/distributed-fs/ceph-client/fs/ntfs/sysctl.c

## Purpose
Provides optional debug sysctl registration for the legacy `ntfs` driver. The code is compiled only under `DEBUG` and `CONFIG_SYSCTL`, exposing a writable integer knob under `fs/ntfs/ntfs-debug` that controls `debug_msgs`.

## Important APIs, Types, And Functions
`ntfs_sysctls[]` is a `ctl_table` with `proc_dointvec` for integer debug-message control. `sysctls_root_table` stores the registration handle. `ntfs_sysctl(int add)` registers the table when `add` is nonzero and unregisters it when `add` is zero.

## Control Flow
`super.c` calls `ntfs_sysctl(1)` during module initialization after slab caches are created and before filesystem registration. On module exit or init rollback, it calls `ntfs_sysctl(0)`. Registration failure returns `-ENOMEM`, causing module initialization to unwind.

## State And Persistence
No disk state is touched. Runtime state is limited to the sysctl header pointer and the global debug integer referenced from `debug.h`. The sysctl is process-visible through procfs while the module is loaded.

## Dependencies And Integration Points
Depends on kernel sysctl/procfs support, `debug_msgs`, and the module initialization path in `super.c`. If `DEBUG` or `CONFIG_SYSCTL` is missing, this file contributes no executable code and `sysctl.h` supplies a success stub.

## Risks And Edge Cases
The unregister path assumes the stored header pointer is valid or NULL-safe for the active kernel API. Double unregister would be unsafe if callers violated the module lifecycle, but normal init/exit sequencing prevents it.

## Test Signals
Build with and without `DEBUG`/`CONFIG_SYSCTL`, verify `/proc/sys/fs/ntfs/ntfs-debug` appears only in the debug build, confirm writes update debug verbosity, and inject registration failure to verify slab cleanup in `init_ntfs_fs()`.
