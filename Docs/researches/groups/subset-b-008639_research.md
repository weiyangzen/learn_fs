# subset-b-008639 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/advanced_options.h -->
# sources/storage-engines/rocksdb/include/rocksdb/advanced_options.h

## Purpose
`advanced_options.h` defines RocksDB's advanced column-family tuning surface. It is a public API header that collects the lower-level options controlling memtable behavior, compaction style and picking, periodic and read-triggered compaction, file temperatures, integrated BlobDB, blob direct write partitioning, user-defined timestamp persistence, in-memory corruption protection, and iterator-driven flush/conversion optimizations. Most declarations are data-bearing structs/enums rather than executable code, but their comments encode important runtime contracts for DB open, `SetOptions()`, flush, compaction, WAL recovery, manifest visibility, and storage-tier integration.

## Important APIs, Types, And Functions
The file starts with compaction selection enums. `CompactionStyle` selects leveled, universal, FIFO, or manual-only compaction. `CompactionPri` selects leveled compaction file priority through compensated size, oldest update sequence, oldest smallest sequence, minimum overlap ratio, or round-robin traversal.

`FileTemperatureAge` is a small equality-comparable pair of `Temperature` and age seconds used by FIFO temperature transitions. `CompactionOptionsFIFO` configures FIFO trimming and optional intra-L0 compaction: `max_table_files_size`, `max_data_files_size`, `allow_compaction`, deprecated `age_for_warm`, `file_temperature_age_thresholds`, `allow_trivial_copy_when_change_temperature`, `trivial_copy_buffer_size`, and `use_kv_ratio_compaction`. Constructors supply a 1 GiB default table-file cap and optional explicit cap/compaction settings. Equality defaults to field equality.

Other supporting enums include `CacheTier` for volatile, volatile compressed, and non-volatile block-cache tiers; `UpdateStatus` for in-place update callbacks; `PrepopulateBlobCache` for blob-cache fill policy; and `VerifyOutputFlags` for compaction-output verification. `VerifyOutputFlags` has bitmask operators `|`, `|=`, `&`, `&=`, and logical negation, allowing options to combine verification types such as block checksum, iteration/hash verification, file checksum, and enablement for local or remote compactions.

`AdvancedColumnFamilyOptions` is the central API. Its memtable/write-buffer fields include `max_write_buffer_number`, `min_write_buffer_number_to_merge`, `max_write_buffer_size_to_maintain`, `inplace_update_support`, `inplace_update_num_locks`, `experimental_mempurge_threshold`, `inplace_callback`, `memtable_prefix_bloom_size_ratio`, `memtable_whole_key_filtering`, `memtable_huge_page_size`, `memtable_insert_with_hint_prefix_extractor`, `bloom_locality`, `arena_block_size`, `memtable_factory`, `max_successive_merges`, `strict_max_successive_merges`, `memtable_protection_bytes_per_key`, `paranoid_memory_checks`, `memtable_verify_per_key_checksum_on_seek`, `memtable_op_scan_flush_trigger`, `memtable_avg_op_scan_flush_trigger`, `min_tombstones_for_range_conversion`, and `memtable_batch_lookup_optimization`.

Compaction and LSM-shape fields include `compression_per_level`, `num_levels`, `level0_slowdown_writes_trigger`, `level0_stop_writes_trigger`, `target_file_size_base`, `target_file_size_multiplier`, `target_file_size_is_upper_bound`, `level_compaction_dynamic_level_bytes`, `max_bytes_for_level_multiplier`, `max_bytes_for_level_multiplier_additional`, `max_compaction_bytes`, `soft_pending_compaction_bytes_limit`, `hard_pending_compaction_bytes_limit`, `compaction_style`, `compaction_pri`, `compaction_options_universal`, `compaction_options_fifo`, `max_sequential_skip_in_iterations`, `optimize_filters_for_hits`, `paranoid_file_checks`, `verify_output_flags`, `force_consistency_checks`, `report_bg_io_stats`, `disallow_memtable_writes`, `ttl`, `periodic_compaction_seconds`, `read_triggered_compaction_threshold`, `sample_for_compression`, `last_level_temperature`, `default_write_temperature`, `default_temperature`, `preclude_last_level_data_seconds`, `preserve_internal_time_seconds`, `bottommost_file_compaction_delay`, and `cf_allow_ingest_behind`.

