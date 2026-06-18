# sources/distributed-fs/ceph-client/fs/sysctls.c

## Purpose
This small file registers shared `/proc/sys/fs` sysctls for overflow UID and GID values used by filesystems that need to map unrepresentable ownership.

## Important APIs, Types, and Functions
It defines `fs_shared_sysctls[]` with `overflowuid` backed by `fs_overflowuid` and `overflowgid` backed by `fs_overflowgid`. Both use `proc_dointvec_minmax`, mode `0644`, minimum `SYSCTL_ZERO`, and maximum `SYSCTL_MAXOLDUID`. `init_fs_sysctls()` registers the table under `"fs"` and is scheduled by `early_initcall`.

## Control Flow and State
At early init, `register_sysctl_init("fs", fs_shared_sysctls)` installs the two integer controls. Runtime reads and writes are handled by the proc sysctl core, which enforces integer bounds.

## Persistence, Dependencies, and Integration
The values are kernel globals rather than on-disk filesystem state. They integrate with VFS ownership mapping paths and proc sysctl infrastructure. Settings are mutable at runtime and may be persisted only by userspace sysctl configuration.

## Risks and Test Signals
Risk is mainly misconfiguration: changing overflow IDs can affect ownership presentation for legacy or unmappable IDs. Tests should verify sysctl registration, permissions, min/max enforcement, and behavior of ownership display paths that fall back to overflow IDs.
