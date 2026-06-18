# sources/distributed-fs/moosefs/mfsmaster/chunks.c lines 1-8929

Work item: `subset-b-007682`

## Purpose

This range is the core MooseFS master-side chunk manager. It owns the in-memory chunk table, per-chunk copies and erasure-coded parts, storage-class membership accounting, chunkserver registration/disconnection state, client-visible chunk version/copy queries, metadata loading for chunk records, and the main background repair/replication/rebalancing scheduler.

The code treats a chunk as a metadata object with:

- A stable `chunkid`, `version`, `lockedto` timestamp, operation state, and flags for archive/trash/allow-read-zeros.
- A sorted `slist` of chunkserver placements, where each entry is either a full copy (`ecid == 0`) or an EC4/EC8 data/checksum part.
- A compact file-reference/storage-class membership encoding in `fhead`, using small inline counts for simple cases and `flist` nodes for multi-storage-class ownership.
- Derived redundancy counters (`storage_mode`, `all_gequiv`, `reg_gequiv`) that feed UI counters, policy checks, and danger queues.

The range also implements policy execution: it detects endangered, undergoal, overgoal, wrong-label, unfinished EC-conversion, marked-for-removal, and IO-readiness cases; queues chunks by priority; and issues chunkserver commands to create, delete, duplicate, truncate, split, join, recover, or replicate chunk material.

## Important Types and State

- `slist`: one copy/part placement. Fields are `csid`, `valid`, `ecid`, `version`, and `next`. Valid states are `INVALID`, `DEL`, `BUSY`, `VALID`, `WVER`, `TDBUSY`, `TDVALID`, and `TDWVER`.
- `chunk`: the primary chunk record. It stores versioning/locking bits, storage class and flags, operation state (`NONE`, `CREATE`, `SET_VERSION`, `DUPLICATE`, `TRUNCATE`, `DUPTRUNC`, `REPLICATE`, `LOCALSPLIT`), file-reference head, server placement list, and hash linkage.
- `flist`: overflow representation for chunks shared by multiple files and/or storage classes. `fhead < FLISTFIRSTINDX` is an inline file count; otherwise it indexes linked `flist` records.
- `csdata`: master-side chunkserver slot state. It carries the server pointer, pending operation chunks, registration/valid flags, and mark-for-removal state (`UNKNOWN_HARD`, `UNKNOWN_SOFT`, `CAN_BE_REMOVED`, `REPL_IN_PROGRESS`, `WAS_IN_PROGRESS`).
- `chq_element`: danger-priority queue node. Queues are split into nine priorities: IO readiness, one-copy, marked-for-removal, unfinished EC, undergoal, overgoal, and wrong labels.
- `replock`: short-lived replication lock keyed by chunk id. It prevents reads/modifications from racing a replication-like operation even when `lockedto` is not used.
- Global accounting matrices: `allchunkcopycounts`, `regchunkcopycounts`, `allchunkec8counts`, `regchunkec8counts`, `allchunkec4counts`, and `regchunkec4counts`, indexed by storage class and flag group, then goal-equivalent count.

Memory is mostly bucket-allocated through `CREATE_BUCKET_ALLOCATOR` for `chunk`, `slist`, queue nodes, `io_ready_chunk`, and `replock`. The chunk hash uses lazily allocated high/low bucket arrays and incremental rehashing.

## Core APIs and Behaviors

### Hashing, Allocation, and Counters

- `chunk_hash_init`, `chunk_hash_add`, `chunk_hash_find`, `chunk_hash_delete`, `chunk_hash_move`, and `chunk_hash_rehash` maintain an expanding hash table over `chunkid`. Rehashing is incremental, so normal lookups and updates also move a bounded number of buckets.
- `chunk_new`, `chunk_find`, and `chunk_delete` allocate, cache, index, and free chunk records. `chunk_find` has a single-entry last lookup cache.
- `chunk_state_fix` recomputes the current storage mode and redundancy from the placement list. It understands full copies, EC4 parts (`0x10..0x1C`), EC8 parts (`0x20..0x30`), mark-for-removal states, and unique-server constraints.
- `chunk_state_change`, `chunk_state_set_counters`, `chunk_state_set_flags`, and `chunk_state_set_sclass` update the global accounting matrices whenever a chunk's derived state, flags, or storage class changes.
- `chunk_info`, `chunk_chart_data`, `chunk_store_chunkcounters`, `chunk_sclass_inc_counters`, and `chunk_sclass_has_chunks` expose aggregated counts for UI/status consumers.

