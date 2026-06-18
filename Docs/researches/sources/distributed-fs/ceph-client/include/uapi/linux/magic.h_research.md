# sources/distributed-fs/ceph-client/include/uapi/linux/magic.h

Purpose: publishes filesystem and pseudo-filesystem magic numbers used by `statfs(2)`, filesystem detection tools, and kernel/userspace ABI checks.

Important APIs and types: constants cover many on-disk and virtual filesystems, including `CEPH_SUPER_MAGIC`, `EXT*_SUPER_MAGIC`, `BTRFS_SUPER_MAGIC`, `FUSE_SUPER_MAGIC`, `NFS_SUPER_MAGIC`, `CIFS_SUPER_MAGIC`, `SMB2_SUPER_MAGIC`, `PROC_SUPER_MAGIC`, `SYSFS_MAGIC`, `BPF_FS_MAGIC`, `ZONEFS_MAGIC`, `GUEST_MEMFD_MAGIC`, and many legacy filesystem identifiers. Some entries are string magic values for ReiserFS variants.

Control flow: no executable flow. Callers compare returned magic values from `statfs`/`statx`-adjacent logic or on-disk probes to identify filesystems or special pseudo-filesystems.

State and persistence: no state. Numeric values are ABI identifiers and must remain stable.

Dependencies and integration points: standalone UAPI header used by filesystem utilities, mount helpers, container runtimes, sandboxes, backup tools, and kernel code exposing filesystem type values.

Risks and test signals: risks are collisions, accidental renumbering, confusing superblock magic with on-disk probe strings, and missing new filesystem constants. Test `statfs` magic comparisons for representative mounted filesystems, userspace build compatibility, and uniqueness/static analysis of assigned values.
