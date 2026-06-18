# subset-b-008640 Research

Grouped research for RocksDB public headers under `sources/storage-engines/rocksdb/include/rocksdb`. Each section preserves its source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/c.h -->
# sources/storage-engines/rocksdb/include/rocksdb/c.h

## Purpose

`c.h` is RocksDB's exported C ABI surface. It exposes opaque handles for the C++ database, options, cache, backup, transaction, compaction, iterator, snapshot, memory, and remote-compaction objects, plus C-callable constructors, destructors, mutators, and operation functions. The header is intentionally broad: it allows non-C++ callers such as JNI, FFI bindings, and shared-library consumers to drive RocksDB without depending on C++ type layout or name mangling. It also states the central C API conventions: all implementation types are opaque pointers; slices are modeled as pointer-plus-length; most fallible calls use `char** errptr`; booleans are `unsigned char`; and pointer arguments are expected non-null.

## Important APIs, Types, and Functions

The file defines `ROCKSDB_LIBRARY_API` for Windows DLL import/export and wraps declarations in `extern "C"`. It forwards dozens of opaque structs, including `rocksdb_t`, `rocksdb_options_t`, `rocksdb_column_family_handle_t`, `rocksdb_iterator_t`, `rocksdb_writebatch_t`, `rocksdb_cache_t`, transaction DB handles, backup handles, and remote compaction handles. `rocksdb_slice_t` is the one exposed value struct, ABI-shaped for zero-copy slice interop with `{const char* data; size_t size;}`.

Core DB lifecycle functions include `rocksdb_open`, TTL/read-only/secondary open variants, column-family open variants, `rocksdb_close`, `rocksdb_destroy_db`, and `rocksdb_repair_db`. Data operations cover put/delete/single-delete/delete-range/merge/write-batch, timestamp variants, multi-get, batched multi-get, `key_may_exist`, pinned get, zero-copy pinned handle APIs, and direct `rocksdb_get_into_buffer`. Read surfaces include iterators, WAL iterators, snapshots, properties, approximate sizes, live-file metadata, metadata trees, and memory-usage accounting.

The options surface is extensive. It includes create/copy/destroy, dynamic `rocksdb_set_options`, DB/CF option setters and getters, table options, compression and blob settings, rate limiters, write/read/compact/flush options, compaction styles, FIFO/universal options, WAL recovery and compression enums, statistics/perf context, Env and EnvOptions, SST file writer and external-file ingest, write buffer manager, SST file manager, cache and allocator configuration, event listeners, compaction filters/factories, comparators including timestamp-aware comparators, filter policies, merge operators, slice transforms, backup/restore, checkpoint/export/import, and transaction/optimistic transaction APIs.

Remote compaction support is represented by callback typedefs for scheduling, waiting, cancellation, and installation notification; `rocksdb_compactionservice_t`; job status enums; scheduler response and job-info accessors; compaction-service option overrides; cancellation flag helpers; and `rocksdb_open_and_compact` entry points.

## Control Flow

This header declares, rather than implements, control flow. The visible flow contract is handle-oriented: callers create option/configuration objects, pass them into open or factory functions, perform DB operations with read/write/compact/flush options, inspect output handles or buffers, then release resources with the matching destroy/close/free functions. Error flow is out-of-band through `char** errptr`: successful calls leave existing error storage unchanged, while failures free any previous error string and replace it with a malloc-owned message.

Several APIs encode callback flow. User-provided C callbacks drive compaction filters, compaction filter factories, comparators, merge operators, slice transforms, loggers, event listeners, and remote compaction services. For event listeners, RocksDB invokes callback pointers on flush/compaction/subcompaction/external-file-ingestion/background-error/stall/memtable events. For remote compaction, RocksDB asks the service to schedule work, waits for job output, cancels queued jobs, and reports installation status.

## State and Persistence Behavior

The API gives callers control over persistent RocksDB state: DB directories, WAL directories, column-family metadata, manifest identity flags, WAL tracking, backups, checkpoints, SST file ingestion, export/import metadata, TTL, user-defined timestamps, blob files, compaction output, and transactions. It also exposes operational state such as snapshots, iterators, pinned values, live files, cache usage, perf context counters, statistics histograms, memory-usage approximations, file deletion disable/enable state, manual compaction enable/disable state, and background work cancellation.