### Label Matching and Server Selection

- `do_advanced_match` implements a modified bipartite matching algorithm between storage-class label expressions and candidate chunkservers. It folds servers into uniqueness groups using configured IP/rack/label uniqueness rules.
- `do_extend_match` fills unmatched labels with remaining servers when the storage-class label mode allows looser placement.
- `chunk_creation_servers` chooses randomized candidate chunkservers for new chunk creation, optionally respecting topology distance to the client IP, labels, overloaded state, and uniqueness rules.
- `chunk_labelset_fix_matching_servers` refreshes `storagemode` matching counts for copy mode, or EC server counters for EC mode.
- `chunk_labelset_can_be_fulfilled` classifies whether a storage mode can currently be fulfilled: no, only no-space/full, only overloaded, yes, or keep existing EC.

### File Reference and Storage Class Membership

- `chunk_add_file_int`, `chunk_delete_file_int`, and `chunk_change_file` maintain `fhead` and the effective `sclassid`.
- `chunk_compact_and_find_sclassid` compresses single-entry `flist` state back to inline form when possible.
- `chunk_recalc_sclassid` recalculates the effective storage class using `sclass_get_joining_priority`, then queues the chunk for policy repair if the effective class changes.

### Client-Facing Chunk Operations

- `chunk_read_check` rejects locked/busy chunks, accepts chunks with a full valid copy or all data EC parts, and can trigger a fast recovery job if enough EC parts exist but data parts are missing.
- `chunk_univ_multi_modify` handles new chunk allocation, in-place version bump for single-file chunks, or copy-on-write duplicate for shared chunks. It sends create, set-version, or duplicate requests to chunkservers and records changelog state indirectly through the caller path.
- `chunk_univ_multi_truncate` mirrors modify flow but sends truncate or duplicate-and-truncate requests.
- `chunk_unlock` and `chunk_mr_unlock` clear `lockedto`, stop write counters, and either run immediate queued work or notify client services.
- `chunk_repair` tries to resolve missing chunks from wrong-version full copies or recoverable EC sets; if repair is impossible and erasure is allowed it removes file ownership, otherwise it can set the read-zeros flag.
- `chunk_get_version_and_csdata`, `chunk_get_version_and_copies`, `chunk_get_version`, `chunk_get_eights_copies`, and `chunk_get_storage_status` return server location, version, EC split, and health data to other master/client-service modules.

### Chunkserver Integration

- `chunk_server_connected`, `chunk_server_register_end`, `chunk_server_disconnected`, and `chunk_server_disconnection_loop` manage `csid` allocation, registration counters, delayed removal of disconnected servers from all placement lists, and FUSE cache invalidation.
- `chunk_server_has_chunk`, `chunk_damaged`, and `chunk_lost` ingest chunkserver reports. They add missing metadata for plausible orphan chunks, mark invalid or wrong-version placements, remove lost placements, update write counters, and queue repair work.
- `chunk_got_delete_status`, `chunk_got_replicate_status`, `chunk_operation_status`, and the operation-specific wrappers reconcile asynchronous chunkserver replies. They transition BUSY entries to VALID/INVALID/WVER/DEL, clear operation lists, update stats, notify client services, and unlock chunks when safe.
- `chunk_got_status_data` compares master metadata against a chunkserver's detailed part inventory and can replace the server-specific placement entries in fix mode.

## Main Background Control Flow

The repair/scheduling engine is `chunk_do_jobs`; `chunk_jobs_main` drives it.

