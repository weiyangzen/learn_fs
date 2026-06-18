<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/kernfs/Kconfig

## Purpose
This Kconfig fragment declares `CONFIG_KERNFS`, the internal pseudo-filesystem infrastructure used by sysfs-like kernel filesystems.

## Important APIs, types, and functions
It defines one boolean symbol, `KERNFS`, with default `n`. There are no functions or types in this file.

## Control flow
`KERNFS` is intended to be selected by users rather than manually enabled. Build inclusion is controlled by other Kconfig entries that depend on kernfs services.

## State and persistence behavior
There is no runtime state or persistent data. The symbol controls whether kernfs objects from this directory are compiled into the kernel.

## Dependencies and integration points
Subsystems such as sysfs or cgroupfs-style users select this symbol to receive the kernfs object model, mount support, inode/file/dir/symlink operations, and namespace-aware directory infrastructure.

## Risks and test signals
Risks are build configuration mistakes: forgetting to select `KERNFS` from a user, or exposing it as a user-facing option unintentionally. Test signals are allyesconfig/allmodconfig builds, minimal configs containing sysfs/cgroup users, and dependency audits ensuring every kernfs caller selects the symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/Kconfig -->