Ownership is a major part of the state contract. Returned malloc-owned strings and buffers must be released with `rocksdb_free` unless a more specific destroy function is documented. Handles created by `*_create` generally require matching `*_destroy`; DB-like handles require close functions; snapshot handles must be released against the owning DB; iterator and pinnable handles pin resources until destroyed. Some comments call out special cases, for example backup stop is one-way for a backup engine, transaction snapshot/write-batch handles have specific free/destroy expectations, and `rocksdb_cache_disown_data` intentionally changes cache ownership behavior.

## Dependencies and Integration Points

`c.h` depends only on C standard headers plus the RocksDB shared-library ABI macro, but each declaration maps to C++ implementations in `db/c.cc` and RocksDB internals. It integrates with the C++ APIs behind `rocksdb/options.h`, `rocksdb/cache.h`, `rocksdb/comparator.h`, `rocksdb/compaction_filter.h`, transaction DB, backup engine, Env, table factories, PerfContext, and compaction-service code. Search signals show `db/c.cc` implements newer surfaces such as `rocksdb_comparator_with_ts_create`, remote compaction options, and `rocksdb_open_and_compact`; `examples/c_simple_example.c` exercises the basic C lifecycle.

The file is also a binding contract. JNI, language wrappers, and external projects rely on symbol names, argument order, enum values, and ownership semantics staying stable. The timestamp-aware comparator and high-performance get APIs are particularly important integration points for newer UDT and zero-copy binding work.

## Risks and Edge Cases

The dominant risks are ABI and ownership errors. Changing opaque type names, exported symbol signatures, enum values, or error conventions can break downstream FFI consumers. Returning memory from different allocators or failing to document the correct destroy/free function can cause leaks or crashes. `char** errptr` requires callers to initialize and retain ownership correctly; multi-get uses per-key error arrays, which is a different error shape from most calls.

Callback APIs are high risk because RocksDB calls into user code from internal threads. Exceptions are not visible in C, but callback implementers can still crash, leak, or violate comparator/filter invariants. Timestamp APIs require consistent timestamp sizes and comparator semantics. `singledelete`, range deletion, compaction filters, ingest-behind, transaction APIs, and remote compaction all expose behaviors that can affect correctness or persistence if used with incompatible options. The header's "all pointers non-null" convention means callers cannot rely on defensive null checks.

## Test Signals

Useful signals include `examples/c_simple_example.c` for basic C API open/write/read/backup flow, `db/c.cc` for wrapper implementation, Java JNI sources for binding expectations, and RocksDB tests for the underlying C++ features. Search references show timestamp comparator tests in `db/db_with_timestamp_*`, `utilities/transactions/write_committed_transaction_ts_test.cc`, comparator implementation tests, cache tests, compaction filter blob tests, and cleanable/cache tests that indirectly validate handles and pinned-resource lifetimes exposed by the C API.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/cache.h -->
# sources/storage-engines/rocksdb/include/rocksdb/cache.h

## Purpose

`cache.h` is the public C++ configuration and factory surface for RocksDB caches. It defines the vocabulary for cache entry roles, shared sharded-cache options, LRU cache options, compressed secondary caches, HyperClockCache, tiered caches, and update functions. The file is intentionally option-heavy: actual cache implementations live elsewhere, while this header lets applications construct block, row, secondary, and tiered caches with stable public configuration types.

## Important APIs, Types, and Functions

`BlockCache` and `RowCache` are currently aliases for `Cache`, with comments documenting a staged future split. `CacheEntryRole` classifies cache charges into data, filter, metadata, index, write-buffer, compression dictionary, filter construction, table-reader, file-metadata, blob, blob-cache, and miscellaneous roles. `kNumCacheEntryRoles`, `GetCacheEntryRoleName`, `CacheEntryRoleSet`, and `BlockCacheEntryStatsMapKeys` support role-based statistics and property maps.

`ShardedCacheOptions` provides common state for shard-based caches: `capacity`, `num_shard_bits`, `strict_capacity_limit`, `memory_allocator`, `metadata_charge_policy`, `secondary_cache`, and expert `hash_seed`. The hash seed constants distinguish quasi-random and host-derived behavior, addressing correlation hazards across hosts and restarts.

