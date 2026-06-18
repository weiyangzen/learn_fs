# subset-b-005669 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/lock_dlm.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/lock_dlm.c

## Purpose
`lock_dlm.c` is GFS2's `lock_dlm` lock manager backend. It translates GFS2 glock state requests into kernel DLM lock modes, updates lock timing statistics, services DLM AST/BAST callbacks, mounts and releases a DLM lockspace, and coordinates cluster journal recovery through DLM recovery callbacks plus two special non-disk locks: the mounted lock and the control lock.

## Important APIs, types, and functions
The exported contract is `const struct lm_lockops gfs2_dlm_ops`, with `lm_mount`, `lm_first_done`, `lm_recovery_result`, `lm_unmount`, `lm_put_lock`, `lm_lock`, `lm_cancel`, and DLM hostdata tokens. Core glock operations are `gdlm_lock`, `gdlm_put_lock`, `gdlm_cancel`, `gdlm_ast`, and `gdlm_bast`. Lock mode conversion is handled by `make_mode`, `middle_conversion`, `down_conversion`, and `make_flags`. Recovery control is organized around `gfs2_control_func`, `control_mount`, `control_first_done`, `gdlm_recover_prep`, `gdlm_recover_slot`, `gdlm_recover_done`, and `gdlm_recovery_result`. The DLM callback table is `gdlm_lockspace_ops`.

## Control Flow
For normal glocks, `gdlm_lock` stores the requested GFS2 state in `gl_req`, converts current/requested states to DLM modes, computes DLM flags, builds a fixed-width resource name for initial locks, and calls `dlm_lock` under `ls_sem`. DLM completion calls `gdlm_ast`, which maps DLM status values to GFS2 outcomes, clears `GLF_BLOCKING`, zeroes invalid LVBs, clears `GLF_INITIAL` after the first successful lock, and completes the glock. Blocking callbacks call `gdlm_bast`, which maps DLM modes back to demotion states for `gfs2_glock_cb`. Dead glocks are released through `gdlm_put_lock`, usually by `dlm_unlock`; during lockspace teardown, `SDF_SKIP_DLM_UNLOCK` allows avoiding per-lock unlocks except where an exclusive LVB must be preserved.

DLM lockspace mount parses the `cluster:fsname` table, initializes recovery arrays, calls `dlm_new_lockspace`, and either uses DLM recovery ops or falls back to older userspace control behavior. With ops enabled, `control_mount` takes the control and mounted locks to detect the first mounter, waits for existing recovery generations and journal bitmap bits to clear, and blocks normal locking through `DFL_BLOCK_LOCKS` until it is safe. The first mounter recovers all journals during mount and calls `control_first_done`, which writes the latest generation into the control LVB, demotes mounted lock to PR, and releases the control lock to NL.

During membership recovery, DLM calls `recover_prep`, `recover_slot`, and `recover_done`. These update `ls_recover_block`, `ls_recover_start`, per-jid `recover_submit` arrays, and queue `sd_control_work`. `gfs2_control_func` serializes on the control lock in EX, merges failed-jid bits and successful recovery results into the control LVB, queues `gfs2_recover_set` for each set bit, and finally thaws glocks when all bits are clear and no newer DLM recovery cycle has reblocked locking.

## State and Persistence
Persistent cluster-visible state is in DLM lock value blocks. Individual glocks may have LVBs attached through `DLM_LKF_VALBLK`. The control LVB stores a little-endian generation in the first four bytes and a failed-jid bitmap starting at offset 8. In-memory state in `struct lm_lockstruct` includes the DLM lockspace pointer, synchronous lock completions, mounted/control `dlm_lksb`s, recovery flags, generation counters, the local jid, and variable-sized `recover_submit`/`recover_result` arrays. Lock statistics are maintained in per-glock and per-CPU `gfs2_lkstats`.

## Dependencies and Integration Points
This file depends on the kernel DLM API (`dlm_lock`, `dlm_unlock`, `dlm_new_lockspace`, `dlm_release_lockspace`), GFS2 glock core APIs, `gfs2_recover_set`, recovery result constants, filesystem logging helpers, tracepoints, and sysfs/uevent-visible state in `gfs2_sbd`. `ops_fstype.c` selects `gfs2_dlm_ops` from the lock protocol name; `recovery.c` reports journal recovery results back through `lm_recovery_result`.

## Risks
The recovery protocol depends on subtle generation comparisons and the control LVB bitmap. A missed update, stale generation, or premature `DFL_BLOCK_LOCKS` clear could allow normal locking before required journal replay. DLM callbacks can arrive during unmount or withdraw, so `ls_sem`, `DFL_UNMOUNT`, and dead lockrefs are important lifetime guards. `sync_lock` uses a single completion object and must be used serially. The fallback path without DLM ops has different journal-id and recovery semantics. The fixed resource-name formatting must remain compatible across nodes.

## Test Signals
Useful signals include multi-node mount and unmount, first-mounter election, spectator mount while recovery is pending, node failure during another recovery, repeated `GAVEUP` recovery results, DLM lock cancel/timeouts, LVB preservation for exclusive glocks, journal-id assignment through `recover_done`, `gfs2_control` logs for generation transitions, glock thaw after all jid bits clear, and lock-stat tracepoints for blocking versus nonblocking requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/lock_dlm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/log.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/log.c

## Purpose
`log.c` owns GFS2's in-memory journal accounting and log flush machinery. It reserves journal and revoke space, merges committed transactions into the incore system transaction, writes log headers, advances the log head and tail, drains the active item lists, handles ordered-data writeout, and runs the `gfs2_logd` background thread.

