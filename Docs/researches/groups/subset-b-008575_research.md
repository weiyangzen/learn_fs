# subset-b-008575 research

## sources/storage-engines/rocksdb/db/compaction/compaction_iterator.cc

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_iterator.cc -->
# sources/storage-engines/rocksdb/db/compaction/compaction_iterator.cc

## Purpose

`compaction_iterator.cc` implements RocksDB's `CompactionIterator`, the forward-only iterator that transforms sorted internal key/value input into the records that should be written by a flush, compaction, or related table-file creation path. It applies compaction semantics across user-key versions: snapshot visibility, range tombstone masking, SingleDelete pairing, merge collapsing, compaction filters, user-defined timestamp history GC, sequence-number zeroing, blob value extraction, and blob garbage collection. It also implements `CompactionBlobResolver`, a lazy wide-column blob resolver used by newer compaction filter APIs.

The file is on a critical correctness path. It decides whether old versions, tombstones, blob references, merge operands, and timed puts are preserved, rewritten, or dropped. Any change can affect point lookup visibility, iterator results, transaction conflict detection, blob-file reachability, or crash-recovery observability.

## Important APIs, types, and functions

`CompactionBlobResolver::Init`, `Reset`, `ResolveColumn`, `IsBlobColumn`, and `NumColumns` provide lazy access to blob-backed columns inside a wide-column entity. `ResolveColumn` can return inline values directly, decode inlined blob values, or fetch blob bytes through `BlobFetcher` and optional `PrefetchBufferCollection`. It updates `CompactionIterationStats` for blob reads and can remember a sticky error for FilterV4 so compaction fails even if a filter notices the error and returns keep.

The two `CompactionIterator` constructors initialize the iterator and create a `RealCompaction` proxy when a real `Compaction` is provided. They wire `SequenceIterWrapper`, comparator, merge helper, snapshot state, range deletion aggregator, blob file builder, compaction filter, shutdown/manual cancellation signals, timestamp history configuration, optional blob fetcher, optional prefetch buffers, and blob GC cutoff state.

`SeekToFirst` starts the scan by calling `NextFromInput` and `PrepareOutput`. `Next` advances through merge-output sub-iterations first, otherwise advances the input iterator as needed, then repeats `NextFromInput` and `PrepareOutput`.

`InvokeFilterIfNeeded` applies `CompactionFilter` to committed value-like records. It handles value, blob index, and wide-column entity inputs; supports stacked BlobDB-specific internal filtering; fetches blob values for integrated BlobDB when required; deserializes wide-column entities; supports lazy FilterV4 blob resolution; translates filter decisions into delete, single delete, changed value, changed blob index, changed wide-column entity, skip-until seek, or failure.

`NextFromInput` is the core compaction state machine. It parses internal keys, tracks current user key and timestamp, checks commit visibility, applies filters, computes snapshot stripes, decides whether to keep/drop SingleDelete, regular deletion, merge, value, timed put, blob index, wide-column entity, or range deletion sentinel records, and propagates shutdown, manual pause, corruption, and input status.

`PrepareOutput` performs final output rewriting: large values become blob indexes, blob indexes may be relocated or inlined by blob GC, wide-column entities may have large columns extracted or blob columns GC'd, and bottommost compactions can zero sequence numbers and user timestamps when safe.

Blob helpers include `ExtractLargeValueIfNeededImpl`, `ExtractLargeValueIfNeeded`, `GarbageCollectBlobIfNeeded`, `ExtractLargeColumnValuesIfNeeded`, `FetchBlobsNeedingGC`, `RelocateBlobValues`, `SerializeEntityAfterGC`, and `GarbageCollectEntityBlobsIfNeeded`. Static helpers compute blob GC cutoff file numbers and construct blob fetch/prefetch resources.

## Control flow

The iterator runs as a loop over an already sorted `InternalIterator`. Each candidate input record is parsed into `ikey_`, with `key_` and `value_` initially pointing at the input. Range-deletion sentinel keys are surfaced immediately. Point keys enter user-key tracking: for a new user key or a new user-defined timestamp bucket, `current_key_` copies the internal key, timestamp state is refreshed, `current_user_key_sequence_` and `current_user_key_snapshot_` reset, and the first committed version may pass through the compaction filter.

