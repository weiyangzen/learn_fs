# subset-b-008526 Research

Grouped research report for subset-b-008526. Each section is delimited for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/directory_lock.go -->

# sources/storage-engines/pebble/internal/base/directory_lock.go

Purpose: Provides `DirLockSet`, `DirLock`, and `LockDirectory` for acquiring Pebble database directory locks through the VFS `LOCK` file. It lets callers pre-acquire a lock and pass it through open paths while preserving a small reference-count protocol.

APIs and types: `DirLockSet.String`, `Close`, and `AcquireOrValidate` manage a list of acquired locks. `LockDirectory` calls `fs.Lock(MakeFilepath(... FileTypeLock ...))` and returns a `DirLock`. `DirLock.refForOpen`, `Refs`, `Close`, and `pathMatches` implement validation and lifecycle.

Control flow and state: `AcquireOrValidate` either validates a pre-acquired lock against `dirname`, increments its ref count from 1 to 2, and records it, or acquires a new VFS lock. `DirLock.Close` atomically decrements refs; only the transition to zero closes the underlying `io.Closer`. `DirLockSet.Close` combines errors while closing all held locks and clears the slice.

Persistence and dependencies: The persistent artifact is the filesystem `LOCK` file lock acquired through `vfs.FS`; path construction depends on `filenames.go`. `pathMatches` deliberately uses `os.Stat` and `os.SameFile` outside VFS to handle relative paths and symlinks.

Integration points: Used by DB open/options code to prevent concurrent opens and to widen the critical section around setup. Invariant finalizers catch leaked locks when invariants are enabled.

Risks: Ref counts must stay in the expected 0/1/2 range. Closing too early can release an active DB lock; reusing a lock already opened by another DB returns an error. `pathMatches` is less portable for non-local VFS implementations because it bypasses VFS.

Test signals: No paired test in this subset, but `Refs` exists for tests and invariant finalizers provide leak detection in invariant builds.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/directory_lock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/doc.go -->

# sources/storage-engines/pebble/internal/base/doc.go

Purpose: Package documentation for `internal/base`, describing Pebble's internal key/value model, LSM layout, levels, memtables, log-structured writes, compaction, range tombstones, snapshots, and comparer semantics.

APIs and types: Exposes no runtime API beyond the `package base` declaration. The file is a long package comment, so its API value is conceptual rather than executable.

Control flow and state: Documents how writes enter WAL and memtable, flushes create L0 tables, compactions merge and rewrite levels, snapshots constrain obsolete-key collection, and range tombstones delete half-open spans.

Persistence and dependencies: Describes durable structures used across the package: WALs, manifests, SSTables, internal key trailers, sequence numbers, and comparer ordering.

Integration points: Sets expectations for downstream packages that use `base.InternalKey`, comparers, file numbers, iterator contracts, and compaction invariants.

Risks: Documentation must remain synchronized with evolving key kinds and LSM behavior. Drift here is risky because it describes rules that many lower-level packages assume.

Test signals: No direct tests; correctness is indirectly enforced by tests for internal keys, filenames, iterators, compactions, and table behavior.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/error.go -->

# sources/storage-engines/pebble/internal/base/error.go

Purpose: Defines common Pebble sentinel and categorized errors, including not-found, corruption, assertion failures, panic catching, and corrupt block data attachment.

APIs and types: `ErrNotFound`, `ErrCorruption`, `MarkCorruptionError`, `IsCorruptionError`, `CorruptionErrorf`, `CorruptBlockData`, `AttachCorruptBlockData`, `ExtractCorruptBlockData`, `AssertionFailedf`, and `CatchErrorPanic`.

Control flow and state: Corruption errors are marked through the CockroachDB errors library and recognized by marker lookup. `CorruptBlockData` wraps a cause and stores the corrupted bytes. `CatchErrorPanic` recovers panics that carry errors while re-panicking non-error payloads.

Persistence and dependencies: No persisted state. Depends on `github.com/cockroachdb/errors`, markers, and `invariants` to decide whether assertion failures are marked as safe details.

Integration points: Used throughout Pebble for stable error classification, especially corruption handling and invariant/assertion failures.

Risks: Losing wrappers or markers can break `errors.Is`/classification. `AttachCorruptBlockData` stores byte slices by reference, so callers must avoid unintended mutation if inspecting later.

Test signals: `error_test.go` verifies corrupt block data can be attached and extracted through wrapping.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/error.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/error_test.go -->

# sources/storage-engines/pebble/internal/base/error_test.go

Purpose: Tests corrupt block data attachment and extraction behavior.

APIs and types: Exercises `AttachCorruptBlockData`, `ExtractCorruptBlockData`, and `errors.Wrap` interaction.

Control flow and state: Creates a base error, attaches `[]byte("foo")`, wraps the error, then confirms extraction still finds the original data through the error chain.

Persistence and dependencies: No persistence. Depends on `cockroachdb/errors` and `testify/require`.

Integration points: Confirms corruption diagnostics survive the same wrapping style used by higher Pebble layers.

Risks: Narrow coverage: it does not test marker classification, nil errors, or mutation of attached data.

Test signals: Positive signal for wrapped-data extraction; broader error classification remains covered elsewhere or by integration tests.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/error_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/filenames.go -->

# sources/storage-engines/pebble/internal/base/filenames.go

Purpose: Centralizes Pebble file/object identifiers, filename construction and parsing, blob file mappings, and diagnostics for unexpected missing files.

APIs and types: `TableNum`, `DiskFileNum`, `BlobFileID`, `BlobReferenceID`, `FileType`, `ObjectInfo`, `ObjectInfoLiteral`, `BlobFileMapping`, `MakeFilename`, `MakeFilepath`, `ParseFilename`, `ParseDiskFileNum`, `MustExist`, `AddDetailsToNotExistError`, and `FileInfo`.

Control flow and state: Formatting functions generate canonical names such as `000123.sst`, `MANIFEST-000123`, `OPTIONS-000123`, `temporary.000123.dbtmp`, `000123.blob`, and `000123.blobmeta`. `ParseFilename` normalizes with `fs.PathBase` and pattern-matches canonical forms. `MustExist` annotates not-exist errors by listing the directory and counting recognized file classes before fataling.

Persistence and dependencies: Encodes the durable naming contract for table, manifest, options, temp, lock, and blob files. Depends on `vfs.FS`, `oserror`, path helpers, redact-safe formatting, and `filepath.Ext` for WAL-ish log counting.

Integration points: Used by DB open, manifest/object storage, blob storage, diagnostics, and directory locking. Blob ID to disk-file mapping is abstracted for manifest blob replacement.