## Important APIs, types, and functions
External functions include `gfs2_struct2blk`, `gfs2_log_is_empty`, `gfs2_log_release_revokes`, `gfs2_log_release`, `gfs2_log_try_reserve`, `gfs2_log_reserve`, `gfs2_write_log_header`, `gfs2_remove_from_journal`, `gfs2_log_flush`, `gfs2_log_commit`, `gfs2_ail1_flush`, `log_flush_wait`, `gfs2_add_revoke`, `gfs2_glock_remove_revoke`, `gfs2_flush_revokes`, `gfs2_ail_drain`, and `gfs2_logd`. Key internal helpers are `gfs2_ail1_start_one`, `gfs2_ail1_empty_one`, `log_pull_tail`, `gfs2_ordered_write`, `gfs2_ordered_wait`, `log_write_header`, `__gfs2_log_flush`, `gfs2_merge_trans`, `log_refund`, and threshold predicates for journal and AIL flushing.

## Control Flow
Transactions reserve space through `gfs2_log_try_reserve` or `gfs2_log_reserve`; revoke reservations are accounted separately through `sd_log_revokes_available`, while log block reservations use `sd_log_blks_free` and `sd_log_blks_needed`. `gfs2_log_commit` refunds unused reservation, attaches or merges the transaction into `sd_log_tr`, recalculates reserved blocks with `calc_reserved`, and wakes `gfs2_logd` when pinned or occupied log blocks cross thresholds.

`gfs2_log_flush` takes `sd_log_flush_lock` and runs `__gfs2_log_flush`. The flush snapshots `sd_log_head`, detaches `sd_log_tr`, reserves minimal flush space if necessary, performs ordered-data writeout, calls `lops_before_commit` to write descriptors and payloads, submits pending journal bios, writes a log header if the log moved or the tail needs advancing, and then calls `lops_after_commit` to unpin buffers and put them on the AIL. Non-normal flushes can force AIL drain, write an additional header, and shut down the journal. On error or withdraw, pending bios are errored, pinned transaction buffers are drained, and the transaction is put on AIL1 so `gfs2_ail_drain` can free it.

AIL management is two-stage. AIL1 contains transaction buffers that still need in-place writeback; once clean, they move to AIL2. `log_pull_tail` empties AIL2 entries whose `tr_first` is behind the new tail and releases log blocks. `gfs2_ail1_flush` starts writeback by mapping buffers back to their inode address spaces and calling either journaled-data or normal writepages. `gfs2_ail1_empty` moves completed buffers, optionally turning eligible completed items into revokes. The background `gfs2_logd` wakes on thresholds or timeouts, performs journal flushes and AIL writeback, and exits on withdraw or kthread stop.

## State and Persistence
Persistent state is the journal stream: log descriptors, metadata/data payloads, revoke blocks, and log headers with sequence, tail, flags, physical address, journal inode, local statfs changes, hash, and CRC. In-memory state includes `sd_log_head`, `sd_log_tail`, `sd_log_flush_head`, `sd_log_flush_tail`, `sd_log_sequence`, `sd_log_tr`, `sd_log_blks_reserved`, `sd_log_num_revoke`, `sd_log_revokes`, `sd_log_ordered`, `sd_ail1_list`, `sd_ail2_list`, and atomic counters for free, needed, pinned, in-flight, and revoke-available blocks.

## Dependencies and Integration Points
`log.c` calls the log operation table in `lops.c`, writes pages through `gfs2_log_write`, uses metadata and bmap helpers, touches glock state and revoke counts, drives ordered writeback for data mode, and integrates with transaction lifecycle in `trans.c`. It is called from glock demotion paths, file sync paths, remount/read-only conversion, freeze, kill-superblock, quota sync, statfs, and recovery clean-up.

## Risks
Journal accounting is corruption-sensitive: `used_blocks` must match reserved blocks, revoke slack must align with descriptor capacity, and `GFS2_LOG_FLUSH_MIN_BLOCKS` protects logd from self-deadlock. AIL flushes can loop for a long time if buffers stay dirty or locked; ten-minute diagnostics and withdraw paths guard this. Barrier-disabled mode relies on ordered wait and log write completion instead of flush/FUA. Error handling must drain pinned buffers and pending transactions without double-freeing bufdata. Freeze and read-only recovery paths constrain which transactions and revokes may be flushed.

## Test Signals
Exercise transaction reservation/refund, forced log flush, sync flush, shutdown flush, freeze flush, barrier and nobarrier modes, AIL tail advancement, revoke-heavy block frees, ordered-data write ordering, journal write I/O errors and withdraw, logd threshold wakeups, unmount with nonempty AIL, and tracepoints for log block accounting and flush start/end.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/log.h -->
# sources/distributed-fs/ceph-client/fs/gfs2/log.h

## Purpose
`log.h` is the public journal-accounting interface used by GFS2 transaction, glock, metadata, inode, superblock, and quota code. It exposes log reservation, release, flush, revoke, ordered-data, AIL, and logd entry points.

## Important APIs, types, and functions
The central constant is `GFS2_LOG_FLUSH_MIN_BLOCKS`, reserving room for revoke and log header activity during flush. The inline helper `gfs2_ordered_add_inode` adds non-journaled ordered-data inodes to `sd_log_ordered` unless the inode is journaled data or the filesystem is not in ordered mode. Prototypes cover `gfs2_struct2blk`, `gfs2_log_is_empty`, `gfs2_log_try_reserve`, `gfs2_log_reserve`, `gfs2_write_log_header`, `gfs2_remove_from_journal`, `gfs2_log_flush`, `gfs2_log_commit`, `gfs2_ail1_flush`, `log_flush_wait`, `gfs2_logd`, revoke helpers, and `gfs2_ail_drain`.

## Control Flow
The header itself has no complex runtime flow. Its APIs define the expected transaction sequence: reserve log space, add buffers/revokes through transaction helpers, commit through `gfs2_log_commit`, let `gfs2_logd` or explicit callers run `gfs2_log_flush`, and use AIL/revoke helpers to release journal space once in-place blocks are safe.

