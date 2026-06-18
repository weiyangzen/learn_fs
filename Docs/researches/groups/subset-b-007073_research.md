# Research: subset-b-007073

This grouped report covers GlusterFS AFR self-heal common logic, data heal, entry heal, metadata heal, name heal, the self-heal public header, and the self-heal daemon scheduler. Each file section is bounded by reconciliation markers and preserves the source path as its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal-common.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal-common.c

## Purpose

`afr-self-heal-common.c` provides the shared machinery used by AFR data, metadata, entry, name, and daemon-initiated heals. It creates self-heal frames, discovers brick state, parses AFR changelog xattrs, computes source/sink direction, handles split-brain source selection, acquires and releases inode/entry locks, updates pending xattrs after healing, logs heal outcomes, and exposes the top-level `afr_selfheal()` flow for a GFID.

The file is the policy center for AFR healing. The more specific files perform data copy, metadata copy, or directory entry replay, but they all depend on this file for consistent source selection, pending-matrix interpretation, GFID repair, locking, and post-op cleanup.

## Important APIs, Types, and Functions

`afr_selfheal()` is the public GFID entry point. It builds a self-heal frame with `afr_frame_create()`, initializes request xdata, and calls `afr_selfheal_do()`.

`afr_selfheal_do()` runs the high-level sequence: unlocked inspection, optional data open for regular files, then `afr_selfheal_data()`, `afr_selfheal_metadata()`, and `afr_selfheal_entry()` according to the detected need and volume options.

`afr_selfheal_unlocked_inspect()` performs unlocked lookup/discovery, detects data, metadata, and entry heal needs from xattrs and stat mismatches, links a usable inode, and reports stale/all-missing conditions.

`afr_selfheal_find_direction()` is the core changelog algorithm. It extracts `AFR_DIRTY` and per-child pending xattrs into a matrix, marks accused bricks, self-accused witnesses, sources, sinks, split-brain flags, and witness counters.

`afr_selfheal_extract_xattr()`, `afr_selfheal_fill_matrix()`, and `afr_selfheal_fill_cell()` decode big-endian AFR changelog arrays from lookup xdata.

`afr_selfheal_undo_pending()` computes negative xattrop arrays to clear dirty and pending bits after a successful heal. It also preserves pending markers for sinks that were not healed and supports entry full-crawl marker cleanup.

`afr_lookup_and_heal_gfid()` assigns missing GFIDs during lookup by issuing a `gfid-req` lookup to bricks lacking a GFID and then copying replies back into the caller's reply array.

Split-brain helpers include `afr_gfid_split_brain_source()`, `afr_mark_split_brain_source_sinks()`, `afr_mark_split_brain_source_sinks_by_heal_op()`, `afr_sh_get_fav_by_policy()`, `afr_sh_fav_by_size()`, `afr_sh_fav_by_mtime()`, `afr_sh_fav_by_ctime()`, and the majority helpers. They implement CLI-requested and configured favorite-child policies.

Lock helpers include `afr_selfheal_inodelk()`, `afr_selfheal_tie_breaker_inodelk()`, `afr_selfheal_uninodelk()`, `afr_selfheal_entrylk()`, `afr_selfheal_tryentrylk()`, `afr_selfheal_tie_breaker_entrylk()`, and `afr_selfheal_unentrylk()`.

`afr_throttled_selfheal()`, `__afr_dequeue_heals()`, `afr_heal_synctask()`, and the refresh callbacks implement background heal throttling for client-side refresh-triggered heals.

`afr_anon_inode_create()` creates or looks up AFR's anonymous-inode directory, used by entry heal to move conflicting directories or hardlinked objects out of the namespace without immediate destructive deletion.

## Control Flow

The normal GFID heal path begins with `afr_selfheal()`, which creates a frame with self-heald PID and AFR lock owner. `afr_selfheal_do()` calls `afr_selfheal_unlocked_inspect()` to gather lookups from up children. The inspection checks pending xattrs first, then type, uid, gid, mode, and regular-file size mismatches. Type mismatch is treated as split brain and returns `-EIO`.

If no heal is needed, the top-level result is `2` for all-zero/no work. If pending xattrs exist but no configured type-specific heal runs, the result may remain `1`. For regular files, the code opens a shared fd before data heal. It then invokes the enabled heal lanes and folds their return values, treating `-EIO` from any lane as split brain.

Each heal lane follows the same common pattern: take domain locks, discover current xattrs under the lock, call `afr_selfheal_find_direction()`, heal selected sinks, restore timestamps, and call `afr_selfheal_undo_pending()` while still holding appropriate locks. Direction finding treats non-accused locked bricks as sources, bricks accused by sources as sinks, and lack of sources as split brain.

GFID repair is separate from content repair. `afr_lookup_and_heal_gfid()` chooses a known GFID from a valid same-type reply, writes it into lookup xdata as `gfid-req`, looks up only bricks missing the GFID, and replaces those replies with the healed lookup results.

Split-brain source selection first honors explicit heal operations in request xdata, such as bigger-file, latest-mtime, or source-brick. Without explicit input, it may use favorite-child policy. Automatic GFID split-brain resolution refuses directories because DHT owns the distributed directory view.