Risks: Filename formats are compatibility-sensitive. `FileTypeLog` construction intentionally panics because WAL naming belongs elsewhere. Blobmeta parsing ignores the offset suffix beyond recognizing the type. Directory diagnostics can race with concurrent file deletion.

Test signals: `filenames_test.go` covers roundtrip formatting/parsing, file type parsing, invalid names, and missing-file diagnostics.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/filenames.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/filenames_test.go -->

# sources/storage-engines/pebble/internal/base/filenames_test.go

Purpose: Validates canonical filename construction, parsing, and missing-file error detail behavior.

APIs and types: Exercises `MakeFilename`, `MakeFilepath`, `ParseFilename`, `ParseDiskFileNum`, `FileTypeFromName`, and `AddDetailsToNotExistError`/`MustExist` related diagnostics.

Control flow and state: Table-driven cases verify known file names and invalid strings. Tests use VFS paths to ensure basename behavior and count directory contents for detail messages.

Persistence and dependencies: Uses test filesystem state to populate directories with recognized and unknown file names; no durable repository state is changed.

Integration points: Protects compatibility of filename formats consumed by DB open, manifest discovery, object storage, and cleanup code.

Risks: Tests are focused on naming grammar and diagnostics, not every object-storage lifecycle path. WAL filename specifics are intentionally outside this package.

Test signals: Strong table-driven coverage for edge cases around parsing and file-number conversion.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/filenames_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/internal.go -->

# sources/storage-engines/pebble/internal/base/internal.go

Purpose: Defines Pebble's core internal key model: sequence numbers, key kinds, trailers, key encoding/decoding, visibility, internal key/value pairs, atomic sequence numbers, compact key bounds, and storage-tier constants.

APIs and types: Key exports include `SeqNum`, `SeqNumRange`, `InternalKeyKind`, `InternalKeyTrailer`, `InternalKey`, `InternalKV`, `KVMeta`, `AtomicSeqNum`, `InternalKeyBounds`, `StorageTier`, constructors/parsers (`MakeInternalKey`, `MakeSearchKey`, `DecodeInternalKey`, `ParseInternalKey`, `ParseInternalKV`, `ParseInternalKeyRange`), and ordering/visibility helpers (`InternalCompare`, `Visible`, `IsExclusiveSentinel`).

Control flow and state: Internal keys sort by user key ascending, then trailer descending so newer versions and higher kinds sort first. `Visible` handles committed and batch sequence spaces, with `SeqNumMax` always visible for sentinels. `Separator` and `Successor` use comparer-provided functions and fall back to original keys unless the shortened user key remains ordered correctly. `InternalKeyBounds` stores two user keys in one immutable string and exposes slices using `unsafe`.

Persistence and dependencies: The trailer layout is durable: 7-byte sequence number plus 1-byte kind, encoded little-endian. Key kind constants are file-format sensitive. Depends on binary encoding, atomics, `invariants`, redact formatting, and comparer callbacks.

Integration points: This file underpins memtables, SSTables, WAL batches, manifest metadata, iterators, compaction, range tombstones, range keys, blob/tiering metadata, and tests/tools parsing debug strings.

Risks: Changing key-kind values or trailer semantics breaks on-disk compatibility. Unsafe string-backed bounds must not be mutated. Parser helpers panic on invalid debug input. Visibility semantics around batch bits and sentinels are subtle and correctness-critical.

Test signals: `internal_test.go` covers encoding, invalid keys, comparer order, kind roundtrips, separators, and exclusive sentinel detection.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/internal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/internal_test.go -->

# sources/storage-engines/pebble/internal/base/internal_test.go

Purpose: Tests the internal key data model and ordering invariants.

APIs and types: Covers `InternalKey.Encode`, `DecodeInternalKey`, `InternalCompare`, `ParseKind`, key kind string roundtrips, `InternalKey.Separator`, and `IsExclusiveSentinel`.

Control flow and state: The tests encode internal keys into buffers, decode invalid short keys, sort/compare keys with equal and differing user keys, and validate separator results over representative key pairs.

Persistence and dependencies: Verifies the durable trailer encoding and kind names used in debug strings and file formats. Uses the default comparer and testify/datadriven-style assertions.

Integration points: Protects the ordering contract depended on by memtables, SSTable block indexes, merging iterators, and compaction.

Risks: Table coverage is meaningful but not exhaustive across every key kind. Parser helpers intentionally panic on invalid input, so invalid-string behavior is only selectively tested.

Test signals: Strong regression signal for key encoding/order and sentinel semantics.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/iterator.go -->

# sources/storage-engines/pebble/internal/base/iterator.go

Purpose: Defines the internal iterator contract, top-level iterator abstraction, seek flag bitsets, and iterator block-read/statistics aggregation.

APIs and types: `InternalIterator`, `InternalIteratorWithKVMeta`, `TopLevelIterator`, `SeekGEFlags`, `SeekLTFlags`, `BlockReadStats`, and `InternalIteratorStats` with string and redact formatting.

Control flow and state: The interface documents absolute and relative positioning rules, prefix iteration mode, bound enforcement responsibilities, error accumulation, and close semantics. `SeekGEFlags` encodes `TrySeekUsingNext`, `RelativeSeek`, and `BatchJustRefreshed`; `SeekLTFlags` encodes `RelativeSeek`. Stats accumulate block byte/count metrics and merge across iterators.

Persistence and dependencies: No durable state; it standardizes runtime iteration state and stats. Depends on context, time, blockkind categories, humanize formatting, redact formatting, and tree-step introspection.

Integration points: Implemented by memtable, batch, sstable, level, merging, and compaction iterators. Public `Iterator` and compaction code rely on its bound and error contracts.

Risks: Bounds are partly caller-enforced, so incorrect caller positioning can produce out-of-bound results. Prefix iteration prohibits some reverse movement. Lazy values may return errors not included in iterator `Error`.

Test signals: `iterator_test.go` verifies seek flag bit composition and string behavior; behavioral iterator conformance is tested by concrete iterator packages.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/iterator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/iterator_test.go -->

# sources/storage-engines/pebble/internal/base/iterator_test.go

Purpose: Tests flag bitset helpers for seek operations.

APIs and types: Exercises `SeekGEFlags` methods for enabling/disabling `TrySeekUsingNext`, `RelativeSeek`, and `BatchJustRefreshed`, plus `SeekLTFlags.RelativeSeek` helpers.

Control flow and state: The test enumerates flag combinations and checks that helper methods set and clear only the intended bits.

Persistence and dependencies: No persistence. Uses basic testing and require-style checks.