## State and Persistence
The header declares no standalone state. It documents the state managed by `log.c`: in-memory reservation counters, ordered inode lists, revokes, AIL lists, and persistent journal headers/descriptors. `gfs2_ordered_add_inode` mutates `sd_log_ordered` under `sd_ordered_lock`.

## Dependencies and Integration Points
Includes `incore.h`, `inode.h`, Linux list/spinlock/writeback definitions, and buffer-head types through prototypes. It is included by transaction code, metadata I/O, lops, recovery, superblock lifecycle, glock operations, quota, resource-group code, and file/inode write paths.

## Risks
Callers must respect locking rules that are only partly visible in the header: `gfs2_log_try_reserve` expects `sd_log_flush_lock`, `gfs2_log_release_revokes` expects flush-lock protection, and ordered inode list insertion depends on double-checked list state. Misuse can produce log-space leaks, deadlocks, or ordered-data violations.

## Test Signals
Compile coverage for all log clients, transaction begin/end paths, ordered-data workloads, revoke-heavy deletes, flush callers under freeze/remount/unmount, and lockdep coverage around flush lock and ordered lock are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/lops.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/lops.c

## Purpose
`lops.c` implements GFS2 log operations for metadata buffers, revoke records, and journaled data buffers. It writes log descriptors and payload blocks during commit, unpins buffers afterward, scans journal descriptors during recovery, replays non-revoked blocks to their in-place locations, and provides low-level journal bio helpers and journal-head discovery.

## Important APIs, types, and functions
External helpers include `gfs2_pin`, `gfs2_log_incr_head`, `gfs2_log_bmap`, `gfs2_log_write`, `gfs2_log_submit_write`, `gfs2_find_jhead`, and `gfs2_drain_revokes`. The operation table is `gfs2_log_ops[]`, containing `gfs2_databuf_lops`, `gfs2_buf_lops`, and `gfs2_revoke_lops`. Important internals include `gfs2_unpin`, `maybe_release_space`, `gfs2_end_log_write`, `gfs2_log_get_bio`, `gfs2_jhead_folio_search`, `gfs2_get_log_desc`, `gfs2_before_commit`, `buf_lo_scan_elements`, `revoke_lo_scan_elements`, and `databuf_lo_scan_elements`.

## Control Flow
During transaction construction, `gfs2_pin` clears buffer dirty state, marks it pinned, moves preexisting AIL entries to AIL2, takes a buffer reference, and increments `sd_log_pinned`. During flush, `lops_before_commit` dispatches to `databuf`, `buf`, and `revoke` handlers. Metadata and data handlers sort buffers by in-place block number, write one or more log descriptor blocks, then write the actual payload blocks to the journal. Journaled data descriptors store both block numbers and escape flags; if a data block begins with the GFS2 magic value, a copied page is written with the magic zeroed and replay later restores it. Revoke commit writes revoke descriptors and continuation blocks from `sd_log_revokes`.

After the log header is committed, `lops_after_commit` unpins metadata and journaled-data buffers. `gfs2_unpin` marks the in-place buffer dirty, updates rgrp clone state and discard information for resource-group buffers, links bufdata into the transaction's AIL1 list, clears `GLF_LFLUSH`, and decrements `sd_log_pinned`. Revokes are drained and their held glocks are released.

For recovery, `gfs2_find_jhead` maps journal extents, reads journal blocks in large bio batches into the journal inode page cache, searches for the highest valid log header sequence, and truncates the page cache afterward. Recovery scanning runs in two passes: pass 0 collects revokes and initializes counters; pass 1 replays metadata and journaled data descriptors unless `gfs2_revoke_check` says the block was revoked after the descriptor. Replayed metadata is validated with `gfs2_meta_check`; resource-group replay emits diagnostics if an in-core rgrp buffer looks obsolete.

## State and Persistence
Persistent journal records are `GFS2_LOG_DESC_METADATA`, `GFS2_LOG_DESC_JDATA`, `GFS2_LOG_DESC_REVOKE`, continuation blocks, and payload blocks. Runtime state includes pinned buffer flags, bufdata lists, transaction counts, `jd_log_bio`, journal extent mappings, journal-head search page-cache folios, replay counters, and in-memory revoke lists. Resource-group clone state can be refreshed when rgrp buffers are unpinned after commit.

## Dependencies and Integration Points
The file depends on bmap extent mapping, glock and glops behavior, metadata I/O, recovery revoke helpers, rgrp bitmap helpers, transaction structs, tracepoints, mempool page allocation, buffer-head state, bio submission, and filesystem block-size geometry. `log.c` calls the lops table for every flush; `recovery.c` calls scan hooks through `lops.h`.

## Risks
The escape path contains a high-risk copy operation because journaled data that looks like metadata magic must be transformed without corrupting caller pages. Commit and replay descriptor lengths must match `buf_limit` and `databuf_limit`. Journal-head search uses page-cache refs and chained bios, so refcount mistakes would leak or prematurely release folios. Replay must honor revokes across wraparound, validate metadata, and avoid stale rgrp state. Log I/O errors set `sd_log_error` and withdraw, so error propagation is intentionally severe.

## Test Signals
Signals include metadata and journaled-data transactions spanning multiple descriptors, data blocks beginning with GFS2 magic, revoke collection and replay skip behavior, journal wraparound head detection, discontinuous journal extents, bio chaining under large journals, rgrp replay diagnostics, log write I/O errors, mempool pressure, and recovery pass counters for found versus replayed blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/lops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/lops.h -->
# sources/distributed-fs/ceph-client/fs/gfs2/lops.h

## Purpose
`lops.h` defines the dispatch interface for GFS2 log operation implementations and declares low-level journal write, pinning, journal-head discovery, and revoke-drain helpers.

