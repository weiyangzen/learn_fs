# subset-b-008598 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_io_failure_test.cc -->
# sources/storage-engines/rocksdb/db/db_io_failure_test.cc

## Purpose

This file is a GoogleTest suite for RocksDB database behavior under injected file-system and I/O failures. It exercises two broad classes of behavior: write-side failures from `SpecialEnv` flags and `SyncPoint` callbacks, and read-side corruption/retry behavior through a custom `FileSystemWrapper`. The tests are regression-oriented: they verify that failed flushes/compactions/manifest writes do not lose committed data, that paranoid mode blocks later writes after serious background failures, and that corruption retry counters are updated only when `verify_and_reconstruct_read` support is advertised.

## Important APIs, types, and functions

`CorruptionFS` wraps a target `FileSystem` and injects corruption into reads. It overrides `NewRandomAccessFile`, `NewSequentialFile`, `NewWritableFile`, and `SupportedOps`. It tracks a corruption trigger count, the corrupted filename and byte range, and a deterministic `Random` generator. `SetCorruptionTrigger()` resets the read counter and arms the next corruption. `MaybeResetOverlapWithCorruptedChunk()` clears the corrupted file marker when a verification/reconstruction read overlaps the corrupted byte range. `VerifyRetry()` confirms a corruption was injected and later repaired by a retry path.

`CorruptionRandomAccessFile` and `CorruptionSequentialFile` are nested wrappers that corrupt successful reads unless `IOOptions::verify_and_reconstruct_read` is set. The random-access wrapper also implements `MultiRead()` with two allocation modes: normal caller scratch buffers and an `FSAllocationPtr`-backed buffer path when the wrapped FS advertises `kFSBuffer`.

`DBIOFailureTest` derives from `DBTestBase` and uses `SpecialEnv` through `env_` to inject drop writes, no space, non-writable filesystem, log, manifest, sync, range sync, and close errors.

`DBIOCorruptionTest` derives from `DBIOFailureTest` and parameterizes three booleans: use FS-provided buffer, use async read options, and advertise retry support through `kVerifyAndReconstructRead`. Its constructor installs `CorruptionFS` in a composite Env, configures statistics, disables auto compactions, and uses a block-based table factory.

## Control flow and scenarios

The early `DBIOFailureTest` cases drive normal writes and flushes to create durable data, then enable an injected failure and assert the DB's returned status, background error counters, write availability, and post-reopen data visibility. `DropWrites` loops over compaction option variants, forces dropped writes during compaction, expects background errors to accumulate, then ensures file count growth remains bounded and compaction sleeps occurred. `DropWritesFlush` checks flush failure increments `rocksdb.background-errors`. `NoSpaceCompactRange` verifies `CompactRange` propagates an `IOError` with `NoSpace`.

`ManifestWriteError` covers a subtle persistence failure: a compaction output may be written to the MANIFEST but fail sync, or the manifest write itself may fail. The test checks data remains readable, paranoid mode blocks writes, reopening with paranoid disabled can recover, and subsequent writes work when safe.

`PutFailsParanoid` verifies that WAL write errors poison future writes only when `paranoid_checks` is true.

The `#if !(defined NDEBUG) || !defined(OS_WIN)` block uses `SyncPoint` callbacks on `SpecialEnv::SStableFile::{RangeSync,Close,Sync}` for both flush and compaction paths. Each test injects an error on the first callback, waits for flush or compaction, asserts the exact error message, confirms later writes are rejected in paranoid mode, and reopens to verify committed data survived.

The parameterized corruption tests inject read corruption at different layers. `GetReadCorruptionRetry`, `IterReadCorruptionRetry`, `MultiGetReadCorruptionRetry`, `CompactionReadCorruptionRetry`, `FlushReadCorruptionRetry`, `ManifestCorruptionRetry`, `FooterReadCorruptionRetry`, `TablePropertiesCorruptionRetry`, and `DBOpenReadCorruptionRetry` compare retry-enabled and retry-disabled behavior through status checks plus `FILE_READ_CORRUPTION_RETRY_COUNT` and `FILE_READ_CORRUPTION_RETRY_SUCCESS_COUNT` tickers.

