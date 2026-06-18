# Group Research: subset-b-008643

Work item `subset-b-008643` covers 12 public RocksDB API headers under `sources/storage-engines/rocksdb/include/rocksdb`. Each section below is wrapped for reconciliation and split into the source-tree-aligned per-file output path.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/io_dispatcher.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/io_dispatcher.h

## Purpose

`io_dispatcher.h` declares RocksDB's experimental block-read dispatch control plane. It lets callers submit a set of block handles for a `BlockBasedTable`, receive a `ReadSet`, and later read blocks by original index or file offset while the implementation decides whether each block came from cache, asynchronous I/O, pending prefetch, or a synchronous fallback read.

## Important APIs, Types, and Functions

The header exposes `IODispatcherOptions`, `JobOptions`, `IOJob`, `ReadSet`, `IODispatcher`, `NewIODispatcher()`, `NewIODispatcher(const IODispatcherOptions&)`, and `TrackingIODispatcher`. `IODispatcherOptions::max_prefetch_memory_bytes` bounds prefetched block memory across read sets, and `statistics` enables memory-limiter counters. `JobOptions` carries the read options, I/O coalescing threshold, and the `block_handles_are_sorted` optimization. `IOJob` binds block handles to a `BlockBasedTable`. `ReadSet` exposes `ReadIndex`, `ReadOffset`, `ReleaseBlock`, `IsBlockAvailable`, and sync/async/cache-hit counters. Internally it tracks pinned blocks, sorted block indices, async state, pending prefetch flags, and dispatcher memory-budget references. `TrackingIODispatcher` wraps another dispatcher and aggregates `ReadSet` counters for tests.

## Control Flow

Callers build an `IOJob`, call `IODispatcher::SubmitJob`, and receive a shared `ReadSet` on success. Submit logic is implemented out of line in `util/io_dispatcher_imp.cc`; the header contract shows the intended sequence: cache lookup and block pinning first, asynchronous coalesced reads where possible, queued pending prefetch when memory is exhausted, and synchronous reads from `ReadIndex` or `ReadOffset` when data was not ready. `ReadOffset` uses a sorted index for lookup by block offset, while `ReadIndex` addresses the original manifest order.

## State and Persistence Behavior

The API does not persist metadata. Runtime state is held in `ReadSet`: pinned cache entries, async I/O handles, pending-prefetch membership, block-size accounting, and atomics for read statistics. `ReadSet` is non-copyable and non-movable, and its destructor has RAII responsibility for aborting active I/O and releasing pinned blocks. `ReleaseBlock` eagerly drops a block and releases prefetch memory; after that, reads for the same block should fail.

## Dependencies and Integration Points

The header depends on RocksDB options/status APIs plus internal table, block, cache, file-system, and async-I/O types. Usage searches show concentrated coverage in `util/io_dispatcher_test.cc`, integration with `BlockBasedTable`, block-cache memory allocation, read-scoped block buffer providers, and `MultiScan`. HISTORY entries mention recent fixes for memory accounting leaks and MultiScan fallback behavior, which indicates the API is actively evolving.

## Risks and Edge Cases

The interface is explicitly experimental. Memory limiting is subtle: a block read out of a `ReadSet` must still release its prefetch budget, and the HISTORY notes a past leak in this area. Incorrectly setting `block_handles_are_sorted` can cause skipped defensive sorting and wrong offset behavior. Asynchronous I/O handles must be deleted exactly once, including abort paths and coalesced requests shared by several block indices. `ReleaseBlock` invalidates later reads, so callers must avoid retaining stale indexes as if data remained available.

## Test Signals

Primary signals are `util/io_dispatcher_test.cc` tests for basic SST reads, cache hits, read-scoped providers, direct I/O scratch, statistics tracking, coalescing, sorted-handle optimization, invalid read-scoped leases, `ReadSet` destruction unpinning, memory-limit blocking/partial prefetch, and MultiScan integration. Useful assertions include sync/async/cache-hit counter values, pinned block-cache usage before and after `ReadSet` lifetime, I/O request details, and memory-limiter statistics.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/io_dispatcher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/io_status.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/io_status.h

## Purpose

`io_status.h` defines `IOStatus`, a filesystem-oriented subclass of `Status` used throughout RocksDB's file and environment abstractions. It preserves normal RocksDB status codes and subcodes while adding I/O-specific retryability, data-loss, and scope metadata.

## Important APIs, Types, and Functions

