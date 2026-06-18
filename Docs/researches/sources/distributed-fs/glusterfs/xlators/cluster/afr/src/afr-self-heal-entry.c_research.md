# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal-entry.c

## Purpose

`afr-self-heal-entry.c` implements directory entry self-heal. It reconciles names under a directory by expunging stale entries, recreating missing entries from a source, repairing GFIDs, detecting type/GFID split brain, moving conflicting entries into the anonymous-inode directory when configured, and clearing entry pending xattrs after a full or granular crawl.

This file handles namespace convergence for replicated directories. It is used both by normal GFID healing and by self-heald index/full crawls.

## Important APIs, Types, and Functions

`afr_selfheal_entry()` is the public directory heal entry point. It opens the directory, takes an entry lock in the self-heal domain, and calls `__afr_selfheal_entry()`.

`__afr_selfheal_entry_prepare()` discovers the parent directory under lock, computes entry sources/sinks through `afr_selfheal_find_direction()`, and finalizes the source with `__afr_selfheal_entry_finalize_source()`.

`afr_selfheal_entry_do()` performs expunge and impunge passes. It can run full directory crawls with `afr_selfheal_entry_do_subvol()` or granular index scans with `afr_selfheal_entry_granular()`.

`afr_selfheal_entry_dirent()` heals one name. It locks the parent entry namespace, prepares parent state, performs a GFID-less lookup of the name across locked bricks, and calls `__afr_selfheal_entry_dirent()`.

`__afr_selfheal_heal_dirent()` repairs a name when a clear source exists. It heals missing GFIDs, deletes entries where the source has `ENOENT`, and recreates entries whose GFID differs from the source.

`__afr_selfheal_merge_dirent()` performs conservative merge when there is no clear source. It gathers all existing entries as sources, heals missing GFIDs, detects GFID/type mismatch, and recreates missing or mismatching sinks from a selected compatible source.

`afr_selfheal_recreate_entry()` deletes an existing sink entry, sets `gfid-req`, marks new-entry pending xattrs if needed, then recreates a directory, symlink, hardlink, or special/regular node with the source GFID.

`afr_selfheal_entry_delete()` removes an entry from one child, using anonymous-inode relocation first when configured and appropriate.

`afr_shd_entry_changes_index_inode()` locates the `entry-changes/<pargfid>` granular index directory, and `afr_shd_entry_purge()` removes processed granular index entries.

## Control Flow

The top-level entry heal opens the directory through `syncop_opendir()`, locks all children in `priv->sh_domain`, and then enters `__afr_selfheal_entry()`. The inner routine locks the directory in the xlator domain, discovers xattrs, and marks healed sinks. If no sinks need healing, it exits with return `1`.

The code decides between full crawl and granular heal using `afr_need_full_heal()`. Granular entry self-heal is available only when `priv->esh_granular` is enabled and no full-heal marker is present. Full crawl scans directory contents with `syncop_readdir()` from selected subvolumes. Granular crawl scans the per-parent `entry-changes` index with `syncop_dir_scan()`.

For each name, the code takes an entry lock in the xlator domain with `name == NULL`, prepares parent source/sink direction, and issues a `GF_GFIDLESS_LOOKUP`. A clear source path heals from the source; a split-brain/no-source path performs conservative merge. GFID repair is attempted before recreate decisions.

Expunge happens on healed sinks first. If a sink has an entry absent on the source, the entry is deleted or moved to the anonymous-inode directory. Impunge then uses the source to recreate entries missing on sinks.

After entry repair, the code reacquires xlator-domain entry locks before undoing pending. This explicitly protects name self-heal from reading parent pending xattrs while SHD is modifying them. It restores source times and calls `afr_selfheal_undo_pending()` for `AFR_ENTRY_TRANSACTION`.

## State and Persistence Behavior

Persistent effects include namespace operations (`mkdir`, `mknod`, `symlink`, `link`, `rename`, `unlink`, `rmdir`), GFID assignment through `gfid-req`, new-entry pending xattrs on sources, deletion of granular index entries, timestamp restoration, and entry pending xattr cleanup.

Anonymous-inode relocation preserves conflict content by renaming an existing entry to `priv->anon_inode_name/<gfid>` when the object may still have useful links or subdirectory hierarchy. Later self-heald cleanup decides when anonymous entries can be purged.

`local->need_full_crawl` is transient but important. When set, entry undo also writes data full-heal markers through `afr_selfheal_undo_pending()` so directory data changelog state is kept consistent.

GFID-less lookup prevents lookup from forcing one GFID too early; the code wants to observe divergent GFIDs and resolve them deliberately.

## Dependencies and Integration Points

The file depends on common self-heal functions for lock handling, direction calculation, GFID healing, anonymous-inode creation, pending xattr updates, and logging. It uses Gluster syncops for directory scan, lookup, rename, mkdir, mknod, symlink, link, unlink, and rmdir.

It integrates with `afr-self-heald.c` through `afr_shd_entry_purge()` and the granular entry changes index. It also integrates with `afr-self-heal-name.c`, which reuses `afr_selfheal_recreate_entry()` and `afr_selfheal_entry_delete()` for single-name repair.

The code depends on AFR private-directory filtering so root-level internal directories are not healed as user entries.

## Risks and Edge Cases

Conservative merge is intentionally cautious, but GFID/type mismatch handling is complex. Incorrect source pruning can recreate the wrong object under a shared name.

Anonymous-inode relocation avoids immediate deletion but introduces cleanup complexity. If cleanup is too aggressive, it can remove still-linked objects; if too weak, hidden directories can accumulate.

Granular heal treats missing sink-side indexes as non-fatal but source-side missing indexes as failures. This distinction is subtle and important during replace-brick and partial index availability.

The code frequently resets copied frames during directory iteration. A lost local frame after reset is treated as `-ENOTCONN`; future changes must preserve that check.

New-entry marking must be present on all relevant source bricks before the code skips marking. Mistakes can leave future heals unaware that a recreated entry needs data/metadata heal.

## Test Signals

Tests should cover full crawl and granular crawl, missing entry recreation for directories, symlinks, regular/special files, hardlink-to-symlink handling, source `ENOENT` expunge, GFID-less lookup with missing GFID, GFID mismatch resolution and failure, type mismatch split brain, anonymous-inode rename and cleanup handoff, granular index purge, root private directory skipping, frame reset failure, and post-op lock mismatch before pending cleanup.

Runtime signals include `performing full entry selfheal` or `performing granular entry selfheal`, expunging/rename warnings, GFID/type split-brain events, index purge behavior under `entry-changes`, and final `afr_log_selfheal()` source/sink output.