## State and persistence behavior

The tests intentionally move data through memtable, SST, manifest, reopen, and compaction states. They validate that failures during output file close/sync/range sync do not publish partial SST state as durable truth. Manifest failure tests protect the VersionSet contract that reopened DB state must not point to a deleted or unpublished compaction output. Corruption retry tests validate that the read path can reconstruct a corrupted read without mutating logical DB contents.

`CorruptionFS` state is protected by `port::Mutex`. Its destructor asserts that armed corruption was either reset or triggered into a non-empty corrupted chunk, helping catch tests that forget to exercise the injected condition. Global `SyncPoint` callbacks mutate process-wide state, so tests disable processing after each injection; footer and table properties tests also clear callbacks.

## Dependencies and integration points

The suite depends on `DBTestBase`, `SpecialEnv`, `SyncPoint`, `BlockBasedTableFactory`, `NewBloomFilterPolicy`, `test::NewSpecialSkipListFactory`, RocksDB `Statistics`, and Env/FileSystem abstractions. It integrates with the DB background error machinery, flush and compaction scheduling, MANIFEST recovery, table reader checksum paths, `MultiGet`, iterator scans, file footer/property reads, and file-system capability advertisement through `SupportedOps`.

## Risks and edge cases

The custom FS corrupts buffers returned by read calls; this is appropriate for tests but is sensitive to aliasing and buffer ownership, especially in the `MultiRead()` FS-buffer path. Tests using `SyncPoint` are global-state sensitive and must always disable or clear callbacks to avoid cross-test interference. Some assertions are platform/configuration gated because debug and Windows behavior differ. `GetReadCorruptionRetry` sets `ro.async_io` but calls `Get(ReadOptions(), ...)`, so that test does not actually exercise its async parameter in the same way as the iterator, compaction, and `MultiGet` tests. The corruption retry matrix still covers async elsewhere.

## Test signals

The file is itself the test signal for DB I/O failure handling. It asserts exact status classes (`IOError`, `Corruption`, `NoSpace`), background-error properties, retry ticker counts, data survival after reopen, and write blocking under paranoid checks. The parameter matrix combines FS buffer support, async I/O, and verify/reconstruct support to make sure corruption recovery is conditional on advertised capability rather than always attempted.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_io_failure_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_iter.cc -->
# sources/storage-engines/rocksdb/db/db_iter.cc

## Purpose

`db_iter.cc` implements `DBIter`, the user-facing RocksDB iterator that converts an ordered stream of internal keys into visible user keys at a snapshot/read sequence. It hides overwritten versions, tombstones, invisible sequence numbers, and timestamp-filtered records; resolves merge operands; optionally fetches blob values; materializes wide-column entities; handles forward/reverse scans and direction changes; records iterator statistics; and coordinates newer read-path optimizations such as contiguous point-tombstone conversion into memtable range tombstones.

## Important APIs, types, and functions

`DBIter::DBIter` wires together `ReadOptions`, immutable/mutable CF options, the wrapped `InternalIterator`, optional `Version`, `ReadCallback`, active memtable, DB tracing, blob state, timestamp bounds, prefix behavior, and flush/range-tombstone thresholds. `HasFullTimestampVisibility()` gates read-path range tombstone conversion so it is only enabled when timestamp filtering cannot hide interior live keys.

Navigation is implemented by `Seek`, `SeekForPrev`, `SeekToFirst`, `SeekToLast`, `Next`, `Prev`, `FindNextUserEntryInternal`, `PrevInternal`, `ReverseToForward`, `ReverseToBackward`, `FindValueForCurrentKey`, `FindValueForCurrentKeyUsingSeek`, and `FindUserKeyBeforeSavedKey`.