`IOStatus` aliases `Status::Code` and `Status::SubCode`, defines `IOErrorScope` values for filesystem, file, and range scope, and provides setters/getters for `retryable_`, `data_loss_`, and `scope_`. Static constructors mirror `Status` families: `OK`, `NotSupported`, `NotFound`, `Corruption`, `InvalidArgument`, `IOError`, `Busy`, `TimedOut`, `NoSpace`, `PathNotFound`, `IOFenced`, and `Aborted`. Copy/move constructors and assignments preserve metadata and state. `status_to_io_status(Status&&)` moves a generic `Status` into an `IOStatus`.

## Control Flow

Most use is value construction and propagation. Filesystem code returns an `IOStatus` directly, often using platform helpers to translate errno or Windows errors into `NoSpace`, `PathNotFound`, or generic `IOError`. The message constructor allocates a joined `msg[: msg2]` string and stores it in inherited status state. Move assignment resets the source object to OK-like defaults after transferring state.

## State and Persistence Behavior

`IOStatus` only carries in-memory status state. It stores code, subcode, retryable flag, data-loss flag, scope, and an optional heap-allocated message inherited from `Status`. It has no durable persistence behavior, but it crosses many persistence boundaries as the error type for file creation, reads, writes, syncs, manifest updates, WAL handling, backup files, and filesystem wrappers.

## Dependencies and Integration Points

The header depends on `rocksdb/slice.h` and `status.h`. Usage spans `env`, `file`, `port/win`, backup, prefetch, manifest, and table I/O layers. `listener.h` wraps `IOStatus` in `IOErrorInfo` for file-I/O callbacks. `WritableFileWriter` uses `IOStatus` to notify listeners about failed writes, syncs, closes, and related operations.

## Risks and Edge Cases

Equality compares only the status code, not subcode, message, retryable flag, data-loss flag, or scope, so tests that need full equivalence must inspect those fields explicitly. Const methods are thread-safe but mutation requires external synchronization. The message constructor asserts that code is non-OK and subcode is valid; invalid constructor use is caught only in assert-enabled builds. `status_to_io_status` can erase explicit I/O metadata if callers first built only a generic `Status`.

## Test Signals

Signals appear in filesystem and environment tests, especially error translation and sync tests. Broader validation comes from RocksDB file readers/writers returning exact subcodes such as `kNoSpace`, `kPathNotFound`, and `kIOFenced`, listener `OnIOError` callback tests, and `ROCKSDB_ASSERT_STATUS_CHECKED` builds that detect unchecked status paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/io_status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/iostats_context.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/iostats_context.h

## Purpose

`iostats_context.h` declares the thread-local I/O statistics context used by RocksDB to collect low-overhead per-thread counters and timing values for file operations. It complements `perf_context` and is enabled according to the configured `PerfLevel`.

## Important APIs, Types, and Functions

`FileIOByTemperature` stores read byte and read count counters for hot, warm, cool, cold, ice, and unknown file temperature categories. `IOStatsContext` exposes `Reset()`, `ToString(bool exclude_zero_counters)`, counters for bytes read/written, open/allocation/write/read/range-sync/fsync/prepare-write/logger/cpu timings, a `thread_pool_id`, nested temperature stats, and `disable_iostats`. `get_iostats_context()` returns a non-null pointer to the active context.

## Control Flow

Callers obtain `get_iostats_context()`, optionally `Reset()`, execute I/O, and inspect counters or stringify the result. The implementation in `monitoring/iostats_context.cc` returns a `thread_local IOStatsContext` unless `NIOSTATS_CONTEXT` is defined. `Reset()` zeros counters and sets `thread_pool_id` to `Env::Priority::TOTAL`. `ToString()` appends counters, optionally skipping zeros.

## State and Persistence Behavior

The state is process-local and normally thread-local, so counters are isolated per worker thread. It is not persisted in the DB. Under `NIOSTATS_CONTEXT`, the implementation returns a global no-op object and updates are ignored, making reads empty/no-op. `disable_iostats` is an escape hatch used to avoid polluting counters for selected file operations such as logging or backup paths.

## Dependencies and Integration Points

The header depends on `rocksdb/perf_level.h`. Usage appears in DB compaction tests, sequence number time tests, DB misc tests, backup engine code, DB implementation, and `monitoring/iostats_context_test.cc`. Temperature counters integrate with tiered storage and file temperature metadata.

## Risks and Edge Cases

Because counters are per-thread, aggregate operation analysis must collect from the correct thread or use surrounding infrastructure to sum threads. BackupEngine relies on some counters regardless of PerfLevel, so broad changes to enabling rules can break existing metrics. The implementation's `ToString()` currently prints many, but not all, temperature counters declared in the header, so consumers should prefer direct fields when exact coverage matters. `disable_iostats` can intentionally hide file operations, which is useful but can surprise tests expecting bytes to move.