Background throttling enqueues `afr_local_t` objects in `priv->heal_waiting` when the background count allows it. Completed synctasks remove their local from the active list and dequeue the next waiting heal.

## State and Persistence Behavior

The durable state managed here is on-brick AFR xattrs, not local files. `afr_selfheal_post_op()` uses `xattrop` with `GF_XATTROP_ADD_ARRAY`; positive arrays mark pending or dirty state and negative arrays undo it. Values are encoded as big-endian `int` arrays with `AFR_NUM_CHANGE_LOGS` slots.

`afr_selfheal_find_direction()` treats pending xattrs as a matrix of who accuses whom. Dirty counters and self-accusals become witness values used by data and metadata tie breakers. Split-brain and pending status are also surfaced through optional `pflag` bits.

The lock state is transient in `locked_on`, `data_lock`, and `postop_lock` arrays. The code is intentionally strict about requiring all children for many heals, because partial views can clear or copy the wrong xattrs.

Frame-local reply state is transient and refcounts xdata dictionaries. `afr_reply_copy()` and `afr_replies_copy()` preserve xdata refs and checksum buffers. Callers are expected to wipe replies with `afr_replies_wipe()`.

Anonymous-inode state is persisted as a special directory with a configured GFID/name. `afr_anon_inode_create()` records per-child availability in `priv->anon_inode[]` and links the inode in the AFR inode table.

## Dependencies and Integration Points

The file depends on AFR private state (`afr_private_t`), frame-local state (`afr_local_t`), Gluster stack-winding APIs, sync barriers, inode tables, dict/xdata helpers, event logging, `protocol-common.h`, and MD5/SHA256 checksum conventions shared with data heal.

It integrates directly with `afr-self-heal-data.c`, `afr-self-heal-metadata.c`, `afr-self-heal-entry.c`, and `afr-self-heal-name.c` through exported helpers and prepare routines. It also integrates with `afr-self-heald.c` through `afr_selfheal()`, `afr_anon_inode_create()`, and `afr_selfheal_newentry_mark()`.

External integration points include CLI heal xdata keys (`heal-op`, `child-name`), GFID assignment through `gfid-req`, Gluster event emission for split brain, and transaction-type indexing via `afr_index_for_transaction_type()`.

## Risks and Edge Cases

The direction algorithm is sensitive to matrix interpretation. Incorrectly treating self-accusals, dirty counters, or failed lookups can convert a split brain into a destructive heal.

Many paths require all children to be locked or successfully discovered. Relaxing those checks risks clearing pending xattrs from a partial view.

Favorite-child policy can overwrite real divergence. The code limits some cases, such as size policy on directories and automatic GFID directory resolution, but policy-driven healing remains a data-loss risk if configured incorrectly.

`afr_selfheal_undo_pending()` must keep unhealed sinks pending. Bugs in the generated negative xattrop arrays can silently lose heal work.

The use of stack allocation sized by child count is pervasive. Very large replica counts increase stack pressure.

`afr_throttled_selfheal()` returns whether it queued or launched a heal, but the naming can be counterintuitive because it sets `can_heal` false when the queue is full.

## Test Signals

Useful tests should cover pending-matrix direction selection, dirty/self-accused witnesses, split-brain detection with no sources, favorite-child policies, CLI source-brick/bigger/latest-mtime resolution, GFID assignment to missing bricks, refusal to auto-resolve directory GFID split brain, lock failure and `EAGAIN` tie-break paths, post-op xattr undo after partial sink failure, stale index cleanup return `2`, and background heal queue throttling.