Integration points: Protects small but important API used by batch, memtable, sstable, and merging iterators for seek optimization decisions.

Risks: Does not test actual iterator behavior under the flags; concrete iterator tests cover that.

Test signals: Good regression signal for flag composition and string output stability.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/iterator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/key_bounds.go -->

# sources/storage-engines/pebble/internal/base/key_bounds.go

Purpose: Defines user-key ranges and boundaries with inclusive/exclusive endpoint semantics, including conversion from internal key bounds.

APIs and types: `KeyRange`, `BoundaryKind`, `UserKeyBoundary`, `UserKeyBounds`, constructors (`UserKeyInclusive`, `UserKeyExclusive`, `UserKeyBoundsInclusive`, `UserKeyBoundsEndExclusive`, `UserKeyBoundsFromInternal`), and methods for validation, containment, overlap, cloning, formatting, and union.

Control flow and state: Bound comparisons use `Compare` callbacks and special handling for exclusive sentinel internal keys. `UserKeyBounds.Valid` requires non-empty bounds and an end that includes the start. `Union` treats unset bounds as identity and expands start/end as needed.

Persistence and dependencies: No direct persistence, but these structures describe persisted object key spans for tables and blobs. Depends on `slices.Clone`, `invariants`, and error assertions for invalid internal-to-user conversions.

Integration points: Used by manifest metadata, compaction overlap checks, object info, span policies, blob mapping, and tests.

Risks: Inclusive/exclusive semantics are subtle, especially for internal sentinels at range ends. `Union` returns slices by reference, so callers needing ownership must clone.

Test signals: `key_bounds_test.go` covers boundary comparison, containment, overlap, validity, formatting, and union cases.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/key_bounds.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/key_bounds_test.go -->

# sources/storage-engines/pebble/internal/base/key_bounds_test.go

Purpose: Tests user-key boundary and range behavior.

APIs and types: Exercises `UserKeyBoundary.IsUpperBoundFor`, `CompareUpperBounds`, `UserKeyBounds.Valid`, `Overlaps`, `ContainsBounds`, `ContainsUserKey`, `ContainsInternalKey`, `Clone`, `String`, and `Union`.

Control flow and state: Table-driven cases compare inclusive and exclusive ends, unset bounds, adjacent spans, contained spans, and internal keys including sentinel-like boundaries.

Persistence and dependencies: No persistence. Uses the default comparer and require/assert helpers.

Integration points: Protects key span logic consumed by manifest, compaction, and object storage decisions.

Risks: Focused on representative cases; comparator-specific unusual orderings are only indirectly covered by using injected compare functions elsewhere.

Test signals: Strong local coverage for interval semantics.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/key_bounds_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/lazy_value.go -->

# sources/storage-engines/pebble/internal/base/lazy_value.go

Purpose: Represents values that may be in-place or lazily fetched from a value block/blob, with optional short attributes and value length metadata.

APIs and types: `ShortAttribute`, `MaxShortAttribute`, `ShortAttributeExtractor`, `AttributeAndLen`, `LazyValue`, `LazyFetcher`, `ValueFetcher`, `LazyValue.Value`, `Len`, `TryGetShortAttribute`, `Clone`, `NoBlobFetches`, and `errValueFetcher`.

Control flow and state: If `LazyValue.Fetcher` is nil, `ValueOrHandle` is the value. Otherwise it is a handle passed to `ValueFetcher.FetchHandle` with blob file ID and expected length. `Clone` copies handle/value bytes into a caller buffer and copies fetcher metadata into caller-provided storage without fetching.

Persistence and dependencies: No direct persistence, but handles and attributes correspond to values stored outside the key in value blocks or blob files. Depends on `context` and base blob ID types.

Integration points: Returned by `InternalIterator` and wrapped by `InternalValue`. Sstable/blob readers implement `ValueFetcher`; `blobtest.Values` provides test fetchers.

Risks: Memory ownership is subtle: iterator-owned value memory is unstable after repositioning, and cloned lazy values may refetch. The current `Value` call uses `context.TODO`, so cancellation must be handled at higher layers or by future API changes. `NoBlobFetches` is intended to catch unexpected blob access.

Test signals: `lazy_value_test.go` verifies in-place/lazy value retrieval, length, attribute, cloning, and fetcher behavior.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/lazy_value.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/lazy_value_test.go -->

# sources/storage-engines/pebble/internal/base/lazy_value_test.go

Purpose: Tests `LazyValue` in-place and lazy-fetch behavior.

APIs and types: Uses a `valueFetcherFunc` implementation and exercises `LazyValue.Value`, `Len`, `TryGetShortAttribute`, and `Clone`.

Control flow and state: Test cases cover raw in-place values, lazy handles with fetch metadata, caller-owned buffers, and cloned lazy values using caller-provided fetcher storage.

Persistence and dependencies: No persistence. Fetching is simulated by the test function.

Integration points: Protects the value contract relied on by iterators and blob/value-block readers.

Risks: Does not exercise real blob readers or iterator repositioning lifetimes; those are integration concerns.

Test signals: Good focused coverage for ownership flags and metadata propagation.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/lazy_value_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/level.go -->

# sources/storage-engines/pebble/internal/base/level.go

Purpose: Encodes an optional LSM level as a compact value with a validity bit.

APIs and types: `Level`, `MakeLevel`, `Get`, `Valid`, and `String`.

Control flow and state: `MakeLevel` stores the numeric level plus a high valid bit. `Get` returns `(level, true)` only when the valid bit is set; otherwise `(0, false)`. `String` renders invalid levels as `?`.

Persistence and dependencies: No direct persistence. Used in runtime metadata/statistics such as cache access levels.

Integration points: Cache APIs accept `base.Level` to attribute metrics; other internal components can represent optional levels without pointers.

Risks: The representation is `uint8`; callers must avoid levels too large to fit after reserving the valid bit.

Test signals: No direct test in this subset; usage is simple and indirectly covered by cache/iterator metrics tests.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/level.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/logger.go -->

# sources/storage-engines/pebble/internal/base/logger.go

Purpose: Defines logging and tracing interfaces plus default, in-memory, and no-op implementations.

APIs and types: `Logger`, `DefaultLogger`, `InMemLogger`, `LoggerAndTracer`, `LoggerWithNoopTracer`, and `NoopLoggerAndTracer`.

Control flow and state: `defaultLogger` writes info/error messages to stderr/stdout style streams and panics/exits through fatal logging behavior. `InMemLogger` stores formatted lines in a mutex-protected buffer and panics on fatal. Tracer methods emit events only when wrapping a real tracer; noop implementations discard everything.

