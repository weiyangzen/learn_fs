# File Research: sources/cow-pools/openzfs/module/zfs/zfs_replay.c

## Summary
Implements ZIL replay for ZPL operations. It decodes log records, rebuilds vattr/xvattr/FUID/ACL context, claims logged object numbers and dnode sizes, and invokes the normal ZFS file operation paths to recreate logged filesystem mutations.

## Main Responsibilities
- Convert logged create, mkdir, symlink, xattr-dir, remove, rmdir, link, rename, write, truncate, setattr, ACL, SA-xattr, whiteout, exchange rename, and clone-range records into ZPL operations.
- Decode extended attributes, creation times, scanstamp/project-id shared fields, and FUID domain tables from variable-length log payloads.
- Handle byte-swapped log records.
- Preserve logged object identity by using `dnode_try_claim()` before replaying creates and whiteouts.
- Maintain replay progress through `zil_replaying()` where needed.

## Key APIs
- `zfs_replay_vector`.
- `zfs_replay_create()`, `zfs_replay_create_acl()`.
- `zfs_replay_remove()`, `zfs_replay_link()`, `zfs_replay_rename()`.
- `zfs_replay_write()`, `zfs_replay_write2()`, `zfs_replay_truncate()`.
- `zfs_replay_setattr()`, `zfs_replay_setsaxattr()`.
- `zfs_replay_acl_v0()`, `zfs_replay_acl()`.
- `zfs_replay_clone_range()`.

## Important Behavior
Create replay smuggles logged creation time, generation, and dnode slot size through otherwise unused `vattr_t` fields because the generic create path does not expose those parameters directly. It then dispatches to `zfs_create()`, `zfs_mkdir()`, `zfs_make_xattrdir()`, or `zfs_symlink()`.

Write replay distinguishes immediate write payloads from `dmu_sync()` block records. Whole-block replay may temporarily write beyond current EOF and pass the intended EOF through `zfsvfs->z_replay_eof`; `TX_WRITE2` only extends the file size when earlier synced block data is already present.

SA xattr replay loads or creates the cached nvlist, applies add/update/remove from the log record, limits value and total SA sizes, calls `zfs_sa_set_xattr()`, and drops the inconsistent cache if persistence fails.

ACL replay handles both old fixed ACE records and modern FUID-aware ACE records. For modern records it reconstructs `z_fuid_replay` so ephemeral IDs embedded in ACEs can be remapped during `zfs_setsecattr()`.

Linux-only rename variants replay `RENAME_EXCHANGE` and `RENAME_WHITEOUT`; other platforms return `ENOTSUP` for those transaction types.

## Dependencies
This file bridges ZIL record definitions, ZPL vnode operations, FUID handling, ACL encoding, SA xattrs, DMU object claiming, block cloning replay, and platform-specific Linux/FreeBSD vnode/idmap contracts.

## Risks
Variable-length payload parsing is offset-sensitive: xvattr data, ACL bytes, FUID arrays, domain strings, names, symlink targets, and xattr values are packed back-to-back. Several replay paths intentionally tolerate missing files because ZIL writes and clones may be logged out of order relative to removal.
