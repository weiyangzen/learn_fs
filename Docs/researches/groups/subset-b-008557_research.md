# Research: subset-b-008557

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/memtable.rs -->
# sources/storage-engines/raft-engine/src/memtable.rs

Purpose: this file owns raft-engine's in-memory index of live Raft log entries and key-value records. A `MemTable` tracks one raft group, mapping logical entry indexes to `FileBlockHandle`s and tracking user key/value records by key. `MemTableAccessor` shards many tables across 128 hash slots and applies log batches after writes or during recovery. `MemTableRecoverContext` is the replay machine used by log recovery to rebuild these tables from append and rewrite queues.

Important APIs and types: `EntryIndex` is the public location record for an entry; `ThinEntryIndex` is the stored compact form without the logical index. `MemTable<A>` exposes `append`, `replay_append`, `rewrite`, `replay_rewrite`, `compact_to`, `get_entry`, `fetch_entries_to`, `fetch_entry_indexes_before`, `fetch_rewritten_entry_indexes`, `put`, `delete`, `rewrite_key`, `scan`, `min_file_seq`, and `apply_rewrite_atomic_group`. `MemTableAccessor<A>` provides region lookup, insertion/removal, fold/collect traversal, tombstone draining, write application, recovery merge, and memory metric flushing. `MemTableRecoverContext<A>` implements `ReplayMachine`, tracks pending rewrite atomic groups, and produces `(MemTableAccessor<A>, Arc<GlobalStats>)` on `finish`. `MemTableRecoverContextFactory` plugs recovery into the generic `Factory` trait. The `swap` feature switches `VecDeque` allocation from the dummy/global path to `SwappyAllocator`.

Control flow: append writes call `prepare_append` to reject holes/overwrites during live operation, truncate overlapping suffixes, then push entry locations and increment append stats. Rewrite writes update the oldest contiguous prefix: rewrite-append uses a `gate` and advances `rewrite_count`; rewrite-rewrite without a gate refreshes already rewritten entries until it meets append data. Compaction drains entries below a target index, updates `first_index`, possibly shrinks the backing deque, and deletes append/rewrite stats according to `rewrite_count`. `fetch_entries_to` validates compacted/not-found ranges and returns at least one entry even with a zero max-size limit. Accessor apply paths ignore internal keys, route append batches to append/compact/clean/KV mutations, and route rewrite batches only to entry rewrites or KV rewrite-key updates.

State and persistence behavior: the table itself is volatile but is the authoritative in-memory projection of persisted append and rewrite log queues. Live entry counts are mirrored into `GlobalStats`; `Drop` decrements stats for remaining entries and KVs. `removed_memtables` stores region clean tombstones until purge can rewrite them to the rewrite queue. `atomic_group` protects rewrite-queue files that are part of an active atomic group from being purged too early by returning the group's start sequence from `min_file_seq`. Recovery treats append and rewrite queues differently: append replay records tombstones for later cross-context merge, while rewrite replay can buffer begin/middle/end atomic groups and apply them only when a complete group is observed.

Dependencies and integration points: depends on log-batch types (`LogItem`, `Command`, `KeyValue`, `CompressionType`, atomic group markers), `FileId`/`FileBlockHandle`/`LogQueue`, `GlobalStats`, failpoints, `hash_u64`, and `MEMORY_USAGE`. It integrates with the engine write path through `apply_append_writes` and `apply_rewrite_writes`, with file recovery through `ReplayMachine`, with purge through `fetch_*`, `min_file_seq`, `take_cleaned_region_logs`, and `apply_rewrite_atomic_group`, and optionally with `swappy_allocator` for bounded memory.

Risks and invariants: the core invariant is that rewritten entries occupy a prefix of `entry_indexes`, append entries occupy the suffix, and `rewrite_count` is the boundary. `prepare_append` panics on live holes or compacted overwrites, so callers must pass ordered consecutive entry indexes. Stats must stay balanced across overwrite, rewrite discard, compaction, drop, and recovery merge paths. Atomic group handling is subtle: incomplete or overlapping groups are discarded or buffered, and incorrect min-file-seq calculation could allow data-loss purge. `has_at_least_some_entries_before` compares only by file sequence and ignores `FileId.queue` beyond caller discipline. The memory accounting under non-swap uses only entry-index capacity and explicitly does not include the KV map.

