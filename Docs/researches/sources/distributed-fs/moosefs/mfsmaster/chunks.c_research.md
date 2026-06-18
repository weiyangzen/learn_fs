# Research: sources/distributed-fs/moosefs/mfsmaster/chunks.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007682`: lines 1-8929, `Docs/researches/chunks/subset-b-007682_research.md`
- `subset-b-007683`: lines 8930-9650, `Docs/researches/chunks/subset-b-007683_research.md`

## Chunk Research

### subset-b-007682: lines 1-8929

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

### subset-b-007683: lines 8930-9650

# sources/distributed-fs/moosefs/mfsmaster/chunks.c lines 8930-9650

## Scope

This chunk covers the tail of MooseFS master chunk management in `chunks.c`. It starts inside `chunk_load()` after a duplicate chunk ID has been detected, then covers chunk metadata store, cleanup/new-filesystem reset, replication-limit parsing, teardown, shared chunk-loop configuration loading, diagnostic output, live reload, and module initialization.

The code in this range is a lifecycle boundary for the chunk subsystem: it reconstructs persisted chunk records, serializes current records back to metadata, resets in-memory structures, exposes chunk-loop diagnostics, applies config changes, and registers periodic/destructor callbacks with the master event loop.

## Purpose

The covered code has three main purposes:

- Persist and restore the master chunk table using the current `0x12` chunk metadata format, including chunk ID, version, lock deadline, flags, and per-storage-class file-reference lists.
- Own chunk-subsystem process lifecycle: cleanup after metadata reloads, initialize fresh filesystems, allocate global tables, free allocator-backed memory on shutdown, and register timers/reload/info callbacks.
- Convert configuration values into bounded runtime controls for replication topology, priority-queue size, job loop timing, delete throttles, replication read/write limits, and chunk hash scan rate.

This is not the chunk repair policy itself; repair/rebalance decisions live earlier in the file. This section initializes and feeds the structures used by that policy, especially priority queues, counters, storage-class statistics, chunkserver slots, and the `chunk_jobs_main()` timer.

## Important APIs, Types, And Functions

### Metadata load/store

- `chunk_load(bio *fd, uint8_t mver, int ignoreflag)` is partially covered. Lines 8930-8980 handle duplicate chunk detection, construction of a new `chunk`, decoding of `version`, `allowreadzeros`, `lockedto`, file-list pairs, storage class, flags, and the terminating zero chunk record.
- `chunk_store(bio *fd)` writes the chunk section in metadata format `0x12`. When called with `fd == NULL`, it returns `0x12` as the store format version. Otherwise it writes the `nextchunkid` header, serializes every chunk in `chunkhashtab` up to `chunkrehashpos`, writes optional dynamic file-list data, appends an all-zero sentinel record, and returns `0` or `0xFF` on write failure.

### Lifecycle

- `chunk_cleanup()` clears priority queues, IO-ready state, replication locks, pending disconnected-server lists, server copy lists, chunk records, the chunk hash table, chunkserver slots, chunk count matrices, and flist pages. This is a reusable cleanup/reset path, not final process teardown.
- `chunk_newfs()` resets only the filesystem-level chunk counters for a newly initialized metadata set: `chunks = 0` and `nextchunkid = 1`.
- `chunk_term()` is the final destructor. It frees internal tables owned by `chunk_calculate_endanger_priority()`, `chunk_do_jobs()`, all chunk count matrices, and the flist backing table.
- `chunk_strinit()` performs startup initialization: loads config, allocates tables, zeros counters, initializes allocators/hashes, primes internal job/endanger state, initializes chunk delay support, and registers callbacks.
- `chunk_reload()` is the live config reload path. It preserves old delete limits if a new soft limit is invalid, updates the millisecond timer when the job period changes, and recomputes loop scan limits.

### Configuration and diagnostics

- `chunk_parse_rep_list(char *strlist, double *replist)` parses replication limit strings in three accepted forms: one scalar value replicated into five slots, four comma-separated values with the fifth set to the maximum of the first four, or the current five-value form.
- `chunk_load_cfg_common()` reads config common to startup and reload, including uniqueness/topology policy, replication delay, acceptable balancing difference, priority queue length, job timer period, per-storage-class fail throttles, and rebalance fail reset interval.
- `chunk_loginfo(FILE *fd)` emits current chunk-loop parameters, per-priority queue lengths and one-minute queue counters, job calls/skips by storage class, and job exit reasons by storage class.

### Local types and global structures used here