Persistence and dependencies: No persistent state. Depends on context, synchronization, and tracing/redaction facilities.

Integration points: Pebble options use these interfaces for logs and slow operation tracing; tests use `InMemLogger` to assert messages.

Risks: Fatal behavior terminates or panics depending on implementation. In-memory logs can grow without bound in long tests if not reset.

Test signals: No paired test here, but many package tests use the interfaces.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/logger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/merger.go -->

# sources/storage-engines/pebble/internal/base/merger.go

Purpose: Defines the value merge abstraction used by Pebble's merge key kind, including a default append merger.

APIs and types: `Merge`, `ValueMerger`, `DeletableValueMerger`, `Merger`, `AppendValueMerger`, and `DefaultMerger`.

Control flow and state: A `Merge` creates a `ValueMerger` from an initial key/value. Merge operations are fed newer and older operands, then `Finish` returns a value and optional closer. `DeletableFinish` allows compaction to produce a deletion when merge semantics permit. `AppendValueMerger` concatenates values in correct order.

Persistence and dependencies: Merge results become persisted values in memtables/SSTables. Depends only on `io` for optional closers.

Integration points: Used by write path, iterators resolving merged values, and compaction. `test_utils.go` provides a deletion-capable test merger.

Risks: User merger ordering must match Pebble's newer/older operand calls. Returning closers requires callers to close resources. Merge implementations must not retain unstable byte slices unless copied.

Test signals: No direct test in this subset; merge behavior is exercised in higher-level DB and iterator tests.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/merger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/metrics.go -->

# sources/storage-engines/pebble/internal/base/metrics.go

Purpose: Provides small reusable metric accumulators for throughput and sampled gauges.

APIs and types: `ThroughputMetric` with `Merge`, `Subtract`, `PeakRate`, `Rate`, and `Utilization`; `GaugeSampleMetric` with `AddSample`, `Merge`, `Subtract`, and `Mean`.

Control flow and state: `ThroughputMetric` accumulates bytes, work duration, and idle duration. Peak rate divides bytes by work duration, observed rate divides by work plus idle time, and utilization reports the work fraction. `GaugeSampleMetric` stores sample sum and count and derives a mean.

Persistence and dependencies: Runtime-only metrics, not persisted. Depends only on `time`.

Integration points: Used by background workers and metrics collection paths that need cumulative throughput or queue-depth style sampled gauges.

Risks: Rate methods return zero only when bytes are zero; callers should avoid nonsensical nonzero bytes with zero duration. `Subtract` can produce negative durations/counts if misused with unrelated samples.

Test signals: `metrics_test.go` validates merge/subtract/rate/utilization-adjacent behavior for throughput and gauge metrics.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/metrics_test.go -->

# sources/storage-engines/pebble/internal/base/metrics_test.go

Purpose: Tests throughput and gauge metric accumulation helpers in `base`.

APIs and types: Exercises `ThroughputMetric.Merge`, `Subtract`, `Rate`, `PeakRate`, and `GaugeSampleMetric.AddSample`, `Merge`, `Subtract`, and `Mean`.

Control flow and state: Constructs representative byte/time metrics, merges duplicate values, subtracts one metric from another, and checks expected rates. Gauge tests add samples, merge gauges, subtract prior samples, and inspect internal sum/count.

Persistence and dependencies: No persistence. Uses test assertions to guard text output.

Integration points: Protects helper arithmetic used by DB metrics and background work accounting.

Risks: Tests cover simple positive cases and one subtraction case; they do not cover zero-duration nonzero-byte edge cases.

Test signals: Good local coverage for arithmetic and rate formulas.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/metrics_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/options.go -->

# sources/storage-engines/pebble/internal/base/options.go

Purpose: Defines shared option interfaces for table filter policies and block property filters.

APIs and types: `TableFilterFamily`, `TableFilterWriter`, `TableFilterPolicy`, `TableFilterDecoder`, `NoFilterPolicy`, internal `noFilter`, and `BlockPropertyFilter`.

Control flow and state: Filter policies create writers/decoders for table filters. `NoFilterPolicy` names the disabled policy and panics for unsupported writer/decoder creation because it should not be used to build filters.

Persistence and dependencies: Filter names and serialized filter data are persisted in table metadata/blocks by implementations outside this file. Depends on CockroachDB errors for assertion panics.

Integration points: SSTable writers/readers, options parsing, and block-property filtering plug into these interfaces.

Risks: Interface implementations must keep names stable for compatibility. Accidentally invoking `NoFilterPolicy.NewWriter` is a programmer error and panics.

Test signals: No direct tests here; concrete filter policies and table readers/writers test implementations.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/placement.go -->

# sources/storage-engines/pebble/internal/base/placement.go

Purpose: Defines object placement identifiers for local, shared, and external storage locations.

APIs and types: `Placement` enum values `Local`, `Shared`, and `External`, plus `String` and redact-safe formatting.

Control flow and state: `String` maps known enum values to stable labels. The zero value is intentionally invalid; unknown values panic when invariants are enabled and return `invalid` otherwise.

Persistence and dependencies: Placement identifiers describe where files/objects are stored and may be persisted by metadata in higher layers. Depends on `errors`, `invariants`, and `redact`.

Integration points: Used by object/table metadata and storage policy paths that distinguish local, shared, and external objects.

Risks: Callers must not rely on the zero value. Adding enum values requires updating string formatting and all metadata/storage consumers.

Test signals: No direct tests in this subset; behavior is simple.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/placement.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/span_policy.go -->

# sources/storage-engines/pebble/internal/base/span_policy.go

Purpose: Defines per-key-span policy hints for compression, value separation, blob storage, and warm/cold tiering.

APIs and types: `SpanPolicy`, `ValueStoragePolicyAdjustment`, `TieringAttribute`, `TieringSpanID`, `TieringPolicy`, and `TieringPolicyAndExtractor`.

Control flow and state: `SpanPolicy.IsDefault` detects whether any non-range policy is set. `StillCovers` checks whether a key remains within the policy end and asserts the key is not before start under invariants. String methods render human-readable policy descriptions. Value storage policy flags describe overrides to global separation heuristics. Tiering policy uses span ID plus age threshold and extractor metadata.

Persistence and dependencies: Span policies are runtime inputs but affect persistent placement of values into SSTables/blob files and tier metadata. Depends on key comparison, time durations, string helpers, and invariants.

Integration points: Flush, compaction, blob rewrite, and tiering decisions call policy providers to decide compression/value-storage/tier assignment. `KVMeta` in `internal.go` carries tiering metadata produced by these paths.