## Important APIs, types, and functions
The main exported object is `extern const struct gfs2_log_operations *gfs2_log_ops[]`. Helper prototypes expose `gfs2_log_incr_head`, `gfs2_log_bmap`, `gfs2_log_write`, `gfs2_log_submit_write`, `gfs2_pin`, `gfs2_find_jhead`, and `gfs2_drain_revokes`. `buf_limit` and `databuf_limit` compute per-descriptor payload capacities from `sd_ldptrs`. Inline dispatchers are `lops_before_commit`, `lops_after_commit`, `lops_before_scan`, `lops_scan_elements`, and `lops_after_scan`.

## Control Flow
`log.c` calls the before/after commit dispatchers during a flush; each walks `gfs2_log_ops[]` and invokes implemented hooks. `recovery.c` calls the scan dispatchers around each replay pass and for each descriptor. `lops_scan_elements` stops on the first hook error. `lops_after_scan` is intended to call each `lo_after_scan` hook when scanning completes.

## State and Persistence
No state is declared in the header. It defines how operations act on transaction lists, journal descriptors, and replay state owned by `gfs2_sbd` and `gfs2_jdesc`. The limits encode persistent descriptor layout capacity.

## Dependencies and Integration Points
Includes `incore.h` for `struct gfs2_sbd`, `struct gfs2_jdesc`, and `struct gfs2_log_operations`. It is consumed by `log.c`, `lops.c`, and `recovery.c`, binding commit-time and recovery-time behavior together.

## Risks
The hook order is part of the journal format behavior: data, metadata, and revokes must remain coherent with recovery passes. `databuf_limit` halves descriptor capacity because each data buffer needs block number plus escape flag. The `lops_after_scan` inline checks `lo_before_scan` before calling `lo_after_scan`, which means a future operation that only has `lo_after_scan` would be skipped unless this condition changes.

## Test Signals
Build-time coverage of all hook users, recovery with all descriptor types, transactions that hit descriptor limits, and tests adding any new log operation without a complete hook set are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/lops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/main.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/main.c

## Purpose
`main.c` is the GFS2 module entry and exit file. It initializes global caches, workqueues, debugfs, quota hash/shrinker state, page pools, and filesystem type registrations, and tears them down in reverse order on module unload.

## Important APIs, types, and functions
The entry points are `init_gfs2_fs` and `exit_gfs2_fs`, wired through `module_init` and `module_exit`. Object constructors are `gfs2_init_inode_once`, `gfs2_init_glock_once`, and `gfs2_init_gl_aspace_once`. The file defines the global `struct workqueue_struct *gfs2_control_wq`; `gfs2_recovery_wq` is defined in `recovery.c` but allocated here. It initializes caches for glocks, glock address spaces, inodes, bufdata, resource groups, quota data, qadata, and transactions.

## Control Flow
Initialization sets up qstrs for `.` and `..`, initializes the quota hash table and sysfs, creates the quota LRU and glock subsystem, allocates all slab caches, registers the quota-data shrinker, creates recovery/control/freeze workqueues, creates the page mempool, registers debugfs, and registers both `gfs2` and `gfs2meta` filesystem types. Each failure label unwinds only the resources already created. Exit unregisters filesystems and debugfs, stops global workqueues, destroys the LRU, waits for pending RCU callbacks with `rcu_barrier`, destroys the page pool and caches, and uninitializes sysfs.

## State and Persistence
The file owns process-wide kernel resources, not on-disk state. Persistent filesystem state is unaffected except through registration availability. The slab constructors initialize per-object list heads, lock state, quota pointers, reservation trees, and address-space objects so later mount-time code can rely on clean invariants.

## Dependencies and Integration Points
It integrates with sysfs (`gfs2_sys_init`), glock subsystem initialization, quota shrinker setup, recovery and control workqueues used by `recovery.c` and `lock_dlm.c`, freeze workqueue used by superblock code, debugfs, the shared page mempool used by log writes, and VFS filesystem registration through `gfs2_fs_type` and `gfs2meta_fs_type`.

## Risks
Initialization order matters because later caches and workqueues depend on earlier global subsystems. Exit must wait for RCU before freeing quota-data cache objects. Workqueues must be destroyed after filesystems are unregistered and mounts have gone away. Constructor omissions can surface as list corruption or stale lock state in reused slab objects.

## Test Signals
Signals include module load/unload, failure injection at each cache/workqueue/mempool/registration step, lockdep and KASAN coverage of slab constructors, mounting after repeated module reloads, quota shrinker registration, and ensuring no global workqueue work remains after filesystem unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/meta_io.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/meta_io.c

## Purpose
`meta_io.c` provides buffer-cache and address-space operations for GFS2 metadata and resource-group blocks. It maps filesystem blocks into glock-specific or global metadata address spaces, submits metadata reads and writeback, creates new metadata buffers, waits for metadata I/O, wipes journal state for freed blocks, and performs metadata readahead.

## Important APIs, types, and functions
Exported address-space operations are `gfs2_meta_aops` and `gfs2_rgrp_aops`. Exported functions include `gfs2_getbuf`, `gfs2_meta_new`, `gfs2_meta_read`, `gfs2_meta_wait`, `gfs2_journal_wipe`, `gfs2_meta_buffer`, and `gfs2_meta_ra`. Important internals are `gfs2_aspace_write_folio`, `gfs2_aspace_writepages`, `meta_prep_new`, `gfs2_meta_read_endio`, `gfs2_submit_bhs`, `gfs2_ail1_wipe`, and `gfs2_getjdatabuf`.