Test signals: embedded tests cover append overlap and hole rejection, compaction and capacity shrink thresholds, fetch error modes and max-size behavior, KV put/delete/scan behavior, entry lookup, complex append/rewrite/stat transitions, rewrite KV handling, merge of append and rewrite recovery tables, neighbor recovery merge equivalence to sequential apply, and nightly memtable put benchmarks. The tests also use `catch_unwind_silent` to assert panic boundaries without noisy panic hooks.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/memtable.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/metrics.rs -->
# sources/storage-engines/raft-engine/src/metrics.rs

Purpose: this file defines raft-engine's Prometheus metrics and a lightweight per-thread performance context. It gives the rest of the engine a uniform way to observe wall-clock durations either into Prometheus histograms, into thread-local cumulative counters, or both.

Important APIs and types: `StopWatch<M: TimeMetric>` records an `Instant` and observes elapsed time on drop. `PerfContext` stores cumulative durations for log population, write wait, file write, rotate, sync, and memtable apply. `get_perf_context`, `take_perf_context`, and `set_perf_context` manipulate the thread-local `TLS_PERF_CONTEXT`. `PerfContextField<P>` and the exported `perf_context!` macro create field projectors. `TimeMetric` abstracts `observe`/`observe_since`; implementations exist for `&Histogram`, `PerfContextField`, and `(M1, M2)`.

Control flow: operation sites create a `StopWatch` or call `observe_since`; the metric implementation either calls Prometheus `Histogram::observe` with seconds or mutates the projected duration inside the thread-local `PerfContext`. `take_perf_context` atomically replaces the current thread-local value with default and returns the old cumulative snapshot.

State and persistence behavior: all state is in process. Prometheus metric instances are global `lazy_static!` registries. `PerfContext` is thread-local and not synchronized across threads unless callers explicitly take or add contexts. `AddAssign<&PerfContext>` supports aggregating contexts into another context snapshot.

Dependencies and integration points: depends on `prometheus`, `prometheus_static_metric`, `lazy_static`, and `InstantExt` from `util.rs` to avoid negative elapsed durations. It exposes labeled metric vector wrappers for `LogQueueKind` and global histograms/gauges/counters used by write, read, purge, background rewrite, log-file accounting, swap-file accounting, log-entry accounting, and memory usage.

Risks and invariants: histogram registration unwraps at initialization, so duplicate names or registration failure panic early. `PerfContextField` uses `RefMut::map` inside TLS and assumes no nested incompatible borrow of the same thread-local context. `StopWatch` observes on drop, so long-lived scopes or early drops affect measured spans. Metrics are process-global, which is expected for Prometheus but makes tests sensitive to global registration reuse.

Test signals: no direct tests in this file. It is indirectly exercised by engine write/read/purge code, by `StopWatch` use in purge and write paths, and by memory/swap metric updates in memtable and swappy allocator.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/pipe_log.rs -->
# sources/storage-engines/raft-engine/src/pipe_log.rs

Purpose: this file defines the generic log storage abstraction used by raft-engine. It provides the queue/file identifiers, block handles, format version behavior, context-sensitive bytes, and the `PipeLog` trait consumed by engine, purge, recovery, and tests.

Important APIs and types: `LogQueue` distinguishes `Append` and `Rewrite`. `FileSeq` is the per-queue sequence type. `FileId` identifies a queue/sequence pair and orders by freshness, treating append files as newer than rewrite files when queues differ. `FileBlockHandle` points to a byte range in a log file. `Version` is a serde-repr enum with `V1` and `V2`; `has_log_signing` enables signing for V2 and can be forced by failpoint. `LogFileContext` carries `FileId` plus version and derives an optional signature. `ReactiveBytes` lets append payloads depend on the target file context. `PipeLog` defines `read_bytes`, `append`, `sync`, `file_span`, `file_at`, `total_size`, `rotate`, and `purge_to`.

