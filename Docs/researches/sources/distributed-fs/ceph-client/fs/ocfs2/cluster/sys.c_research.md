# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/sys.c

## Purpose
`sys.c` creates the O2CB sysfs root under `/sys/fs/o2cb`, exposes the nodemanager interface revision, and attaches the logmask sysfs group.

## Important APIs, types, and functions
Public functions are `o2cb_sys_init` and `o2cb_sys_shutdown`. The `interface_revision` attribute is implemented by `version_show` and reports `O2NM_API_VERSION`.

## Control flow
Initialization creates the `o2cb` kset under `fs_kobj`, adds the interface revision group, then initializes masklog sysfs under the same kset. Shutdown unregisters masklog and the kset.

## State and persistence behavior
Runtime state is the `o2cb_kset` pointer and registered sysfs attributes. It is not persistent; userspace observes it while the module is loaded.

## Dependencies and integration points
It depends on kobject/sysfs APIs, `fs_kobj`, nodemanager ABI constants, and masklog sysfs initialization. `nodemanager.c` calls it during module init/exit.

## Risks and test signals
Risks include init unwind leaving partial sysfs state, shutdown ordering with masklog, and userspace depending on revision format. Test signals include module load/unload, sysfs read of `interface_revision`, masklog file presence, and simulated `sysfs_create_group`/`mlog_sys_init` failure paths.
