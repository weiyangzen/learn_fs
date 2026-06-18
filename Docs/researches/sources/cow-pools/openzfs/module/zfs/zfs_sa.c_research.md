# File Research: sources/cow-pools/openzfs/module/zfs/zfs_sa.c

## Summary
Defines the ZPL system-attribute registration table and kernel helpers for symlink storage, scanstamp attributes, SA-backed xattrs, and upgrading old bonus-buffer znodes into SA-format znodes.

## Main Responsibilities
- Register ZPL SA attributes such as times, mode, size, parent, uid/gid, ACLs, symlink, scanstamp, DXATTR, and project ID.
- Read and write symlink contents from bonus buffers or file data blocks.
- Get and set antivirus scanstamp xvattrs for both old and SA znode formats.
- Load and persist SA-backed extended attributes stored as packed nvlists.
- Convert old znode bonus layouts to SA layouts when possible.
- Provide transaction hold helpers for SA upgrades.

## Key APIs
- `zfs_attr_table`.
- `zfs_sa_readlink()`, `zfs_sa_symlink()`.
- `zfs_sa_get_scanstamp()`, `zfs_sa_set_scanstamp()`.
- `zfs_sa_get_xattr()`, `zfs_sa_set_xattr()`.
- `zfs_sa_upgrade()`, `zfs_sa_upgrade_txholds()`.

## Important Behavior
Small symlinks are stored after `ZFS_OLD_ZNODE_PHYS_SIZE` in the bonus buffer; larger symlinks use object data blocks after growing the block size.

`zfs_sa_set_xattr()` packs the cached xattr nvlist into XDR, enforces `SA_ATTR_MAX_LEN`, optionally logs `TX_SETSAXATTR` when the pool feature and module parameter allow it, updates ctime, and commits synchronously when dataset sync mode is `always`.

`zfs_sa_upgrade()` refuses to upgrade symlinks or znodes without cached ACLs. It carefully handles `z_lock`, bulk-reads old attributes, adds a default project ID when project quotas are enabled, builds a new SA template including ACLs and optional scanstamp, switches the bonus type to `DMU_OT_SA`, replaces all attributes, frees external ACL objects, and marks `z_is_sa`.

## Dependencies
Depends on the SA framework, DMU bonus buffers, ZFS ACL transformation and locators, nvlist packing, ZIL xattr logging, project quota feature state, and znode lock/ACL cache state.

## Risks
SA upgrade can only proceed when ACL state is already cached; otherwise the old format remains until a later opportunity. SA xattr persistence mutates both the cached nvlist and on-disk SA value, so replay and error paths must drop inconsistent caches when persistence fails.
