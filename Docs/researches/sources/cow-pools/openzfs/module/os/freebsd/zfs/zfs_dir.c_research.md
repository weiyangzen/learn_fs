# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_dir.c

## Purpose

Implements FreeBSD ZFS directory operations and directory-related znode lifecycle helpers: name lookup, parent lookup, unlinked-set recovery, rmnode deletion, link creation/destruction, extended attribute directory creation, and sticky-directory remove permission checks.

## Lookup Path

- `zfs_match_find()`
  - Performs directory ZAP lookup.
  - Uses `zap_lookup_norm()` when normalization/case handling is enabled.
  - Uses plain `zap_lookup()` otherwise.
  - Extracts the object number from packed dirent values with `ZFS_DIRENT_OBJ()`.
- `zfs_dirent_lookup()`
  - Looks up a child entry, rejecting `.`, `..`, and `.zfs`.
  - Supports flags:
    - `ZNEW`: fail with `EEXIST` if found.
    - `ZEXISTS`: fail with `ENOENT` if absent.
    - `ZXATTR`: look up the xattr directory through `SA_ZPL_XATTR`.
  - Applies normalization and case-match policy based on `zfsvfs->z_norm` and `zfsvfs->z_case`.
  - Converts the object id to a live znode using `zfs_zget()`.
- `zfs_dd_lookup()`
  - Reads `SA_ZPL_PARENT` and returns the parent znode.
- `zfs_dirlook()`
  - Handles empty name and `.` by returning the directory itself.
  - Handles `..` through `zfs_dd_lookup()`.
  - Handles ordinary names through `zfs_dirent_lookup(..., ZEXISTS)`.
  - Enables directory prefetch on successful ordinary lookup.

## Unlinked Set and Deletion

- `zfs_unlinked_add()`
  - Adds a zero-link znode id to `zfsvfs->z_unlinkedobj`.
  - Updates dataset unlinks kstat.
- `zfs_unlinked_drain()`
  - Iterates entries in the unlinked set after crash/force-unmount recovery.
  - Validates object type, fetches znodes, locks them, forces link count to zero if necessary, and marks them `z_unlinked`.
  - Does not directly delete every object in this pass; it prepares znodes for normal inactive deletion.
- `zfs_purgedir()`
  - Deletes contents of an inactive xattr directory.
  - Assumes entries are only regular files or symlinks.
  - Returns a count of skipped/failed entries so callers can leave the directory in the unlinked set.
- `zfs_rmnode()`
  - Final znode deletion path for objects with zero links.
  - Purges xattr directories or frees file data with `dmu_free_long_range()`.
  - Finds xattr object and external ACL object.
  - Removes the znode from the unlinked set, updates kstats, deletes SA/znode state, and commits the transaction.
  - Special FreeBSD behavior: if an xattr directory exists, it is added to the unlinked set and `z_unlinked_drain_task` is enqueued to avoid recursive `zfs_zget()`/`getnewvnode()` stack growth.

## Directory Entry Encoding

- `zfs_dirent()`
  - Packs `zp->z_id`.
  - For filesystems at `ZPL_VERSION_DIRENT_TYPE` or newer, encodes file type in high bits using `IFTODT(mode) << 60`.

## Link Creation

- `zfs_link_create()`
  - Adds `name -> zp` to parent directory `dzp`.
  - Enforces `ZFS_LINK_MAX`.
  - Refuses to relink already unlinked znodes unless renaming.
  - Increments target link count for non-rename paths.
  - Adds the packed dirent to the parent ZAP.
  - Activates `SPA_FEATURE_LONGNAME` when names reach/exceed `ZAP_MAXNAMELEN`.
  - Updates target SA attributes: links, parent, flags, ctime when appropriate.
  - Updates parent directory size, link count, mtime, ctime, and flags.

## Link Destruction

- `zfs_dropname()`
  - Removes a name from the parent directory ZAP.
  - Uses normalized removal when filesystem normalization is active.
- `zfs_link_destroy()`
  - Removes a directory entry and adjusts link counts.
  - Rejects removal of non-empty directories outside rename paths.
  - If target link count drops to the directory baseline, marks it `z_unlinked`, sets links to zero, and either returns this through `unlinkedp` or adds it to the unlinked set.
  - Updates parent size/link count and timestamps.
  - Contains defensive recovery for impossible low link counts via `zfs_panic_recover()`.

## Extended Attribute Directories

- `zfs_make_xattrdir()`
  - Creates an xattr directory under a base znode.
  - Builds ACL ids, checks quota, reserves a vnode, creates a new znode, updates the parent’s `SA_ZPL_XATTR`, logs `TX_MKXATTR`, and returns the new znode.
- `zfs_get_xattrdir()`
  - Looks up an existing xattr directory.
  - Creates one when `CREATE_XATTR_DIR` is set and the filesystem is writable.
  - Returns `ENOATTR` if absent and creation was not requested.
  - Unlocks the newly created xattr vnode before returning.

## Permission Helper

- `zfs_sticky_remove_access()`
  - Implements sticky-directory removal policy.
  - Allows removal if caller owns the directory, owns the entry, can write a regular file entry, or passes `secpolicy_vnode_remove()`.
  - Bypasses checks during ZIL replay.

## Concurrency and Transactions

- Lookup and link operations assert vnode locks when not replaying.
- DMU transactions explicitly hold affected SA handles, ZAP objects, unlinked set, ACL objects, and free ranges.
- `zfs_rmnode()` coordinates with `dd_activity_lock` and broadcasts when the unlinked set becomes empty.

## Important Interactions

- Uses SA attributes for parent, xattr pointer, links, timestamps, flags.
- Uses ZAP for directory contents and unlinked set.
- Uses `zfsvfs_taskq` for deferred unlinked drain work.
- Tightly coupled with `zfs_zget()`, `zfs_znode_delete()`, `zfs_acl_ids_*()`, ZIL create logging, and dataset kstats.