`LRUCacheOptions` extends sharded options with high/low-priority pool ratios and adaptive mutex selection. It exposes `MakeSharedCache()` and `MakeSharedRowCache()`, while deprecated `NewLRUCache` overloads wrap those constructors for compatibility. `CompressedSecondaryCacheOptions` extends LRU options with `compression_type`, `compression_opts`, split/merge toggles, and a role set excluded from compression; it returns `std::shared_ptr<SecondaryCache>`.

`HyperClockCacheOptions` configures the recommended high-concurrency block cache. Key fields include `estimated_entry_charge`, `min_avg_entry_charge`, and `eviction_effort_cap`, plus inherited sharding, capacity, allocator, and metadata charge policy. `NewClockCache` is retained only as a compatibility wrapper that returns LRU because the old clock cache was removed. `TieredCacheOptions`, `NewTieredCache`, and `UpdateTieredCache` define an experimental two-tier/three-tier topology across primary uncompressed cache, compressed secondary cache, and optional non-volatile secondary cache.

## Control Flow

Most control flow is construction-time. Callers fill an options struct, then call `MakeSharedCache`, `MakeSharedRowCache`, `MakeSharedSecondaryCache`, `NewTieredCache`, or a deprecated wrapper. The returned shared pointer is installed into DB/table/blob/row-cache options. Runtime update flow exists only for tiered caches: `UpdateTieredCache` mutates total capacity, compressed-secondary ratio, and admission policy for a cache originally built by the tiered factory.

The header's inline wrappers construct temporary option structs and immediately delegate to the method-based factories. That keeps backward-compatible function signatures while centralizing future behavior in options objects.

## State and Persistence Behavior

Cache state is in-memory and non-persistent, but it directly affects persistence-adjacent IO behavior. Block cache contents, blob cache entries, write-buffer charges, and secondary-cache contents influence read amplification, write throttling, and memory pressure, but not the durable key/value state itself. Secondary caches can be non-volatile, and the tiered API can admit compressed blocks to an optional persistent secondary tier; nevertheless this header only models cache configuration, not on-disk format ownership.

The most important mutable state is capacity accounting: charges can include only entry charge or cache metadata overhead, strict capacity can reject insertions under pinned pressure, and WriteBufferManager reservations can be costed into the block cache. Sharding and hash seeds become stable runtime properties that affect contention and eviction distribution.

## Dependencies and Integration Points

The header depends on `compression_type.h`, `data_structure.h`, `memory_allocator.h`, forward-declared `Cache`, `SecondaryCache`, and `ConfigOptions`. It is used by `BlockBasedTableOptions::block_cache`, `DBOptions::row_cache`, blob cache options, WriteBufferManager integration, and tools such as db_bench/db_stress. Search signals show extensive use in table tests, `db_block_cache_test.cc`, `db_write_buffer_manager_test.cc`, `db_stress_test_base.cc`, `tools/db_bench_tool.cc`, Java JNI cache wrappers, and block-based table reader/factory code.

`CacheEntryRole` also integrates with table-builder/reader memory charging, compression dictionary guidance, filter construction, file metadata charging, and the `DB::Properties::kBlockCacheEntryStats` property map.

## Risks and Edge Cases

The aliasing plan for `BlockCache`, `RowCache`, and `Cache` is a compatibility risk: users treating row cache and block cache as fully interchangeable may need migration when the split happens. `CacheEntryRole` has an ordering invariant: adding roles requires updating string tables and keeping `kMisc` last. Misconfigured `num_shard_bits`, tiny shard capacities, or fixed hash seeds can create contention or thrashing. Strict capacity limit can surface insertion failures under pinned entries.

HyperClockCache is not a general cache despite returning `std::shared_ptr<Cache>`; using it outside compatible block-cache paths is risky. `estimated_entry_charge` that is badly wrong can degrade HCC performance. Tiered cache is experimental, has update limitations, and cannot re-enable compressed secondary after disabling it by setting the ratio to zero.

## Test Signals