The snapshot stripe logic compares the candidate sequence to the configured snapshots, plus optional `SnapshotChecker`, to find the earliest snapshot that can see the candidate. If a newer version for the same user key is visible to the same or a later snapshot stripe, rule A drops the older record as hidden. When a `SnapshotChecker` says a key is not committed at the compaction job snapshot, the iterator keeps it without normal compaction so transaction engines do not lose unresolved writes.

SingleDelete is handled with lookahead because correctness depends on the following point key. The code skips range tombstone sentinels with the same user key, then checks whether the next real key is a matching value-like record in the same snapshot stripe. Depending on timestamp GC eligibility, prior output in the stripe, write-conflict snapshot requirements, bottommost state, and lower-level existence, it can drop both records, keep the SingleDelete, keep the SingleDelete and clear the matching value's payload for a later output, report contract violations, or drop fall-through SingleDeletes that cannot affect future reads.

Deletion markers can be dropped when the compaction proves no lower/higher output-level data can make them visible and they are visible to the earliest snapshot. Bottommost deletions get a special path that skips same-stripe older versions and keeps the deletion only if another version in an older snapshot still needs it. Range tombstones are queried through `CompactionRangeDelAggregator::ShouldDelete` for ordinary point keys and timed puts.

Merge operands are delegated to `MergeHelper::MergeUntil`. The compaction iterator pins input blocks while the merge helper consumes operands, then emits `MergeOutputIterator` records before returning to the main input stream. A `MergeInProgress` status is treated specially so partial merge output can be written before a remaining base record.

Timed put (`kTypeValuePreferredSeqno`) entries can swap in their packed preferred sequence number only when they are visible to the earliest snapshot and no lower-level key can reappear. The code also checks whether swapping would make a range tombstone cover the key; if so it leaves the timed put unchanged.

After `NextFromInput` marks a record valid, `PrepareOutput` performs value representation changes and bottommost sequence zeroing. This separation keeps visibility/drop decisions distinct from output serialization.

## State and persistence behavior

`current_key_` owns the current output key buffer when the input key needs rewriting. `key_` and `value_` are slices into either input data or internal buffers such as `current_key_`, `blob_index_`, `blob_value_`, `compaction_filter_value_`, or `rewritten_entity_`. `at_next_` records lookahead consumption so `Next` does not accidentally skip the already positioned input. `has_current_user_key_`, `current_user_key_`, `current_user_key_sequence_`, and `current_user_key_snapshot_` define the active user-key stripe. `has_outputted_key_`, `clear_and_output_next_key_`, `last_key_seq_zeroed_`, and `current_key_committed_` refine SingleDelete, snapshot, and transaction behavior.

`validity_info_` compactly stores valid/invalid plus a debug context enum, which helps identify why a record was surfaced. `status_` is sticky for hard failures such as corrupt internal keys, missing merge operator, unsupported blob filtering context, blob read errors, compaction filter IO errors, serialization failures, shutdown, or manual compaction pause.

Persistent effects are indirect: the iterator itself does not write table files, but its output controls what table builders persist. It can remove obsolete records, rewrite internal key types, zero sequence numbers, rewrite user timestamps to zero for timestamp GC, emit blob index values, inline relocated blob values, or serialize V2 wide-column entities with blob references. Blob file persistence is delegated to `BlobFileBuilder::Add` and `Finish` outside this file.

Input-entry counting is mediated by `SequenceIterWrapper`. If exact counting is required, seeks are emulated by repeated `Next` calls; otherwise skip-until/filter seeks invalidate exact count availability.

## Dependencies and integration points

The implementation integrates with `InternalIterator`, `InternalKeyComparator`, `ParsedInternalKey`, `MergeHelper`, `CompactionRangeDelAggregator`, `SnapshotChecker`, `Compaction`, `Version`, `VersionStorageInfo`, `BlobFetcher`, `BlobFileBuilder`, `BlobIndex`, `PrefetchBufferCollection`, `WideColumnSerialization`, `WideColumnsHelper`, `CompactionFilter`, `Env`, `SystemClock`, RocksDB logging, and sync points.