- `chunk` stores persistent fields serialized here: `chunkid`, `version`, `allowreadzeros`, `lockedto`, `flags`, `sclassid`, and `fhead`, plus transient fields such as danger-list and operation state initialized elsewhere.
- `flist` is a compact linked representation of storage-class file reference counts. `fhead < FLISTFIRSTINDX` is an inline count shortcut, while `fhead >= FLISTFIRSTINDX` points into flist pages.
- `csdata` table `cstab` holds chunkserver registration/validity state and is allocated and reset in this chunk.
- Priority queue globals `chq_queue_head`, `chq_queue_tail`, `chq_queue_elements`, `chq_hash`, and `chq_elements` are initialized here; the enqueue/dequeue logic is earlier in the file.
- Counter matrices `allchunkcopycounts`, `regchunkcopycounts`, `allchunkec8counts`, `regchunkec8counts`, `allchunkec4counts`, and `regchunkec4counts` are allocated as `MAXSCLASS * 4` rows by 11 goal-equivalent buckets.

## Control Flow

### Loading persisted chunks

The covered `chunk_load()` branch is reached after a record has been read and `chunkid > 0`.

1. If `chunk_find(chunkid)` already returns a chunk, the loader logs an error. Without `ignoreflag`, it asks for `-i` and aborts; with `ignoreflag`, it skips creating a duplicate and continues.
2. For a new chunk, it calls `chunk_new(chunkid)`, copies the high version bit into `allowreadzeros`, masks the version to 30 bits, and stores `lockedto`.
3. If file-list `pairs` exist, the dynamic payload is decoded. For multiple pairs, every `(sclassid, fcount)` becomes an allocated `flist` node and the final byte is treated as the calculated storage class. For a single pair, small counts are stored directly in `c->fhead`, while large counts allocate one flist node.
4. The chunk state is updated through `chunk_state_set_sclass()` and `chunk_state_set_flags()`.
5. A zero `chunkid` is the section terminator only when `version`, `lockedto`, and `flags` are also zero. Any non-zero payload on the zero sentinel is treated as metadata corruption.

### Storing chunks

`chunk_store()` mirrors the loader but always writes the current format.

1. `fd == NULL` is a version-query convention and returns `0x12`.
2. The function writes `nextchunkid` as an 8-byte header.
3. It scans the hash table from bucket zero to `chunkrehashpos - 1`. Each chunk emits an 18-byte static record: chunk ID, version with `allowreadzeros` in bit `0x80000000`, `lockedto`, flags, and pair count.
4. File-list state is encoded into a separate dynamic buffer. No file references means zero pairs; inline `fhead` means one pair; linked flist nodes become one pair per node. When more than one pair exists, the calculated `c->sclassid` is appended as an extra byte.
5. Pair counts above 255 use flag bit `0x80` as the high pair-count bit and store the low byte in the pair-count field, supporting up to `CHUNKMAXPAIRS` (`255 + 128`) pairs.
6. The function writes the static record, then the dynamic payload if any. Any short write returns `0xFF`.
7. An all-zero static record terminates the section.

### Initialization and reload

`chunk_strinit()` and `chunk_reload()` share most config parsing, but differ in error policy.

- Startup treats invalid delete limits and parse failures as fatal and prints to `stderr`.
- Reload logs warnings and keeps service running; if the reloaded soft delete limit is zero, it reuses the previous soft/hard limits.
- Both paths support deprecated `CHUNKS_LOOP_TIME`. When present, `HashCPTMax` is set to `0xFFFFFFFF`, effectively disabling the per-tick hash chunk cap. Otherwise `CHUNKS_LOOP_MAX_CPS` is bounded and converted to per-tick chunks using `TicksPerSecond`.
- Startup allocates all global tables and registers `chunk_reload()`, `chunk_loginfo()`, `chunk_jobs_main()`, the one-minute counter shifts, and `chunk_term()` with the main loop.

## State And Persistence Behavior

The persistent state in this chunk is the chunk metadata section:

- Header: `nextchunkid`.
- Per chunk: `chunkid`, `version`, `allowreadzeros`, `lockedto`, `flags`, and storage-class file reference data.
- Terminator: a zeroed `CHUNKFSIZE` record.

The format is explicitly versioned as `0x12`. Comments immediately before this span document older `0x10` and `0x11` static formats and the current dynamic pair payload. `chunk_is_afterload_needed()` returns false for `mver >= 0x12`, meaning this format carries enough storage-class/file-list state to avoid older after-load reconstruction.

Most other state here is transient and rebuilt on process start or metadata reload:

- Priority queues and the hash used to deduplicate queued chunks.
- Chunkserver slot table and disconnected-server cleanup queues.
- Copy/EC count matrices used for UI, stats, and repair eligibility.
- Job call/skip and job-exit reason counters, shifted once per minute.
- Flist pages and free-list indices.

`lockedto` is persisted as read from the chunk object. There is commented-out code that would have suppressed old locks and in-progress replication/local split locks during store; because it is disabled, lock deadlines are serialized exactly as currently stored in the chunk.

## Dependencies And Integration Points

This code integrates with several MooseFS master subsystems:

- `bio` provides metadata reads and writes.
- `datapack` helpers (`get*bit`, `put*bit`) define endian-stable binary encoding.
- `mfs_log` and `stderr` provide load/startup/reload diagnostics.
- Chunk allocation/hash helpers (`chunk_new`, `chunk_find`, `chunk_free_all`, `chunk_hash_init`, `chunk_hash_cleanup`) manage the master chunk index.
- `flist_*` functions manage compact per-chunk file-reference lists.
- `chunk_state_set_sclass()`, `chunk_state_set_flags()`, `chunk_state_fix()`, and `chunk_write_counters()` maintain derived chunk counters and queue eligibility outside this span.
- `matocsserv_disconnection_finished()` is called during cleanup for queued disconnected chunkservers; `matocsserv_servers_count()` and receiving-state checks gate later job-loop behavior.
- `storageclass` APIs (`sclass_get_name()`, and earlier counter users such as `sclass_get_keeparch_storagemode()`) provide names and goal-equivalent interpretation for logs and stats.
- `cfg_*` reads MooseFS config values; `main_*_register()` and `main_msectime_change()` integrate reload, diagnostics, timers, one-minute counter shifts, and destruction with the master event loop.
- `chunk_delay_init()`, `chunk_io_ready_init()`, `chunk_replock_init()`, `chunk_calculate_endanger_priority()`, and `chunk_do_jobs()` initialize supporting repair/replication machinery defined earlier in the file.

## Risks And Edge Cases

- Metadata format compatibility is fragile. The loader supports older static sizes via code before this span, but `chunk_store()` only writes `0x12`. Any change to `CHUNKFSIZE`, pair encoding, or version flag bits must preserve upgrade behavior.
- The `0x80` flag bit is overloaded as the high bit of the pair count during store/load. It is stripped from `flags` during load. Future chunk flags cannot use this bit without changing the metadata format.
- `pairsbuff` capacity depends on `CHUNKMAXPAIRS` and the loop limit in `chunk_store()`. If an internal flist has more nodes than the format can store, the code logs a serious error but still writes the truncated list.
- `chunk_load()` mutates chunk state as it reads. If a later record fails, callers need broader metadata-load error handling to discard partial state.
- `chunk_parse_rep_list()` uses `strtod()` but does not explicitly verify that a numeric conversion consumed characters. Malformed strings beginning with non-numeric text may leave parsing behavior dependent on delimiter/end checks after `strtod()`.
- Startup parse failures in `chunk_strinit()` return before `free(repstr)` in the error cases for write/read replication limits, leaking a small config string on a fatal initialization path.
- `chunk_reload()` preserves old delete limits only for zero soft limit. Other bad reload values are clamped or logged, but invalid replication limit strings leave whatever partial writes `chunk_parse_rep_list()` performed before returning `-1`.
- `TicksPerSecond = 1000 / JobsTimerMilliSeconds` is integer division. Values not dividing 1000 exactly reduce effective rate precision, which affects `HashCPTMax`.
- `chunk_cleanup()` assumes tables such as `cstab` and counter matrices are already allocated. It is a post-initialization cleanup path, not safe as a pre-init no-op.
- `chunk_term()` frees matrix rows and top-level matrices but does not null pointers. This is fine for process teardown, but not safe for accidental double invocation.

## Test Signals

Useful validation signals for changes touching this chunk:

- Metadata round-trip tests that create chunks with no file-list data, inline single-pair data, one allocated flist node, multiple flist nodes, `pairs > 255`, `allowreadzeros`, non-zero `lockedto`, and `FLAG_ARCH`/`FLAG_TRASH`, then store and reload.
- Compatibility load tests for metadata versions `0x10`, `0x11`, and `0x12`, including duplicate chunk IDs with and without ignore mode and malformed zero terminators.
- Fault-injection tests around `bio_read()` and `bio_write()` short reads/writes to confirm `-1` or `0xFF` propagation and no silent partial success.
- Config parser tests for one-value, four-value, five-value, whitespace-padded, malformed, and partially malformed `CHUNKS_WRITE_REP_LIMIT` and `CHUNKS_READ_REP_LIMIT`.
- Reload tests that change `JOBS_TIMER_MILLISECONDS`, delete limits, deprecated `CHUNKS_LOOP_TIME`, `CHUNKS_LOOP_MAX_CPS`, and priority queue length, verifying `main_msectime_change()` and clamping behavior.
- Startup/shutdown leak and double-cleanup tests using sanitizers around `chunk_strinit()`, `chunk_cleanup()`, and `chunk_term()`.
- Diagnostics tests or golden-output checks for `chunk_loginfo()` after queue activity and one-minute counter shifts, especially storage class names and deleted-class reporting.

## Chunk Boundary Notes

Lines 8930-9650 begin in the final third of `chunk_load()` and end at the end of `chunk_strinit()`, which is also the end of the visible file content in this source snapshot. Earlier chunks are required for the definitions of chunk repair policy, priority queue operations, state/counter maintenance, chunkserver registration, and job-loop execution that this tail section initializes and reports.