Control flow: a log implementation appends `ReactiveBytes` to a queue and returns a `FileBlockHandle`. For reactive payloads, the implementation supplies `LogFileContext` before serializing bytes. `file_at` clamps a ratio to `[0, 1]`, calculates the current file count from `file_span`, and returns the sequence at that percentile. Purge callers use `purge_to` to remove all files older than a given `FileId` within that queue.

State and persistence behavior: this file stores no log data itself, but its contracts describe persistence boundaries. Append and rewrite queues are independent sequence spaces; `FileBlockHandle` is the durable locator stored in memtables. `Version::V2` adds per-file signing through `LogFileContext::get_signature`, currently the low 32 bits of the file sequence.

Dependencies and integration points: depends on `fail`, `num_traits`, `num_derive`, `serde_repr`, `strum`, and the crate `Result`. It is used by memtable entry locations, purge watermarks, engine log reads/writes, event listeners, stress hooks, and test utilities.

Risks and invariants: the `Ord` implementation intentionally imposes cross-queue freshness semantics; code that wants pure sequence ordering must compare only within a queue. `get_signature` assumes file counts stay below `u32::MAX` for practical signing uniqueness. `file_at` uses floating-point truncation and includes the active file in the count, so purge callers must clamp to `active_file - 1` when the active file is not purgeable.

Test signals: no direct tests in this file. Dummy constructors for `FileId` and `FileBlockHandle` are test-only and are used heavily by memtable and write-path tests. Failpoints can force V2 signing behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/pipe_log.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/purge.rs -->
# sources/storage-engines/raft-engine/src/purge.rs

Purpose: this file implements background log garbage collection. `PurgeManager` decides when append or rewrite queues need rewriting, rewrites still-live records into the rewrite queue, asks callers to compact heavy raft groups, and purges log files whose data is no longer referenced. `PurgeHook` prevents append files from being purged before their writes have been applied to memtables.

Important APIs and types: `PurgeManager<P: PipeLog>` is constructed from config, memtables, a pipe log, global stats, and event listeners. Public entry points are `purge_expired_files`, `must_rewrite_append_queue`, `must_rewrite_rewrite_queue`, and `must_purge_all_stale`. Internal helpers include `needs_rewrite_log_files`, `append_queue_watermarks`, `rewrite_or_compact_append_queue`, `rewrite_rewrite_queue`, `rewrite_append_queue_tombstones`, `rescan_memtables_and_purge_stale_files`, `rewrite_memtables`, and `rewrite_impl`. `PurgeHook` implements `EventListener`.

Control flow: `purge_expired_files` takes a try-lock so only one purge runs; if rewrite queue exceeds threshold and garbage ratio, it rewrites rewrite data and rescans/purges stale rewrite files. If append queue exceeds threshold, it calculates rewrite and force-compact watermarks, gathers listener barriers, rewrites clean tombstones first, rewrites eligible light regions or returns heavy regions for compaction, then rescans and purges append files up to the listener barrier. `rewrite_memtables` fetches entry indexes and KVs from selected memtables, reads raw entry bytes, chunks batches by `max_batch_bytes`, optionally wraps rewrite-rewrite chunks in atomic groups, periodically syncs to cap unsynced bytes, and calls `rewrite_impl`. `rewrite_impl` populates/compresses a `LogBatch`, appends it to rewrite queue, optionally syncs, applies rewrite locations back to memtables, notifies listeners, and records background rewrite bytes.

State and persistence behavior: purge does not delete data directly from memtables; it rewrites live data into rewrite files, updates memtables, then purges files that no memtable or listener references. `force_rewrite_candidates` tracks raft groups repeatedly requested for compaction and eventually forces rewrite if compaction does not happen. Append tombstones are rewritten before append entries to preserve region deletion across restart. Rewrite-rewrite uses atomic groups to preserve all-or-nothing recovery across split batches. `PurgeHook` tracks append file application reference counts from `post_new_log_file`, `on_append_log_file`, and `post_apply_memtables`, then returns the first not-ready file as a purge barrier.

Dependencies and integration points: depends on `Config`, `read_entry_bytes_from_file`, `EventListener`, `LogBatch`, `AtomicGroupBuilder`, memtables, metrics, `PipeLog`, `GlobalStats`, failpoints, and parking_lot locks. It is called by `Engine::purge_expired_files` and stress `spawn_purge`; it feeds returned region IDs back to callers for forced compaction.