## Test Signals

`monitoring/iostats_context_test.cc` validates string output and zero filtering. DB and compaction tests reset the context, perform reads or compactions, and assert byte/timing counters and temperature buckets. Backup-related tests indirectly exercise the guarantee that required counter metrics remain available even when timer-oriented PerfLevel behavior differs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/iostats_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/iterator.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/iterator.h

## Purpose

`iterator.h` defines the public `Iterator` interface for ordered key/value traversal over RocksDB data sources such as DBs, column families, tables, and composed internal iterators. It extends `IteratorBase` with value access, wide-column access, iterator properties, timestamps, and MultiScan preparation.

## Important APIs, Types, and Functions

`Iterator` inherits from `IteratorBase` and adds pure virtual `value()`, virtual `columns()`, `GetProperty(std::string, std::string*)`, `timestamp()`, and `Prepare(const MultiScanArgs&)`. It also declares factory helpers `NewEmptyIterator()` and `NewErrorIterator(const Status&)`. Documented properties include `rocksdb.iterator.is-key-pinned`, `rocksdb.iterator.is-value-pinned`, `rocksdb.iterator.super-version-number`, `rocksdb.iterator.internal-key`, and `rocksdb.iterator.write-time`.

## Control Flow

Normal iteration flow is inherited from `IteratorBase`: seek, check `Valid()`, read `key()` and `value()` or `columns()`, advance with `Next()` or `Prev()`, and finally inspect `status()`. `Prepare()` is an optional optimization path for MultiScan-style workloads: callers provide scan ranges, implementation prefetches relevant blocks, and then callers seek to each range start in order. If subsequent seeks diverge from the prepared scan sequence, implementations should disregard prepared state until `Prepare()` is called again.

## State and Persistence Behavior

The header defines no storage itself. Implementations hold snapshots, pinned blocks, table-reader state, prepared scan state, and buffers for key/value/column slices. Returned `Slice` and `WideColumns` references are valid only until the next iterator modification unless a property reports pinned lifetime. `timestamp()` is virtual and defaults to an assertion failure because only timestamp-aware iterators should expose it.

## Dependencies and Integration Points

The header depends on `iterator_base.h`, `options.h`, and `wide_columns.h`. It is consumed across table iterators, DB iterators, merging iterators, external table iterators, BlobDB, secondary index utilities, Java bindings, and `multi_scan.h`. The implementation of `NewEmptyIterator` and `NewErrorIterator` lives in `table/iterator.cc`.

## Risks and Edge Cases

The default `columns()` and `timestamp()` assert false, so callers must only use them when the implementation contract says they are supported. Slice lifetimes are short unless pinning is guaranteed. `GetProperty` support is implementation-specific. Prepared MultiScan state depends on ordered seeks and correct upper bounds; HISTORY entries show recent bugs around MultiScan upper bounds, unpinning, and limit handling. Wide-column conversion must preserve default anonymous column semantics.

## Test Signals

Tests in `table/table_test.cc` and related DB iterator suites validate `PrepareValue`, BlobDB on-demand value loading, pinned key/value properties, MultiScan prefetch, wide-column scan/dump behavior, and error iterators. Failures surface as invalid iterators, non-OK status, wrong key/value order, assertion failures in unsupported accessors, or stale slice use.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/iterator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/iterator_base.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/iterator_base.h

## Purpose

`iterator_base.h` declares `IteratorBase`, the minimal cleanable cursor interface shared by RocksDB iterators. It captures positioning, forward/backward movement, refresh, deferred value preparation, key access, and status reporting without prescribing value representation.

## Important APIs, Types, and Functions

`IteratorBase` inherits from `Cleanable` and declares pure virtual `Valid`, `SeekToFirst`, `SeekToLast`, `Seek`, `SeekForPrev`, `Next`, `Prev`, `key`, and `status`. It provides virtual defaults for `Refresh()`, `Refresh(const Snapshot*)`, and `PrepareValue()`. Copy and assignment are deleted. `Seek` and `SeekForPrev` accept user keys without timestamps.

## Control Flow

The expected control flow is seek, check `Valid()`, consume `key()` and subclass-specific value APIs, advance, and inspect `status()`. Seek methods clear prior error state so `status()` after a seek reflects only the seek and later movement. `Refresh()` invalidates the iterator and moves it to a latest DB state or a supplied snapshot, after which callers must seek again. `PrepareValue()` is called when `ReadOptions::allow_unprepared_value` let the iterator defer loading expensive values.

## State and Persistence Behavior