Blob-related fields include `enable_blob_files`, `min_blob_size`, `blob_file_size`, `blob_compression_type`, `blob_compression_opts`, `enable_blob_garbage_collection`, `blob_garbage_collection_age_cutoff`, `blob_garbage_collection_force_threshold`, `blob_compaction_readahead_size`, `blob_file_starting_level`, `blob_cache`, `prepopulate_blob_cache`, `enable_blob_direct_write`, `blob_direct_write_partitions`, and `blob_direct_write_partition_strategy`.

The struct also defines `TablePropertiesCollectorFactories`, stores `table_properties_collector_factories`, and exposes constructors `AdvancedColumnFamilyOptions()` and `explicit AdvancedColumnFamilyOptions(const Options& options)` for defaults and conversion from the broader `Options` struct.

## Control Flow
This header does not implement the DB algorithms, but it drives several control-flow decisions elsewhere. The write path uses write-buffer sizing and counts to decide when mutable memtables become immutable, when writes slow down, and when flushing must block. If `min_write_buffer_number_to_merge` is above one, immutable memtables can be merged before flushing unless atomic flush sanitizes the value to one. `max_write_buffer_size_to_maintain` controls whether flushed immutable memtables remain in memory for transaction conflict checking.

In-place updates alter Put control flow: RocksDB checks current memtable state and value sizes, optionally calls `inplace_callback`, and either mutates the existing memtable value, inserts a merged value, or falls back/fails according to `UpdateStatus`. The callback runs in the write path and must be deterministic across reopen because WAL stores the original delta, not the callback-produced merged value.

Memtable bloom and prefix-hint options affect lookup and insertion paths. Bloom filters can include prefixes, whole keys, or both when `memtable_prefix_bloom_size_ratio` is enabled. Insert hints are used only by the default skiplist memtable and are ignored by concurrent-write and non-skiplist paths. Merge write flow can also attempt value lookup once `max_successive_merges` is reached; `strict_max_successive_merges` allows blocking filesystem reads to enforce the limit.

Compaction scheduling and execution branch on `compaction_style`. Leveled compaction uses L0 file triggers, dynamic level-byte shaping, target file sizes, pending compaction byte limits, compaction priority, and read-triggered thresholds. Universal compaction uses `compaction_options_universal`, periodic compaction semantics, and tiering options such as `last_level_temperature` and `preclude_last_level_data_seconds`. FIFO compaction uses file-age and size-based dropping, optionally considering SST plus blob bytes through `max_data_files_size`, changing file temperatures by age threshold, and running optional intra-L0 compaction when `allow_compaction` and related KV-ratio settings permit it.

Blob flow starts only when `enable_blob_files` is set. Large values at or above `min_blob_size` can be separated into blob files during flush/compaction according to `blob_file_starting_level`, blob file size, compression, cache, and GC options. With `enable_blob_direct_write`, the write path writes qualifying values directly to blob files and replaces WAL/memtable values with blob indexes, subject to significant restrictions around writer mode, WAL recovery, backups/checkpoints/live files, MemPurge, user-defined timestamps, and write-batch ingestion.

Iterator-driven optimizations can feed back into write/flush behavior. `memtable_op_scan_flush_trigger` and `memtable_avg_op_scan_flush_trigger` can mark the active memtable for flush after expensive scans over invisible entries. `min_tombstones_for_range_conversion` can insert logically redundant range tombstones into the current mutable memtable during forward or reverse iteration when enough contiguous point tombstones are observed and the iterator configuration permits full visibility.