Risks and invariants: ordering around append queue purge is critical: append barriers must be sampled before tombstone rewrite, tombstones must be rewritten before entries, and purge must not pass active append files. `needs_rewrite_log_files` divides deleted rewrite entries by total rewrite entries; callers rely on sane stats to avoid NaN/threshold surprises. Rewriting reads raw entry bytes and can be memory-heavy without the batch split guard. Atomic group start/end tracking must match memtable recovery or rewrite queue purge could break recovery. The `PurgeHook` assumes append file sequences are contiguous and indexes `active_log_files` by `seq - front`.

Test signals: no direct tests here, but failpoints expose `max_rewrite_batch_bytes` and `force_use_atomic_group`. Behavior is indirectly covered by engine failpoint tests, memtable atomic group tests, stress purge threads, and metrics around purge/rewrite durations and background bytes.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/purge.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/swappy_allocator.rs -->
# sources/storage-engines/raft-engine/src/swappy_allocator.rs

Purpose: this file provides `SwappyAllocator`, an unstable allocator-api allocator that enforces an in-memory budget and spills excess allocations into mmap-backed swap files. It is intended for internal data structures such as memtable entry indexes under the `swap` feature and is explicitly not suitable as a global allocator.

Important APIs and types: `SwappyAllocatorCore<A>` stores the budget, swap path, memory usage counter, wrapped memory allocator, maybe-swapped flag, page sequence, and page list. `SwappyAllocator<A>` is cloneable and implements `Allocator`; `new_over` constructs it over a custom allocator and cleans the swap directory, `new` uses `Global`, and `memory_usage` reports current in-memory usage. `Page` owns a file and `MmapMut`, tracks a bump `tail`, active allocation count, and sequence. Page helpers are `new`, `allocate`, `deallocate`, `release`, `contains`, and `page_file_name`.

Control flow: `allocate` first reserves in-memory usage; if the budget would be exceeded and the layout is non-empty, it tries `allocate_swapped`. Successful swap allocation rolls back memory usage and returns a pointer into the last page or a new page sized at least 64 MiB. If swapping fails, allocation falls back to the wrapped allocator unless that allocator also fails, in which case usage is rolled back. `deallocate` checks `maybe_swapped`; if the pointer belongs to a page it decrements that page's ref count and releases/removes the page file when the count reaches zero. `grow` moves allocations to swap when budget is exceeded or the old pointer is already swapped; otherwise it delegates to the wrapped allocator and adjusts usage by the size delta. `shrink` can move a swapped allocation back to memory if the new size fits budget, otherwise it returns the same mmap pointer with a smaller slice length.

State and persistence behavior: swap files are temporary runtime backing stores under the configured path. `new_over` attempts to remove any stale directory. `Page::new` creates/truncates a file, extends it to page size, maps it mutable, and increments `SWAP_FILE_COUNT`; `release` drops the mmap, removes the file, and decrements the gauge. Page allocation is bump-only; individual frees do not reclaim space until all allocations in a page are gone. Memory usage tracks only allocations handled by the wrapped memory allocator, not mmap-backed swapped allocations or allocator metadata.

Dependencies and integration points: depends on nightly allocator APIs, `memmap2`, `parking_lot::Mutex`, log warnings/errors, failpoints, and the `SWAP_FILE_COUNT` metric. It integrates with `memtable.rs` via `SelectedAllocator` when the `swap` feature is enabled, with config memory limits, and with tests through a `WrappedGlobal` allocator.

Risks and invariants: pointer classification depends on `maybe_swapped` and page membership checks; false negatives would deallocate mmap pointers via the wrong allocator, while false positives are guarded by page search. Page allocation uses `align_offset` relative to the current tail; layout arithmetic must stay correct for large alignments and sizes. Bump pages can waste disk space until all allocations in a page are freed. `grow_zeroed` zeroes the whole returned slice, which may also zero copied old bytes after `grow`; callers must tolerate allocator-api semantics as used by standard collections. Stale swap cleanup is best-effort and logs rather than fails construction.