The interface owns no persistence. Concrete iterators may hold cleanup callbacks through `Cleanable`, DB version references, snapshots, file handles, pinned cache blocks, or deferred value state. `PrepareValue()` can change iterator validity and status if loading fails. `status()` may return `Status::Incomplete()` for non-blocking I/O paths that would need additional I/O.

## Dependencies and Integration Points

The header depends on `cleanable.h`, `slice.h`, and `status.h`, and forward-declares `Snapshot`. `Iterator` in `iterator.h` builds on it. Internal wrappers like `IteratorWrapper`, table readers, merge iterators, BlobDB, external table wrappers, and multi-column-family iterators rely on this base contract.

## Risks and Edge Cases

Callers must not call `Next`, `Prev`, or `key` unless `Valid()` is true. Refresh invalidates current positioning and can silently change snapshot semantics to the latest state when no snapshot is supplied. `allow_unprepared_value` requires applications or wrapper iterators to call `PrepareValue()` before accessing values; HISTORY entries note past incorrect values when wrappers failed to do so. Non-blocking I/O users must treat `Incomplete` as a state, not data absence.

## Test Signals

Relevant signals include iterator tests for refresh semantics, BlobDB and multi-column-family `PrepareValue()` behavior, table iterator status propagation, invalid-state assertions, and `Status::Incomplete()` handling in non-blocking paths. Existing HISTORY notes around `BaseDeltaIterator` and unprepared values are useful regression targets.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/iterator_base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/ldb_tool.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/ldb_tool.h

## Purpose

`ldb_tool.h` declares the embeddable public interface for RocksDB's `ldb` command-line tool. It lets the standalone `tools/ldb.cc` binary and external callers run ldb commands with supplied DB options, column-family descriptors, and custom display formatting.

## Important APIs, Types, and Functions

The header exposes `SliceFormatter`, `LDBOptions`, and `LDBTool`. `SliceFormatter::Format` converts raw `Slice` keys to readable strings. `LDBOptions` carries a shared `key_formatter` and `print_help_header`, defaulting to `"ldb - RocksDB Tool"`. `LDBTool::Run` is deprecated because it exits the process. `LDBTool::RunAndReturn` executes command parsing and returns an integer status.

## Control Flow

`tools/ldb.cc` constructs `LDBTool` and calls into this interface. The implementation in `tools/ldb_tool.cc` delegates to `LDBCommandRunner::RunCommand`, which prints help or version for short invocations, creates a concrete `LDBCommand` from argv, validates command-line options, runs the command, emits command execution text to stderr, deletes the command object, and returns 0 or 1. `Run` simply calls `exit(RunAndReturn(...))`.

## State and Persistence Behavior

The header stores no durable state itself. Commands behind the interface can open DBs, read or mutate keys, write external SSTs, update manifests, repair, backup, restore, checkpoint, ingest files, and inspect metadata. The supplied `Options` and optional column-family descriptors control DB open behavior.

## Dependencies and Integration Points

It depends on `rocksdb/db.h` and `rocksdb/options.h`. Implementation integrates with `rocksdb/utilities/ldb_cmd.h` and `tools/ldb_cmd_impl.h`. Build files expose `ldb`, `ldb_cmd_test`, and Python `tools/ldb_test.py`. HISTORY entries show ldb is a compatibility and operations surface for blob files, wide columns, file checksums, secondary/follower opens, option loading, unsafe metadata repair, and consistency checks.

## Risks and Edge Cases

Using deprecated `Run` from libraries can terminate the host process and trigger leak reports because default options are not unwound. `SliceFormatter` affects display only; command behavior must not depend on formatted keys unless explicitly wired by command code. ldb commands can perform dangerous persistence operations such as manifest updates and unsafe SST removal, so options validation and clear exit codes matter. Option loading from copied DBs has historically been subtle around `wal_dir`.

## Test Signals

Primary signals are `tools/ldb_cmd_test.cc`, `tools/ldb_test.py`, shell scripts using `ldb scan`, and HISTORY regressions for wide-column dump/scan, blob checksum output, option loading, compression support errors, and consistency checks. For embedders, `RunAndReturn` exit status and stderr execution result are the key observable signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/ldb_tool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/listener.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/listener.h

## Purpose

`listener.h` defines RocksDB's public event notification interface. It supplies structured event payloads and `EventListener` callbacks for flushes, compactions, file creation/deletion, blob files, file I/O, write stalls, background errors, recovery, ingestion, DB shutdown, and background job pressure.

## Important APIs, Types, and Functions