The `CompactionProxy` abstraction, declared in the header, lets tests provide only the subset of compaction behavior needed by this iterator. Real production compactions use `RealCompaction` to forward bottommost, level, lower-level existence, blob GC, mmap, readahead, and ingest-behind decisions.

The file supports both integrated BlobDB behavior and stacked BlobDB's older compaction-filter-based GC behavior. It also supports non-compaction table-file creation through `input_version` and `SetBlobFetcher`, which is important for flush or recovery paths that can encounter direct-write wide entities containing blob references.

## Risks and edge cases

Snapshot and transaction semantics are the main risk. Dropping a record too aggressively can make old snapshots incorrect or break write-prepared/write-unprepared conflict checking. The `SnapshotChecker` and `released_snapshots_` behavior is subtle because a released snapshot must not become the earliest visible snapshot for older values.

SingleDelete handling is high risk because it uses lookahead and makes decisions from a combination of matching key type, snapshot stripe, write-conflict snapshot, timestamp GC eligibility, lower-level existence, and configured contract enforcement. The `clear_and_output_next_key_` optimization intentionally emits an empty value after a kept SingleDelete; consumers must preserve that behavior.

Blob and wide-column paths are high risk for lifetime and serialization issues. `value_` can point into several temporary buffers, lazy blob resolution caches fetched values, and `entity_deserialized_` is reused to avoid double deserialization. The code explicitly resets this state at loop boundaries and after filter rewrites to prevent stale entity data from leaking into another record.

Filter APIs can seek the input and can rewrite key types. `RemoveAndSkipUntil` must reject backwards skip targets, and `kChangeBlobIndex`/`kIOError` are restricted to stacked BlobDB internal filters. Lazy FilterV4 resolution intentionally fails compaction if blob fetching failed during inspection.

Timestamp GC only operates when comparator timestamp size and `full_history_ts_low_` are configured consistently. Incorrect timestamp comparison can collapse or preserve too much history, especially with range tombstones and bottommost sequence zeroing.

## Test signals

`compaction_iterator_test.cc` exercises the main state machine: empty outputs, corrupt keys, SingleDelete with values, range deletion, filter skip-until seeks, shutdown during filter and merge, merge output, bottommost deletion removal, sequence zeroing, timed put preferred sequence swaps, snapshot checker behavior, ingest-behind behavior, user timestamp GC, wide-column blob extraction, wide-column blob reference preservation, lazy resolver null-fetcher behavior, and deserialization cache reset after filtered entities.

Additional integration signals are noted in comments for real blob GC with `Version`, especially wide-column entity blob GC coverage in broader DB tests. The tests emphasize expected output key/value sequences and iterator call logs, which is appropriate because much of this file's correctness is observable as exact output ordering and exact input advancement behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_iterator.cc -->

## sources/storage-engines/rocksdb/db/compaction/compaction_iterator.h

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_iterator.h -->
# sources/storage-engines/rocksdb/db/compaction/compaction_iterator.h

## Purpose

`compaction_iterator.h` declares the public and private contract for RocksDB's compaction output iterator. It defines the narrow API used by compaction/table-building code, the small `CompactionProxy` abstraction that decouples iterator logic from full `Compaction`, the `SequenceIterWrapper` used to count scanned input entries, and the `CompactionBlobResolver` used by wide-column compaction filters.

The header is a map of the iterator's responsibilities. It shows that compaction iteration is not simply deduplication; it coordinates snapshots, transaction commit visibility, range deletions, merge helpers, compaction filters, user-defined timestamps, blob extraction, blob relocation, wide-column entity serialization, input scan accounting, and shutdown/manual pause handling.

## Important APIs, types, and fields

`CompactionBlobResolver` derives from `WideColumnBlobResolver`. It exposes `Init`, `Reset`, `ResolveColumn`, `IsBlobColumn`, `NumColumns`, and `resolve_status`. It stores the current user key, column vector, blob-column side list, blob fetcher, prefetch buffers, iteration stats, a small resolved-value cache, and optional sticky error state.