Test signals: tests cover Vec behavior across memory and swap, page refill and file deletion, zero-sized allocations staying in memory allocator, shrink reuse and moving back to memory, grow routing regressions, wrapped allocator failure accounting, extensive `VecDeque` behavior copied from standard tests, panic/drop behavior during draining, and allocator microbenchmarks for global, fast path, and slow path.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/swappy_allocator.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/test_util.rs -->
# sources/storage-engines/raft-engine/src/test_util.rs

Purpose: this file centralizes small test helpers for constructing raft entries, constructing memtable entry indexes, and controlling panic-hook noise in tests.

Important APIs and types: `generate_entries(begin_index, end_index, data)` returns raft `Entry` values with consecutive indexes and optional data. `generate_entry_indexes` and `generate_entry_indexes_opt` build `EntryIndex` records for a half-open index range and optional `FileId`. `catch_unwind_silent` temporarily suppresses the default panic hook while catching a panic. `PanicGuard` installs a panic hook that prints a prompt before forwarding to the previous hook, then restores the previous hook on non-panicking drop.

Control flow: generators allocate vectors sized from the requested ranges and fill indexes monotonically. `catch_unwind_silent` stores the previous hook, installs a no-op hook, calls `panic::catch_unwind(AssertUnwindSafe(f))`, and restores the hook. `PanicGuard::with_prompt` stores the previous hook in an `Arc`, installs a hook that prints the prompt and invokes the previous hook, and restores on drop unless the current thread is already panicking.

State and persistence behavior: no persistent state. Panic hook manipulation is process-global and must be scoped carefully; `PanicGuard` deliberately avoids restoration during unwinding to avoid hook churn while panicking.

Dependencies and integration points: depends on raft `Entry`, memtable `EntryIndex`, and pipe-log handle types. It is used by memtable and swappy allocator tests to generate fixtures and assert panic behavior without noisy output.

Risks and invariants: range arguments are half-open and `generate_entry_indexes_opt` asserts `end_idx >= begin_idx`. Generated `EntryIndex` values use offset and length zero/one defaults and are not valid real file locations beyond tests. Panic-hook changes are global, so concurrent tests that also mutate hooks can interfere.

Test signals: this is itself support code. Its behavior is indirectly checked by tests that rely on generated indexes and silent panic catching, especially memtable panic boundary tests and allocator failure tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/test_util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/util.rs -->
# sources/storage-engines/raft-engine/src/util.rs

Purpose: this file provides general utilities shared across raft-engine: binary size formatting/parsing, saturating time elapsed, CRC32, reversible u64 hashing, LZ4 block compression helpers, a generic factory trait, and alignment helpers.

Important APIs and types: binary unit constants `B`, `KIB`, `MIB`, `GIB`, `TIB`, and `PIB`; `ReadableSize` with constructors `kb`, `mb`, `gb`, `as_mb`, arithmetic ops, `Display`, `FromStr`, serde serialize/deserialize; `InstantExt::saturating_elapsed`; `crc32`; `hash_u64` and `unhash_u64`; `lz4::append_compress_block` and `lz4::decompress_block`; `Factory<Target>`; `round_up` and `round_down`.

Control flow: `ReadableSize::from_str` splits an ASCII string into numeric and unit components, supports decimal/scientific notation, maps accepted binary units, and truncates `f64 * unit` to `u64`. Serialization writes the display string; deserialization accepts integers or strings. LZ4 compression appends a 4-byte little-endian decoded length followed by compressed bytes to the same buffer after a `skip` prefix. Decompression reads the length, allocates the decoded buffer, calls `LZ4_decompress_safe`, and validates the decoded size. `hash_u64`/`unhash_u64` are SplitMix64 permutation and inverse.

State and persistence behavior: no persistent state. The encoded LZ4 block format is persisted when log batches choose compression, so its layout `{decoded_len | compressed content}` is a storage compatibility concern. `ReadableSize` string forms are persisted in TOML configs.

Dependencies and integration points: depends on `crc32fast`, `serde`, `lz4_sys`, and crate `Error`/`Result`. `ReadableSize` is used by config, stress CLI parsing, benchmarks, and display. `InstantExt` is used by metrics. `hash_u64` is used to shard memtable accessors. LZ4 helpers are used by log-batch compression/decompression paths.