Important payload types include `FileCreationBriefInfo`, `TableFileCreationInfo`, `BlobFileCreationInfo`, `CompactionJobInfo`, `SubcompactionJobInfo`, `FlushJobInfo`, `MemTableInfo`, `ExternalFileIngestionInfo`, `BackgroundErrorRecoveryInfo`, `IOErrorInfo`, and `BackgroundJobPressure`. Enumerations include `CompactionReason`, `FlushReason`, `BackgroundErrorReason`, and `FileOperationType`, with string helpers for compaction and flush reasons. `EventListener` extends `Customizable`, offers `CreateFromString`, `Type`, `Name`, and many virtual no-op callbacks. `ShouldBeNotifiedOnFileIO()` gates file-I/O finish and error callbacks.

## Control Flow

RocksDB invokes listener callbacks from the thread performing the event: background flush threads call flush callbacks, compaction threads call compaction callbacks, file readers/writers call file-I/O callbacks, and user-operation threads can call ingestion or background-error callbacks. Compaction ordering is explicitly modeled: `OnCompactionBegin`, subcompaction callbacks, `OnCompactionPreCommit` after output files are written but before manifest commit releases inputs, then `OnCompactionCompleted` after commit. File creation callbacks have started and completed variants, and completed callbacks can carry failed status.

## State and Persistence Behavior

The header stores no listener state, but payloads snapshot DB state and file metadata at event time. Some payload references and DB pointers are only valid during callback execution and must be copied for later use. Callbacks observe persistent transitions such as new SSTs, blob files, file deletion, manifest commits, write-stall state, and background error state. `OnBackgroundError` can mutate the pending background error, potentially preventing the DB from entering read-only mode.

## Dependencies and Integration Points

The header depends on advanced options, compaction stats, compression types, customization, `IOStatus`, `Status`, table properties, and core RocksDB types. Usage spans DB implementation, flush/compaction jobs, file readers and writers, C API event listener wrappers, Java event listeners, db_bench, db_stress, BlobDB, external SST ingestion, and tests. HISTORY shows the API is heavily maintained, including atomic flush fixes, pre-commit compaction race avoidance, blob callbacks, file-I/O expansion, and DB shutdown notification.

## Risks and Edge Cases

Callbacks must not throw into RocksDB. Blocking writes, manual compactions, or long work from callbacks can deadlock or slow background workers, especially when compaction is needed to resolve write stalls. Compaction callbacks are skipped during DB shutdown for some cases. `OnCompactionCompleted` fires after input files have been released, so listeners tracking in-progress files should use `OnCompactionPreCommit`. File-I/O callbacks require opting in via `ShouldBeNotifiedOnFileIO`. References passed to callbacks have limited lifetime.

## Test Signals

Signals include `db/db_flush_test.cc` listener ordering tests, DB basic table/blob file listener tests, external SST listener tests, Java `EventListenerTest`, C API listener tests, and db_stress `DbStressListener` checks for pre-commit ordering, background pressure, file I/O, and concurrent compaction tracking. Good assertions cover callback counts, ordering, payload status, file numbers, blob metadata, write-stall transitions, background recovery old/new errors, and absence of deadlocks under callback activity.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/listener.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/memory_allocator.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/memory_allocator.h

## Purpose

`memory_allocator.h` declares RocksDB's pluggable allocation interface for cache and table/block memory. It lets applications replace default heap allocation with custom allocators, including jemalloc-backed no-core-dump allocation for large caches.

## Important APIs, Types, and Functions

`MemoryAllocator` extends `Customizable` and exposes `Allocate(size_t)`, `Deallocate(void*)`, `UsableSize(void*, size_t)`, `CreateFromString`, `Type`, and `GetId`. `JemallocAllocatorOptions` configures tcache size limiting, lower/upper tcache bounds, and number of jemalloc arenas. `NewJemallocNodumpAllocator` constructs a jemalloc allocator that applies `MADV_DONTDUMP` to allocated cache memory when supported.

## Control Flow

Caches and block/table readers receive a shared allocator from cache options. Allocation paths call `Allocate`, use the returned memory for blocks or metadata, optionally inspect `UsableSize`, and later call `Deallocate` through cache/block deleters. `MemoryAllocator::CreateFromString` registers built-ins once and loads a managed object from the object registry. `NewJemallocNodumpAllocator` is used directly by db_bench and by configurations that request that allocator.

## State and Persistence Behavior

Allocators manage process memory only. The no-dump jemalloc allocator creates dedicated arenas and marks allocations outside core dumps, reducing persisted crash-dump footprint rather than changing DB contents. Allocator instances can carry internal counters, arena handles, tcache configuration, and wrapped target allocators.