## State And Persistence Behavior
Most fields are in-memory options copied into `ColumnFamilyOptions`, but many influence durable state. Compression, compaction, blob, temperature, timestamp, and table-property decisions affect SST and blob file contents, table properties, file metadata, and manifest-visible file placement. Several comments explicitly separate dynamically changeable options from immutable or restart-only options.

`ttl` and `periodic_compaction_seconds` are persisted indirectly through compaction rewrites and file deletion. In leveled mode they select old files for compaction; in FIFO mode `ttl` can delete old files; in universal mode `periodic_compaction_seconds` controls broad periodic rewrites and the effective value may combine with `ttl` for backward compatibility. File age is derived from table properties or filesystem modification times.

Temperature options integrate with tiered filesystems. FIFO age thresholds can rewrite files to a different `Temperature`; `last_level_temperature` and `default_write_temperature` influence new SST file creation; `default_temperature` affects read accounting for files without explicit temperature but is not dynamically changeable. `preclude_last_level_data_seconds` and `preserve_internal_time_seconds` require sequence-number-to-time metadata in SST properties and affect compaction placement and sequence zeroing.

Blob settings create persistent blob files referenced by SST values. Blob GC relocates live blobs during compaction so obsolete blob files can be removed once all referenced blobs are gone. Direct-write blob files are more constrained: recovery currently only supports blob files that became manifest-visible through flush/SST creation, so active direct-write blob files cannot be replayed from WAL by themselves.

User-defined timestamp persistence is controlled by `persist_user_defined_timestamps`. When false, timestamps are stripped from user keys persisted to SST metadata and blob files while still being present in WAL if WAL is enabled. This supports backward-compatible SST formats but requires cutoff management through `DB::IncreaseFullHistoryTsLow`, best-effort flush retention, and careful downgrade procedure after flushing active WALs.

Integrity options store or compute extra checksums. `memtable_protection_bytes_per_key` suffixes memtable entries, `block_protection_bytes_per_key` constructs per-key protection for in-memory blocks, and `verify_output_flags`/`paranoid_file_checks` add post-write verification of compaction output files. These do not necessarily alter all on-disk formats, but they can change memory layout, file validation, or compaction failure behavior.

## Dependencies And Integration Points
The header includes `blob_file_partition_strategy.h`, `cache.h`, `compression_type.h`, `memtablerep.h`, and `universal_compaction.h`, and forward-declares `Slice`, `SliceTransform`, `TablePropertiesCollectorFactory`, `TableFactory`, and `Options`. It depends on public RocksDB concepts including `Cache`, `Temperature`, `CompressionType`, `CompressionOptions`, `CompactionOptionsUniversal`, `MemTableRepFactory`, `SkipListFactory`, and `BlobFilePartitionStrategy`.

Major integration points include DB open/sanitize logic, `DB::SetOptions()`, `ColumnFamilyOptions` construction, write controllers, memtable factories, skiplist memtable optimizations, transaction conflict checking, merge operators, compaction pickers/builders, table factories, table property collectors, file systems with temperature support, cache implementations, BlobDB read/write/GC code, WAL recovery, backup/checkpoint/live-file enumeration, ingestion, and read/iterator implementations.

## Risks
Because this is public API, compatibility risk is high. Changing defaults, mutability, enum values, or callback behavior can break existing option files, dynamic `SetOptions()` strings, applications compiled against numeric enum values, and persisted OPTIONS/manifest expectations.

Several options deliberately weaken consistency or increase write-path latency. `inplace_update_support` breaks snapshot/iterator point-in-time consistency under concurrent updates, disables reliable backward memtable iteration, and requires exception-free deterministic callbacks. `strict_max_successive_merges` can block writes on filesystem reads. MemPurge and direct blob write are experimental and have explicit incompatibilities.

Compaction and tiering options interact in subtle ways. Dynamic level bytes reinterpret `compression_per_level` relative to base level; `cf_allow_ingest_behind` and `preclude_last_level_data_seconds` reserve the last level; universal/FIFO/leveled compaction assign different meanings to TTL and periodic compaction. Incorrect sanitization or migration handling can lead to read amplification, space amplification, or preserving/dropping tombstones incorrectly.