Risks: Tiering invariants are cross-layer and eventual-consistency tolerant but subtle; conflicting span IDs over overlapping key ranges can corrupt tiering assumptions. Policy string output must track added fields. Value-separation overrides interact with MVCC suffix heuristics.

Test signals: No direct tests in this subset; correctness depends on compaction/blob/tiering integration tests.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/span_policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/stopwatch.go -->

# sources/storage-engines/pebble/internal/base/stopwatch.go

Purpose: Provides a small stopwatch abstraction and deterministic testing hook for read duration measurements.

APIs and types: `DeterministicReadDurationForTesting`, `MakeStopwatch`, `deterministicStopwatchForTesting`, `Stop`, and `SlowReadTracingThreshold`.

Control flow and state: The testing hook flips a package-level boolean and returns a cleanup closure. `MakeStopwatch` either captures `time.Now` or returns a deterministic stopwatch. `Stop` returns elapsed time or deterministic duration when enabled.

Persistence and dependencies: Runtime-only timing state. Depends on `time`.

Integration points: Cache read-handle waits and slow read tracing use this to produce metrics/traces that can be made deterministic in tests.

Risks: The package-level testing flag is not concurrency-isolated; tests must use cleanup correctly.

Test signals: No direct test in this subset, but cache/read tests use deterministic timing hooks.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/stopwatch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/test_utils.go -->

# sources/storage-engines/pebble/internal/base/test_utils.go

Purpose: Provides reusable test helpers: a deletion-capable sum merger, fake internal key/value construction, a fake internal iterator, and user-key bounds parser.

APIs and types: `NewDeletableSumValueMerger`, `deletableSumValueMerger`, `FakeKVs`, `NewFakeIter`, `FakeIter`, `ParseUserKeyBounds`, and helper `fakeIkey`.

Control flow and state: The test merger parses integer values, sums newer/older operands, and can emit a deletion from `DeletableFinish` when the sum is zero and a base was included. `FakeIter` maintains sorted `InternalKV` slice position plus lower/upper bounds, implements seeks/next/prev, tracks close errors, and exposes `InternalIterator` methods.

Persistence and dependencies: Test-only runtime state; no persistence. Depends on context, sort/search helpers, strconv, and `treesteps`.

Integration points: Used by internal iterator, merge, and compaction tests that need controlled key streams without real memtables/SSTables.

Risks: Fake iterator simplifies some real iterator contracts, so tests using it must not assume it validates all bound misuse. Parser helpers panic on malformed strings.

Test signals: It is itself support code, indirectly validated wherever used.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/test_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/value.go -->

# sources/storage-engines/pebble/internal/base/value.go

Purpose: Wraps either an in-place value or a `LazyValue` in one `InternalValue` representation used by internal KVs.

APIs and types: `InternalValue`, `MakeLazyValue`, `MakeInPlaceValue`, `IsBlobValueHandle`, `IsInPlaceValue`, `InPlaceValue`, `LazyValue`, `Len`, `InternalLen`, `ValueOrHandle`, `Value`, and `Clone`.

Control flow and state: `InternalValue` stores a `LazyValue`; nil fetcher means in-place value, non-nil fetcher means lazy handle/blob. Methods enforce in-place access under invariants, delegate value fetching to `LazyValue`, and clone values/handles into caller buffers.

Persistence and dependencies: Represents values read from persisted tables or blob handles, but this wrapper is runtime-only. Depends on `errors` and `invariants`.

Integration points: Embedded in `InternalKV` and returned by iterators; used by `blobtest.ParseInternalValue` and table readers.

Risks: Calling `InPlaceValue` on a blob/lazy value panics under invariants. Ownership and cloning caveats mirror `LazyValue`.

Test signals: Covered indirectly by `lazy_value_test.go`, internal KV tests, and blob tests.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/value.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/batchskl/iterator.go -->

# sources/storage-engines/pebble/internal/batchskl/iterator.go

Purpose: Implements an iterator over the batch skiplist, returning `base.InternalKey` values derived from batch-record offsets.

APIs and types: `Iterator`, internal `splice`, methods `Close`, `SeekGE`, `SeekLT`, `First`, `Last`, `Next`, `Prev`, `KeyInfo`, `String`, `SetBounds`, and `seekForBaseSplice`.

Control flow and state: The iterator holds current node offset, cached key, bounds, and cached bound nodes. `SeekGE` optionally tries a bounded number of `Next` steps when `TrySeekUsingNext` is set, otherwise searches the skiplist. Forward methods enforce upper bound; reverse methods enforce lower bound, matching the base iterator contract.

Persistence and dependencies: Iterates in-memory batch storage; no independent persistence. Depends on `batchskl.Skiplist` internals and `base` flags/key types.

Integration points: Used by indexed batches/memtable-like batch iteration. `KeyInfo` maps the current node back to batch record offsets for higher-level batch logic.

Risks: Caller must respect missing lower/upper checks on first/last/seek directions. Iterator state after `SetBounds` is undefined until repositioned. Copy-by-value is supported but shares the same list.

Test signals: `skl_test.go` covers next/prev/seeks/bounds and overflow behavior.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/batchskl/iterator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/batchskl/skl.go -->

# sources/storage-engines/pebble/internal/batchskl/skl.go

Purpose: Implements Pebble's non-concurrent in-memory skiplist index for batch records, storing node metadata separately from raw batch key/value storage.

APIs and types: `Skiplist`, `NewSkiplist`, `Reset`, `Init`, `Add`, `NewIter`, `ErrTooManyRecords`, internal `node`, `links`, random height/probability helpers, and splice search helpers.

Control flow and state: `Init` seeds random state, allocates head/tail sentinels, and links all levels. `Add` parses a batch record at `keyOffset`, extracts key boundaries, computes an abbreviated key, finds splice positions, allocates a variable-height node in a byte slice, and links base-to-top. In-order insertions use a fast path from tail. Equal keys are inserted before existing equal keys so newer batch entries iterate first.

Persistence and dependencies: Indexes external batch storage by offsets; it does not own the actual records. Node memory is a byte slice with unsafe node views and uint32 offsets. Depends on binary varints, rand/v2, unsafe, base comparer/abbreviated keys, and CockroachDB errors.

Integration points: Used by batch indexing and batch iterators. Internal keys encode the record offset with `SeqNumBatchBit` so batch entries participate in internal-key ordering.

Risks: Non-concurrent by design. Unsafe node layout and uint32 offsets require careful allocation bounds; `ErrTooManyRecords` protects against overflow. Corrupted batch record lengths return errors. Reset may retain up to 1 MiB of node memory.