Value handling is split across `PrepareValueInternal`, `SetValueAndColumnsFromPlain`, `SetValueAndColumnsFromBlob`, `SetValueAndColumnsFromBlobImpl`, `SetValueAndColumnsFromEntity`, `MaterializeLazyEntityColumns`, `PrepareValue`, `MergeValuesNewToOld`, `MergeWithNoBaseValue`, `MergeWithPlainBaseValue`, `MergeWithBlobBaseValue`, `MergeWithWideColumnBaseValue`, and `SetValueAndColumnsFromMergeResult`.

Range and skip accounting is handled by `TrackContiguousTombstone`, `FlushPendingTombstoneRun`, `MaybeInsertRangeTombstone`, `TooManyInternalKeysSkipped`, `IsVisible`, `SetSavedKeyToSeekTarget`, `SetSavedKeyToSeekForPrevTarget`, and the `Prepare`/`ValidateScanOptions`/`SetScanOptionsForPrepare` multi-scan path.

## Control flow

Forward iteration starts with a seek target encoded as an internal key using the read sequence and `kValueTypeForSeek`. `FindNextUserEntryInternal()` loops over internal records until it finds a visible user entry. It skips newer sequence numbers, timestamp-filtered versions, duplicate versions of the saved user key, and records hidden by visible deletions. For values it prepares the underlying iterator value, flushes any pending tombstone run, saves the user key, and populates plain/blob/wide-column state. For merge records it enters `MergeValuesNewToOld()`, accumulating operands from newest to oldest until it reaches a deletion, base value, blob base, wide-column base, or key boundary.

Reverse iteration keeps a different invariant: the internal iterator is positioned before the exposed user key. `Prev()` converts from forward state through `ReverseToBackward()` when needed, then `PrevInternal()` scans lower keys. `FindValueForCurrentKey()` walks versions for the current user key from old-to-new iterator position, keeps only visible versions, requires pinned values for reverse presentation, tracks deletion vs value vs merge base type, and may switch to `FindValueForCurrentKeyUsingSeek()` when too many versions make linear reverse scanning expensive.

Direction changes are explicit. `ReverseToForward()` seeks or advances until the internal iterator is at or after the current saved key. `ReverseToBackward()` seeks around a merged current entry if necessary and then calls `FindUserKeyBeforeSavedKey()` to restore the reverse invariant.

Seek methods reset temporary pinned data, blob state, value/column state, skipped-key counters, tombstone tracking, and prefix state. They record trace events, enforce lower/upper bounds, optionally extract a prefix for prefix-same-as-start or tombstone conversion, then delegate to the forward or reverse finder.

## State and persistence behavior

Most state is per-iterator and transient: `saved_key_`, `ikey_`, `saved_write_unix_time_`, merge operands, pinned iterator manager, value/blob state, timestamp bounds, scan range index, direction, and validity. Statistics are buffered in `LocalStatistics` in the header and flushed to global tickers in the destructor.

There is one important read-path mutation: when configured and safe, contiguous visible point tombstones observed during reads can be inserted into the active memtable as logically redundant range tombstones. `MaybeInsertRangeTombstone()` refuses insertion if the run is below threshold, no active memtable exists, the iterator snapshot predates the memtable, prepared/uncommitted writes could be shadowed, or an existing range tombstone already covers the span. It inserts at the read sequence under the CF ingest-SST lock and records inserted/discarded tickers.

The iterator can also mark the active memtable for flush when too many hidden active-memtable operations are scanned, either per operation or averaged since the last seek. This is another read-side feedback path into storage state.

## Dependencies and integration points

`DBIter` integrates with `InternalIterator`, `IteratorWrapper`, `Version::GetBlob`, `BlobFilePartitionManager`, `BlobFetcher`, `WideColumnSerialization`, `ReadPathBlobResolver`, `MergeHelper`, `MergeContext`, `ReadCallback`, `ReadOnlyMemTable`, `ColumnFamilyData`, `DBImpl` tracing, `IODispatcher`, `PinnedIteratorsManager`, `ThreadStatusUtil`, `PerfContext`, `Statistics`, user comparators with timestamp support, and range tombstone iterators.

External callers reach this implementation through `DBIter::NewIter` declared in `db_iter.h`, normally via DB read APIs constructing iterators over memtables and SSTs.