`SequenceIterWrapper` derives from `InternalIterator` and wraps another internal iterator without owning it. It increments `num_itered_` on `Next` except for delete-range sentinel keys. Its `Seek` either delegates directly and marks counts unreliable, or simulates seek with repeated `Next` when exact counting is required. `HasNumItered` and `NumItered` expose count validity and value.

`CompactionIterator::CompactionProxy` is the reduced compaction interface needed by the iterator: level, bottommost status, number of levels, lower-level key existence checks, largest user key, ingest-behind, mmap reads, blob GC options, blob readahead, input version, blob-file reference checks, access to the real compaction, and per-key placement support. `RealCompaction` implements this by forwarding to `Compaction`.

The public `CompactionIterator` API consists of two constructors, destructor, `ResetRecordCounts`, `SetBlobFetcher`, `SeekToFirst`, `Next`, accessors for `key`, `value`, `status`, `ikey`, `Valid`, `user_key`, `iter_stats`, input-entry scan state, `InputStatus`, and `IsDeleteRangeSentinelKey`.

Important private methods are `NextFromInput`, `PrepareOutput`, blob extraction/GC helpers, `InvokeFilterIfNeeded`, `findEarliestVisibleSnapshot`, `KeyCommitted`, snapshot helper predicates, timestamp update, and blob fetcher/prefetch factory helpers.

`ValidContext` records why a candidate output is valid, including merge paths, parse error, uncommitted key, SingleDelete cases, timestamp-history keep, deletion keep, new user key, range deletion, and preferred-sequence swap. `ValidityInfo` stores valid bit plus context in a byte.

## Control flow represented by the declarations

Callers create `CompactionIterator` with an already positioned or positionable input iterator, comparator, merge helper, snapshot vector, range tombstone aggregator, and optional compaction/filter/blob dependencies. `SeekToFirst` begins producing output. Each `Next` either drains pending merge output or advances the wrapped input, then calls into the private input-processing and output-preparation stages.

The header's private method split indicates the major phases. `NextFromInput` decides which input record becomes a logical output and which records are skipped. `PrepareOutput` performs final rewrites on that logical output. Filter invocation is separated from both so the iterator can apply filters only to the first committed version of a user key or merge-helper-managed operands.

The blob helper API shows a two-family design: ordinary value/blob-index records use `ExtractLargeValueIfNeeded` and `GarbageCollectBlobIfNeeded`; wide-column entities use `ExtractLargeColumnValuesIfNeeded` and `GarbageCollectEntityBlobsIfNeeded`, with helper methods for fetching, relocating, and serializing only the relevant blob-backed columns.

## State and persistence behavior

The iterator holds several classes of state. Input and dependencies include `input_`, `cmp_`, `merge_helper_`, `snapshots_`, `snapshot_checker_`, `range_del_agg_`, `blob_file_builder_`, `compaction_`, `compaction_filter_`, `shutting_down_`, `manual_compaction_canceled_`, and timestamp-history settings.

Visibility state includes `earliest_write_conflict_snapshot_`, `job_snapshot_`, `earliest_snapshot_`, `visible_at_tip_`, `released_snapshots_`, `current_key_committed_`, `current_user_key_sequence_`, and `current_user_key_snapshot_`. These fields preserve transaction and snapshot correctness across multiple versions of the same user key.

Output lifetime state includes `key_`, `value_`, `ikey_`, `current_key_`, `current_user_key_`, `curr_ts_`, `status_`, `validity_info_`, `has_current_user_key_`, `at_next_`, `has_outputted_key_`, `clear_and_output_next_key_`, and `last_key_seq_zeroed_`. These fields let the iterator point to input memory when safe and use owned buffers when rewriting internal keys or values.

