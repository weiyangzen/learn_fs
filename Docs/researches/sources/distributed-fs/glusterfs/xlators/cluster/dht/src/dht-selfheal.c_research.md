# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-selfheal.c

## Purpose
Implements DHT directory self-heal and layout repair. It refreshes on-disk directory layouts from child subvolumes, detects holes/overlaps/missing directories/down bricks, creates missing directory copies, heals attributes and selected xattrs, recomputes hash ranges, writes layout xattrs, and updates rebalance commit hashes.

## Important APIs and Functions
- `dht_refresh_layout` / `dht_refresh_layout_cbk`: lookup every subvolume with DHT layout xattr requested, merge results into `selfheal.refreshed_layout`, then decide whether repair is needed.
- `dht_should_heal_layout` and `dht_should_fix_layout`: policy predicates for normal self-heal versus fix-layout, considering holes, overlaps, missing dirs, down/misc errors, commit hash changes, decommissioned bricks, and weighted/equal distribution.
- `dht_selfheal_layout_lock`: acquires layout-domain inodelks on all subvolumes, or only the hashed subvolume for new directories, before refreshing and writing layouts.
- `dht_selfheal_dir_mkdir`, `dht_selfheal_dir_mkdir_lookup_*`, `dht_selfheal_dir_mkdir_cbk`: protect namespace, re-lookup to avoid racing rmdir, create missing directories with requested GFID/internal context, and continue to attr/xattr healing.
- `dht_selfheal_layout_new_directory`, `dht_fix_layout_of_directory`, `dht_selfheal_layout_maximize_overlap`: compute new hash ranges, optionally weighted by disk usage, randomized by GFID, and adjusted to maximize overlap with old ranges.
- `dht_dir_heal_xattrs`, `dht_dir_attr_heal`, `dht_update_commit_hash_for_layout`: sync user/quota/MDS xattrs, mode/uid/gid, and commit-hash layout xattrs.

## Control Flow
Normal directory self-heal starts with a merged layout and iatt state from lookup. It links the inode, copies MDS attrs/xattrs when needed, rejects repair if bricks are down or anomalies are unrecoverable, sorts by subvolume name, computes a fix when holes/overlaps/missing entries exist, and calls `dht_selfheal_dir_mkdir`. Missing directory creation first takes namespace protection on the hashed/MDS subvolume, re-lookups all children under lock, creates only entries still missing or forced, then heals attrs and layout xattrs.

Layout xattr healing writes a 4-int disk-layout blob (`conf->xattr_name`) to each participating subvolume and writes 0-0/dummy layouts to non-participating subvolumes so stale overlaps are removed. A refresh pass sorts on-disk layout and either invokes the healer or swaps in the refreshed layout and finishes. Commit-hash update is a rebalance-only path that locks local subvolumes, updates `layout->list[j].commit_hash`, extracts disk layout blobs, sets xattrs, then unlocks.

## State and Persistence
Persistent state is stored as trusted DHT layout xattrs, MDS xattrs, quota/user xattrs, directory attrs, GFIDs, and commit hashes on child bricks. Runtime state lives in `local->selfheal`: current/refreshed layout refs, anomaly counters, forced mkdir, callbacks, healer predicate, plus `need_attrheal`, `need_xattr_heal`, MDS buffers, and lock wrappers.

## Dependencies and Integration Points
Uses DHT layout parsing/sorting/anomaly helpers, namespace and inodelk wrappers, synchronous FOP helpers for background attr/xattr heal, dict APIs, GFID/inode APIs, `dht_common_mark_mdsxattr`, and volume options from `dht_conf_t` such as `dir_spread_cnt`, `do_weighting`, `randomize_by_gfid`, `du_stats`, `decommissioned_bricks`, and local subvolumes. It is called from lookup/mkdir/fix-layout/rebalance paths.

## Risks
- Some comments note non-layout xattr healing remains secondary and may not run when layout is otherwise well-formed.
- Repair is skipped when subvolumes are down, leaving layout anomalies until later.
- Weighted layout depends on current `du_stats`; missing or uneven stats switch behavior and can alter placement.
- Several paths continue after failures with logged errors, so partial xattr or attr heal can remain.
- `dht_selfheal_layout_maximize_overlap` uses stack allocation proportional to old*new layout count.

## Test Signals
The unit tests in this subset only cover `dht_layout_new`; this file needs broader regression coverage through directory lookup/mkdir/fix-layout/rebalance tests. Important signals include layout hole/overlap repair, add-brick 0-0 layout clearing, decommissioned brick exclusion, MDS xattr heal, root directory attr behavior, forced restore, and commit-hash update under lock.