## Risks and edge cases

Correctness depends on strict internal-iterator ordering by user key, sequence, and value type. The code has many direction-specific invariants, especially around merged entries and reverse iteration requiring pinned values. Timestamp range mode changes key skipping and can expose multiple versions of a user key, so comparisons switch between timestamp-aware and timestamp-stripped forms. Lazy blob and entity paths must preserve backing storage when the underlying iterator moves; the implementation copies serialized entities before lazy deserialization to avoid dangling slices and self-aliased string assignment.

Range tombstone conversion is deliberately conservative because a table filter, prefix bloom behavior, timestamp filtering, old snapshots, or uncommitted writes can make a read-observed deletion run unsafe to convert. `max_skippable_internal_keys` can terminate scans with `Incomplete`, so callers must treat status as part of iterator validity. Multi-scan preparation requires exact seek order and matching upper bounds; misuse returns `InvalidArgument`.

## Test signals

This implementation is directly stressed by `db_iter_stress_test.cc`, which compares random DBIter operations against a reference iterator under injected internal-iterator errors and mutations. Broader RocksDB iterator tests cover timestamps, bounds, merges, blobs, wide columns, prefix scans, and pinning. The implementation itself records many perf and ticker signals: DB seek/next/prev counts, bytes read, internal skips, merge counts, reseeks, read-path range tombstone insert/discard counts, and corruption/incomplete statuses.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_iter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_iter.h -->
# sources/storage-engines/rocksdb/db/db_iter.h

## Purpose

`db_iter.h` declares and largely defines the public/private shape of `DBIter`, RocksDB's adapter from an `InternalIterator` over `(user key, sequence, value type)` records to the public `Iterator` interface over visible user entries. The header documents the iterator's core contract: at a given sequence number, expose the newest live value for each user key while accounting for tombstones, merges, blob indexes, wide columns, timestamps, bounds, and prefix scan constraints.

## Important APIs, types, and members

`DBIter::NewIter()` is the allocation/factory entry point. It accepts environment, read options, immutable and mutable CF options, comparator, wrapped internal iterator, version, sequence, optional read callback, active memtable, optional column-family handle, blob-index exposure flag, optional arena, and optional DB/CF data. It can allocate from an arena and derives `DBImpl`/`ColumnFamilyData` from `ColumnFamilyHandleImpl` when provided.

Public `Iterator` methods include `Valid`, `key`, `value`, `columns`, `status`, `timestamp`, `GetProperty`, `Next`, `Prev`, `Seek`, `SeekForPrev`, `SeekToFirst`, `SeekToLast`, `PrepareValue`, and `Prepare`. `set_sequence`, `set_valid`, and `set_status` are testing/internal adjustment hooks.

`Direction` captures the positioning invariant: forward mode usually points at the current entry or just after merge contributors, while reverse mode positions the internal iterator before all entries for the exposed key.

`LocalStatistics` batches iterator tickers locally and flushes them in the destructor to avoid per-step atomic-counter overhead.

`BlobReader`/`BlobState` centralize blob value retrieval, lazy blob-index exposure, and direct-write fallback through a blob file cache. `ValueColumnsState` owns the default value slice, materialized wide columns, saved serialized value buffer, lazy entity column vectors, lazy blob-column indexes, resolver, and mutex used to materialize V2 wide-column entities with blob columns.

Private helpers declare all major state-machine operations: direction transitions, seek target encoding, forward/reverse user-entry discovery, merge resolution, visibility checks, value/blob/entity population, tombstone-run tracking, prefix checks, scan preparation, and memtable flush marking.

## Control flow encoded by the declarations

The header separates public movement from internal state machines. Public movement methods reset per-operation state and call helpers. `FindNextUserEntry` drives forward scans. `PrevInternal`, `FindValueForCurrentKey`, and `FindUserKeyBeforeSavedKey` drive reverse scans. `ReverseToForward` and `ReverseToBackward` repair underlying iterator position when callers switch directions.