Blob and wide-column state includes `blob_garbage_collection_cutoff_file_number_`, `blob_fetcher_`, `prefetch_buffers_`, `blob_index_`, `blob_value_`, `compaction_filter_value_`, `rewritten_entity_`, `entity_columns_`, `entity_blob_columns_`, `entity_wide_columns_`, `filter_existing_columns_`, `blob_resolver_`, and `entity_deserialized_`. These fields reduce allocations and preserve slice lifetimes during filter, extraction, and GC work.

The iterator itself does not persist files, but the state declared here determines what downstream table builders and blob builders persist. It can surface rewritten keys and values, expose blob index values created by `BlobFileBuilder`, and update `CompactionIterationStats` for records dropped, bytes read, blobs relocated, and filter time.

## Dependencies and integration points

This header depends on RocksDB internals including blob index/build/fetch abstractions, compaction metadata, compaction iteration stats, merge helper, pinned iterator manager, range deletion aggregator, snapshot checker, column-family options, compaction filter API, and `Slice`. It forward-declares blob/cache/version/prefetch types where possible to keep compile dependencies lower.

The public constructor signatures are integration-heavy. They are used by real compaction code and also by flush/recovery-style paths that may not have a `Compaction` but still need blob resolution through `input_version` or `SetBlobFetcher`. The custom `CompactionProxy` constructor is explicitly for tests and allows targeted validation without constructing full RocksDB version/compaction state.

`CompactionIterator` also integrates with merge operators through `MergeHelper`, with `CompactionFilter` versions through filter support flags and resolver callbacks, with manual compaction cancellation through an atomic flag, and with input scan accounting through `SequenceIterWrapper`.

## Risks and edge cases

The constructor surface is broad, and many arguments are raw pointers whose lifetime must outlive the iterator: input iterator, comparator, merge helper, snapshots vector, environment, range deletion aggregator, blob file builder, compaction filter, shutdown flag, timestamp lower bound, and optional input version. Mismanaged lifetimes would cause slice or pointer invalidation.

`SequenceIterWrapper` count accuracy depends on whether `Seek` was used and whether exact counting was requested. Consumers must call `HasNumInputEntryScanned` before trusting `NumInputEntryScanned` unless `must_count_input_entries` was true.

Many state fields are reused across records for performance. The header makes clear that `entity_deserialized_`, wide-column buffers, blob resolver cache, `compaction_filter_value_`, and `rewritten_entity_` require careful reset discipline in the implementation.

Snapshot correctness depends on sorted `snapshots_`, valid `earliest_snapshot_`, `preserve_seqno_min`, and compatible `SnapshotChecker`. Debug assertions check some invariants, but production correctness still depends on callers providing coherent compaction context.

Blob GC factory helpers depend on `Version` and `VersionStorageInfo` when compaction enables blob GC. Test proxies that report blob GC without a real version would violate implementation assertions.

## Test signals

The companion test file constructs `CompactionIterator` through the proxy constructor, validating that the reduced `CompactionProxy` interface is sufficient for bottommost, ingest-behind, lower-level existence, and blob-reference scenarios. Tests also exercise `SequenceIterWrapper` indirectly by checking logged input `Next` and `Seek` calls for compaction filter skip-until behavior.

`CompactionBlobResolver` has explicit tests for null fetcher behavior, blob-column detection, non-blob column resolution, and multi-column resolution failure. Wide-column tests validate the `entity_deserialized_` optimization and reset behavior implied by the header's reusable state fields.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_iterator.h -->

## sources/storage-engines/rocksdb/db/compaction/compaction_iterator_test.cc

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_iterator_test.cc -->
# sources/storage-engines/rocksdb/db/compaction/compaction_iterator_test.cc

## Purpose

`compaction_iterator_test.cc` is the focused unit-test suite for `CompactionIterator` and `CompactionBlobResolver`. It builds synthetic internal-key streams and verifies the exact compaction output for point keys, range tombstones, merges, SingleDelete, snapshot checker behavior, timed puts, user-defined timestamp GC, ingest-behind, compaction filters, wide-column blob extraction, and wide-column blob-reference handling.

The tests are important because `CompactionIterator` is a dense state machine with many cross-cutting conditions. Most tests assert precise output keys and values, which directly captures whether compaction would persist the right table records.

## Important fixtures, helpers, and test doubles