## Dependencies and Integration Points

The header depends on `Customizable` and `Status`. Implementations live under `memory/`, with helpers in `utilities/memory_allocators.h`. Integration points include `advanced_cache.h`, `cache.h`, block fetcher, block-based table reader, meta-block loading, `IODispatcher`, C API cache allocator setters, options/customizable tests, db_bench cache options, and table/block fetcher tests.

## Risks and Edge Cases

All methods must be thread-safe because caches and readers call them concurrently. `Deallocate` must pair with the same allocation family; mixing allocators can corrupt memory. `UsableSize` defaults to the requested allocation size, which is conservative but may underreport real allocator capacity. Jemalloc no-dump support depends on build and platform features, so creation can fail. Tcache and arena settings trade memory footprint against contention and must be tuned for thread count and block size.

## Test Signals

Tests include `memory/memory_allocator_test.cc`, block fetcher allocator accounting, `BlockBasedTableTest.MemoryAllocator`, options/customizable allocator loading, and C API allocator wiring. Useful signals are allocation/deallocation balance, nonzero custom allocator usage, successful CreateFromString for built-ins, graceful failure when jemalloc support is unavailable, and absence of leaks or mismatched frees under cache eviction.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/memory_allocator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/memtablerep.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/memtablerep.h

## Purpose

`memtablerep.h` defines the pluggable in-memory data-structure contract backing RocksDB memtables. It allows skip list, vector, hash skip list, hash linked list, and custom representations to store encoded internal keys and values before flush.

## Important APIs, Types, and Functions

Core types are `KeyHandle`, `MemTableRep`, nested `MemTableRep::KeyComparator`, nested `MemTableRep::Iterator`, and `MemTableRepFactory`. `MemTableRep` exposes allocation, insertion variants with optional hints and concurrent insertion, `BatchPostProcess`, `Contains`, `MarkReadOnly`, `MarkFlushed`, point lookup `Get`, validation lookup `GetAndValidate`, sorted-key `MultiGet`, approximate entry count, random sampling, memory usage, iterators, dynamic-prefix iterators, and feature predicates for merge operators and snapshots. Factories include `SkipListFactory`, `VectorRepFactory`, `NewHashSkipListRepFactory`, and `NewHashLinkListRepFactory`.

## Control Flow

MemTable code asks the configured `MemTableRepFactory` to create a representation with a comparator, allocator, prefix extractor, logger, and optionally column-family id. Writers allocate encoded entries and insert them; concurrent insert-capable reps use `InsertConcurrently` and `BatchPostProcess`. Readers call `Contains`, `Get`, `MultiGet`, or create iterators and seek through encoded internal keys. When a mutable memtable stops accepting writes, RocksDB calls `MarkReadOnly`; after stable flush, it calls `MarkFlushed`.

## State and Persistence Behavior

The representation owns in-memory entries allocated through an `Allocator`; entries are never deleted individually. It is mutable until read-only, then flushed to SST by higher layers. Implementations may maintain skip-list nodes, vectors, hash buckets, thread-local buffers, hints, and memory outside the allocator reported through `ApproximateMemoryUsage`. `MarkFlushed` is a lifecycle notification, not persistence itself.

## Dependencies and Integration Points

The header depends on `Customizable` and `Slice`, and forward-declares allocator, arena, lookup key, prefix transform, logger, and DB options. Built-in factory parsing is implemented in `table/plain/plain_table_factory.cc` and exposed through options as `memtable_factory`. Integration points include write path memtables, options parsing, Java samples, custom factory tests, vector and prefix hash modes, and validation paths that detect key ordering corruption.

## Risks and Edge Cases

The encoded key format is part of the API contract through `KeyComparator::decode_key`; custom reps must preserve it. Duplicate handling is optional and must match `CanHandleDuplicatedKey`. Concurrent insertion support must be accurately advertised. Prefix-hash reps are workload-specific and can make cross-prefix iteration expensive. Iterator allocation in an arena requires callers to destroy the iterator manually without `delete`. Validation APIs can return `NotSupported`, so callers must have fallback or feature checks.

## Test Signals

Signals include options tests for `skip_list`, `vector`, `prefix_hash`, and `hash_linkedlist` parsing; custom factory loading tests; memtable read/write, concurrent write, duplicate-key, merge, snapshot, iterator ordering, and corruption-validation tests; plus db_stress exercising configured memtable factories. Assertions should cover sorted iteration, successful lookups, approximate memory accounting, no duplicate insertion when advertised, and no long blocking in `MarkFlushed`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/memtablerep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/merge_operator.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/merge_operator.h