Blob direct write carries crash-recovery and tooling risk because active blob files are not fully recoverable from WAL replay and checkpoint/backup/live-file enumeration may need flushing. Custom `blob_direct_write_partition_strategy` is not serialized in OPTIONS, so applications must supply it on every open or partitioning behavior changes silently.

Integrity and verification options trade performance for detection. Per-key memtable/block checksums and output verification can add CPU and memory costs, while disabling or misconfiguring them can leave corruption paths undetected. `target_file_size_is_upper_bound`, compaction byte caps, and FIFO KV-ratio targets can also shift file sizing assumptions in downstream tests and operations.

## Test Signals
Useful tests should cover option sanitization and dynamic-mutability rules, including atomic flush forcing `min_write_buffer_number_to_merge`, bloom ratio clamping, arena block sizing, `max_compaction_bytes` defaults versus FIFO KV-ratio behavior, restart-only fields, and `SetOptions()` parsing for nested FIFO/universal options and `VerifyOutputFlags`.

Write-path tests should exercise in-place update success/failure/merged-value paths, deterministic WAL replay with callbacks, memtable write-history retention for transactions, memtable checksum protection, prefix-hint behavior with skiplist and concurrent memtable writes, max successive merge enforcement with and without strict reads, and scan-triggered flush/range tombstone conversion.

Compaction tests should cover all compaction styles, dynamic level-byte migrations, TTL/periodic compaction interactions, read-triggered compaction thresholds, output verification flags for local/remote compaction, bottommost file delay, ingest-behind last-level reservation, temperature assignment, and internal-time preservation.

Blob tests should cover value separation thresholds, blob compression options, cache prepopulation, GC age and force thresholds, starting-level extraction, FIFO size decisions using `max_data_files_size`, direct-write restrictions, partition strategy reuse for wide-column entities, crash/reopen behavior, backup/checkpoint/live-file flushing behavior, and missing custom strategy on reopen.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/advanced_options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/attribute_groups.h -->
# sources/storage-engines/rocksdb/include/rocksdb/attribute_groups.h

## Purpose
`attribute_groups.h` defines the public types used to group wide-column attributes across RocksDB column families. The write path uses owning `AttributeGroup` values, the read path uses pinnable `PinnableAttributeGroup` values, and iterator paths use pointer-backed `IteratorAttributeGroup` values to avoid copying wide-column collections while scanning. The file also defines the abstract `AttributeGroupIterator` interface for cross-column-family iteration.

## Important APIs, Types, And Functions
`AttributeGroup` owns a `ColumnFamilyHandle*` and a `WideColumns` collection. It exposes `column_family()`, const and mutable `columns()`, and equality/inequality operators that compare the column-family handle pointer and column contents. `AttributeGroups` is a `std::vector<AttributeGroup>`, with `kNoAttributeGroups` declared as the external empty constant.

`PinnableAttributeGroup` stores a `ColumnFamilyHandle*`, a `Status`, and `PinnableWideColumns`. It exposes accessors for the column family, status, and `WideColumns` view, plus `SetStatus`, `SetColumns(PinnableWideColumns&&)`, and `Reset()`. `Reset()` returns status to `Status::OK()` and resets the pinnable columns. `PinnableAttributeGroups` is a `std::vector<PinnableAttributeGroup>`.

`IteratorAttributeGroup` stores a `ColumnFamilyHandle*` and a `const WideColumns*`. It can be built directly from a handle and pointer, or from an `AttributeGroup`, in which case it points at the original group's columns. Its equality operators compare the handle pointer and dereferenced column contents. `IteratorAttributeGroups` is a `std::vector<IteratorAttributeGroup>`, with `kNoIteratorAttributeGroups` declared externally.

`AttributeGroupIterator` derives from `IteratorBase`, disables copying, has a virtual destructor, and adds one pure virtual method: `const IteratorAttributeGroups& attribute_groups() const`.