`ValueWithPreferredSeqno` packs a preferred sequence number into a timed-put value. It supports tests for `kTypeValuePreferredSeqno` and preferred sequence swapping.

`NoMergingMergeOp` fails if merge methods are invoked, useful when tests expect merge operands to pass through without actual merging. `SingleMergeOp` verifies partial and full merge paths and supports single operand merging. Several tests use built-in string append merge operators.

`StallingFilter` is a compaction filter that busy-waits on selected keys and always returns remove. It is used to verify shutdown during filter and merge processing. `FilterAllKeysCompactionFilter` returns remove for every filterable key. Later wide-column tests define `KeepAllCompactionFilter` with FilterV4 support and `DropKeyKeepRestCompactionFilter`.

`LoggingForwardVectorIterator` extends `VectorIterator` and records `SeekToFirst`, `Seek`, and `Next`. The skip-until test uses this to verify that compaction filter decisions cause the intended seeks and do not scan extra keys.

`FakeCompaction` implements `CompactionIterator::CompactionProxy` for ordinary tests. It exposes toggles for bottommost level, ingest-behind, lower-level key absence, and per-key placement support. `FakeCompactionWithBlobGC` supports the subset needed by wide-column blob tests while intentionally disabling real blob GC because it has no `Version`.

`TestSnapshotChecker` maps snapshot sequence numbers to last visible sequence numbers and implements `CheckInSnapshot`. This allows tests to model uncommitted data and released/limited visibility without a full transaction DB.

`CompactionIteratorTest` owns the common setup: comparator, internal comparator, snapshots, merge helper, logging iterator, compaction range deletion aggregator, optional snapshot checker, shutdown flag, and `CompactionIterator`. `InitIterators` assembles range tombstone iterators, optional fake compaction, merge helper, input iterator, and the compaction iterator under test. `RunTest` consumes the iterator and compares output sequences.

Specialized fixtures include `CompactionIteratorWithSnapshotCheckerTest`, `CompactionIteratorWithAllowIngestBehindTest`, `CompactionIteratorTsGcTest`, `WideColumnEntityBlobExtractionTest`, and `WideColumnEntityBlobGCTest`.

## Coverage and control flow

The initial parameterized tests cover baseline behavior with and without a snapshot checker. `EmptyResult` verifies SingleDelete plus matching value can compact to no output. `CorruptionAfterSingleDeletion` ensures a corrupt internal key after SingleDelete fails compaction. Timed put compatibility tests show timed puts act like puts for SingleDelete and range deletion in relevant paths.

Range deletion tests create fragmented range tombstone state through `CompactionRangeDelAggregator` and verify covered point keys are dropped while uncovered keys remain. `CompactionFilterSkipUntil` provides a detailed mixed stream of values, merges, timed puts, and skip targets, then checks both output records and the exact underlying iterator actions.

Shutdown tests start compaction in another thread with a stalling filter, set the shutdown flag while the filter is running, and verify the iterator exits with `ShutdownInProgress` and no further filter calls. These tests exercise best-effort cancellation while inside filter and merge helper paths.

Merge tests cover single merge operands, multi-operand partial merges, full merge with a base value, and timed puts losing preferred sequence data when merged into a normal put. Bottommost tests verify sequence-number zeroing, deletion removal, SingleDelete removal, and merge-to-put conversion at the last level.

Snapshot-checker tests verify uncommitted keys are preserved as-is, committed older keys compact normally, and same-snapshot duplicate records are deduplicated for values, timed puts, deletions, merges, SingleDelete, and blob indexes. They also cover cases where bottommost sequence zeroing or deletion removal must not occur because the key is not visible to the earliest snapshot or because an older snapshot still needs a value.

SingleDelete write-conflict tests ensure SingleDeletes can be kept for conflict checking and that the matched value/blob/entity/timed-put record is emitted as `kTypeValue` with an empty payload when the optimization is used. Ingest-behind tests verify a compaction that is nominally bottommost does not assume there will never be future lower-level data.