## Control Flow
`gfs2_getbuf` chooses the glock address space or the filesystem metadata address space, computes the folio index and buffer index from the filesystem block number, optionally creates the folio and empty buffers, maps the selected buffer to the block device, and returns a referenced `buffer_head`. `gfs2_meta_new` gets a created buffer and initializes the metadata magic after marking the buffer uptodate. `gfs2_meta_read` gets the buffer, locks it, queues a metadata read if not uptodate, optionally queues one-block readahead, submits adjacent buffers as one or more bios, and waits if `DIO_WAIT` is requested. `gfs2_meta_wait` waits for a buffer and turns failed reads into EIO, with extra error reporting if the current transaction was touched.

`gfs2_aspace_writepages` iterates dirty metadata folios. `gfs2_aspace_write_folio` locks dirty buffers, marks them async write, starts folio writeback, submits each buffer with metadata/prio flags, and ends writeback immediately if no buffer was submitted. Journal wiping first removes matching buffers from AIL1, then searches metadata or journaled-data page cache buffers for the block range, removes pinned/AIL journal state with `gfs2_remove_from_journal`, and clears dirty/uptodate state. `gfs2_meta_buffer` wraps read plus metatype validation. `gfs2_meta_ra` starts a bounded extent readahead and returns the first buffer, waiting when needed.

## State and Persistence
Runtime state is in buffer-head flags, folio writeback state, glock address-space mappings, AIL and pinned journal lists, and current transaction flags. Persistent effects include metadata writes to in-place disk blocks and removal of freed/deleted blocks from future journal replay. New metadata buffers receive only the GFS2 magic here; callers fill type and body fields.

## Dependencies and Integration Points
This file depends on glock address spaces, log and lops buffer state, transaction helpers, rgrp release paths, metadata validation in `util.h`, Linux buffer-head/page-cache/writeback APIs, and block bio submission. It is used by bmap, dir, xattr, quota, recovery, rgrp, superblock, and lops replay code.

## Risks
Correctness depends on block-size-to-page indexing, buffer refcounts, and locked-buffer state. `gfs2_submit_bhs` assumes the buffer array contains initialized entries; zero-entry submission is avoided by callers' flow. Journal wiping must coordinate `sd_log_lock` and `sd_ail_lock` with buffer locks to avoid leaving stale pinned or AIL buffers that later replay freed blocks. Metadata reads during withdraw return EIO. Readahead must not exceed tune limits and must handle partial extent completion.

## Test Signals
Signals include metadata reads with and without wait, readahead on inode and directory extents, failed metadata I/O in touched transactions, metadata writeback under memory pressure, block free/truncate journal wipe for metadata and journaled-data files, AIL removal of freed blocks, metatype validation failures, and lockdep around log/AIl/buffer lock ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/meta_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/meta_io.h -->
# sources/distributed-fs/ceph-client/fs/gfs2/meta_io.h

## Purpose
`meta_io.h` declares GFS2 metadata buffer I/O helpers and small buffer manipulation utilities used throughout the filesystem.

## Important APIs, types, and functions
Inline helpers are `gfs2_buffer_clear`, `gfs2_buffer_clear_tail`, `gfs2_buffer_copy_tail`, `gfs2_mapping2sbd`, and `gfs2_meta_inode_buffer`. It declares `gfs2_meta_aops`, `gfs2_rgrp_aops`, `gfs2_meta_new`, `gfs2_meta_read`, `gfs2_meta_wait`, `gfs2_getbuf`, `gfs2_journal_wipe`, `gfs2_meta_buffer`, and `gfs2_meta_ra`. The `REMOVE_JDATA` and `REMOVE_META` enum values select accounting behavior in `gfs2_remove_from_journal`. `buffer_busy` tests dirty, locked, or pinned buffer state.

## Control Flow
The header has no standalone flow. Callers use `gfs2_getbuf` and `gfs2_meta_read` to access metadata, `gfs2_meta_buffer` or `gfs2_meta_inode_buffer` when metatype validation is required, and `gfs2_journal_wipe` when blocks are freed or inode creation is abandoned.

## State and Persistence
The inline buffer helpers directly mutate buffer data. `gfs2_mapping2sbd` interprets mappings owned by `gfs2_meta_aops` as glock address spaces and other mappings as inode-backed filesystem mappings. The declared functions manage persistent metadata and journal visibility through buffer-head state and disk I/O.

## Dependencies and Integration Points
Includes Linux buffer-head and string helpers plus `incore.h`. It is included by most metadata-heavy GFS2 files, including bmap, dir, xattr, quota, log/lops, recovery, rgrp, inode, and superblock code.

## Risks
The tail-copy helper assumes `from_head >= to_head` and uses buffer sizes directly; incorrect offsets would corrupt metadata. `gfs2_mapping2sbd` relies on address-space operations identity. `buffer_busy` is a compact predicate used by log/AIL code, so semantic changes to buffer flags would affect journal tail advancement.

## Test Signals
Compile coverage, metadata block allocation and zeroing, stuffed-to-unstuffed transitions, directory/xattr metadata copies, journal wipe tests, and lockdep/KASAN around buffer offset helpers are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/meta_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/ops_fstype.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/ops_fstype.c

## Purpose
`ops_fstype.c` implements GFS2 and GFS2 meta-filesystem mount, reconfigure, and kill-superblock operations. It allocates and initializes `struct gfs2_sbd`, parses mount options, joins the selected lock manager, reads and validates the on-disk superblock, initializes journals/statfs/rgrp/quota/per-node state, starts per-mount threads, and unwinds those resources on mount failure or unmount.

