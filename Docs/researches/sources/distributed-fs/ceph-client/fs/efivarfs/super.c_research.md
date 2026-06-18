<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/super.c -->
# sources/distributed-fs/ceph-client/fs/efivarfs/super.c

## Purpose
`super.c` registers and mounts efivarfs, populates the root directory from firmware EFI variables, maintains superblock flags as EFI write support changes, supports uid/gid mount options, reports firmware storage capacity, and resynchronizes after freeze/thaw.

## Important APIs, types, and functions
Important functions include `efivarfs_fill_super`, `efivarfs_get_tree`, `efivarfs_init_fs_context`, `efivarfs_reconfigure`, `efivarfs_kill_sb`, `efivarfs_create_dentry`, `efivarfs_callback`, `efivarfs_check_missing`, `efivarfs_freeze_fs`, `efivarfs_unfreeze_fs`, dentry hash/compare helpers, and `efivarfs_statfs`. The file defines `efivarfs_type` and `efivarfs_ops`.

## Control flow
Mount context allocation checks `efivar_is_available`, initializes root uid/gid defaults, and installs fs-context operations. Fill-super sets block sizes, magic, dentry operations, read-only status when firmware lacks writes, creates the root inode, registers an EFI ops notifier, and enumerates firmware variables through `efivar_init`, creating persistent dentries for each non-random-seed variable. Dentry comparison treats variable names case-sensitive and GUID suffixes case-insensitive. Freeze is a no-op; unfreeze scans existing dentries to refresh sizes/remove vanished variables, then enumerates firmware to create missing dentries.

## State and persistence
Runtime superblock state includes mount options, notifier block, root dentry tree, dentry hash rules, and read-only flag. Persistent state is firmware NVRAM; dentries are cached projections and may be resynced after thaw or EFI ops mode changes.

## Dependencies and integration points
It depends on EFI runtime variable APIs, fs_context, simple/persistent dentry helpers, blocking notifier chain `efivar_ops_nh`, statfs, suspend freeze integration, and GUID/UTF-8 conversion helpers.

## Risks and test signals
Risks include duplicate firmware variable loops, stale dentries after external firmware changes, read-only flag races, notifier lifetime on mount failure, mount option parsing errors, and case-sensitive/case-insensitive dentry hash mismatches. Test signals include mount/unmount on EFI systems, uid/gid options, remount rw when SetVariable is unavailable, statfs with and without QueryVariableInfo, freeze/thaw resync, duplicate variable firmware behavior, and GUID-case lookup aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/super.c -->