Relevant tests include `db/db_block_cache_test.cc` for cache role stats and HCC/LRU behavior, `db/db_write_buffer_manager_test.cc` for cache-charged memtable memory, table/block-based tests for block cache interactions, and db_bench/db_stress option paths for realistic cache construction. Role charging validation appears in `table/block_based/block_based_table_factory.cc` and its tests; secondary-cache helpers live under `test_util/secondary_cache_test_util.*`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/cache_bench_tool.h -->
# sources/storage-engines/rocksdb/include/rocksdb/cache_bench_tool.h

## Purpose

`cache_bench_tool.h` is a narrow public declaration for the RocksDB cache benchmark tool entry point. It lets a tool binary, test harness, or embedding layer call the benchmark driver through `ROCKSDB_NAMESPACE::cache_bench_tool(int argc, char** argv)` without exposing implementation details in the header.

## Important APIs, Types, and Functions

The only API is `int cache_bench_tool(int argc, char** argv);`. It follows the conventional C/C++ command-line entry signature, returning an integer process-style status. The file includes `rocksdb/rocksdb_namespace.h`, `rocksdb/status.h`, and `rocksdb/types.h`, though this header itself does not expose `Status` or additional types in the signature.

## Control Flow

The header has no local control flow. The expected control flow is external: a caller constructs `argc`/`argv`, invokes `cache_bench_tool`, and receives a numeric exit code after the implementation parses flags, constructs cache workloads, and runs the benchmark. It is an adapter-style declaration rather than a reusable cache API.

## State and Persistence Behavior

No state is defined here. Any benchmark state, cache instances, command-line options, random workload state, and metrics are owned by the implementation. Persistence impact is expected to be none or temporary benchmark output only; this declaration does not model DB files or durable cache data.

## Dependencies and Integration Points

The header integrates with the cache benchmark implementation under RocksDB tools/cache code and the build system that produces the executable. It belongs in the public include tree so tools can compile against the entry point while remaining namespace-correct.

## Risks and Edge Cases

The main risk is signature stability. Since callers may use it as a `main`-like entry, changing return type, namespace, or arguments would break tool integration. The extra includes can also make this tiny header more sensitive to dependency churn than its signature requires.

## Test Signals

Signals are mostly build-level: successful compilation of the cache benchmark target and any tests or scripts that launch the benchmark. Since the header contains only a declaration, substantive behavior should be validated in the corresponding tool implementation rather than here.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/cache_bench_tool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/cleanable.h -->
# sources/storage-engines/rocksdb/include/rocksdb/cleanable.h

## Purpose

`cleanable.h` defines a small RAII cleanup registry used throughout RocksDB to attach deferred cleanup actions to iterators, pinned slices, async IO buffers, cache handles, and other objects that need lifetime-coupled release callbacks. It also defines `SharedCleanablePtr`, a copyable reference-counted wrapper for a `Cleanable` that allows multiple outer objects to share cleanup ownership efficiently.

## Important APIs, Types, and Functions

`Cleanable` owns a linked list of cleanup records. Each record stores a `CleanupFunction` and two opaque arguments. Public operations include construction/destruction, move construction/assignment, `RegisterCleanup(function, arg1, arg2)`, `DelegateCleanupsTo(Cleanable* other)`, `Reset()`, and `HasCleanups()`. Copy construction and copy assignment are deleted to prevent accidental double execution.

The first cleanup is stored inline in `cleanup_`; additional cleanups are heap-allocated `Cleanup` nodes linked through `next`. The protected `RegisterCleanup(Cleanup* c)` transfers ownership of an existing cleanup node to this object. Private `DoCleanup()` executes the inline function first, then each linked cleanup, deleting heap nodes as it goes. `Reset()` runs cleanup and nulls the inline function/next pointers for reuse.

`SharedCleanablePtr` exposes empty construction, copy/move construction and assignment, destructor, `Allocate()`, `Reset()`, dereference/arrow/get accessors, `RegisterCopyWith(Cleanable* target)`, and `MoveAsCleanupTo(Cleanable* target)`. Its hidden `Impl` carries the refcounted `Cleanable`.

## Control Flow

Cleanup flow is destructor-driven unless `Reset()` is called explicitly. When a `Cleanable` is destroyed, it calls registered functions in registration-list order as encoded by the implementation, then deletes extra cleanup nodes. `DelegateCleanupsTo` moves this object's cleanup chain to another `Cleanable`, extending the target's cleanup set and preventing this object from running them. Move operations transfer cleanup ownership instead of duplicating it.