## Important APIs, types, and functions
External symbols include `free_sbd`, `gfs2_lm_unmount`, `gfs2_online_uevent`, `gfs2_destroy_threads`, `gfs2_fs_type`, and `gfs2meta_fs_type`. Major internal functions are `gfs2_tune_init`, `init_sbd`, `gfs2_check_sb`, `gfs2_sb_in`, `gfs2_read_super`, `gfs2_read_sb`, `init_names`, `init_locking`, `init_sb`, `gfs2_jindex_hold`, `init_statfs`, `init_journal`, `init_inodes`, `init_per_node`, `gfs2_lm_mount`, `wait_on_journal`, `init_threads`, `gfs2_fill_super`, `gfs2_get_tree`, `gfs2_parse_param`, `gfs2_reconfigure`, `gfs2_meta_get_tree`, `gfs2_evict_inodes`, and `gfs2_kill_sb`.

## Control Flow
Mount starts through fs-context parsing. `gfs2_init_fs_context` allocates default `gfs2_args`; `gfs2_parse_param` fills lock protocol/table/hostdata, spectator mode, ACL, quota, data mode, discard, barrier, error, commit, statfs, and quota timing options. `gfs2_get_tree` calls `get_tree_bdev`, which invokes `gfs2_fill_super`. Fill-super initializes `sdp`, applies spectator/read-only and feature flags, sets VFS operations, creates the metadata inode/address space, auto-detects lock names from the on-disk superblock if needed, creates per-mount workqueues/debugfs/sysfs, joins the lock manager, acquires nondisk mount/live/rename/freeze glocks, rereads the superblock under the superblock glock, waits for DLM journal id assignment when needed, initializes journals and hidden inodes, loads rgrps, initializes per-node quota-change inode state, starts `logd` and `quotad` for writable mounts, takes the freeze lock, and makes the filesystem writable if requested.

Journal initialization loads the `jindex` directory entries into `gfs2_jdesc` objects, validates the selected journal, maps its extents, initializes statfs inodes, and runs first-mount or local journal recovery. First mounter recovery replays or checks every journal and then calls `gfs2_others_may_mount`. Failure labels undo each initialized subsystem in reverse order. Reconfigure forbids changing cluster identity, hostdata, spectator mode, localflocks, or gfs2/meta role, allows read-only toggles through `gfs2_make_fs_ro/rw`, updates ACL/barrier/tuning flags, and emits an online uevent. The `gfs2meta` filesystem does not mount independently; it locates an existing GFS2 mount by block device and returns its master directory.

## State and Persistence
The file initializes most per-mount runtime state in `gfs2_sbd`: tune values, waitqueues, completions, glock stats, jindex list, quota list and bitmap controls, statfs state, log counters and AIL lists, journal descriptors, hidden inode dentries, workqueues, sysfs/debugfs state, and mount arguments. Persistent reads include the superblock, master/root inode numbers, jindex, statfs, per-node files, quota file, and rindex. Persistent writes can occur during journal recovery, statfs initialization/recovery, quota changes, and make-rw transitions.

## Dependencies and Integration Points
This file is the integration point between VFS/fs_context, block devices, locking (`lock_nolock` or `lock_dlm`), glocks, recovery, log, quota, statfs, rgrp, superblock operations, sysfs/debugfs, kthreads, freeze handling, export operations, quota control, and the hidden meta filesystem. `main.c` registers the `gfs2_fs_type` and `gfs2meta_fs_type` defined here.

## Risks
Mount ordering is fragile: locking must be live before trusted superblock reread, journal recovery needs statfs inodes, per-node quota files need a selected journal, and writable transition must happen after recovery. Failure unwind must not double-drop dentries, glocks, or workqueues. Spectator mounts are forced read-only and cannot perform first-mounter recovery. DLM journal-id assignment can be interrupted. Reconfigure must keep cluster identity immutable. `gfs2_kill_sb` flushes the log and uses cooperative inode eviction to avoid cluster iopen deadlocks.

## Test Signals
Signals include lock_nolock and lock_dlm mounts, missing or invalid locktable/protocol, spectator and meta mounts, first mounter and non-first mounter recovery, invalid superblock format/block size, no journals, bad selected journal id, mount failure injection at every initialization stage, remount ro/rw and tuning changes, disallowed reconfigure changes, quota/statfs/rgrp initialization, kill-superblock with unlinked inodes, and uevents for online and first-mount completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/ops_fstype.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/quota.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/quota.c

## Purpose
`quota.c` implements GFS2 clustered quota accounting and quota control. It caches quota records in per-ID glocks with LVBs, records local per-node quota deltas in `quota_change<JID>` files, periodically syncs those deltas into the shared quota inode, checks allocations against limits, exposes VFS quotactl operations, and runs the `gfs2_quotad` background sync thread.

## Important APIs, types, and functions
External APIs include `gfs2_qa_get`, `gfs2_qa_put`, `gfs2_quota_hold`, `gfs2_quota_unhold`, `gfs2_quota_lock`, `gfs2_quota_unlock`, `gfs2_quota_check`, `gfs2_quota_change`, `gfs2_quota_sync`, `gfs2_quota_refresh`, `gfs2_quota_init`, `gfs2_quota_cleanup`, `gfs2_wake_up_statfs`, `gfs2_quotad`, `gfs2_qd_shrinker_init`, `gfs2_qd_shrinker_exit`, `gfs2_quota_hash_init`, and `gfs2_quotactl_ops`. Important internals include `qd_get`, `qd_alloc`, `qd_put`, slot and buffer helpers (`slot_get`, `bh_get`, `qdsb_get`), `do_qc`, `gfs2_adjust_quota`, `do_sync`, `update_qd`, `do_glock`, `need_sync`, `gfs2_get_dqblk`, and `gfs2_set_dqblk`.

## Control Flow
Quota data objects are hashed by `(sdp, kqid)` into an RCU hlist and linked on a per-superblock list plus a global LRU. `qd_get` first searches under RCU, allocates a new object and quota glock if needed, and inserts it under `qd_lock` plus a bucket lock. Objects use `lockref`; when their count reaches zero, they move to `gfs2_qd_lru` unless the journal is no longer live, in which case they are disposed.