Risks and invariants: `ReadableSize::from_str` accepts signs and exponent notation in the numeric substring; negative parsed values cast through `f64` to `u64` can be surprising if not rejected by caller expectations. Display prints `0KiB` for zero. LZ4 compression rejects content longer than `i32::MAX`; decompression treats non-empty inputs shorter than or equal to four bytes as corruption. `round_up` uses `div_ceil` and will panic on zero alignment.

Test signals: unit tests cover readable-size arithmetic, TOML serialization/deserialization, valid/invalid parse cases including scientific notation, hash/unhash inversion, rounding, and LZ4 basic compression/decompression including empty input.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/src/write_barrier.rs -->
# sources/storage-engines/raft-engine/src/write_barrier.rs

Purpose: this file implements a low-level write-group barrier. Concurrent callers enqueue `Writer`s; exactly one leader receives a `WriteGroup` containing a linked list of writers to process, while followers wait until their leader has set outputs.

Important APIs and types: `Writer<P, O>` wraps a mutable payload pointer, output slot, sync flag, entered time, and performance context diff. `Writer::new`, `mut_payload`, `set_output`, and `finish` are the caller-facing methods. `WriteGroup` exposes `iter_mut` over grouped writers and calls `leader_exit` on drop. `WriterIter` walks the intrusive linked list. `WriteBarrier<P, O>` has `enter` as the public synchronization method. `WriteBarrierInner` stores head/tail, pending leader, and pending condition-variable index.

Control flow: the first writer entering an empty barrier becomes leader immediately. Later writers append themselves to the current linked list. If another pending leader already exists, they wait on the follower condvar for that future group and return `None` after being processed. If no pending leader exists, the arriving writer becomes the leader of the next group and waits on `leader_cv`; when awakened it receives a group from its node through the current tail. Dropping a `WriteGroup` calls `leader_exit`, which wakes the next pending leader and the followers of the just-finished group, or clears head/tail and wakes current followers when no next leader exists.

State and persistence behavior: all state is in memory. Writers contain raw pointers into caller-owned payloads and must not outlive those payloads. Outputs are stored back into each writer by the leader and consumed by each caller with `finish`.

Dependencies and integration points: depends on `parking_lot` `Mutex`/`Condvar`, `fail` for a `leader_exit` failpoint, and `PerfContext`. It is used by the engine write path to batch concurrent writes and carry sync/performance metadata through the group leader.

Risks and invariants: this module relies on unsafe intrusive pointers and explicit caller discipline: the original payload must not be accessed while the writer exists, and every writer must remain stack-valid while linked/waiting. `WriteGroup` drop is essential for progress; leaking it would block future groups. The two follower condvars are alternated by `pending_index`; off-by-one errors would wake the wrong generation. `finish` panics if no output was set.

Test signals: `test_sequential_groups` checks single-writer groups and output propagation. `test_parallel_groups` orchestrates multiple waves of threads, validates one leader per group, verifies grouped payload/output processing, and exercises follower/leader handoff with condition variables.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/src/write_barrier.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/stress/Cargo.toml -->
# sources/storage-engines/raft-engine/stress/Cargo.toml

Purpose: this manifest defines the standalone `stress` binary crate for exercising raft-engine under configurable read/write/purge workloads.

Important APIs and types: as a Cargo manifest, it declares package metadata (`name = "stress"`, version `0.4.2`, Rust 2018) and dependencies. The most important dependency is `raft-engine = { path = "..", features = ["internals"] }`, which gives the stress binary access to engine internals and event listener hooks.

Control flow: Cargo uses this manifest to build the stress tool independently from the main crate. The dependency set enables command-line parsing (`clap` derive/cargo), constant formatting for default CLI strings, latency histograms, raft protobuf entries, spin-wait timing, randomness, distributions, and summary statistics.

State and persistence behavior: no runtime state is stored here. The dependency on `raft` from the master branch of `tikv/raft-rs` is a build-time external source, and the path dependency ties the stress crate directly to the checked-out raft-engine implementation.

