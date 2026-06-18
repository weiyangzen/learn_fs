# sources/distributed-fs/ceph-client/tools/include/uapi/linux/mount.h

Purpose: defines mount API flags and structures for legacy `mount(2)` flags and the newer file-descriptor-based mount API (`fsopen`, `fsconfig`, `fsmount`, `move_mount`, `open_tree`, `mount_setattr`, and mount ID queries).

Important APIs/types: legacy `MS_*` flags cover read-only, nosuid, nodev, noexec, sync, remount, mandlock, dirsync, noatime, nodiratime, bind, move, recursive, silent, POSIX ACL, unbindable/private/slave/shared propagation, relatime, strictatime, lazytime, and active/no-user internal bits. New API flags include `OPEN_TREE_*`, `MOVE_MOUNT_*`, `FSMOUNT_*`, `FSCONFIG_*`, `MOUNT_ATTR_*`, and lookup flags. Structures include `mount_attr`, `mnt_id_req`, and `statmount` with masks for mount attributes, propagation, IDs, fs type, root, point, options, and namespace ID.

Control flow, state, and persistence: userspace opens/configures a filesystem context, creates a detached mount, moves/attaches it, or changes attributes recursively. Kernel mutates namespace mount topology and per-mount attributes; state persists in the mount namespace until unmounted or namespace teardown.

Dependencies and integration points: depends on Linux types. Integrates VFS, containers, namespace setup, systemd-style mount management, idmapped mounts, and filesystem configuration.

Risks and test signals: risks include confusing superblock flags with per-mount attributes, recursive propagation mistakes, mount namespace races, incompatible lookup/empty-path semantics, and structure size extension handling. Tests should cover legacy and new mount flows, bind/move/recursive attributes, idmapped mount userns fds, statmount queries with variable string buffers, and permission failures in user namespaces.