## Control Flow
The file is mostly type declarations with inline accessors. Write callers construct `AttributeGroup` objects with a target column-family handle and owned wide columns, then pass vectors through APIs that understand wide-column entities. Read callers construct or receive `PinnableAttributeGroup` objects, fill each group with either a status or moved pinnable columns, and call `Reset()` before reuse.

Iterator control flow is pointer-oriented. `IteratorAttributeGroup` avoids copying `WideColumns` during iteration by retaining a pointer to columns owned elsewhere, usually an `AttributeGroup` or iterator-internal storage. `AttributeGroupIterator::attribute_groups()` returns the current key's grouped columns in comparator order across column families.

## State And Persistence Behavior
These types do not persist data by themselves. They are transient API containers around column-family handles and wide-column data. `AttributeGroup` owns its `WideColumns`; `PinnableAttributeGroup` owns a `PinnableWideColumns` wrapper whose underlying buffers may be pinned to RocksDB-managed memory; `IteratorAttributeGroup` is non-owning and depends on the lifetime of the pointed-to `WideColumns`.

The `ColumnFamilyHandle*` fields are raw pointers and are compared by identity. The file does not manage handle lifetimes, reference counts, or column-family persistence. Any durable behavior comes from the DB write/read/iterator operations that consume or produce these groups.

## Dependencies And Integration Points
The header includes `rocksdb/iterator_base.h` and `rocksdb/wide_columns.h`, and forward-declares `ColumnFamilyHandle`. It depends on `Status`, `WideColumns`, `PinnableWideColumns`, and `IteratorBase` from RocksDB public APIs.

Integration points are wide-column write APIs, entity reads, multi-column-family reads, and cross-column-family iterators. `AttributeGroupIterator` follows the same basic iterator lifecycle as other `IteratorBase` derivatives while exposing grouped wide columns instead of a single value.

## Risks
The main risk is lifetime safety. `IteratorAttributeGroup` dereferences a raw `const WideColumns*`, so producers must ensure the referenced columns outlive the returned iterator groups and remain stable until the next iterator movement or invalidation point. Similarly, `PinnableAttributeGroup::columns()` exposes data whose backing may be pinned and reset, so callers must not retain references after `Reset()` or object reuse.

Handle identity comparisons can surprise code expecting logical column-family equality. Two handles for the same column family would compare unequal if their pointers differ, while a stale/destroyed handle pointer would be unsafe. The header does not guard against null handles or null column pointers.

Because `AttributeGroupIterator` is abstract, implementations must maintain the base iterator status/validity/key ordering contracts in addition to returning attribute groups in comparator order. Returning references to temporary vectors or columns would be a correctness bug.

## Test Signals
Tests should cover equality/inequality for owned and iterator groups, mutation through non-const `AttributeGroup::columns()`, `PinnableAttributeGroup` status/column setting and reset behavior, and empty constants. Iterator tests should verify stable group contents at valid positions, invalidation after movement/reset/destruction, correct cross-column-family ordering, and behavior when a per-group read status is non-OK.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/attribute_groups.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/blob_file_partition_strategy.h -->
# sources/storage-engines/rocksdb/include/rocksdb/blob_file_partition_strategy.h

## Purpose
`blob_file_partition_strategy.h` defines the callback interface used by RocksDB blob direct write to choose a blob-file partition for each value or wide-column entity. It lets applications control partition placement while keeping the caller responsible for mapping the returned value into the configured partition count.

## Important APIs, Types, And Functions
`BlobFilePartitionStrategy` is an abstract base class with a virtual destructor, `Name()`, and two `SelectPartition` overloads. `Name()` returns a debug/logging identifier. The primary overload takes `num_partitions`, `column_family_id`, `key`, and a plain `Slice value`, and returns a `uint32_t` selector. The caller applies modulo `num_partitions`.

The wide-column overload takes `num_partitions`, `column_family_id`, `key`, and `const WideColumns& columns`. The default implementation chooses the default wide column value when present, otherwise the first column value, otherwise an empty `Slice`, then delegates to the plain-value overload. The comments remind derived classes that override only the Slice overload to add `using BlobFilePartitionStrategy::SelectPartition;` so the wide-column overload remains visible.