`SharedCleanablePtr` adds reference-counted flow: only after all copies are gone do the cleanups registered with the pointed-to `Cleanable` execute. `RegisterCopyWith` and `MoveAsCleanupTo` register the shared pointer's eventual destruction as a cleanup on a target object, delaying inner cleanup until the target's cleanup runs.

## State and Persistence Behavior

The state is entirely in-memory: callback pointers, opaque arguments, a linked cleanup list, and a hidden refcount for shared cleanables. It does not persist data, but it protects resources that may represent persistent or external state, such as cache handles, pinned blocks, file buffers, or iterators over DB state. Correct cleanup ordering prevents use-after-free for pinned slices and avoids leaks of cache references or IO allocations.

## Dependencies and Integration Points

The header only depends on `rocksdb/rocksdb_namespace.h`, but it is foundational across the read path. `IteratorBase` and internal iterators derive from `Cleanable`; `PinnableSlice` uses it to pin data and transfer ownership; cache helper utilities register cache handle releases; `GetContext` delegates value-pinner cleanups to pinned iterator managers; `io_dispatcher` uses `SharedCleanablePtr` for shared read-buffer cleanup; transaction code registers iterator cleanup callbacks. `table/cleanable_test.cc` is the direct behavioral test suite.

## Risks and Edge Cases

The biggest risks are double cleanup, missed cleanup, and cleanup cycles. The deleted copy operations avoid one double-free class, but incorrect delegation or manual reuse can still be hazardous. `SharedCleanablePtr` explicitly warns that reference cycles prevent cleanup forever. Callback functions receive untyped `void*` arguments, so type/lifetime mistakes are unchecked. `DoCleanup()` does not reset pointers; only `Reset()` does, so calling cleanup-like paths incorrectly could repeat work if implementation details are bypassed.

Exception safety matters even though this header does not mention exceptions: cleanup callbacks should not throw through destructors. Thread safety is not advertised; users should assume registration and cleanup are externally synchronized unless an owning object provides stronger guarantees.

## Test Signals

`table/cleanable_test.cc` directly covers registration, destructor cleanup, delegation into empty and non-empty targets, `PinnableSlice` interaction, shared wrapping, and `SharedCleanablePtr` behavior. Search signals also show integration coverage in cache helpers, IO dispatcher tests, transaction iterator cleanup, and read-path tests that depend on pinned data remaining valid until cleanups run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/cleanable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/compaction_filter.h -->
# sources/storage-engines/rocksdb/include/rocksdb/compaction_filter.h

## Purpose

`compaction_filter.h` defines the public extension point for application logic that inspects, drops, or rewrites records during table-file creation, especially compaction. It also introduces wide-column and blob-aware filtering support, including lazy blob-column resolution so filters can avoid unnecessary blob file IO. A companion `CompactionFilterFactory` creates per-table-creation filter instances based on context.

## Important APIs, Types, and Functions

`WideColumnBlobResolver` is an abstract interface with `ResolveColumn`, `ResolveColumns`, `IsBlobColumn`, and `NumColumns`. Its contract says resolved slices remain valid until `FilterV4` returns and resolver instances are single-compaction-thread objects.

`CompactionFilter` derives from `Customizable`. It defines `ValueType` values for plain values, merge operands, legacy BlobDB blob indexes, and wide-column entities. Its `Decision` enum includes `kKeep`, `kRemove`, `kChangeValue`, `kRemoveAndSkipUntil`, internal legacy blob decisions, `kPurge`, `kChangeWideColumnEntity`, and `kUndetermined` for key-only blob filtering. `BlobDecision` remains for internal stacked BlobDB use. `Context` exposes table-creation metadata: full/manual compaction flags, input start level, column family id, creation reason, and input table properties.

The filtering API is layered for compatibility. Old code can override `Filter` for plain key/value records and `FilterMergeOperand` for merge operands. `FilterV2` unifies plain values and merge operands and defaults to the older functions. `FilterV3` adds wide-column entities and defaults to keeping wide columns while delegating other types to `FilterV2`. `FilterV4` adds `WideColumnBlobResolver` and defaults to `FilterV3`. `SupportsFilterV4()` defaults false to force eager resolution for backward compatibility. `FilterBlobByKey` lets integrated BlobDB filters make decisions based on key without reading the blob value.

