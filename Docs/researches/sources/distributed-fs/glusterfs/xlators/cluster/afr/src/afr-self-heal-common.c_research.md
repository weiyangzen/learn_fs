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