## Control Flow
The strategy is called on the write hot path for blob direct writes and can be called concurrently from multiple writer threads. For regular Put/Merge-style value separation, RocksDB calls the Slice overload. For `PutEntity()` wide-column separation, RocksDB calls the wide-column overload once per entity before writing any blob-backed columns, then reuses the chosen partition for all blob-backed columns in that entity.

The default wide-column control flow scans columns for `kDefaultWideColumnName`; if not found and the entity is non-empty, it uses `columns.front().value()`. Empty entities pass an empty `Slice` to the Slice overload. No modulo operation is performed by the strategy implementation in this header; the internal caller normalizes the returned selector.

## State And Persistence Behavior
The interface permits implementations to keep internal state, but it warns that any mutation must be synchronized because calls are concurrent. Implementations should avoid I/O, callbacks into RocksDB APIs, blocking operations, and expensive work because they execute on the write path.

The strategy object itself is an application-supplied callback, not a serialized OPTIONS object. As described by `advanced_options.h`, applications relying on custom partitioning must provide the strategy again on every DB open. Persistent blob placement is affected by the returned partition choices, but the strategy's state and code are not persisted by RocksDB.

## Dependencies And Integration Points
The header includes `rocksdb/rocksdb_namespace.h` and `rocksdb/wide_columns.h`, and forward-declares `Slice`. It depends on `WideColumns`, `WideColumn` accessors, `kDefaultWideColumnName`, and `Slice`.

Its primary integration point is `AdvancedColumnFamilyOptions::blob_direct_write_partition_strategy`, used when `enable_blob_direct_write` is enabled. It also integrates with wide-column `PutEntity()` handling by ensuring all blob-backed columns in one entity share a partition.

## Risks
The biggest correctness risks are write-path latency, thread safety, and exception safety. A slow or blocking strategy directly slows writers. Unsynchronized mutable state can race across writer threads. Exceptions must not escape into RocksDB because RocksDB is not exception-safe.

Partition determinism can matter operationally. Changing the strategy between opens or deploying different strategy implementations across processes changes future blob placement and can affect load distribution. Returning arbitrary large values is allowed, but callers must handle modulo correctly and implementations should still consider `num_partitions` to avoid pathological skew.

The wide-column overload has a C++ name-hiding pitfall: a derived class that overrides only the Slice overload without a `using` declaration hides the base overload. That can produce surprising compile-time or dispatch behavior for wide-column calls.

## Test Signals
Tests should verify default wide-column delegation with default column, first-column fallback, and empty-column fallback. Custom strategies should be tested for modulo behavior at the caller, concurrent invocation safety, deterministic placement, no exception propagation, and visibility of both overloads when derived classes override one or both methods. Blob direct write tests should confirm one partition selection per `PutEntity()` and reuse across all blob-backed columns.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/blob_file_partition_strategy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/block_cache_trace_writer.h -->
# sources/storage-engines/rocksdb/include/rocksdb/block_cache_trace_writer.h

## Purpose
`block_cache_trace_writer.h` defines the public tracing records, options, abstract writer interface, and factory for capturing RocksDB block cache accesses. Table readers build `BlockCacheTraceRecord` values for cache lookups and inserts, then pass them to a `BlockCacheTraceWriter` implementation that serializes a trace header and per-access payloads through the generic trace infrastructure.

## Important APIs, Types, And Functions
`BlockCacheTraceRecord` is the central data structure. It records `access_timestamp`, `block_key`, `block_type`, `block_size`, `cf_id`, `cf_name`, `level`, `sst_fd_number`, `caller`, `is_cache_hit`, `no_insert`, `get_id`, `get_from_user_specified_snapshot`, `referenced_key`, `referenced_data_size`, `num_keys_in_block`, and `referenced_key_exist_in_block`. `kReservedGetId` is declared as a static reserved ID. The struct provides a default constructor and a full constructor for populating all fields.