`CompactionFilterFactory` derives from `Customizable`, provides `ShouldFilterTableFileCreation(TableFileCreationReason)`, and creates a `std::unique_ptr<CompactionFilter>` from a `CompactionFilter::Context`. The default `ShouldFilterTableFileCreation` preserves old behavior by filtering only compaction-created files.

## Control Flow

During table-file creation, RocksDB decides whether to use a filter. A single `Options::compaction_filter` can be shared across threads, or a factory can create one filter per table-creation thread. The table builder/compaction/flush paths pass records through the filter before writing output. The filter returns a `Decision`, and RocksDB keeps, removes, rewrites, purges, converts to wide-column entity, or skips a key range according to that decision.

The versioned API flow is fallback-based. If a filter only overrides `Filter`, `FilterV2` adapts bool/value_changed outputs to `Decision`; `FilterV3` and `FilterV4` delegate down. If a filter overrides `FilterV4` and returns `SupportsFilterV4() == true`, wide-column blob values can be resolved lazily; otherwise blob-backed columns are eagerly fetched before legacy filtering. `FilterBlobByKey` runs before value-based filtering for blob-backed values when a key-only decision is possible; `kUndetermined` resumes the normal value path.

## State and Persistence Behavior

Compaction filters can permanently change durable DB contents by removing entries, rewriting values, changing wide-column entities, emitting tombstones, single-delete tombstones, or dropping ranges from output table files. The header explicitly warns that snapshots do not preserve repeatable reads in the presence of compaction filters; filtered data can disappear from snapshot views after a new table file is installed. It also notes that `IgnoreSnapshots()` is deprecated and false is unsupported.

Filter objects can hold application state, but if a single filter instance is configured directly it must be thread-safe under multithreaded compaction. Factory-created filters are per table-creation thread, reducing thread-safety burden while allowing multiple concurrent instances. Blob resolver state is transient and valid only during a `FilterV4` call.

## Dependencies and Integration Points

The header depends on `customizable.h`, `table_properties.h`, `types.h`, and `wide_columns.h`, with forward declarations for `Slice` and `SliceTransform`. Integration points include `Options::compaction_filter`, `Options::compaction_filter_factory`, table builder code, flush job code, compaction iterator/merge helper logic, BlobDB integrated compaction, wide-column storage, and config-string customization. Search signals show creation in `db/builder.cc` and `db/flush_job.cc`, compaction stats integration in `db_impl_compaction_flush.cc`, and many blob/wide-column tests under `db/blob/db_blob_index_test.cc` and `db/blob/db_blob_compaction_test.cc`.

## Risks and Edge Cases

This is a correctness-sensitive API. Incorrect `kRemove`, `kPurge`, or `kRemoveAndSkipUntil` decisions can delete data or expose older values. The header highlights TransactionDB risks when filtering merge operands: conflicts may be missed, so merge filtering should usually live in the merge operator. `kRemoveAndSkipUntil` ignores snapshots, can expose overwritten older values, does not work with PlainTable prefix mode, and has compaction readahead implications. Unsupported internal decisions must not be returned by applications.

Exception propagation from overridden methods is forbidden because RocksDB is not exception-safe. `FilterV4` lazy resolution errors must be handled conservatively: the header recommends returning `kKeep` for the current entry and allowing RocksDB to fail compaction after the resolver error is surfaced. A filter claiming `SupportsFilterV4()` without handling resolver semantics can change IO and correctness behavior. Thread safety differs sharply between direct filters and factory-created filters.

## Test Signals

Direct signals include `db/blob/db_blob_compaction_test.cc` for `FilterBlobByKey`, blob filtering, invalid decisions, and value mutation; `db/blob/db_blob_index_test.cc` for plain blob FilterV4, lazy wide-column blob resolution, resolver error paths, FilterV3 fallback, and TTL-based entity dropping; `db_stress_tool/db_stress_compaction_filter.h` for stress coverage of FilterV3/FilterV4 paths; and Java compaction filter tests for binding-level integration. Flush and builder code paths should be checked when changing factory decisions because filters can now apply outside ordinary compaction depending on `ShouldFilterTableFileCreation`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/compaction_filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/compaction_job_stats.h -->
# sources/storage-engines/rocksdb/include/rocksdb/compaction_job_stats.h