Timed-put preferred sequence tests verify the conditions for swapping the preferred sequence number: visibility to earliest snapshot, no lower-level entries, and no range tombstone resurfacing after the swap. They cover no-swap and swap cases, including bottommost zeroing.

User-defined timestamp GC tests run with `BytewiseComparatorWithU64TsWrapper`. They validate no-GC when history threshold is absent or keys are newer than the threshold, dropping tombstones and old versions when eligible, merge behavior across timestamp thresholds, rewriting timestamp and sequence to zero at bottommost, and SingleDelete timestamp GC behavior.

Wide-column blob extraction tests create serialized entities, run compaction with `BlobFileBuilder`, and assert large columns are replaced by blob references while smaller columns remain inline. They cover one column, multiple columns, below-threshold no extraction, mixed sizes, and default column extraction.

Wide-column blob-reference tests create V2 entities with blob indices and verify the iterator preserves structure and blob metadata when real GC is not enabled. They also test `CompactionBlobResolver` without a fetcher, the deserialization skip optimization when FilterV4 kept an already-deserialized entity, and reset of `entity_deserialized_` after a filter drops one blob-backed entity before processing the next.

## State and persistence behavior under test

The suite verifies output-state transitions by checking internal key type, sequence number, timestamp, and value bytes. It covers records becoming deletions after filtering, blob or wide-column records becoming empty values in SingleDelete optimization, timed puts becoming regular values after preferred sequence swap or merge, and bottommost keys becoming sequence zero.

The blob extraction fixture uses `MockEnv`, `BlobFileBuilder`, mutable/immutable CF options, and blob file addition vectors. Tests assert blob file additions when extraction should write blob files, and no additions when values are below the threshold.

The wide-column blob GC fixture uses serialized V2 entities with explicit `BlobIndex` metadata. Because it lacks a real `Version`, it does not enable full integrated blob GC; instead it verifies that current iterator deserialization and serialization paths preserve blob references and do not corrupt entity layout.

Sync point callbacks count whether `PrepareOutput` deserializes a wide-column entity or skips because `InvokeFilterIfNeeded` already did it. This provides a regression signal for both performance and stale-state correctness.

## Dependencies and integration points

The tests depend on RocksDB test harness utilities, `VectorIterator`, internal key formatting helpers, `CompactionRangeDelAggregator`, range tombstone iterators, merge operators, mock environment/file system support, blob file builder/addition classes, blob index encoding/decoding, wide-column serialization, sync points, and port threading utilities.

The suite integrates directly with the custom `CompactionProxy` constructor rather than full compaction jobs for most cases. This keeps tests small and targeted but means some production-only integration points, notably real `Version`-based blob GC cutoff computation and real blob fetches from storage, are covered elsewhere.

## Risks and gaps

The tests are comprehensive for deterministic iterator output, but most use synthetic in-memory iterators and fake compaction proxies. Full production interactions with table builders, actual `VersionStorageInfo`, blob file cache, mmap reads, prefetch buffers, and real compaction scheduling are not exercised here.

`FakeCompactionWithBlobGC` explicitly disables integrated blob GC because no real `Version` is available. The wide-column blob GC helper accepts a GC cutoff parameter but does not use it, so these tests are preservation and serialization tests, not full relocation tests. Comments point to broader DB tests for real blob GC coverage.

Threaded shutdown tests use busy-waiting filters, which are effective for deterministic unit testing but can be sensitive to scheduling if reused in slower environments. They do, however, assert the key property that no additional filter calls happen after shutdown is observed.

The timestamp GC tests cover many conditions, but correctness still depends on comparator timestamp extraction and ordering contracts outside this file. Any comparator changes would need broader tests.

## Test signals

Strong signals include exact output key/value assertions in `RunTest`, exact input iterator action logs in `CompactionFilterSkipUntil`, status assertions for corruption and shutdown, blob file addition counts, decoded `BlobIndex` size/file/offset checks, wide-column deserialization checks, and sync-point counters for deserialization caching.

The file's `main` installs the RocksDB stack trace handler and runs all GoogleTests, so the suite is directly executable as a normal RocksDB unit-test binary.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_iterator_test.cc -->
