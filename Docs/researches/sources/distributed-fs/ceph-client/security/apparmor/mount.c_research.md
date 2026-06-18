# sources/distributed-fs/ceph-client/security/apparmor/mount.c

Purpose: mediates mount, remount, bind, move, propagation-change, unmount, and pivotroot operations against AppArmor mount policy.

Important functions: `audit_mnt_flags()`, `audit_mount()`, `match_mnt_flags()`, `do_match_mnt()`, `match_mnt_path_str()`, `match_mnt()`, `aa_remount()`, `aa_bind_mount()`, `aa_mount_change_type()`, `aa_move_mount()`, `aa_move_mount_old()`, `aa_new_mount()`, `aa_umount()`, `build_pivotroot()`, and `aa_pivotroot()`.

Control flow: LSM mount hooks normalize mount flags and select an operation helper. Helpers allocate pathname buffers, resolve mountpoint/source paths where needed, determine binary mount-data handling from filesystem flags, and run each confined profile through a DFA sequence: mountpoint, null, source, null, type, null, ordered flags, optional data, then permission lookup. Pivotroot can build and install a replacement label after successful policy match.

State and persistence: no standalone persistent state; decisions use profile rules, path flags, global path buffers, current labels, and VFS path refs. Pivotroot may persistently change the current label.

Dependencies and integration: depends on path lookup, DFA matching, file system type lookup, audit, domain label replacement, and LSM mount hooks. Risks include path lookup failure semantics, binary data non-matching, flag normalization, source path resolution for detached mounts, and pivotroot transition auditing gaps. Test all mount modes, missing device on `FS_REQUIRES_DEV`, bind/move with disconnected paths, binary mount data, propagation flags, unmount auditing, and pivotroot label transitions.