Allocation paths call `gfs2_quota_lock_check` from the header or explicitly call `gfs2_quota_lock`. `gfs2_quota_hold` prepares qadata for current uid/gid and optional new uid/gid, obtains quota-change slots and buffers, and stores qd pointers on the inode. `gfs2_quota_lock` sorts qds to avoid deadlocks and locks each quota glock through `do_glock`, which reads from the LVB or refreshes from the quota inode under an exclusive quota glock. `gfs2_quota_check` compares requested/minimum allocation against hard and warning limits using LVB value plus local unsynced change. `gfs2_quota_change` updates the per-node quota-change buffer inside the active transaction through `do_qc`.

Unlock checks whether local changes are close enough to a limit to need immediate sync. Periodic or forced sync uses `gfs2_quota_sync`, which increments `sd_quota_sync_gen`, grabs batches of changed qds, maps their quota-change buffers, and calls `do_sync`. `do_sync` locks qd glocks and the quota inode, reserves allocation space if new quota records are needed, begins a transaction, applies each local delta to the shared quota record through `gfs2_adjust_quota`, subtracts the delta from `quota_change`, ends the transaction, flushes the quota inode glock, and advances each qd's sync generation. `gfs2_quota_init` scans the per-node quota-change file at mount, reconstructs changed qds and slot bitmap state, and zeros duplicate slots. `gfs2_quotad` periodically runs statfs sync and quota sync and wakes for forced statfs work.

## State and Persistence
Persistent state is split between the shared `quota` inode (`struct gfs2_quota` records indexed as user/group pairs) and the per-node `quota_change<JID>` inode (`struct gfs2_quota_change` slots). Runtime state includes the qd hash, qd LRU, per-qd glock/LVB cache, qd change counters, slot bitmap, qadata arrays on inodes, quota sync generation, and quiet/warning flags. Quota glock LVBs cache limit, warn, and usage values with `GFS2_MAGIC`.

## Dependencies and Integration Points
Quota code depends on glocks and quota glops, bmap/iomap, metadata I/O, transactions, log flushing, rgrp allocation reservation, inode hidden-file handling, VFS quota APIs, netlink quota warnings, shrinkers, RCU, list_lru, and mount options from `ops_fstype.c`. Allocation and ownership-changing paths in inode, bmap, file, xattr, dir, rgrp, and superblock code call into this API.

## Risks
Clustered quotas are intentionally fuzzy because local deltas are synced periodically, so enforcement can temporarily overrun limits. Correctness relies on transactionally updating quota-change slots with allocation changes; missed `gfs2_quota_change` calls would corrupt accounting. Lock ordering (`qd_lock -> bucket lock -> qd lockref -> LRU`, and qd sorting before glock acquisition) is deadlock-sensitive. Cleanup asserts journal liveness state and waits up to 60 seconds for qds. `gfs2_quota_init` duplicate-slot repair must write back dirty buffers. Page-boundary quota records and stuffed quota inode unstuffing require conservative transaction reservations.

## Test Signals
Signals include quota on/account/off/quiet modes, uid and gid hard/soft limit checks, warning period and quiet reset, allocation/free/change-owner flows, immediate sync near limits, periodic `quotad` sync, forced statfs wake, quotactl get/set, quota records crossing page or block boundaries, stuffed quota inode expansion, duplicate quota_change slot detection, shrinker reclamation, mount-time reconstruction of unsynced deltas, cleanup with live qd references, and multi-node overrun behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/quota.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/quota.h -->
# sources/distributed-fs/ceph-client/fs/gfs2/quota.h

## Purpose
`quota.h` declares the clustered quota API used by GFS2 allocation, inode, xattr, directory, superblock, and mount code.

## Important APIs, types, and functions
It defines sentinel uid/gid values `NO_UID_QUOTA_CHANGE` and `NO_GID_QUOTA_CHANGE`. It declares qadata lifetime functions, hold/unhold, lock/unlock, check/change, sync/refresh, init/cleanup, quotad, statfs wake, quotactl ops, qd shrinker setup/teardown, global qd LRU, and quota hash initialization. The inline `gfs2_quota_lock_check` combines common allocation behavior: assume unlimited allocation, bypass quotas when off or caller has `CAP_SYS_RESOURCE`, lock quota qds, skip enforcement in account-only mode, otherwise run `gfs2_quota_check` and unlock on failure.

## Control Flow
Allocation callers typically call `gfs2_quota_lock_check` before reserving or allocating blocks, then call `gfs2_quota_change` inside the transaction and `gfs2_quota_unlock` afterward. More complex ownership-change or metadata paths can call hold/lock/check/change/unlock directly.

## State and Persistence
No state is defined here except external declarations. The API controls state maintained by `quota.c`: inode qadata, qd cache/LRU/hash, quota glock LVBs, per-node quota_change slots, and shared quota records.

## Dependencies and Integration Points
The header depends on `list_lru.h` and GFS2 core structs. It is consumed by mount/module initialization, allocation and free paths, inode operations, file writes, xattr changes, directory operations, sysfs-triggered sync, and superblock read-only transitions.

## Risks
Callers must pair lock/hold APIs correctly and must call `gfs2_quota_unlock` to drop glocks and potentially sync local deltas. Bypassing the inline for privileged or quota-off cases is valid, but bypassing `gfs2_quota_change` after allocation/free is not. `GFS2_QUOTA_ACCOUNT` records usage but intentionally skips enforcement.

## Test Signals
Compile coverage of all quota clients, allocation failure due to hard limits, account-only mode, privileged allocation bypass, owner change with old/new ids, cleanup of qadata references, and lockdep coverage of quota lock/unlock pairing are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/recovery.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/recovery.c