Dependencies and integration points: dependencies are `clap`, `const_format`, `hdrhistogram`, `num-traits`, `parking_lot_core`, git `raft`, path `raft-engine` with internals, `rand`, `rand_distr`, and `statistical`. These map directly to the parser, version conversion, spin wait, entry generation, event hooks, workload randomness, and reporting in `stress/src/main.rs`.

Risks and invariants: the git dependency on raft master can make builds non-reproducible unless Cargo.lock pins it. The `internals` feature means the binary can rely on non-public engine APIs. This manifest is for tooling/stress validation, not a library consumed by production.

Test signals: no tests in the manifest. Successful build of the stress crate is the main signal that its dependency graph remains compatible.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/stress/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/stress/src/main.rs -->
# sources/storage-engines/raft-engine/stress/src/main.rs

Purpose: this file implements a command-line stress test for raft-engine. It opens an engine, spawns configurable writer, reader, and purge threads, runs for a fixed duration, and prints throughput, latency, fairness, and write bandwidth.

Important APIs and types: `ControlOpt` is the `clap::Parser` CLI surface. `TestArgs` stores normalized runtime parameters and validates thread/region constraints. `ThreadSummary` records per-thread latency histogram and timing; `Summary` aggregates and prints results. `MessageExtTyped` adapts raft `Entry` to the engine's `MessageExt` trait. Workload helpers are `spawn_write`, `spawn_read`, `spawn_purge`, `prepare_entries`, `wait_til`, and `WrittenBytesHook`.

Control flow: `main` parses CLI options, maps storage/config options into `Config`, maps workload options into `TestArgs`, optionally removes existing data unless `--reuse-data` is set, sanitizes config, opens `Engine::open_with_listeners` with `WrittenBytesHook`, starts purge/read/write threads according to counts, sleeps for the configured duration, flips a shared shutdown flag, joins workers, and prints summaries. Writers prebuild random entry payloads, repeatedly choose regions assigned to their thread, append entries and optional compact commands into a `LogBatch`, rate-limit if requested, and call `engine.write`. Readers choose assigned regions, read the newest entry to avoid compaction conflicts, rate-limit if requested, and record latency. Purge periodically calls `engine.purge_expired_files` and compacts returned regions by `force_compact_factor`.

State and persistence behavior: the stress tool writes real raft-engine data under `--path`. With `--reuse-data` it preserves existing files; otherwise it removes the directory before opening. Each region's log indexes are advanced by querying engine first/last indexes. The write bandwidth hook observes append file handles and counts appended bytes with an atomic counter.

Dependencies and integration points: uses `Engine`, `Config`, `LogBatch`, `Command`, `ReadableSize`, `Version`, internals `EventListener` and `FileBlockHandle`, raft `Entry`, random data generation, hdrhistogram, and `parking_lot_core::SpinWait`. It exercises write, read, compact, purge, compression, format version, log recycle, and listener paths together.

Risks and invariants: `TestArgs::validate` requires regions to be at least write/read thread counts and write-region-count to fit each writer's region partition. Default `write_without_sync` field is named inversely to `DEFAULT_WRITE_SYNC`, so the CLI controls the sync flag as `!write_without_sync`. `ThreadSummary::record` only sets `last` in the non-first branch, so QPS is zero for a single recorded operation. `wait_til` spin/sleep rate limiting is best-effort and does not compensate for slow previous operations. The force-compact calculation assumes `last >= first` for returned regions.

Test signals: this is not a unit test but a workload generator. Useful signals are sustained write/read QPS, latency percentiles, fairness, write bandwidth, and whether purge/compaction runs without errors under randomized mixed load.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/stress/src/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/tests/benches/bench_recovery.rs -->
# sources/storage-engines/raft-engine/tests/benches/bench_recovery.rs

Purpose: this Criterion benchmark measures `Engine::open` recovery cost over generated raft-engine directories of different sizes and batch/compression patterns.

Important APIs and types: `MessageExtTyped` adapts raft `Entry` indexes. Local `Config` describes benchmark data shape: total data size, region count, batch size, item size, entry size, and compression threshold. `generate` creates a temporary engine directory populated to the target size. `dir_size` sums file sizes in a directory. `bench_recovery` registers the benchmark group.

