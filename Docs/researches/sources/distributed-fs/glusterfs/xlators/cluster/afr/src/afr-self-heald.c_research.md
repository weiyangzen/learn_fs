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
