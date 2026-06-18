# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_dir.c

## Purpose

Directory-entry, lookup, unlink-drain, link-count, xattr-directory, and sticky-directory helper implementation for Linux ZFS. It bridges ZFS ZAP directories, znodes, SA updates, normalization/case-folding semantics, unlinked-set recovery, and Linux permission helpers.

## Dirent Lookup And Locking

`zfs_match_find()` performs ZAP lookup for a name. It uses `zap_lookup_norm()` when normalization is active, optionally returns the real matched name and case-conflict flags, tolerates `EOVERFLOW` for entries where the first integer remains the object id, and strips dirent type bits with `ZFS_DIRENT_OBJ()`.

`zfs_dirent_lock()` serializes access to a directory name using per-directory `z_dirlocks` under `z_lock`, plus `z_name_lock` unless `ZHAVELOCK` is supplied. It rejects `.`, `..`, and `.zfs`, determines normalized/case-sensitive match type, decides when DNLC-style updates are safe, chooses wide versus narrow locks for case-folding/rename situations, supports shared locks, checks unlinked directories, performs lookup or xattr lookup, enforces `ZNEW`/`ZEXISTS`, and returns a held target znode if found.

`zfs_dirent_unlock()` releases the name lock if owned, decrements shared count or removes the dirlock from the list, wakes waiters, frees copied names, destroys the condition variable, and frees the dirlock.

## Directory Lookup

`zfs_dirlook()` handles special names:

- Empty string or `.` returns the directory itself.
- `..` returns parent, with a special path for snapshots mounted under `.zfs`.
- `.zfs` returns the control directory unless snapdir is disabled.
- Other names use `zfs_dirent_lock()` with `ZEXISTS | ZSHARED` and optional case-insensitive lookup.

It enables prefetching on successful ordinary lookup and fills the real pathname buffer for ignore-case special cases.

## Unlinked Set And Removal

`zfs_unlinked_add()` inserts an unlinked znode id into the filesystem unlinked object and updates kstats.

`zfs_unlinked_drain_task()` iterates the unlinked set after crash/force-unmount recovery, checks object type, gets each znode, marks it unlinked, and releases it so inactive cleanup can free it. `zfs_unlinked_drain()` dispatches this asynchronously on the pool unlinked-drain taskq or falls back to synchronous execution. `zfs_unlinked_drain_stop_wait()` cancels/waits for the drain task during unmount.

`zfs_purgedir()` deletes all regular-file/symlink entries in an inactive xattr directory using synthetic dirlocks and transactions, returning a skipped count so the parent can remain in the unlinked set if cleanup failed.

`zfs_rmnode()` is final znode deletion for link-count-zero inactive znodes. It purges xattr directory contents, frees regular file data, finds and unlinks xattr directories, frees external ACL objects, removes the znode from the unlinked set, broadcasts when the unlinked set becomes empty, updates kstats, calls `zfs_znode_delete()`, and commits. If space/transaction/freeing problems occur, it leaves the object in the unlinked set for later drain.

## Link Create/Destroy

`zfs_dirent()` packs object id with file type bits when supported by the ZPL version.

`zfs_link_create()` links a znode into a directory ZAP entry. It rejects new links to unlinked znodes, increments link count for non-new/non-rename links, writes the ZAP entry, activates the longname feature for long names, updates parent/flags/ctime on the child, increments directory size and parent link count for subdirectories, updates parent timestamps/pflags/link count, and persists all via SA bulk updates.

`zfs_dropname()` removes a directory ZAP entry, using normalized removal when needed and choosing match-case rules according to filesystem case mode and lookup flags.

`zfs_drop_nlink_locked()` validates directory emptiness, recovers impossible link counts, drops one link, marks the znode unlinked and clears nlink when it reaches the directory terminal count, updates links/ctime/flags, and optionally adds it to the unlinked set.

`zfs_drop_nlink()` wraps the locked helper. `zfs_link_destroy()` removes the name from the parent, drops the target link unless this is a rename-only removal, updates parent size/link count/timestamps, and either reports or enqueues final unlink state.

`zfs_dirempty()` checks that no dirlocks are active and the ZAP count is zero. It is exact only when the caller holds the right locks; otherwise it is a hint.

## Extended Attribute Directories

`zfs_make_xattrdir()` creates an xattr directory znode with ACL IDs, quota checks, SA/ZAP/FUID transaction holds, parent pointer verification in debug builds, parent `SA_ZPL_XATTR` update, optional intent log entry, and returns the held xattr znode.

`zfs_get_xattrdir()` locks the xattr pseudo-entry, returns an existing xattr directory if present, optionally creates it when `CREATE_XATTR_DIR` is set, rejects creation on readonly datasets, sets sticky world-writable directory attributes, maps ids, handles `ERESTART`, and returns `ENOENT` when not creating.

## Sticky Directory Removal

`zfs_sticky_remove_access()` enforces sticky-bit removal restrictions: replay bypasses checks, non-sticky directories allow removal, otherwise the caller must own the directory, own the target, have write access to the target, or pass `secpolicy_vnode_remove()`.