## Purpose

`compaction_job_stats.h` defines `CompactionJobStats`, the public aggregate of timing, IO, input/output, blob, deletion, corruption, and key-prefix metrics for a compaction job. It is a plain data carrier with `Reset()` and `Add()` helpers so compaction code can populate per-job stats and listeners/bindings can expose them.

## Important APIs, Types, and Functions

`CompactionJobStats` constructs by calling `Reset()`, provides `Reset()` to clear fields, and `Add(const CompactionJobStats&)` to aggregate another instance. Fields include elapsed wall-clock and CPU microseconds, an accuracy flag for input-record counts, input/output record counts, blob read counts, input/output table and blob file counts, trivially moved and filtered input file counts, full/manual/remote compaction flags, input/output byte totals, skipped input bytes, replaced-record counts, raw key/value bytes, deletion and expired-deletion counts, corrupt key count, optional background IO nanosecond counters, smallest/largest output key prefixes, and single-delete fallthrough/mismatch counters.

`kMaxPrefixLength` is the public maximum for output key prefix strings. The TODO notes missing output-to-proximal-level information.

## Control Flow

This header contains no algorithmic compaction control flow. The compaction engine creates a stats object, records values as the job runs, may aggregate sub-job or remote-worker stats with `Add()`, and reports the final struct to logs, event listeners, Java JNI, or DB internals. `Reset()` supports object reuse and construction initialization.

## State and Persistence Behavior

Stats are in-memory observations about persistent compaction work. They do not directly change database state, but they describe changes to durable table/blob files and compaction side effects. The fields distinguish compaction input from output, bytes skipped by optimizations, blob files read/written, tombstones expired, and corrupt keys encountered and written out. `is_remote_compaction` lets monitoring separate local and remote execution paths.

Accuracy is not absolute. `has_accurate_num_input_records` documents that input record counts can be inaccurate across subcompactions depending on compaction iterator implementation details. Background IO fields are only populated when `options.report_bg_io_stats` is true.

## Dependencies and Integration Points

The header depends on standard size/integer headers, `<string>`, and `rocksdb_namespace.h`. It integrates with compaction execution in `db/compaction/compaction_job.cc`, DB implementation compaction/flush notification paths, event listener compaction info accessors in the C API, Java JNI `CompactionJobStats`, and logging/monitoring surfaces. Search signals show usage in `db_impl_compaction_flush.cc`, `db_impl.h`, Java `rocksjni/compaction_job_stats.cc`, and compaction tests.

## Risks and Edge Cases

Because this struct is public, adding/removing/retyping fields can affect ABI/API users and language bindings. Aggregation must handle booleans, accuracy flags, strings, and optional IO stats carefully; simple numeric addition is not always semantically sufficient. Counter overflow is theoretically possible for very large or long-running workloads. Consumers must respect the accuracy flag and the `report_bg_io_stats` condition rather than treating all zeros as measured zeros.

Remote compaction makes provenance important: aggregating local and remote stats without preserving `is_remote_compaction` can obscure operational behavior. Prefix strings are limited to eight bytes and are not full keys, so diagnostics must not infer exact key ranges solely from them.

## Test Signals

Tests around compaction execution and Java JNI stats access are relevant. Search points to Java `CompactionJobStatsTest`, JNI getters in `java/rocksjni/compaction_job_stats.cc`, and compaction job tests under `db/compaction`. Changes should also be validated through event listener compaction callbacks and options enabling `report_bg_io_stats`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/compaction_job_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/comparator.h -->
# sources/storage-engines/rocksdb/include/rocksdb/comparator.h

## Purpose

`comparator.h` defines RocksDB's public key ordering contract. Comparators impose the total order used by memtables, SSTables, range tombstones, indexes, iterators, compaction, transactions, and DB open compatibility checks. The header also exposes built-in bytewise and reverse-bytewise comparators, timestamp-aware variants, and utilities for encoding/decoding `uint64_t` user-defined timestamps.

## Important APIs, Types, and Functions