## Purpose
`recovery.c` implements GFS2 journal replay and recovery result reporting. It reads journal blocks, builds revoke replay state, validates log headers, iterates active journal descriptors, replays non-revoked metadata and journaled data via lops hooks, repairs statfs accounting from log headers, writes clean recovery headers, and coordinates asynchronous recovery work.

## Important APIs, types, and functions
External APIs are `gfs2_replay_read_block`, `gfs2_revoke_add`, `gfs2_revoke_check`, `gfs2_revoke_clean`, `__get_log_header`, `gfs2_recover_func`, `gfs2_recover_journal`, and `gfs2_log_pointers_init`. Internal helpers include `get_log_header`, `foreach_descriptor`, `clean_journal`, `gfs2_recovery_done`, `update_statfs_inode`, and `recover_local_statfs`. The global workqueue `gfs2_recovery_wq` is defined here and allocated in `main.c`.

## Control Flow
`gfs2_recover_journal` marks a journal descriptor with `JDF_RECOVERY`, queues `gfs2_recover_func`, and optionally waits for the bit to clear. The worker refuses recovery on withdrawn or spectator mounts. For foreign journals, it tries to acquire the journal glock exclusively with `LM_FLAG_TRY`; busy journals are treated as another node doing the work. It also locks the journal inode glock shared. It validates the journal descriptor, finds the journal head with `gfs2_find_jhead`, and skips replay if the head has `GFS2_LOG_HEAD_UNMOUNT`.

If replay is required, the worker locks `sd_freeze_mutex`, rejects frozen or read-only-block-device cases, and may temporarily allow recovery on a read-only mount if the device is writable and recovery has not yet been checked. Under `sd_log_flush_lock` read mode, it runs two descriptor passes from `lh_tail` to `lh_blkno`: pass 0 lets lops collect revokes, pass 1 replays metadata and journaled data. It then applies local statfs changes from the log header to the master statfs inode, zeros the local statfs inode for that jid, writes a clean recovery log header, and releases locks. Recovery of the local journal initializes `sd_log_sequence`, tail, head, and flush pointers from the recovered head. Completion sends a uevent and invokes `lm_recovery_result` so `lock_dlm.c` can clear or retain control-LVB jid bits.

## State and Persistence
Persistent state read during recovery includes journal log headers, descriptors, revoke records, metadata/data payloads, and statfs deltas stored in log headers. Persistent writes include replayed in-place metadata/data buffers, statfs inode updates, zeroed local statfs changes, and a clean recovery header marked with `GFS2_LOG_HEAD_RECOVERY`. In-memory state includes `jd_revoke_list`, replay counters, `jd_recover_error`, `JDF_RECOVERY`, and recovery status fields in `lm_lockstruct`.

## Dependencies and Integration Points
Recovery depends on journal extent mapping and metadata readahead, log header parsing and writing from `log.c`, lops scan hooks from `lops.c`, glocks and journal glops, statfs helpers, freeze/read-only superblock state, DLM lock-manager result callbacks, uevents, and the global recovery workqueue. `ops_fstype.c` invokes recovery during mount; `lock_dlm.c` schedules recovery for failed jids.

## Risks
Replay must not run while the filesystem is frozen or on a read-only block device. The two-pass scan requires revokes to be collected before payload replay; wraparound logic in `gfs2_revoke_check` is critical. `foreach_descriptor` treats unexpected headers or metatype failures as consistency errors. Concurrent log flushes and recovery share `jd_log_bio`, so `sd_log_flush_lock` protects them. Error paths must unlock freeze mutex and glocks exactly once and must report `LM_RD_GAVEUP` so another node can retry.

## Test Signals
Signals include clean journal detection, dirty journal replay, revoke skip behavior across wraparound, metadata and journaled-data replay, statfs delta recovery and zeroing, recovery on read-only mount with writable device, rejection on read-only block device, frozen filesystem rejection, busy foreign journal glock, malformed log header/hash/CRC, descriptor metatype errors, local journal pointer initialization, uevent status, and DLM recovery result propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/recovery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/recovery.h -->
# sources/distributed-fs/ceph-client/fs/gfs2/recovery.h

## Purpose
`recovery.h` declares GFS2 journal recovery and replay helpers shared by recovery, lops, mount, sysfs, and lock-manager code.

## Important APIs, types, and functions
It declares the global `gfs2_recovery_wq`, inline `gfs2_replay_incr_blk`, block read helper `gfs2_replay_read_block`, revoke replay helpers, `gfs2_recover_journal`, worker `gfs2_recover_func`, log header parser `__get_log_header`, and `gfs2_log_pointers_init`.

## Control Flow
The inline `gfs2_replay_incr_blk` advances a journal block number and wraps to zero at `jd_blocks`. Recovery code uses it when scanning descriptors, payload blocks, and writing clean headers. Other declarations support queuing recovery work, waiting for completion, parsing journal headers, and initializing local log pointers after replay.

## State and Persistence
The header itself stores no state. Its APIs operate on `gfs2_jdesc` replay lists, journal block positions, log header host structures, and superblock log pointers.

## Dependencies and Integration Points
Includes `incore.h` for GFS2 core structures. `lops.c` uses revoke and replay block helpers; `ops_fstype.c` and sysfs code call `gfs2_recover_journal`; `lock_dlm.c` receives recovery results indirectly through lock operations; `main.c` allocates the declared recovery workqueue.

## Risks
The wraparound helper is tiny but central; incorrect journal block advancement would corrupt replay boundaries. Callers must respect `JDF_RECOVERY` serialization in `gfs2_recover_journal` and must not parse untrusted log headers without checking the return value from `__get_log_header`.

## Test Signals
Compile coverage, journal wraparound replay, asynchronous and synchronous recovery callers, log header validation tests, and recovery workqueue lifetime across module load/unload are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/recovery.h -->
