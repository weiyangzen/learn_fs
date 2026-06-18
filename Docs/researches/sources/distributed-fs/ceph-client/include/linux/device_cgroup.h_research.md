# sources/distributed-fs/ceph-client/include/linux/device_cgroup.h

Purpose: Defines device-cgroup permission helpers for block/character device access and mknod checks, with optional cgroup-BPF integration.

Important APIs, types, and functions: Defines access bits `DEVCG_ACC_MKNOD`, `DEVCG_ACC_READ`, `DEVCG_ACC_WRITE`, device type bits `DEVCG_DEV_BLOCK`, `DEVCG_DEV_CHAR`, `DEVCG_DEV_ALL`, `devcgroup_check_permission()`, `devcgroup_inode_permission()`, and `devcgroup_inode_mknod()`.

Control flow: VFS permission paths call `devcgroup_inode_permission()` for block/char inodes with read/write masks; mknod paths call `devcgroup_inode_mknod()` with mode and device number. Helpers classify block versus character devices, ignore non-device inodes and whiteouts, translate mask bits to access bits, and delegate to `devcgroup_check_permission()`. Disabled builds allow all access.

State and persistence: Permission policy state lives in device cgroup and/or cgroup BPF subsystems, not this header. Helpers operate on transient inode/mknod inputs.

Dependencies and integration points: Depends on VFS inode mode/device helpers, `WHITEOUT_DEV`, cgroup device controller, and cgroup BPF. Integrated into filesystem permission and mknod enforcement.

Risks and test signals: Risks include failing to exempt overlay whiteouts, wrong major/minor extraction, read/write mask under-enforcement, and disabled-config behavior diverging from policy expectations. Test block and char read/write/mknod permissions, wildcard policies, cgroup BPF hooks, overlay whiteout creation, non-device inodes, and configs without device cgroups.