Value exposure is layered. Plain values set both the default value and a single default wide column. Blob indexes either become the exposed value for legacy BlobDB, stay lazy when `allow_unprepared_value` is true, or are fetched immediately. Wide-column entities deserialize into materialized columns or lazy entity metadata and then resolve blob columns before a valid iterator position is published. Merge helpers normalize no-base, plain-base, blob-base, and wide-column-base cases into a final value or wide-column entity.

## State and persistence behavior

The header makes clear that `DBIter` is mostly transient read state, but it can feed back into mutable DB state. `active_mem_`, memtable sequence lower bound, per-op and average scan-flush triggers, contiguous tombstone counters, range tombstone keys, and ingest-SST lock support read-path flush marking and logically redundant range tombstone insertion. The destructor releases pinned data, deletes the wrapped iterator according to arena mode, records deleted-iterator ticks, resets skipped-key accounting, and flushes local statistics.

Pinning state is explicit. `TempPinData`, `ReleaseTempPinnedData`, `pin_thru_lifetime_`, and `PinnedIteratorsManager` allow short-lived or iterator-lifetime block pinning depending on read options. `DirtyTracked<BlobState>` and `DirtyTracked<ValueColumnsState>` track whether cleanup or reset-sensitive nested state has been mutated.

Timestamp state is also explicit: upper and lower timestamp pointers, timestamp size, saved reverse timestamp, and comparison helpers determine whether keys are compared with or without timestamps. When a lower timestamp bound is active, skip comparisons preserve timestamp distinctions so multiple versions of a user key can be returned.

## Dependencies and integration points

The header includes RocksDB DB, iterator, wide-column, blob, arena, CF options, DB implementation, table iterator wrapper, and dirty-tracking dependencies. It forward-declares `BlobFileCache`, `Version`, and `port::RWMutex`. It is included by `db_iter.cc` and by tests such as `db_iter_stress_test.cc`, and it is part of the DB read path construction pipeline.

`DBIter` sits between storage-specific internal iterators and the public `rocksdb::Iterator` API. It integrates with column families, snapshots/read callbacks, user comparators, prefix extractors, merge operators, blob storage, wide columns, DB tracing, statistics, and active memtable maintenance.

## Risks and edge cases

Because many methods expose slices into saved buffers, pinned blocks, or deserialized entity vectors, lifetime and reset order are critical. Reverse iteration is only supported when underlying values can be pinned for the cases that need to carry a value while moving the internal iterator. The arena allocation path requires destructor behavior to delete the wrapped iterator without assuming ordinary heap ownership of `DBIter` itself. Prefix and timestamp modes alter both correctness and optimization eligibility; enabling range tombstone conversion when scans are incomplete would risk hiding live keys. Multi-scan preparation stores scan options and requires later seeks to match the prepared ranges exactly.

## Test signals

The header's contracts are exercised by the implementation and by stress tests that call `DBIter::NewIter` directly. Useful test signals include direction switching, key/value pinning, merge results, status propagation, timestamp range iteration, prefix bounds, lazy blob value preparation through `PrepareValue`, wide-column materialization through `columns`, and local-to-global statistic flushing on destruction.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_iter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_iter_stress_test.cc -->
# sources/storage-engines/rocksdb/db/db_iter_stress_test.cc

## Purpose

This file is a randomized differential stress test for `DBIter`. It builds a synthetic ordered internal-key dataset, wraps it in an `InternalIterator` that can fail or mutate visibility during operations, and compares `DBIter` behavior with a simpler reference iterator. The goal is to catch iterator state-machine bugs around forward/reverse movement, seek positioning, merges, deletions, invisible versions, status propagation, and data changing under the iterator.

## Important APIs, types, and functions

`Entry` represents an internal record with user key, `ValueType`, sequence number, encoded internal key, value, and a `visible` flag used to simulate entries appearing/disappearing. Its ordering sorts by user key ascending and sequence/type descending, matching RocksDB internal-key order.