## Purpose

`merge_operator.h` declares the application-defined semantics for RocksDB merge operands. It lets RocksDB store incremental updates and later combine them during reads, iteration, flush, or compaction using client-supplied logic.

## Important APIs, Types, and Functions

`MergeOperator` extends `Customizable` and exposes deprecated `FullMerge`, `FullMergeV2`, wide-column-capable `FullMergeV3`, `PartialMerge`, `PartialMergeMulti`, `Name`, `AllowSingleOperand`, `ShouldMerge`, and `CreateFromString`. Input/output structs include `MergeOperationInput`, `MergeOperationOutput`, `MergeOperationInputV3`, and `MergeOperationOutputV3`. `OpFailureScope` lets failed merges distinguish try-merge failures from must-merge failures. `AssociativeMergeOperator` provides a simpler `Merge` method and implements the generic methods in terms of associative pairwise merging.

## Control Flow

Write operations can append merge operands without reading the old value. Later, RocksDB calls full merge when a base value or deletion boundary is available, or calls partial merge to collapse operands before a base value is known. During `Get`, RocksDB can call `ShouldMerge` to decide whether to force a full merge after seeing a reversed operand stack. During compaction, failed try-merge can make background work fail, while must-merge failures can allow compaction to keep original operands.

## State and Persistence Behavior

Merge operands are persisted in memtables, WALs, and SSTs as merge records until collapsed. The operator object itself is not persisted in this header; `Name()` is intended for mismatch checking, but the comment notes the name is not persistently enforced and clients must reopen with consistent semantics. V3 supports plain values, no value, and wide-column entities as merge bases and outputs.

## Dependencies and Integration Points

The header depends on `Customizable`, `Slice`, and `wide_columns.h`. Implementations and built-ins are registered in `utilities/merge_operators.cc`, including string append, uint64 add, bytesxor, max, sortlist, and put variants. Integration points include `table/get_context.cc`, table properties, options parsing, Java/JNI merge operators, TTL wrapping merge operator, transaction tests, and SST file writer/reader tests.

## Risks and Edge Cases

Exceptions must not propagate into RocksDB. Merge semantics must be deterministic and stable across DB reopen, backup, compaction, and language bindings. Returning false has serious consequences: reads can fail and flush/compaction can put the DB in read-only mode depending on `OpFailureScope`. Partial merges must preserve exact sequential semantics. The operand order differs for `ShouldMerge`, which receives reversed order for performance. Wide-column fallback in `FullMergeV3` can preserve non-default columns while merging only the default column, which custom operators must understand.

## Test Signals

Signals include options tests for `MergeOperator::CreateFromString`, table and SST reader tests using string append and uint64 add, transaction merge tests, TTL merge operator tests, Java merge operator tests, and get-context handling of `kMergeOperatorFailed`. Good tests cover full merge with/without base value, partial merge equivalence, false-return scopes, reopen with matching operator, wide-column merge behavior, and compaction/read differences.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/merge_operator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/metadata.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/metadata.h

## Purpose

`metadata.h` declares public metadata structs describing RocksDB files, live SSTs, blob files, LSM levels, column families, and export/import file sets. These structures support backups, checkpoints, metadata inspection, import, custom compaction decisions, and language bindings.

## Important APIs, Types, and Functions

The header defines `FileStorageInfo`, `LiveFileStorageInfo`, `SstFileMetaData`, `LiveFileMetaData`, `BlobMetaData`, `LevelMetaData`, `GetColumnFamilyMetaDataOptions`, `ColumnFamilyMetaData`, and `ExportImportFilesMetaData`. Fields cover relative filename, directory, file number, file type, size, temperature, checksums, replacement contents, trim-to-size behavior, sequence number bounds, key bounds, sampled reads, compaction state, entry/deletion counts, blob references, creation and ancestor times, epoch number, levels, blob file summaries, and comparator name for import safety.

## Control Flow

DB APIs populate these structs through `GetLiveFilesMetaData`, `GetLiveFilesStorageInfo`, `GetColumnFamilyMetaData`, `GetAllColumnFamilyMetaData`, checkpoint/export flows, and import column-family flows. `GetColumnFamilyMetaDataOptions` filters metadata by optional key range and level. Constructors normalize SST names into `relative_filename` and deprecated leading-slash `name` fields.

## State and Persistence Behavior

The structs are snapshots of persistent DB file state. SST metadata is immutable once produced, while `LiveFileStorageInfo` accounts for mutable live files such as `CURRENT` using `replacement_contents` and `trim_to_size`. Export/import metadata carries enough file and comparator information for `CreateColumnFamiliesWithImport` safety checks. Deprecated fields remain for API compatibility.

