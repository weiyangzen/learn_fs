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