`CompareInterface` is the minimal abstraction with `Compare(const Slice&, const Slice&)`. `Comparator` derives from `Customizable` and `CompareInterface`, stores a `timestamp_size_`, and requires overrides for `Name()`, `Compare()`, `FindShortestSeparator()`, and `FindShortSuccessor()`. Optional overrides include `Equal()`, `IsSameLengthImmediateSuccessor()`, `CanKeysWithDifferentByteContentsBeEqual()`, `GetRootComparator()`, `GetMaxTimestamp()`, `GetMinTimestamp()`, `TimestampToString()`, `CompareTimestamp()`, `CompareWithoutTimestamp()`, and `EqualWithoutTimestamp()`.

Static/customization helpers include `Comparator::CreateFromString` and `Comparator::Type()`. Built-ins include `BytewiseComparator()`, `ReverseBytewiseComparator()`, `BytewiseComparatorWithU64Ts()`, and `ReverseBytewiseComparatorWithU64Ts()`. Timestamp helpers include `DecodeU64Ts`, `EncodeU64Ts`, `MaxU64Ts`, and `MinU64Ts`.

## Control Flow

RocksDB calls `Compare()` throughout read and write paths whenever user-key order matters. With user-defined timestamps enabled, `Compare()` compares the user-key plus timestamp, ordering newer timestamps first for the same user key. Internal code calls `CompareWithoutTimestamp()` when it needs user-key ordering independent of timestamp, such as range checks, file overlap checks, range tombstone handling, transaction lock ranges, and table iterator bounds.

Index construction calls `FindShortestSeparator()` and `FindShortSuccessor()` to shorten index keys without violating ordering. Prefix/auto-prefix code can call `IsSameLengthImmediateSuccessor()` for bound reasoning, but the header documents a bug constraint: it must only return true when no other keys starting with the successor are ordered before it. `CreateFromString` lets configuration parse known comparator names to built-in comparator objects.

## State and Persistence Behavior

Comparator choice is persistent DB metadata. The comparator `Name()` is stored/checked so opening an existing DB with an incompatible ordering fails instead of corrupting interpretation of SSTables. Any change to ordering must use a new comparator name. Timestamp size is comparator state that affects key layout and read/write semantics; built-in U64 timestamp comparators define max/min timestamp slices and encode/decode helpers.

The built-in comparator functions return immortal pointers that callers must not delete. `EncodeU64Ts` returns a `Slice` backed by caller-provided string storage, so its lifetime depends on `ts_buf`.

## Dependencies and Integration Points

The header depends on `<string>`, `customizable.h`, and `rocksdb_namespace.h`, with `Slice` forward-declared. It integrates broadly with `options.comparator`, memtable/table/index code, compaction pickers and outputs, range tombstone fragmentation, transaction lock managers, write-batch-with-index, SST file writer/reader, iterator timestamp APIs, and C API comparator constructors. Search signals show heavy use of `CompareWithoutTimestamp` in table, DB, compaction, transaction, and range tombstone code; implementation and built-in registration live in `util/comparator.cc`.

## Risks and Edge Cases

Comparator mistakes are severe: non-total or non-thread-safe ordering can corrupt DB behavior. Changing `Name()` incorrectly can either block valid opens or, worse, allow incompatible opens if the name is reused after ordering changes. Exceptions must not escape overrides. `CanKeysWithDifferentByteContentsBeEqual()` defaults true, which may disable or constrain hash-index optimizations unless overridden accurately. Timestamp-aware comparators must override timestamp min/max and compare-without-timestamp behavior coherently.

The `IsSameLengthImmediateSuccessor` bug note is important for auto-prefix mode; returning true too broadly can omit keys within iterator bounds. `FindShortestSeparator` and `FindShortSuccessor` may legally do nothing, but incorrect shortening can violate table index ordering. `EncodeU64Ts` lifetime is easy to misuse if the backing string is destroyed too early.

## Test Signals

Relevant tests include `db/comparator_db_test.cc` for successor behavior, `util/udt_util_test.cc` and `utilities/types_util_test.cc` for timestamp encoding/decoding, many `db/db_with_timestamp_*` and transaction timestamp tests for UDT semantics, table/block-based tests for timestamp-aware ordering, and `db/c.cc` plus C API tests for `rocksdb_comparator_with_ts_create`. Broad use of `CompareWithoutTimestamp` in compaction and range tombstone code means comparator changes need wider DB regression coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/comparator.h -->