`BlockCacheTraceOptions` controls sampling with `sampling_frequency`, defaulting to one captured request per request. `BlockCacheTraceWriterOptions` configures the built-in writer's `max_trace_file_size`, defaulting to 64 GiB.

`BlockCacheTraceWriter` is an abstract class with virtual destructor, `WriteBlockAccess(const BlockCacheTraceRecord&, const Slice& block_key, const Slice& cf_name, const Slice& referenced_key)`, and `WriteHeader()`. The method takes `Slice` references for string payloads to avoid extra copies.

`NewBlockCacheTraceWriter(SystemClock* clock, const BlockCacheTraceWriterOptions& trace_options, std::unique_ptr<TraceWriter>&& trace_writer)` allocates the built-in implementation that writes block cache trace events to a caller-provided `TraceWriter`.

## Control Flow
Tracing begins when a writer implementation writes a header through `WriteHeader()`, typically when tracing is initiated. During table-reader operations, each block cache lookup or insert produces a `BlockCacheTraceRecord`. The caller passes the record plus slice views of the block key, column-family name, and referenced key to `WriteBlockAccess()`.

Records distinguish lookup/insert context through `no_insert`, cache hit/miss through `is_cache_hit`, and higher-level operation through `TableReaderCaller`. Get and MultiGet details use `get_id`, snapshot flag, referenced key, useful referenced data size, number of keys found in a block, and false-positive indication. Sampling is controlled outside the record by trace options.

The built-in factory wires the block-cache trace writer to the generic trace writer. The comment describes each access as serialized with a timestamp and type followed by payload, and `max_trace_file_size` bounds output size for that implementation.

## State And Persistence Behavior
The header defines trace data, not RocksDB data persistence. Trace output is external diagnostic state written through `TraceWriter`. `BlockCacheTraceRecord` stores strings by value, while `WriteBlockAccess()` also accepts `Slice` views to avoid copying at serialization time; implementations must not retain those slice references beyond the call unless they copy the data.

`access_timestamp` is supplied in the record, and the built-in writer also receives a `SystemClock*`, implying timestamping and header metadata are clock-integrated in the implementation. Trace files may stop or roll/fail according to `max_trace_file_size` behavior implemented elsewhere.

## Dependencies And Integration Points
The header includes `rocksdb/options.h`, `rocksdb/system_clock.h`, `rocksdb/table_reader_caller.h`, `rocksdb/trace_reader_writer.h`, and `rocksdb/trace_record.h`. It depends on `Status`, `Slice`, `SystemClock`, `TraceWriter`, `TraceType`, and `TableReaderCaller`.

Integration points are block-based table readers, block cache lookup/insert code, Get/MultiGet instrumentation, generic trace reader/writer infrastructure, and any tooling that replays or analyzes block cache traces. Column-family and SST metadata fields connect cache events back to LSM placement.

## Risks
Tracing can be high-volume and performance-sensitive. Capturing every access with large keys/names can increase CPU, allocation, and I/O overhead; `sampling_frequency` and `max_trace_file_size` need enforcement by the implementation and trace owner. Missing or inconsistent fields can reduce trace replay fidelity, especially for Get/MultiGet false positives and useful data-size accounting.

The API passes string data both in the record and as slices. Implementations must avoid lifetime bugs by serializing immediately or copying slices. They also need to preserve status errors from the underlying `TraceWriter` so tracing failures do not masquerade as successful capture.

Schema compatibility matters for trace tools. Adding or reinterpreting `TraceType`, `TableReaderCaller`, or record fields can break readers unless versioned through the trace header. `kReservedGetId` must remain distinct from real Get/MultiGet IDs.

## Test Signals
Tests should cover header writing, serialization/deserialization compatibility, default and populated `BlockCacheTraceRecord` fields, lookup versus insert records, hit versus miss records, Get/MultiGet metadata, snapshot flag handling, false-positive blocks, size cap behavior, sampling frequency behavior, propagation of `TraceWriter` errors, and lifetime safety when the passed slices reference temporary buffers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/block_cache_trace_writer.h -->