Runtime signals include `AFR_MSG_SPLIT_BRAIN`, `EVENT_AFR_SPLIT_BRAIN`, `AFR_MSG_SELF_HEAL_INFO`, pending `pflag` bits, source/sink logs from `afr_log_selfheal()`, and xdata response messages such as `sh-fail-msg` and `gfid-heal-msg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal-data.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal-data.c

## Purpose

`afr-self-heal-data.c` implements AFR data self-heal for regular files. It selects an authoritative source, truncates sinks to the source size, copies data blocks from source to sinks, avoids unnecessary writes through checksum and sparse-file checks, fsyncs if durability is required, restores timestamps, and clears data pending xattrs.

The file owns byte-range content repair. It relies on common self-heal logic for locks, direction calculation, pending-xattr cleanup, and split-brain policies.

## Important APIs, Types, and Functions

`afr_selfheal_data()` is the public entry point. It takes a self-heal domain inode lock, then delegates to `__afr_selfheal_data()`.

`__afr_selfheal_data_prepare()` discovers locked replies, calls `afr_selfheal_find_direction()` for `AFR_DATA_TRANSACTION`, initializes `healed_sinks`, and finalizes the source through `__afr_selfheal_data_finalize_source()`.

`__afr_selfheal_data_finalize_source()` handles split brain, CLI/favorite-child selection, source witness tie breakers, size mismatches, largest-file policy, newest-file tie breaking, arbiter empty-file behavior, and final source selection via `afr_choose_source_by_policy()`.

`afr_selfheal_data_do()` performs the copy loop. It chooses full or diff heal, sizes the block window, copies with a reusable iter frame, and fsyncs healed sinks if enabled.

`afr_selfheal_data_block()` locks a byte range, optionally skips a diff block by comparing checksums, and calls `__afr_selfheal_data_read_write()`.

`__afr_selfheal_data_read_write()` reads from the source with `syncop_readv()` and writes the buffer to each healed sink with `syncop_writev()`, unmarking any sink whose write fails.

`__afr_can_skip_data_block_heal()` issues `rchecksum` on source and sinks and skips matching blocks, with special handling for zero-filled sparse regions.

`__afr_selfheal_truncate_sinks()` performs up-front `ftruncate` on healed sinks. Arbiter sinks are also included so changelog/geo-rep state can capture data transactions.

`afr_selfheal_data_open()` opens an inode on up children and binds the fd if at least one open succeeds.

## Control Flow

The entry point first locks the file in `priv->sh_domain` with `afr_selfheal_tie_breaker_inodelk()`. If every child cannot be locked, it returns `-ENOTCONN`. Under that outer lock, `__afr_selfheal_data()` takes the xlator-domain file lock, discovers replies, computes sources/sinks, and decides whether there is real work.

If a source is selected and at least one sink is marked, the code rejects non-empty arbiter sources. It truncates healed sinks to the source size and drops the xlator-domain lock before copying file data. If the only sink is an arbiter or the file is empty on all children, it skips data copy and proceeds to timestamp restoration and pending cleanup.

The copy loop uses `block = 128 KiB * data_self_heal_window_size`, reduced to `128 KiB` for files with holes. Dynamic heal mode chooses diff heal when any participant has non-zero size, otherwise full heal. Each block is separately range-locked before read/write.

For diff blocks, checksums are requested from source and sinks. A matching checksum can skip the write. Sparse files get extra handling to avoid filling holes with zero writes, except where the final block is needed to establish file size.

After data copy, the code restores source atime/mtime/ctime to healed sinks, reacquires the xlator-domain lock when needed, and calls `afr_selfheal_undo_pending()` for `AFR_DATA_TRANSACTION`.

## State and Persistence Behavior

Persistent effects are writes, truncates, fsyncs, timestamps, and AFR pending xattrs on bricks. The function treats `healed_sinks[]` as mutable success state: a sink starts as a target but is cleared if truncate, write, fsync, or metadata update fails.

`locked_replies` preserve source and sink stat/xattr state from the locked discovery. Source size and sparse status drive block iteration and skip decisions.

Arbiter state is special. The arbiter is temporarily removed from data copy targets, can remain a sink for metadata/changelog purposes, and is never accepted as the source for non-empty data.

`ensure_durability` controls whether successful sink writes must be followed by `fsync`; fsync failures turn those sinks back into unhealed sinks before pending xattrs are cleared.

## Dependencies and Integration Points

This file depends on common helpers from `afr-self-heal-common.c` for locks, source/sink direction, split-brain handling, xattr undo, timestamp restoration, logging, and reply management. It also uses Gluster syncops for `readv`, `writev`, `ftruncate`, `fsync`, and `open`.

It integrates with AFR configuration fields such as `data_self_heal_algorithm`, `data_self_heal_window_size`, `ensure_durability`, `arbiter_count`, `local[]`, and `pending_key[]`.

It shares checksum semantics with lower translators through `rchecksum` xdata keys `check-zero-filled`, `buf-has-zeroes`, and `fips-mode-rchecksum`.

## Risks and Edge Cases

Sparse-file handling is deliberately conservative and comments note that proper FIEMAP/discard support is missing. Incorrect zero-skip logic can alter disk usage or fail to preserve holes.

The source-selection tie breakers combine xattr witnesses, size, ctime, favorite-child policy, and arbiter rules. Small changes can convert a no-heal or split-brain condition into data overwrite.

The function clears pending xattrs only for sinks still marked healed. Any path that forgets to clear a failed sink before post-op can lose pending state.

Range locks around each block reduce concurrency risk but increase exposure to lock loss and reconnect behavior during long heals.

Checksum skip depends on comparable checksum algorithms. FIPS-mode SHA256 and default MD5 lengths are tracked per reply; mismatches here can cause false equality or unnecessary copying.

## Test Signals

Tests should cover full and diff algorithms, dynamic mode selection, sparse source with zero blocks, non-sparse zero-filled blocks, failed sink write/truncate/fsync, durability enabled and disabled, arbiter-only sink, arbiter source rejection, empty-file heal, size-mismatch source selection, witness tie breaking, range-lock failures, and pending xattr cleanup after partial success.

Runtime signals include `performing data selfheal`, block debug logs with GFID/offset/size, `afr_log_selfheal()` source/sink output, split-brain events from common helpers, and changes in AFR index counts after pending xattrs are cleared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal-data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal-entry.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal-entry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal-metadata.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal-metadata.c

## Purpose

`afr-self-heal-metadata.c` implements AFR metadata self-heal. It repairs uid, gid, mode, and user xattrs from a selected source to healed sinks, handles metadata split brain, supports directory time-only split-brain resolution, restores source timestamps, and clears metadata pending xattrs.

This file is the metadata-specific counterpart to data and entry heal, using the common direction and locking logic while owning attribute and xattr copy semantics.

## Important APIs, Types, and Functions

`afr_selfheal_metadata()` is the main entry point. It takes a tie-breaker inode lock at offset `LLONG_MAX - 1`, prepares source/sink state, copies metadata, restores times, and undoes pending xattrs.

`__afr_selfheal_metadata_prepare()` discovers locked replies, computes direction for `AFR_METADATA_TRANSACTION`, gives preference to source witnesses, and calls `__afr_selfheal_metadata_finalize_source()`.

`__afr_selfheal_metadata_finalize_source()` handles split brain, favorite-child/CLI resolution, directory time-only split brain, forced metadata split-brain heal, source pruning for stat/xattr mismatch, and optional marking of pending xattrs when all bricks were initially sources but mismatches are found.

`__afr_selfheal_metadata_do()` copies metadata. It gets xattrs from the source, removes ignorable keys, sets uid/gid/mode on each healed sink, removes old sink xattrs, and sets the source xattr set.

`afr_dirtime_splitbrain_source()` detects the special case where only directory atime/mtime/ctime differ while GFID, type, mode, uid, gid, and non-ignorable xattrs match; it selects the newest mtime source.

`afr_selfheal_metadata_by_stbuf()` builds an inode from a supplied stat buffer and runs metadata heal, useful for callers that already have authoritative iatt state.

## Control Flow

Metadata heal starts with an inode lock in the xlator domain at a high offset to avoid conflicting with normal data ranges. The prepare step does a locked discover and interprets metadata changelogs. If any source has witness counts, it is selected and other sources are converted to healed sinks.

Finalize handles hard cases. If every locked child is a sink or no source exists, it first tries common split-brain source selection. If that fails, it checks for directory time-only split brain and selects the most recent directory time. If forced metadata split-brain heal is enabled, it arbitrarily picks a locked sink as source; otherwise it emits a split-brain event and returns `-EIO`.

When a source is selected, other sources are compared against the source's type, uid, gid, mode, and xattrs. Mismatching sources are downgraded to sinks. If all children were initially sources and mismatches are found, the code marks metadata pending xattrs on sources and refreshes replies before the actual heal.

The copy phase fetches source xattrs once, removes ignorable AFR/internal keys, applies uid/gid/mode through `setattr`, removes old sink xattrs by passing the old dict to `removexattr`, and writes the source xattrs to each sink. Sink failures clear `healed_sinks[i]`.

After copy, the code restores timestamps and uses `afr_selfheal_undo_pending()` to clear metadata pending state only for successfully healed sinks.

## State and Persistence Behavior

Persistent state includes inode ownership, mode, xattrs, timestamps, and AFR metadata changelog xattrs. The macro `AFR_HEAL_ATTR` limits attribute copy to uid, gid, and mode; timestamps are restored separately.

Ignorable xattrs are filtered both from the source xattr set and old sink xattrs before removal. This prevents AFR/internal or otherwise ignored keys from being copied or deleted as user metadata.

`metadata_splitbrain_forced_heal` changes persistence behavior significantly by allowing an arbitrary locked sink to become source when no policy/source can resolve split brain.

The directory time-only path treats mtime/ctime divergence as a repairable artifact of platform-specific directory timestamp behavior after entry changes.

## Dependencies and Integration Points

This file depends on common AFR self-heal helpers for lock, direction, split-brain policy, pending cleanup, timestamp restoration, xattr equality, and logging. It uses syncops for `getxattr`, `setattr`, `removexattr`, and `setxattr`.

It integrates with AFR configuration for arbiter xattr comparisons, favorite-child policy, and forced metadata split-brain healing. It also uses Gluster event logging for unresolved metadata split brain.

## Risks and Edge Cases

Removing old sink xattrs with a dictionary is powerful and risky. If ignorable filtering is incomplete, internal or externally managed xattrs may be removed incorrectly.

Forced metadata split-brain heal can overwrite metadata arbitrarily and must remain an explicit configuration choice.

The all-sources-but-mismatching path marks pending xattrs before healing. Failures between marking and completion must leave enough pending state for a later heal.

Directory time-only detection must compare all non-time fields and xattrs. If it misses a meaningful difference, it can silently choose the newest timestamp as source and overwrite real divergence.

## Test Signals

Tests should cover uid/gid/mode repair, user xattr copy and old xattr removal, ignorable xattr preservation, sink failure during setattr/removexattr/setxattr, directory time-only split brain, forced and non-forced metadata split brain, source witness selection, all-sources mismatch marking, favorite-child policy rejection for metadata heal-op modes, and timestamp restoration.

Runtime signals include `performing metadata selfheal`, `clear time split brain`, metadata split-brain events, debug logs for iatt/xattr mismatch, and final `afr_log_selfheal()` status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal-metadata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal-name.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal-name.c

## Purpose

`afr-self-heal-name.c` implements narrow self-heal for a single basename under a parent GFID. It repairs divergent lookup results, missing GFIDs, absent entries, stale entries, and compatible GFID differences for one name without crawling the entire directory.

This file is used by full self-heald tree walks and by callers that need to heal a specific name. It complements entry heal, which repairs directory contents in bulk.

## Important APIs, Types, and Functions

`afr_selfheal_name()` is the public entry point. It finds the parent inode, creates a self-heal frame, performs an unlocked inspection, and runs the locked name heal only if needed.

`afr_selfheal_name_unlocked_inspect()` does a cross-child lookup of the basename and sets `need_heal` when replies differ, `ENODATA` appears, or GFIDs differ.

`afr_selfheal_name_do()` takes an entry lock for the specific name, prepares parent source/sink state, performs a GFID-less lookup of the basename, and calls `__afr_selfheal_name_do()`.

`__afr_selfheal_name_prepare()` discovers parent entry changelogs and uses `afr_selfheal_find_direction()` for `AFR_ENTRY_TRANSACTION` to decide whether there is a clear source or a conservative merge.

`__afr_selfheal_name_do()` decides the single-name action: no-op, expunge if the source side is empty, type mismatch failure, GFID mismatch resolution, missing-GFID assignment, and impunge/recreate.

`afr_selfheal_name_type_mismatch_check()` detects incompatible file types among source candidates and emits split-brain events.

`afr_selfheal_name_gfid_mismatch_check()` detects divergent non-null GFIDs and calls `afr_gfid_split_brain_source()` to select or reject a source.

`__afr_selfheal_assign_gfid()` delegates missing GFID repair to `afr_lookup_and_heal_gfid()`, requiring all bricks up and locked if no GFID exists anywhere and the caller supplied `gfid_req`.

`__afr_selfheal_name_impunge()` recreates the chosen GFID on bricks that do not have it, using `afr_selfheal_recreate_entry()`. `__afr_selfheal_name_expunge()` deletes all existing copies when the source side is empty.

## Control Flow

The public path first checks whether a heal is necessary with unlocked lookups. If all observed replies agree, it returns success without taking locks. Otherwise, it locks the specific basename in the xlator domain.

Under the name lock, the code prepares parent direction from parent entry changelog xattrs. If there is no clear source or witnesses exist, it sets all locked non-sources as healed sinks and uses conservative merge.

The basename lookup uses `GF_GFIDLESS_LOOKUP` so divergent or absent GFIDs can be observed. The action step first rechecks whether the name actually needs repair. If all sources are `ENOENT`, it expunges existing copies. Otherwise it rejects type mismatch, resolves GFID mismatch or missing GFID, assigns a GFID where needed, and recreates the selected object on non-source bricks.

When GFID is completely absent, all children must be up and locked before assignment. This prevents assigning a caller-provided GFID while a down brick may already contain a conflicting GFID.

## State and Persistence Behavior

Persistent effects are limited to the single name: entry deletion, recreation, GFID assignment by `gfid-req`, and new-entry pending xattrs set indirectly by `afr_selfheal_recreate_entry()`.

Name heal does not perform data or metadata copy itself. Recreated entries may still require later data or metadata heal according to pending xattrs.

Request/response dictionaries can carry CLI GFID split-brain resolution inputs and outputs. `heal-op`, `child-name`, and `gfid-heal-msg` are passed through to common split-brain handling.

The function uses transient `sources`, `sinks`, `healed_sinks`, `locked_on`, and reply arrays, and wipes reply xdata before returning.

## Dependencies and Integration Points

This file depends heavily on entry/common helpers: `afr_selfheal_recreate_entry()`, `afr_selfheal_entry_delete()`, `afr_lookup_and_heal_gfid()`, `afr_gfid_split_brain_source()`, `afr_selfheal_find_direction()`, and entry locks.

It integrates with `afr-self-heald.c` full crawl through `afr_shd_selfheal_name()`, and with CLI split-brain resolution through request/response dicts.

It also depends on Gluster inode lookup semantics, `GF_GFIDLESS_LOOKUP`, and AFR parent pending xattrs to determine whether conservative merge is appropriate.

## Risks and Edge Cases

Single-name healing can recreate namespace entries without copying data or metadata immediately. Correct pending xattr marking is therefore essential for follow-up heals.

Missing-GFID assignment is dangerous if any brick is down; the all-up/all-locked guard must be preserved.

Source-empty detection treats source candidates with `ENOENT` as empty. Wrong source selection can turn a legitimate entry into an expunge operation.

GFID and type mismatch checks only consider valid successful replies. Error handling around `ENODATA`, `ENOENT`, and stale replies must remain precise to avoid false split-brain or missed repair.

## Test Signals

Tests should cover no-op matching replies, `ENODATA` needing heal, source-empty expunge, missing GFID with all bricks up, missing GFID with a down brick, GFID mismatch resolved by CLI source, unresolved GFID split brain, type mismatch split brain, conservative merge without clear source, recreate on absent sink, and response dict messages for GFID heal.

Runtime signals include type/GFID split-brain events, `gfid-heal-msg`, `sh-fail-msg` from common policy code, entry recreate/expunge warnings from entry helpers, and successful return from `afr_selfheal_name()` after previously divergent lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal-name.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal.h

## Purpose

`afr-self-heal.h` declares the shared AFR self-heal API and several macros used to wind synchronous operations across replica children. It is the contract between the common self-heal engine, the data/metadata/entry/name heal implementations, and self-heald.

The header centralizes public helper prototypes, split-brain user messages, lock APIs, source/sink preparation APIs, and reply/xattr utility functions.

## Important APIs, Types, and Functions

`afr_granular_esh_args_t` carries state for granular entry self-heal callbacks: heal fd, xlator, frame, and a mismatch flag.

`AFR_ONALL`, `AFR_ONLIST`, and `AFR_SEQ` are synchronous stack-wind macros. They wipe local replies, wind a requested FOP to all up children or a supplied child mask, and wait on `local->barrier`.

`ALLOC_MATRIX` allocates a child-count square matrix on the stack. `IA_EQUAL` compares `struct iatt` fields by their `ia_` member.

The header declares top-level operations: `afr_selfheal()`, `afr_throttled_selfheal()`, `afr_selfheal_name()`, `afr_selfheal_data()`, `afr_selfheal_metadata()`, and `afr_selfheal_entry()`.

It declares lock APIs for inode and entry locks, including tie-breaker variants and unlock functions.

It declares discovery/lookup APIs: `afr_selfheal_unlocked_discover()`, `afr_selfheal_unlocked_discover_on()`, `afr_selfheal_unlocked_lookup_on()`, `afr_selfheal_unlocked_inspect()`, and `afr_lookup_and_heal_gfid()`.

It declares direction, xattr, and post-op APIs such as `afr_selfheal_find_direction()`, `afr_selfheal_extract_xattr()`, `afr_selfheal_fill_matrix()`, `afr_selfheal_undo_pending()`, `afr_selfheal_post_op()`, and `afr_selfheal_restore_time()`.

It declares source policy and split-brain helpers, including favorite-child functions, GFID split-brain source selection, source/sink marking for empty files, and child index lookup.

## Control Flow

Callers use this header in two layers. High-level callers invoke `afr_selfheal()` for a GFID or `afr_selfheal_name()` for a specific parent/name. Type-specific modules call the common prepare functions and helpers to implement their healing sequence.

The wind macros define the common asynchronous-to-synchronous control pattern: prepare a child mask, set the barrier wait count, clear prior replies, wind child FOPs with the child index as cookie, and wait for callbacks to fill `local->replies`.

The prepare functions declared here provide a common source/sink contract for data, metadata, and entry heals: callers pass locked children, reply arrays, and output arrays for sources, sinks, and healed sinks.

## State and Persistence Behavior

The header itself persists no state, but its APIs operate on AFR pending xattrs, inode/entry locks, `afr_local_t` reply arrays, inode tables, and brick namespace state.

`AFR_ONALL` snapshots `priv->child_up` before winding so a single operation sees a stable set of children even if child-up state changes concurrently.

Stack allocation macros mean most source/sink matrices and child masks are transient and frame-scoped. Callers must not retain them after returning.

The declared message constants are used in xdata responses and logs for split-brain and CLI heal operations.

## Dependencies and Integration Points

The header assumes inclusion after AFR core types are available, especially `xlator_t`, `call_frame_t`, `inode_t`, `fd_t`, `dict_t`, `afr_private_t`, `afr_local_t`, `struct afr_reply`, and `afr_transaction_type`.

It integrates all files in this subset and is also included by other AFR files that need self-heal primitives. `afr-self-heald.h` separately declares daemon-specific types but depends on functions declared here.

## Risks and Edge Cases

`AFR_ONALL` and `AFR_ONLIST` set `barrier.waitfor` to the child count and then call `syncbarrier_wait()`. Incorrect masks or callbacks that fail to wake the barrier will deadlock self-heal.

The macros use `alloca`, so child-count-dependent allocations consume stack. `ALLOC_MATRIX` is especially expensive for large replica counts.

Because macros wipe `local->replies`, callers must copy replies they still need before issuing another macro-driven FOP.

The header exposes many internal helpers, making cross-file coupling tight. Changing source/sink array semantics in one implementation can break others.

## Test Signals

Compile-time coverage should catch prototype drift among self-heal files. Runtime tests should indirectly validate `AFR_ONALL`, `AFR_ONLIST`, and `AFR_SEQ` through lock, lookup, xattrop, fsync, and setattr paths across child masks.

Useful fault-injection tests include missing callback wakeups, child-down changes during a macro invocation, reply wiping between operations, and large replica counts that stress stack allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heald.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heald.c

## Purpose

`afr-self-heald.c` implements the AFR self-heal daemon side: per-subvolume healer threads, index crawls, full crawls, thin-arbiter coordination, split-brain/statistics history, anonymous-inode cleanup, child-up triggering, and management operations exposed through `afr_xl_op()`.

This file turns the self-heal primitives into background maintenance. It scans AFR index directories for GFIDs needing heal, walks full brick trees on request, invokes `afr_selfheal()` and `afr_selfheal_name()`, and records outcomes for CLI/status consumers.

## Important APIs, Types, and Functions

`afr_selfheal_daemon_init()` allocates and initializes index/full healer arrays, split-brain event history, and per-child statistics histories.

`afr_selfheal_childup()` starts index healers for up children when this process is self-heald.

`afr_xl_op()` handles management operations such as index heal, full heal, statistics, and heal-count queries. It fills output dictionaries with per-child status and counters.

`afr_shd_index_healer()` is the long-running index healer thread. It waits for rerun/timeout, verifies local subvolume ownership, runs index sweeps, cleans anonymous-inode directories, and handles thin-arbiter xattr cleanup.

`afr_shd_full_healer()` runs a requested full tree crawl and then exits until respawned.

`afr_shd_index_sweep_all()` scans `GF_XATTROP_INDEX_GFID`, `GF_XATTROP_DIRTY_GFID`, and `GF_XATTROP_ENTRY_CHANGES_GFID`. `afr_shd_index_sweep()` locates each index inode and scans it with `syncop_mt_dir_scan()`.

`afr_shd_index_heal()` parses GFID index entries, invokes `afr_shd_selfheal()`, purges stale index entries on `ENOENT`/`ESTALE`, and zeroes stale xattrop links when `afr_selfheal()` returns `2`.

`afr_shd_selfheal()` resolves a GFID to a path for reporting, calls `afr_selfheal()`, updates crawl counters, and records split-brain history.

`afr_shd_full_heal()` heals a walked directory entry by first healing the parent/name relation and then healing the entry GFID.

Thin-arbiter helpers include `afr_shd_fill_ta_loc()`, `_afr_shd_ta_get_xattrs()`, `afr_shd_ta_needs_heal()`, `afr_shd_ta_get_xattrs()`, `afr_shd_ta_check_and_unset_xattrs()`, and `afr_shd_ta_unset_xattrs()`.

Anonymous-inode cleanup is implemented by `afr_cleanup_anon_inode_dir()` and `afr_shd_anon_inode_cleaner()`.

## Control Flow

Daemon initialization creates two healer slots per child: an index healer and a full healer. Each slot has its own mutex, condition variable, thread handle, child index, local/running/rerun flags, and crawl event state.

Index healers are spawned on child-up events or CLI index-heal requests. The thread waits on a timed condition. If self-heal is disabled, it continues waiting. When active, it checks at least two bricks are up and that the target child is local to this self-heald instance.

An index sweep opens each index directory in turn, scans entries concurrently with `syncop_mt_dir_scan()`, parses GFIDs from entry names, and calls `afr_selfheal()`. As long as a sweep heals at least one GFID, it sleeps briefly and repeats, because healing directories can expose more index work.

Full healers are spawned by CLI full-heal requests. They run one filesystem tree walk from root on a local child with `syncop_ftw()`. For each entry, they call name heal on the parent/basename and then GFID heal on the entry itself.

Each crawl calls `afr_shd_sweep_prepare()` and `afr_shd_sweep_done()` around the scan. These reset counters, set start/end times, mask cancellation, and save a copy into the statistics event history.

Thin-arbiter handling snapshots TA pending xattrs before the crawl. If the crawl completes without failures and the xattrs are unchanged, the good self-heald unsets TA pending xattrs. If another healer's pending key is set or state changes during the crawl, it schedules rerun instead.

`afr_xl_op()` is the control-plane dispatcher. It decodes `xl-op`, writes an xlator id into output, starts eligible local healers, reports remote/down/not-connected states, dumps statistics history, and reports index hardlink counts.

## State and Persistence Behavior

Healer thread state is transient in `struct subvol_healer`: running/rerun/local flags, mutex/condition, crawl counters, and thread id. The event histories `eh_t` retain recent split-brain paths and crawl statistics in memory.

Persistent effects happen through invoked heals, index entry purges, zeroing xattrop links, thin-arbiter xattrop cleanup, and anonymous-inode cleanup. `afr_shd_zero_xattrop()` sends zero-valued dirty and pending arrays to all bricks when an index entry has no pending changelog.

`crawl_event_t` tracks healed, split-brain, and failed counts plus start/end time and crawl type. A `start_time` of zero means no valid active crawl state; nonzero start with zero end means in progress.

Locality is recomputed with `syncop_is_subvol_local()` against the root inode. Non-local subvolumes are skipped so multiple self-heald processes do not all heal the same brick.

Anonymous-inode cleanup only proceeds when all bricks are up. It checks whether a hidden GFID exists only in the anonymous dir, whether the object has multiple links, and whether any non-anonymous entry still exists before purging.

## Dependencies and Integration Points

This file depends on `afr-self-heal.h` for GFID/name heal and anonymous-inode helpers, `afr-self-heald.h` for daemon types, Gluster syncop directory traversal utilities, event history (`eh_t`), pthreads, and AFR private configuration.

It integrates with CLI/glfs-heal through `afr_xl_op()` output dictionary keys, with index xlator directories via `GF_XATTROP_*` keys, with thin-arbiter code via `afr_ta_post_op_lock()` and pending-key conventions, and with entry heal through `afr_shd_entry_purge()`.

It also uses `syncop_gfid_to_path()` for split-brain reporting and `syncop_inode_find()` with `GF_INDEX_IA_TYPE_GET_REQ/RSP` to associate index directory entries with inode type.

## Risks and Edge Cases

Thread rerun/running state is subtle. Missing a condition signal or mishandling `safe_break()` can leave full healers stuck or index healers spinning.

Index crawls intentionally repeat while progress is made, but a persistent index entry from ongoing I/O can cause repeated work. The one-second sleep mitigates busy loops.

Locality checks are required in clustered self-heald deployments. If they are wrong, multiple daemons may heal or purge the same brick concurrently.

Thin-arbiter cleanup must only clear xattrs when crawl input and output state match and no heal failures occurred. Clearing TA pending state early can hide pending replica changes.

Anonymous-inode cleanup has destructive `unlink`/`rmdir` behavior. It relies on all-bricks-up and cross-child lookup checks to avoid deleting recoverable objects.

`afr_subvol_name()` checks `subvol > child_count`, which allows `subvol == child_count`; callers appear to pass valid indices, but the boundary is fragile.

## Test Signals

Tests should cover index healer spawn on child-up, CLI index/full heal status output for down/remote/local bricks, index scans over all three index directories, stale index purge on `ENOENT`/`ESTALE`, zero xattrop on return `2`, split-brain history recording, statistics history output, full crawl name+GFID heal ordering, thin-arbiter rerun and cleanup paths, anonymous-inode cleanup with all bricks up/down, and safe healer thread rerun behavior.

Runtime signals include index/full crawl start and finish logs, `statistics_*` output dict keys, split-brain event history entries with paths, index hardlink counts from `GF_XATTROP_INDEX_COUNT`, and warnings from anonymous-inode expunge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heald.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heald.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heald.h

## Purpose

`afr-self-heald.h` declares the data structures and public functions for AFR's self-heal daemon. It separates daemon scheduling/state types from the generic self-heal APIs in `afr-self-heal.h`.

The header defines how per-subvolume healer threads, crawl statistics, split-brain history, and daemon configuration are represented in `afr_private_t`.

## Important APIs, Types, and Functions

`shd_event_t` records a split-brain or daemon event path and child index for history storage.

`crawl_event_t` records crawl counters (`healed_count`, `split_brain_count`, `heal_failed_count`), timing (`start_time`, `end_time`), crawl type, and child index.

`struct subvol_healer` is the per-child healer state: owning xlator, current crawl event, mutex, condition variable, thread, subvolume index, locality flag, running flag, and rerun flag.

`afr_self_heald_t` is the daemon aggregate embedded in AFR private state. It holds index and full healer arrays, split-brain and statistics event histories, timeout and threading limits, thin-arbiter latency setting, and enabled/iamshd flags.

The header declares `afr_selfheal_daemon_init()`, `afr_xl_op()`, and `afr_shd_entry_purge()`.

## Control Flow

Initialization code allocates `afr_self_heald_t.index_healers` and `.full_healers`, then initializes each `subvol_healer`. Runtime code signals or spawns the relevant healer for a child. CLI/control operations enter through `afr_xl_op()`.

`crawl_event_t` timing fields define crawl lifecycle: `start_time == 0` means inactive/invalid stats, nonzero start with zero end means in progress, and nonzero end means completed history.

## State and Persistence Behavior

The structures in this header are in-memory daemon state. They do not persist across process restarts. Persistent effects are caused by the daemon implementation when it calls heal, purge, and xattrop operations.

The mutex and condition in each `subvol_healer` protect `running` and `rerun` coordination. The event-history pointers retain bounded in-memory statistics and split-brain event data.

`enabled` gates whether healers should perform work, while `iamshd` identifies the self-heal daemon process role.

## Dependencies and Integration Points

The header includes `pthread.h` and assumes Gluster/AFR types such as `xlator_t`, `eh_t`, `inode_t`, `ia_type_t`, and `dict_t` are visible from including contexts.

It is included by `afr-self-heald.c` and by AFR code that needs daemon initialization or management dispatch declarations.

## Risks and Edge Cases

`crawl_event_t` comments contain a typo, but the semantics are clear and used by statistics reporting. Code must honor those timing conventions or in-progress statistics become misleading.

The header exposes thread primitives directly, so lifecycle correctness depends on every user following the same locking and signaling rules.

Bounded history sizes are defined in the `.c` file rather than the struct. Consumers should not assume unbounded statistics retention.

## Test Signals

Compile-time tests should catch struct/prototype drift between daemon code and AFR private state. Runtime tests should verify that initialized healers have valid mutex/condition state, crawl events report inactive/in-progress/completed status correctly, and `afr_xl_op()` can safely read daemon state while healers are running.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heald.h -->