Test signals: `skl_test.go` covers pointer-free layout, empty/basic behavior, ordering, overflow, iterator seeks/bounds, and benchmarks.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/batchskl/skl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/batchskl/skl_test.go -->

# sources/storage-engines/pebble/internal/batchskl/skl_test.go

Purpose: Tests and benchmarks the batch skiplist and iterator.

APIs and types: Exercises `Skiplist`, `Iterator`, `ErrTooManyRecords`, `NewIter`, `Add`, `SeekGE`, `SeekLT`, `First`, `Last`, `Next`, `Prev`, and bounds handling.

Control flow and state: Test storage encodes batch records, inserts ordered and unordered keys, checks forward/reverse lengths, verifies duplicate/newer ordering, forces overflow, and validates bound semantics. Benchmarks measure random and ordered writes plus iteration.

Persistence and dependencies: Uses in-memory encoded batch records only. Depends on base comparer, rand, errors, and testify.

Integration points: Protects batch indexing behavior used by write batch readers and indexed batches.

Risks: TODO notes missing dedicated tests for `First` and `Last`; they are still touched by length helpers and benchmarks.

Test signals: Strong local coverage for skiplist mechanics, seek correctness, bounds, and performance-sensitive paths.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/batchskl/skl_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/binfmt/binfmt.go -->

# sources/storage-engines/pebble/internal/binfmt/binfmt.go

Purpose: Provides a binary formatter that consumes a byte slice and emits annotated, aligned descriptions of binary layouts.

APIs and types: `New`, `Formatter`, methods for prefixes, anchor offsets, relative data, widths, offsets, peeking integers, binary/hex/uvarint formatting, treeprinter output, unsafe pointers, and `Line` builder methods.

Control flow and state: `Formatter` tracks `off`, `anchorOff`, original data, line width, and buffered `(binary, comment)` lines. Formatting calls consume bytes and append aligned output. `Line` enforces that the caller formats exactly the declared number of bytes.

Persistence and dependencies: Runtime diagnostic formatter only. Depends on binary encoding, bytes buffers, math/strconv/string formatting, treeprinter, and unsafe pointer access.

Integration points: Used by tools/tests that explain table, blob, or WAL binary structures.

Risks: Most methods assume enough remaining bytes and will panic on out-of-range or assertion failures. `Pointer` exposes unsafe pointers into the backing slice. `HexBytesln` returns the depleted local `n` (zero after consumption), so callers should not expect original length.

Test signals: No direct test for `Formatter` in this subset; `hexdump_test.go` covers the simpler hexdump utility.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/binfmt/binfmt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/binfmt/hexdump.go -->

# sources/storage-engines/pebble/internal/binfmt/hexdump.go

Purpose: Implements a compact hex dump utility with optional offsets and ASCII sidebars.

APIs and types: `HexDump(data, width, includeOffsets)` and `FHexDump(w, data, width, includeOffsets)`.

Control flow and state: Iterates data in rows of `width`, optionally prints zero-padded hex offsets, groups hex bytes every four bytes, pads incomplete rows, and prints printable ASCII or `.` for non-printable bytes.

Persistence and dependencies: Diagnostic runtime output only. Depends on `fmt`, `io`, `strconv`, and `bytes.Buffer`.

Integration points: Used by datadriven tests and binary-format debugging tools.

Risks: `width` must be positive; zero or negative width would break loop progress. Output format is test-sensitive.

Test signals: `hexdump_test.go` verifies output through datadriven cases over generated and file-backed data.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/binfmt/hexdump.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/binfmt/hexdump_test.go -->

# sources/storage-engines/pebble/internal/binfmt/hexdump_test.go

Purpose: Datadriven tests for hex dump formatting.

APIs and types: Exercises `HexDump` with `read-file` and `sequential` commands, configurable width, offsets, and data slices.

Control flow and state: Each datadriven command builds or reads bytes, slices by position/length, then returns formatted dump output for comparison.

Persistence and dependencies: Reads testdata files only. Depends on `datadriven`, `os.ReadFile`, and testify require.

Integration points: Protects diagnostic output used by binary format explainers.

Risks: Does not test invalid widths. Output changes require datadriven fixture updates.

Test signals: Good text-format regression coverage for row/offset/ascii rendering.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/binfmt/hexdump_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/bitflip/bitflip.go -->

# sources/storage-engines/pebble/internal/bitflip/bitflip.go

Purpose: Provides a diagnostic helper that searches for a single-bit flip that would make a byte slice match an expected checksum.

APIs and types: `CheckSliceForBitFlip` and internal `checkByteForFlip`.

Control flow and state: Scans up to 40 KiB of the slice, flips each bit of each byte, computes checksum, restores the byte, and returns the first index/bit that matches the expected checksum.

Persistence and dependencies: Mutates the provided slice transiently but restores each bit before returning. No external dependencies.

Integration points: Useful in corruption diagnostics to identify likely one-bit memory or disk corruption.

Risks: O(n*8*checksum) and capped at 40 KiB, so it may miss flips beyond the cap or multi-bit corruption. A checksum collision can produce a false positive.

Test signals: No direct test in this subset; behavior is straightforward but relies on checksum callback correctness.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/bitflip/bitflip.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/blobtest/handles.go -->

# sources/storage-engines/pebble/internal/blobtest/handles.go

Purpose: Test helper for parsing human-readable blob handles, synthesizing values, fetching lazy blob values, writing blob files, and mapping blob file IDs to inline reference IDs.

APIs and types: `Values`, `FetchHandle`, `ParseInternalValue`, `IsBlobHandle`, `Parse`, `ParseInlineHandle`, `IsEmpty`, `WriteFiles`, `References`, and `MapToReferenceID`.

Control flow and state: `Values.Parse` reads `blob{...}` fields, fills omitted file/block/value IDs from recent handles, defaults length to value length or 12, records explicit or synthesized values, and tracks most recent handles. `FetchHandle` decodes a handle suffix and returns tracked or deterministic derived bytes. `WriteFiles` groups handles by blob file, sorts them, fills value-ID gaps with derived values, writes blobs through `blob.FileWriter`, and returns file stats.

Persistence and dependencies: Writes real blob objects via caller-provided `objstorage.Writable` factory. Depends on base lazy values, blob handle encoding, string parser, slices/cmp, rand/v2, and CockroachDB errors.

Integration points: Used by table/blob tests that need debug text fixtures and lazy value fetching without a full DB.

Risks: Parser recovers panics into errors but still depends on exact debug syntax. Derived values are deterministic but artificial. `WriteFiles` assumes blob file IDs map directly to disk file numbers for tests.