`Data` owns the vector of entries, indexes of hidden entries, and a set of keys whose visibility changed since the last seek. Recently touched keys are excluded from exact reference comparison because the underlying iterator is allowed to mutate during a single DBIter operation.

`StressTestIterator` implements `InternalIterator`. It supports `SeekToFirst`, `SeekToLast`, `Seek`, `SeekForPrev`, `Next`, `Prev`, `key`, `value`, `status`, and pinning checks. `MaybeFail()` injects `Incomplete` or `IOError` according to probability. `MaybeMutate()` randomly hides or unhides entries to simulate compaction-like disappearance or reappearance. `SkipForward` and `SkipBackward` advance over hidden entries.

`ReferenceIterator` is a compact model of visible DB iteration. It scans the sorted `Data` with binary search, ignores recently touched keys, applies snapshot sequence filtering, handles `kTypeDeletion`, `kTypeValue`, and `kTypeMerge`, and implements stringappend-style merge by concatenating operands/base values from oldest to newest reference order.

## Control flow

The single `StressTest` uses a deterministic `Random64` seed. It iterates over combinations of entry count, key-space density, prevalent entry type, error probability, mutation probability, and target hidden fraction. For each combination it creates sorted internal entries with random keys, sequence numbers equal to insertion index, mostly one prevalent type plus occasional other types, and encoded internal keys via `AppendInternalKey`.

During each run, a new `DBIter` and `ReferenceIterator` are created about every 30 operations at a random snapshot sequence. The DBIter wraps a fresh `StressTestIterator` and is constructed through `DBIter::NewIter` with a stringappend merge operator. Each iteration randomly chooses forward or reverse movement. It performs `Next`/`Prev` most of the time when valid, and otherwise or occasionally performs `Seek`, `SeekForPrev`, `SeekToFirst`, or `SeekToLast`.

After each operation, the test compares outcomes. If DBIter is valid and the key was not recently touched, key and value must exactly match the reference iterator. If the DBIter lands on a recently mutated key, the test checks only monotonic movement and that DBIter did not skip a stable reference key. If DBIter is invalid with OK status, the reference must also be invalid. If DBIter has non-OK status, the next reference operation is forced to reseek because exact position is no longer meaningful.

## State and persistence behavior

The test has no durable storage; all state is in memory. It nevertheless models key RocksDB iterator conditions: hidden entries stand in for records removed or obscured by compaction, random failures stand in for underlying storage errors, and repeated reconstruction of iterators models new snapshots. The deterministic seed makes failures reproducible. `StressTestIterator` advertises pinned keys and values, which is important because DBIter reverse paths require pinned value support in some cases.

## Dependencies and integration points

The test includes `db/db_iter.h`, `db/dbformat.h`, RocksDB comparator/options/slice headers, the test harness, random/string utilities, and `utilities/merge_operators.h`. It directly constructs `ImmutableOptions` and `MutableCFOptions` from `Options`, uses `BytewiseComparator`, and passes `version=nullptr`, no read callback, and no active memtable, isolating the core DBIter state machine from actual DB storage.

Command-line integration is optional through gflags. With `FLAGS_verbose`, the test prints generated entries, operations, injected errors, and mutations, which helps reproduce a failing trace.

## Risks and edge cases

The reference model intentionally implements only part of full DBIter behavior: no timestamps, prefix extractors, bounds, blob indexes, wide columns, range tombstone conversion, unprepared values, or read callbacks. The file's TODO notes these coverage gaps and also suggests testing pinning more aggressively. Because mutations happen inside underlying iterator operations, exact comparison is impossible for recently touched keys; the test uses directional and non-skip assertions instead. High mutation and error probabilities increase coverage but can make a failure trace long, hence the verbose debug flag.

## Test signals

At the end, the test requires more than 10,000 exact matches, end-reached cases, non-OK statuses, and recently-mutated-key cases. These counters verify that the randomized matrix exercised all major result classes. The strongest signal is differential agreement between DBIter and `ReferenceIterator` across random direction changes, seeks, deletions, merges, invisible entries, errors, and mutations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_iter_stress_test.cc -->