`chunk_jobs_main` first processes delayed disconnections, then services priority zero IO-readiness jobs. It pauses regular work while chunkserver counters are in progress or initial replication delay has not elapsed. It then drains danger queues in priority order, bounded by `HashCPTMax` and per-storage-class failure counters, and finally walks the chunk hash incrementally based on `LoopTimeMin`, `TicksPerSecond`, and the current hash size. It also broadcasts periodic chunk status probes for unlocked active chunks.

`chunk_do_jobs` is a decision tree:

1. On special modes (`JOBS_INIT`, `JOBS_EVERYLOOP`, `JOBS_EVERYTICK`, `JOBS_TERM`) it resets counters, snapshots loop stats, adjusts temporary delete limits, or frees static buffers.
2. It removes disconnected placements, stops write counters after locks expire, classifies all placements into valid, busy, invalid, deleting, wrong-version, EC4/EC8 masks, duplicate masks, and mark-for-removal masks.
3. It computes current copy/EC goal-equivalent redundancy and storage policy from the effective storage class. EC mode can be forced back to keep/copy mode when there are not enough servers to safely convert or maintain EC.
4. It repairs inconsistent operation state, wrong-version-only chunks, unexpected busy placements, invalid placements, unfinished replication locks, and unused chunks.
5. It blocks lower-priority work when higher-priority queues contain urgent items, or when chunkserver maintenance requests stop jobs.
6. It chooses replication/deletion limits based on priority and configured read/write replication rates.
7. It handles EC-specific recovery and conversion: duplicate EC parts on one server, missing EC data recovery from survivors, missing checksum creation, local split from full copy, split copy to EC parts, join EC data parts back to full copies, EC/copy cleanup after format conversion, and EC wrong-label repair.
8. It handles copy-mode overgoal, undergoal, wrong-label repair, and mark-for-removal disk cleanup.
9. If no correctness work remains, it may rebalance by moving a copy or EC part from a high-usage server to a lower-usage server while preserving labels, uniqueness, topology, and replication limits.

The danger queue is populated by `chunk_calculate_endanger_priority` and `chunk_priority_queue_check`. Priority calculation combines storage-class goals, EC mode, label feasibility, unique-server counts, mark-for-removal state, duplicate parts, wrong formats, wrong labels, and available replication servers.

## State and Persistence

The live in-memory state is authoritative during master runtime, while durable metadata and changelog entries preserve it across restarts and replication/replay:

- Changelog calls in this range include `SETVERSION`, `CHUNKADD`, `CHUNKDEL`, and `CHUNKFLAGSCLR` in paths that create orphan metadata, delete unused chunks, repair versions, or clear flags.
- Metadata replay helpers include `chunk_mr_nextchunkid`, `chunk_mr_chunkadd`, `chunk_mr_chunkdel`, `chunk_mr_flagsclr`, `chunk_mr_multi_modify`, `chunk_mr_multi_truncate`, `chunk_mr_increase_version`, `chunk_mr_set_version`, and `chunk_mr_unlock`.
- `chunk_load` reads metadata versions `0x10`, `0x11`, and `0x12`. Version `0x12` persists flags and dynamic storage-class/file-count pairs. A zero chunk record terminates the stream. The mapped range reaches the duplicate-chunk error branch inside this loader; the rest of the loader and `chunk_store` are immediately after the mapped range.
- `chunk_is_afterload_needed` returns false for `mver >= 0x12`, because newer metadata stores enough storage-class reference data directly.
- Runtime placement state from chunkservers is not fully persisted here; it is rebuilt by chunkserver reports and reconciled by status probes, damage/loss reports, and background jobs.

## Dependencies and Integration Points

Major module dependencies:

- `matocsserv`: server inventory, server health/load counters, label matching, replication/delete/create/truncate/split/join command sends, chunk status broadcasts, chunkserver data serialization, write counters, and registration state.
- `matoclserv`: client-visible chunk status and unlock notifications, FUSE chunk-cache invalidation.
- `storageclass`: storage mode, label mode, goal-equivalent calculations, class joining priority, and EC/copy policy data.
- `topology`: rack/IP distance and rack identity for placement and rebalance choices.
- `csdb`: whether all known servers are present and whether chunk jobs should pause for maintenance.
- `chunkdelay`: protects recently replicated chunks from immediate deletion.
- `changelog`, `metadata`, and `bio`: durable metadata/replay plumbing.
- `datapack`, `hashfn`, `bitops`, `random`, `buckets`, and `clocks`: serialization, hashing, bitset counts, randomization, pooled allocation, and timing.

This file is therefore a central integration point between filesystem metadata, chunkserver protocol commands, storage-class policy, client IO readiness, and master metadata persistence.

## Risks and Edge Cases

- The EC repair/rebalance decision tree is dense and stateful. Small changes to masks, goal-equivalent calculations, or priority ordering can create data-loss, livelock, or excessive replication risk.
- Many helper buffers are static and reused (`do_advanced_match`, `chunk_can_be_fixed`, `chunk_do_jobs`, label fulfillment helpers). This assumes master code runs these paths serially or under external synchronization.
- `chunk_do_jobs` uses many early returns after one action. Reordering checks can change repair precedence, especially around invalid deletion, EC recovery, wrong-version repair, and mark-for-removal cleanup.
- `lockedto`, `operation`, BUSY states, `replock`, and `opchunks` must stay consistent. Incomplete replies or disconnections are repaired, but missing a cleanup path can keep chunks locked/busy or notify clients incorrectly.
- EC4/EC8 IDs and masks are hand-coded. Off-by-one mistakes in checksum/data ranges or mask thresholds can make the master believe data is recoverable when it is not, or delete useful parts.
- Label and uniqueness behavior is split across copy mode, EC mode, strict/default/loose label modes, and global `DoNotUseSameIP`/`DoNotUseSameRack`. Tests must cover each mode because fallback behavior intentionally differs.
- The loader accepts older metadata versions and duplicate chunks conditionally through `ignoreflag`. Corrupt or partial metadata can leave counters wrong unless load-time state setters and post-load reconciliation are exercised.
- Queue bounding (`DangerMinLeng`, `DangerMaxLeng`), per-class failure counters, and temporary delete-limit escalation can hide starvation or bursty delete behavior under large clusters.

## Test Signals

Useful verification targets for this range:

- Unit or integration tests for `chunk_state_fix` across full copies, EC4, EC8, TDVALID/TDBUSY, duplicate EC parts, same-server EC parts, and wrong-version/invalid states.
- Metadata round-trip tests for versions `0x10`, `0x11`, and `0x12`, including multi-storage-class `flist` pairs, archive/trash flags, `allowreadzeros`, large pair counts using the high bit, duplicate chunk handling, and malformed terminators.
- Operation completion tests for create, set-version, duplicate, truncate, dup-truncate, replicate, and local split, including success, `MFS_ERROR_NOTDONE`, timeout, disconnection during operation, and all-nospace replies.
- Scheduler tests that seed danger queues and assert priority blocking: IO readiness first, one-copy before undergoal, bounded unfinished-EC/overgoal behavior, and per-class retry caps.
- EC recovery tests for missing data part recovery from survivors, checksum generation, split from full copy, join from EC parts, EC4-to-EC8 or EC-to-copy cleanup, and wrong-label EC part relocation.
- Copy-mode placement tests for strict/default/loose labels, uniqueness by IP/rack/label mask, overloaded/no-space server fallbacks, mark-for-removal copies, undergoal replication, overgoal deletion, and rebalance.
- Chunkserver report tests for nonexistent chunk creation-for-deletion, damaged/lost reports, version mismatch reporting, detailed status-data mismatch detection with and without fix mode, and delayed disconnection cleanup.
- Stress tests for large hash tables and incremental rehashing, ensuring no chunks are skipped by `chunk_jobs_main` hash walking or deleted while queued.