## Dependencies and Integration Points

The header depends on `options.h` and `types.h`. Integration points include DB metadata APIs in `db.h`, Java/JNI metadata classes, backup and checkpoint code, BlobDB live-file snapshots, db_stress metadata verification, compact-files examples, sorted run builder, option-change migration, ldb `list_live_files_metadata`, file checksum dump, and import/export tests.

## Risks and Edge Cases

Some fields are optional or zero when unavailable, such as creation time, ancestor time, epoch number, and file checksums. Deprecated `name` and `db_path` must stay consistent with newer `relative_filename` and `directory` for old callers. `BlobMetaData` constructor names appear easy to misuse: it assigns `_file_checksum` to `checksum_method` and `_file_checksum_func_name` to `checksum_value`, so consumers should verify semantics before display. `being_compacted` has had data-race history, so metadata gathering must synchronize with compaction state.

## Test Signals

Signals include Java `RocksDBTest.getColumnFamilyMetaData`, JNI conversions, db_stress `TestGetAllColumnFamilyMetaData`, SST file reader metadata tests, backup engine `LiveFileStorageInfo` tests, BlobDB metadata tests, ldb metadata output tests, and import/checkpoint tests. Assertions should cover level ordering, file counts and sizes, blob summaries, checksum fields, temperature propagation, range/level filtering, and import comparator mismatch rejection.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/metadata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/multi_scan.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/multi_scan.h

## Purpose

`multi_scan.h` declares an experimental range-scan container API that iterates over multiple ordered scan ranges using standard input-iterator style. It presents a nested iteration model: `MultiScan` yields `Scan` objects, and each `Scan` yields key/value pairs for one range.

## Important APIs, Types, and Functions

The header defines `MultiScanException`, `Scan`, `Scan::ScanIterator`, `MultiScan`, and `MultiScan::MultiScanIterator`. `MultiScanException` wraps a non-OK `Status`. `ScanIterator` yields `std::pair<Slice, Slice>` from an underlying `Iterator`, checks status after advancing, and throws on invalid dereference or scan errors. `MultiScan` owns read options, scan arguments, DB and column-family pointers, an upper-bound slice, and a unique DB iterator.

## Control Flow

Callers create `MultiScan` through `DB::NewMultiScan`, then loop over scans and over key/value pairs. Construction creates a DB iterator, configures the first range upper bound, and calls `Iterator::Prepare(scan_opts)` unless mixed bounded/unbounded ranges force a slow path. `MultiScanIterator` seeks to the start key of the current range in its constructor. Incrementing the outer iterator checks current status, advances the range index, updates or clears `iterate_upper_bound`, recreates the DB iterator if bound presence changes, seeks the next start key, and throws on errors.

## State and Persistence Behavior

The API stores only scan execution state. It does not persist data. Returned slices are backed by the underlying iterator and follow normal iterator lifetime rules. `read_options_` is copied and mutated internally for per-range upper bounds. The `upper_bound_` member owns storage for the current bound because `ReadOptions::iterate_upper_bound` points to it.

## Dependencies and Integration Points

The header depends on `db.h`, `iterator.h`, and `options.h`. The implementation lives in `db/multi_scan.cc` and checks filesystem async-I/O support before honoring `MultiScanArgs::use_async_io`. Integration points include `DB::NewMultiScan`, `MultiScanArgs` and `ScanOptions` in `options.h`, block-based table MultiScan prefetch, `IODispatcher`, read-scoped block buffers, user-defined indexes, statistics tickers/histograms, and external table tests.

## Risks and Edge Cases

The interface is experimental and throws exceptions, unlike most RocksDB APIs that return `Status`. Empty scan vectors, missing start keys, invalid dereference, and out-of-range advancement throw logic errors or status exceptions. Mixed ranges with and without limits skip Prepare and recreate iterators on bound-mode changes. HISTORY shows recent fixes for upper-bound respect, page unpinning, async fallback, max sequential skip, dictionary compression fallback, and incorrect results across files, so boundary and ownership behavior are high risk.

## Test Signals

Signals include `table/table_test.cc` DBMultiScan and block-based MultiScan validation, user-defined-index MultiScan failure tests, `util/io_dispatcher_test.cc` MultiScan read-scoped provider coverage, statistics counters/histograms, and HISTORY regression cases. Tests should assert range ordering, correct start/limit behavior, no cross-range leakage, expected exceptions/statuses, async fallback when unsupported, bounded prefetch memory, and valid slice contents until iterator advancement.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/multi_scan.h -->