Test signals: No direct test in this subset, but it is support code for blob/value-separation tests.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/blobtest/handles.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/buildtags/cgo_off.go -->

# sources/storage-engines/pebble/internal/buildtags/cgo_off.go

Purpose: Defines build-time `Cgo` as false when the `cgo` build tag is not active.

APIs and types: Package constant `Cgo = false` behind `//go:build !cgo`.

Control flow and state: Compile-time selection only; no runtime control flow.

Persistence and dependencies: No persistence or imports.

Integration points: Manual-memory/cache code uses this constant to choose Go allocation fallbacks when cgo is unavailable.

Risks: Incorrect build constraints would select the wrong allocation strategy.

Test signals: Covered implicitly by building with and without cgo.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/buildtags/cgo_off.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/buildtags/cgo_on.go -->

# sources/storage-engines/pebble/internal/buildtags/cgo_on.go

Purpose: Defines build-time `Cgo` as true when the `cgo` build tag is active.

APIs and types: Package constant `Cgo = true` behind `//go:build cgo`.

Control flow and state: Compile-time selection only.

Persistence and dependencies: No persistence or imports.

Integration points: Cache/manual allocation paths use this to decide whether C-backed manual allocation is available.

Risks: Must stay mutually exclusive with `cgo_off.go`.

Test signals: Covered implicitly by cgo-enabled builds.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/buildtags/cgo_on.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/buildtags/invariants_off.go -->

# sources/storage-engines/pebble/internal/buildtags/invariants_off.go

Purpose: Defines build-time `Invariants` as false when the `invariants` tag is absent.

APIs and types: Package constant `Invariants = false` behind `//go:build !invariants`.

Control flow and state: Compile-time feature flag only.

Persistence and dependencies: No persistence.

Integration points: Invariant checks, leak finalizers, and assertions consult buildtag-driven invariant settings.

Risks: Wrong build constraint would disable or enable expensive/debug checks unexpectedly.

Test signals: Covered by normal builds without the invariants tag.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/buildtags/invariants_off.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/buildtags/invariants_on.go -->

# sources/storage-engines/pebble/internal/buildtags/invariants_on.go

Purpose: Defines build-time `Invariants` as true when the `invariants` tag is present.

APIs and types: Package constant `Invariants = true` behind `//go:build invariants`.

Control flow and state: Compile-time feature flag only.

Persistence and dependencies: No persistence.

Integration points: Enables invariant-heavy code paths and leak detection in cache, locks, and maps.

Risks: Must remain mutually exclusive with `invariants_off.go`; invariant builds may expose latent lifecycle bugs.

Test signals: Covered by invariant-tag CI/test lanes where configured.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/buildtags/invariants_on.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/buildtags/race_off.go -->

# sources/storage-engines/pebble/internal/buildtags/race_off.go

Purpose: Defines build-time `Race` as false when the race detector tag is absent.

APIs and types: Package constant `Race = false` behind `//go:build !race`.

Control flow and state: Compile-time selection only.

Persistence and dependencies: No persistence.

Integration points: Used by invariant/finalizer/manual-memory code to avoid incompatible behavior under race builds.

Risks: Incorrect constraint would misclassify race builds.

Test signals: Covered by non-race builds.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/buildtags/race_off.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/buildtags/race_on.go -->

# sources/storage-engines/pebble/internal/buildtags/race_on.go

Purpose: Defines build-time `Race` as true when built with the race detector.

APIs and types: Package constant `Race = true` behind `//go:build race`.

Control flow and state: Compile-time flag only.

Persistence and dependencies: No persistence.

Integration points: Allows code to disable finalizers or unsafe/manual-memory features that interfere with race detection.

Risks: Must stay paired with `race_off.go`.

Test signals: Covered by race-enabled CI/test runs.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/buildtags/race_on.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/buildtags/slow_build_off.go -->

# sources/storage-engines/pebble/internal/buildtags/slow_build_off.go

Purpose: Defines build-time `SlowBuild` as false when the `slowbuild` tag is absent.

APIs and types: Package constant `SlowBuild = false` behind `//go:build !slowbuild`.

Control flow and state: Compile-time feature gate only.

Persistence and dependencies: No persistence.

Integration points: Lets tests or code avoid slow paths unless explicitly requested.

Risks: Build tag name must match the corresponding on file and caller expectations.

Test signals: Covered by default builds.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/buildtags/slow_build_off.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/buildtags/slow_build_on.go -->

# sources/storage-engines/pebble/internal/buildtags/slow_build_on.go

Purpose: Defines build-time `SlowBuild` as true when the `slowbuild` tag is present.

APIs and types: Package constant `SlowBuild = true` behind `//go:build slowbuild`.

Control flow and state: Compile-time feature gate only.

Persistence and dependencies: No persistence.

Integration points: Enables slow or exhaustive paths in selected builds/tests.

Risks: Must remain mutually exclusive with `slow_build_off.go`.

Test signals: Covered by any slowbuild CI lane or manual tag builds.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/buildtags/slow_build_on.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/buildtags/tracing_off.go -->

# sources/storage-engines/pebble/internal/buildtags/tracing_off.go

Purpose: Defines build-time `Tracing` as false when the `tracing` tag is absent.

APIs and types: Package constant `Tracing = false` behind `//go:build !tracing`.

Control flow and state: Compile-time feature flag only.

Persistence and dependencies: No persistence.

Integration points: Reference-count and cache tracing code uses this to compile in lightweight behavior by default.

Risks: Wrong tag constraint would unexpectedly remove or add tracing overhead.

Test signals: Covered by default builds.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/buildtags/tracing_off.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/buildtags/tracing_on.go -->

# sources/storage-engines/pebble/internal/buildtags/tracing_on.go

Purpose: Defines build-time `Tracing` as true when the `tracing` tag is present.

APIs and types: Package constant `Tracing = true` behind `//go:build tracing`.

Control flow and state: Compile-time flag only.

Persistence and dependencies: No persistence.

Integration points: Enables reference-count/cache tracing paths that help diagnose leaks and lifecycle bugs.

Risks: Tracing may significantly slow execution; constraints must match off file.

Test signals: Covered by tracing-tag diagnostic builds if run.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/buildtags/tracing_on.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/bytealloc/bytealloc.go -->

# sources/storage-engines/pebble/internal/bytealloc/bytealloc.go

Purpose: Implements a simple chunk allocator for byte slices with shared lifetime and exponential growth.

APIs and types: Type `A []byte`, constants `chunkAllocMinSize` and `chunkAllocMaxSize`, methods `Alloc`, `Copy`, `Reset`, and internal `reserve`.