Control flow: `generate` opens an engine in a tempdir, tracks the last index per region, repeatedly builds `LogBatch`es until directory size reaches the target, fills batches with random entries distributed across regions, writes without sync, syncs once, drops the engine, and returns the tempdir. `bench_recovery` defines default, compressed, small-batch, and 10 GiB configs, prints them, enables a failpoint to skip fadvise effects, generates data for each config, and benchmarks repeated `Engine::open` calls with that directory/config.

State and persistence behavior: benchmark data is persisted in temporary directories for the lifetime of each benchmark input. It intentionally creates realistic append log files and optional compressed batches, then measures recovery from disk by reopening the engine. `TempDir` cleanup removes data afterward.

Dependencies and integration points: depends on Criterion, raft entries, raft-engine `Engine`, `LogBatch`, `ReadableSize`, `MessageExt`, random generation with seeded `StdRng`, `HashMap`, and failpoints. It exercises write/populate/sync before measuring recovery parsing and memtable reconstruction.

Risks and invariants: the 10 GiB config is expensive and can dominate benchmark runtime/disk usage. Writes are unsynced until final sync, which is appropriate for setup but means setup failure modes differ from production sync-per-write workloads. `dir_size` sums immediate directory entries and assumes raft-engine files are direct children. Failpoint cleanup must run after benchmarks to avoid leaking behavior into later tests.

Test signals: Criterion sample size is set in `mod.rs`; this file reports recovery latency across configurations. It is a performance signal, not a correctness assertion, but generation failures or open failures expose recovery incompatibilities.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/tests/benches/bench_recovery.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/tests/benches/mod.rs -->
# sources/storage-engines/raft-engine/tests/benches/mod.rs

Purpose: this is the Criterion bench harness entry point for raft-engine integration benchmarks.

Important APIs and types: it imports `criterion_main`, declares `mod bench_recovery`, and invokes `criterion_main!(bench_recovery::benches)`.

Control flow: when Cargo runs this bench target, Criterion uses this module as the main function and executes the benchmark group exported from `bench_recovery.rs`.

State and persistence behavior: no state is stored here. Temporary data is managed by the benchmark modules it invokes.

Dependencies and integration points: depends on Criterion and the sibling `bench_recovery` module. `extern crate libc` is present for benchmark/test environment linkage even though this file does not use it directly.

Risks and invariants: all benchmark groups must be wired through this file to run. If `bench_recovery::benches` changes name or is not exported by `criterion_group!`, the harness fails to compile.

Test signals: successful bench harness compilation confirms Criterion wiring. Runtime signals come from the included benchmark groups.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/tests/benches/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/tests/failpoints/mod.rs -->
# sources/storage-engines/raft-engine/tests/failpoints/mod.rs

Purpose: this file is the module root for failpoint-driven integration tests and contains one local regression test for log-batch full behavior.

Important APIs and types: it enables `allocator_api` under the `swap` feature, declares helper and test modules (`util`, `test_engine`, `test_io_error`), initializes logging with a ctor, imports `FailGuard` and raft-engine public APIs, and defines `test_log_batch_full`.

Control flow: `init` runs before tests and initializes `env_logger`. `test_log_batch_full` enables failpoint `log_batch::1kb_entries_size_per_batch`, builds two batches with 800-byte entries, verifies merging two full-ish batches returns `Error::Full` without mutating either original clone, then verifies adding entries to a full clone also returns `Error::Full` without partial mutation.

State and persistence behavior: failpoint guards are scoped to the test and removed on drop. The test only manipulates in-memory `LogBatch` values. Logger initialization is process-global.

Dependencies and integration points: integrates with failpoint-enabled engine tests in sibling modules, local failpoint utilities, `LogBatch`, raft entry generation helpers, and error matching. The `swap` cfg attr allows failpoint tests to compile when allocator-api-backed swap support is enabled.

Risks and invariants: because logging initialization is global, duplicate initialization would panic if another test root did the same without guarding; this file assumes the ctor setup is acceptable for this test binary. The full-batch test asserts transactional behavior: failed merge/add must leave both source and destination batches unchanged.

Test signals: this module's explicit signal is the `test_log_batch_full` regression. The broader file also wires failpoint integration suites for engine and I/O error behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/tests/failpoints/mod.rs -->