Control flow and state: The allocator is itself the current chunk. `Alloc` reserves a new rawalloc chunk when remaining capacity is insufficient, returns a full-slice-capacity allocation, and advances length. `Copy` allocates then copies. `Reset` reuses the current chunk by setting length to zero.

Persistence and dependencies: Runtime memory only. Depends on `internal/rawalloc`.

Integration points: Used by components needing many same-lifetime byte copies while reducing allocation overhead.

Risks: Returned slices share backing chunks; resetting while slices are still in use can corrupt callers. Large chunks can be pinned by small surviving slices.

Test signals: No direct tests in this subset; behavior is simple but lifetime-sensitive.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/bytealloc/bytealloc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/bytesprofile/bytesprofile.go -->

# sources/storage-engines/pebble/internal/bytesprofile/bytesprofile.go

Purpose: Records byte-count samples grouped by call stack and produces sorted text or structured reports.

APIs and types: `Profile`, `NewProfile`, `Record`, `String`, `Collect`, `StackStats`, and internal `stack`/`aggSamples`.

Control flow and state: `Record` captures callers, locks a mutex, increments count and bytes for the stack. `all` snapshots/sorts stack keys by descending bytes while locked and yields samples. `String` and `Collect` symbolize stack frames with `runtime.CallersFrames`.

Persistence and dependencies: In-memory profiling only. Depends on runtime stack APIs, maps/slices/iter, synchronization, and humanize formatting.

Integration points: Useful for internal allocation/bytes diagnostics where pprof-style export is not yet implemented.

Risks: Holding the mutex while sorting and yielding could block concurrent recorders during formatting. Fixed stack depth of 30 may truncate deep stacks. TODO notes possible pprof export.

Test signals: `bytesprofile_test.go` verifies aggregation, sorting, string output, and structured collection.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/bytesprofile/bytesprofile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/bytesprofile/bytesprofile_test.go -->

# sources/storage-engines/pebble/internal/bytesprofile/bytesprofile_test.go

Purpose: Tests byte profile aggregation and formatting.

APIs and types: Exercises `NewProfile`, `Record`, `String`, and `Collect`.

Control flow and state: Records two distinct call stacks with known byte totals and counts, checks formatted output contains expected humanized counts/bytes, then checks structured stats ordering.

Persistence and dependencies: No persistence. Uses testify require.

Integration points: Protects diagnostic reporting used by internal profiling tools.

Risks: Stack identity relies on call sites remaining distinct; refactors can require expectation updates.

Test signals: Good focused coverage for aggregation and descending-byte ordering.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/bytesprofile/bytesprofile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/block_map.go -->

# sources/storage-engines/pebble/internal/cache/block_map.go

Purpose: Wraps a Swiss hash map specialized for block-cache key to entry mappings with manual allocation and leak checking.

APIs and types: `blockMap`, `newBlockMap`, `Init`, `Close`, `findByValue`, `blockMapAllocator`, `fibonacciHash`, and `blockMapOptions`.

Control flow and state: The allocator obtains and frees map group storage through Pebble manual memory. The map uses a custom Fibonacci-style hash over handle ID, file number, and offset, a max bucket capacity, and the allocator. `Close` releases Swiss map memory and marks the map closed; invariant finalizer exits if a map is leaked.

Persistence and dependencies: Runtime cache index only; no persistence. Depends on `swiss`, `manual`, unsafe, and invariants.

Integration points: Used by cache shards to map block keys to cache entries while avoiding Go heap overhead.

Risks: Manual allocation requires `Close` exactly once. Unsafe conversions must match Swiss group layout. `findByValue` scans the map and is for diagnostics/invariant checks, not hot path.

Test signals: `block_map_test.go` benchmarks Swiss map behavior against Go maps; functional coverage is primarily through cache tests outside this subset.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/block_map.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/block_map_test.go -->

# sources/storage-engines/pebble/internal/cache/block_map_test.go

Purpose: Benchmarks `blockMap` against Go maps for insert, hit lookup, and miss lookup workloads.

APIs and types: Uses `newBlockMap`, `Put`, `Get`, and `Close` over cache `key` and `entry` values.

Control flow and state: Generates randomized file/offset keys sized to a plausible per-shard block count, then compares repeated map insertions and lookups. Benchmarks close block maps to release manual memory.

Persistence and dependencies: Runtime benchmark only. Depends on rand/v2, runtime keepalive, testing, and base file numbers.

Integration points: Provides performance signal for the cache shard map implementation.

Risks: Benchmarks are not correctness tests and do not exercise eviction or lifecycle beyond close.

Test signals: Useful performance regression signal; functional cache behavior is covered elsewhere.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/block_map_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/cache.go -->

# sources/storage-engines/pebble/internal/cache/cache.go

Purpose: Implements the public surface of Pebble's sharded block cache and cache handles, backed by per-shard CLOCK-Pro replacement and manual-memory values.

APIs and types: `Cache`, `New`, `NewWithShards`, `Ref`, `Unref`, `NewHandle`, `Reserve`, `MaxSize`, `Size`, `Handle`, `handleID`, `Handle.Cache`, `Peek`, `Get`, `GetWithReadHandle`, `Set`, `Delete`, `EvictFile`, `Close`, and `CategoryHidden`.

Control flow and state: `New` chooses shard count as `4*GOMAXPROCS` unless that would create tiny shards, then initializes shards and metrics windows. Cache lifetime is reference-counted; `Unref` destroys shards at zero. Handles allocate unique namespace IDs and keep cache refs. Gets route a `(handleID,fileNum,offset)` key to a shard; `GetWithReadHandle` coordinates cache misses with read-entry turn taking and context cancellation. `Reserve` temporarily lowers effective shard capacity and returns a one-shot release closure.

Persistence and dependencies: Cache contents are runtime-only copies of immutable table blocks. Depends on base file/level types, shard/read-entry/value implementations, metrics windows, atomics, sync, runtime/debug, invariants, and errors.

Integration points: Used by DB/table readers to share blocks across Pebble instances while isolating file-number namespaces by handle. Exposes metrics and read-handle coordination for block reads.

Risks: Every `Value` returned by get paths must be released by callers. Cache and handle refs must be balanced or invariant finalizers exit. Manual memory leaks or double releases are serious. `Reserve` closure panics on double release. Read-handle callers must call `SetReadValue` or `SetReadError` when they receive a valid handle.

Test signals: This subset includes `block_map_test.go`; broader cache behavior is tested in other cache package tests such as clockpro/read-shard/value tests not assigned here.

<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/cache/cache.go -->
