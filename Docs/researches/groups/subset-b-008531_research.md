# Research: subset-b-008531

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/l0_sublevels_test.go -->
# sources/storage-engines/pebble/internal/manifest/l0_sublevels_test.go

## Purpose
This test file exercises Pebble manifest L0 sublevel construction, visualization, compaction selection, in-use range calculation, flush split keys, incremental L0 updates, and manifest replay benchmarks. It is the primary test signal for the L0 organizer behavior that turns unordered overlapping L0 files into ordered sublevels and compaction candidates.

## Important APIs, Types, And Helpers
- `readManifest` replays a record log manifest into a `Version` by repeatedly decoding `VersionEdit`, accumulating a `BulkVersionEdit`, applying it, and updating an `L0Organizer`.
- `visualizeSublevels` renders L0 sublevels and optional lower levels as compact ASCII spans, marking base compaction, intra-L0 compaction, and compacting states.
- `TestL0Sublevels` is datadriven and dispatches commands such as `define`, `add-l0-files`, `pick-base-compaction`, `pick-intra-l0-compaction`, `in-use-key-ranges`, `flush-split-keys`, `max-depth-after-ongoing-compactions`, `l0-check-ordering`, and `update-state-for-compaction`.
- `TestAddL0FilesEquivalence` randomized-checks incremental `addL0Files` against full `newL0Sublevels` reconstruction.
- Benchmarks cover manifest replay with L0 sublevels, fresh sublevel initialization, and initialization plus base compaction picking.

## Control Flow
The datadriven `define` path parses table specs into `TableMetadata`, sorts L0 by sequence number and L1+ by smallest key, constructs `LevelMetadata`, and either initializes sublevels from scratch or updates an existing sublevel structure with newly added L0 files. Compaction commands use the already-built `l0Sublevels` state to select compactions and then render the selection. State mutation commands mark files compacting and update L0 file state so subsequent queries observe active compactions.

## State And Persistence Behavior
The test reads actual MANIFEST testdata through Pebble record readers, so it covers persisted `VersionEdit` replay into in-memory `Version` and `L0Organizer` state. The datadriven parser constructs in-memory table metadata directly and initializes physical backings because later version/sublevel code expects backing state to exist.

## Dependencies And Integration Points
It integrates with `record.Reader`, `VersionEdit`, `BulkVersionEdit`, `Version`, `L0Organizer`, `LevelMetadata`, table compaction state, `base.Comparer`, and `datadriven`. Testdata under `internal/manifest/testdata/l0_sublevels` and `MANIFEST_import` is part of the effective contract.

## Risks And Test Signals
The riskiest areas are L0 ordering with overlapping user keys, incremental sublevel updates that depend on previous indices, active compaction state, and flush split key generation. The randomized equivalence test is a strong regression signal for `addL0Files`, while the benchmarks signal performance risk in manifest replay and L0 compaction selection.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/l0_sublevels_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/layer.go -->
# sources/storage-engines/pebble/internal/manifest/layer.go

## Purpose
`layer.go` defines `Layer`, a compact descriptor for a logical section of the LSM: a whole level, an L0 sublevel, or the flushable-ingests layer above the LSM. It gives code that iterates or reports across levels/sublevels a single typed value instead of loose integer conventions.

## Important APIs, Types, And Functions
- `Layer` stores a `layerKind` and `uint16` value.
- `Level(level int)` constructs whole-level layers for L0 through L6 and panics on invalid levels.
- `L0Sublevel(sublevel int)` constructs a specific L0 sublevel, bounded by `uint16`.
- `FlushableIngestsLayer()` constructs the special ingest layer.
- `IsSet`, `IsFlushableIngests`, `IsL0Sublevel`, `Level`, `Sublevel`, `String`, and `SafeFormat` expose inspection and redaction-safe formatting.

## Control Flow
Construction validates inputs and stores a kind/value pair. Accessors branch on the kind and panic on invalid use, for example calling `Level` on flushable ingests or `Sublevel` on a non-sublevel. Formatting maps kinds to strings like `L4`, `L0.2`, and `flushable-ingests`.

## State And Persistence Behavior
`Layer` is in-memory identification state only. It is not a manifest record format; it is used to label table iteration, ordering checks, and logging/debug output.

## Dependencies And Integration Points
The file depends on `NumLevels`, CockroachDB errors, and redaction formatting. `Version.AllLevelsAndSublevels`, `Version.AllTables`, and `CheckOrdering` consume `Layer` values.

## Risks And Test Signals
The main risks are invalid layer construction and accidental misuse of level/sublevel accessors. Panics are deliberate invariant enforcement. `layer_test.go` locks down user-visible string output for levels, sublevels, and flushable ingests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/layer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/layer_test.go -->
# sources/storage-engines/pebble/internal/manifest/layer_test.go

## Purpose
This small unit test verifies the public string representation of all normal `Layer` variants. It protects debugging, datadriven output, and error messages that rely on stable layer names.

## Important APIs And Functions
- `TestLayer` builds `Level(0)` through `Level(6)`, `L0Sublevel(0)` through `L0Sublevel(2)`, and `FlushableIngestsLayer`.
- It asserts `Layer.String()` returns `L0`, `L1`, `L0.0`, and `flushable-ingests` style values.

## Control Flow
The test iterates a fixed case table and runs each expected string as a subtest. Each subtest calls `String` once and compares with `require.EqualValues`.

## State And Persistence Behavior
There is no persistent state. The test only covers the in-memory layer value's presentation contract.

## Dependencies And Integration Points
It depends on the constructors in `layer.go` and `testify/require`. The checked strings appear in version debug output and ordering errors.

## Risks And Test Signals
The file does not test invalid constructor panics or accessor misuse. Its signal is narrow but important: changes to layer display names will be caught immediately.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/layer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/level_metadata.go -->
# sources/storage-engines/pebble/internal/manifest/level_metadata.go

## Purpose
`level_metadata.go` implements the in-memory collection, slicing, and iteration model for table metadata within one LSM level. It wraps Pebble's copy-on-write B-tree with aggregate metrics, immutable `LevelSlice` views, and bounded/filterable `LevelIterator`s.

## Important APIs, Types, And Functions
- `LevelMetadata` holds the level number, aggregate table size, aggregate blob reference size, virtual table count/size, and a B-tree of `*TableMetadata`.
- `MakeLevelMetadata`, `insert`, `remove`, `clone`, and `release` construct and mutate the B-tree-backed level state while maintaining aggregate metrics.
- `LevelSlice` is an immutable bounded view over a level, with `All`, `Iter`, `Len`, `Reslice`, `Overlaps`, `HasOverlap`, and size-summing helpers.
- `LevelIterator` provides `First`, `Last`, `Next`, `PeekNext`, `Prev`, `SeekGE`, `SeekLT`, `Current`, `Take`, and `Filter`.
- `KeyType` distinguishes combined, point-only, and range-only table keyspaces.

## Control Flow
Levels are built with sequence-number ordering for whole L0 and smallest-key ordering for L1+ or L0 sublevels. Slices preserve immutable iterator bounds over the underlying B-tree. Seek operations binary-search within key-sorted B-tree nodes, then constrain to slice bounds and skip tables filtered out by key type. `Reslice` passes mutable start/end iterators to a caller and constructs a new inclusive bounded slice from their final positions.

## State And Persistence Behavior
This file owns in-memory state derived from manifests rather than the manifest format itself. Clones preserve copy-on-write B-tree references; `release` decrements table references through the B-tree. Aggregate table size, estimated reference size, and virtual table metrics must remain consistent with B-tree insertions/removals.

## Dependencies And Integration Points
It depends on the manifest B-tree implementation, `TableMetadata` bounds and key-type helpers, `base.UserKeyBounds`, metrics, invariants, and Go iterator sequences. `Version`, `BulkVersionEdit.Apply`, compaction picking, overlap calculation, and scan cursors all use `LevelMetadata` and `LevelIterator`.

## Risks And Test Signals
Important risks include using `SeekGE`/`SeekLT` on a sequence-sorted whole L0 iterator, off-by-one errors from inclusive slice bounds, stale aggregate metrics after edits, and filter logic that misses point-only or range-only tables. `level_metadata_test.go` covers datadriven iteration, filtered iteration, seek correctness over 10k tables, find behavior across levels, and `PeekNext` consistency.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/level_metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/level_metadata_test.go -->
# sources/storage-engines/pebble/internal/manifest/level_metadata_test.go

## Purpose
This test file validates `LevelMetadata`, `LevelSlice`, and `LevelIterator` behavior, especially bounded iteration, seeking, filtering by key type, and finding exact table metadata within levels.

## Important APIs And Helpers
- `TestLevelIterator` uses datadriven commands over `testdata/level_iterator` to define slices and execute iterator commands.
- `TestLevelIteratorFiltered` uses parsed debug table metadata and filters iterators by point/range/both keyspaces.
- `runIterCmd` drives `first`, `last`, `next`, `prev`, `seek-ge`, and `seek-lt`; it randomly cross-checks `PeekNext` against `Next`.
- `makeTestTableMetadata` builds 10,000 non-overlapping tables and key probes for deterministic seek testing.
- `TestLevelIteratorSeek` and `TestLevelIteratorFind` exercise direct seek and exact lookup behavior.

## Control Flow
Datadriven tests parse table definitions, construct key-sorted `LevelSlice`s, optionally reslice them, and run scripted iterator operations. The large seek test alternates probe keys that do and do not exist in table bounds to verify `SeekGE` and `SeekLT` choose the expected adjacent table.

## State And Persistence Behavior
There is no on-disk persistence, but the tests initialize `TableBacking` where needed because level B-trees and release paths rely on refcountable metadata. The datadriven filter tests parse the same debug format used by other manifest tests.

## Dependencies And Integration Points
The tests integrate with `ParseTableMetadataDebug`, `NewLevelSliceKeySorted`, `MakeLevelMetadata`, `bytealloc`, `testkeys`, and datadriven fixtures under `testdata/level_iterator*`.

## Risks And Test Signals
The tests strongly signal correctness for B-tree seek semantics and bounded iterators. Residual risk remains around invariant-only panics and uncommon interleavings of filters with reslicing, but the scripted and large-table coverage catches common iterator regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/level_metadata_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/manifest_test.go -->
# sources/storage-engines/pebble/internal/manifest/manifest_test.go

## Purpose
This external-package integration test validates `Version.CalculateInuseKeyRanges` against a randomly generated Pebble database produced by metamorphic tests. It checks the manifest replay path and in-use range calculation on realistic database state.

## Important APIs And Helpers
- `TestInuseKeyRangesRandomized` runs a metamorphic workload, replays the generated manifest, chooses random spans and start levels, and verifies coverage.
- `replayManifest` uses `pebble.Peek`, `record.Reader`, `VersionEdit.Decode`, `BulkVersionEdit.Accumulate`, `BulkVersionEdit.Apply`, and `L0Organizer.PerformUpdate` to reconstruct the current manifest version.

## Control Flow
The test creates random Pebble operations, executes them, replays the manifest into a fresh `Version`, then performs 200 randomized range checks. For every overlapping file at or below the chosen level, it truncates the file bounds to the query span and asserts some returned in-use range contains that truncated span.

## State And Persistence Behavior
This file explicitly exercises persisted MANIFEST state. It does not rely on in-memory DB structures after the metamorphic run; it reopens manifest records and reconstructs the version state from encoded edits.

## Dependencies And Integration Points
It integrates the public `pebble` package with `internal/manifest`, `metamorphic`, `record`, `base`, `testkeys`, and build tags. Running in package `manifest_test` gives a useful external-consumer perspective.

## Risks And Test Signals
The test is randomized and may expose rare in-use range bugs that deterministic fixtures miss. It is heavier than normal unit tests and scales down operation count under slow/instrumented builds. Failures include the random seed for replay.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/manifest_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/marked_for_compaction.go -->
# sources/storage-engines/pebble/internal/manifest/marked_for_compaction.go

## Purpose
`marked_for_compaction.go` implements an ordered set of tables that have been marked for compaction, commonly from upgrade or manifest state. It gives compaction picking a deterministic priority order.

## Important APIs, Types, And Functions
- `MarkedForCompactionSet` wraps a generic Google B-tree keyed by `tableAndLevel`.
- Ordering is decreasing LSM level, then increasing table `SeqNums.High`, then increasing table number.
- `Count`, `Insert`, `Delete`, `Contains`, `Clone`, and `Ascending` provide set operations and ordered iteration.

## Control Flow
The set lazily allocates its B-tree on first insert. `Insert` uses `ReplaceOrInsert` and panics under invariants if the table-level pair already existed. `Ascending` wraps B-tree ascent in an `iter.Seq2`.

## State And Persistence Behavior
The set is in-memory state inside `Version` and `BulkVersionEdit`. Marks are persisted by `VersionEdit.TablesMarkedForCompaction` records and reconstructed/updated during `BulkVersionEdit.Accumulate` and `Apply`.

## Dependencies And Integration Points
It depends on `TableMetadata`, `base.TableNum`, `github.com/google/btree`, and invariants. `VersionEdit` decodes/encodes mark records, and `BulkVersionEdit` deletes marks when tables are deleted while carrying marks into the new `Version`.

## Risks And Test Signals
The priority order is subtle: highest levels are processed first, with older/lower high sequence numbers earlier within a level. Duplicate inserts are caught only in invariant builds. Version edit tests cover parse/encode/apply paths for compaction marks.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/marked_for_compaction.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/scan_cursor.go -->
# sources/storage-engines/pebble/internal/manifest/scan_cursor.go

## Purpose
`scan_cursor.go` models a resumable position for scanning the LSM by level and by file order, currently focused on finding external virtual tables after a cursor within user-key bounds.

## Important APIs, Types, And Functions
- `ScanCursor` stores `Level`, lower-bound `Key`, and tie-breaking `SeqNum`.
- `EndScanCursor`, `AtEnd`, `String`, and `Compare` provide cursor primitives.
- `MakeScanCursor` and `MakeScanCursorAfterFile` position at or immediately after a table.
- `FileIsAfterCursor` compares a file against a cursor.
- `NextExternalFile`, `NextExternalFileOnLevel`, and `FirstExternalFileInLevelIter` find the next external virtual table across L0 sublevels and L1+ levels.

## Control Flow
The scan orders files by level, then smallest user key, and for L0 ties by high sequence number. `NextExternalFile` searches the current level and advances to the next level when none is found. L0 searches all sublevel iterators and chooses the minimum cursor position; L1+ uses the level iterator directly. Candidate files must be virtual and backed by an external object according to the object provider.

## State And Persistence Behavior
The cursor is lightweight resumable in-memory state. It references persisted table metadata indirectly through `Version`, but the cursor itself is not encoded in the manifest.

## Dependencies And Integration Points
It depends on `base.Compare`, `base.UserKeyBounds`, `objstorage.Provider`, `objstorage.IsExternalTable`, `Version.Levels`, `Version.L0SublevelFiles`, and `LevelIterator.SeekGE`.

## Risks And Test Signals
Risks include off-by-one advancement after a file, L0 tie ordering, end-bound trimming, and behavior when the cursor is already at end. `scan_cursor_test.go` covers datadriven external-file iteration and checks idempotence before advancing the cursor.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/scan_cursor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/scan_cursor_test.go -->
# sources/storage-engines/pebble/internal/manifest/scan_cursor_test.go

## Purpose
This datadriven test validates `ScanCursor` traversal across manifest versions and external virtual table detection. It verifies cursor stability and advancement semantics.

## Important APIs And Helpers
- `mockExternalObjProvider` implements `objstorage.Provider.Lookup` and marks disk file numbers at or above a threshold as external.
- `TestScanCursor` supports datadriven `define` and `cursor` commands.
- Cursor script commands include `start`, `next-external-file`, and `iterate-external-files`.

## Control Flow
`define` parses a debug version and initializes L0 sublevels. `cursor` creates user-key bounds, initializes the cursor, repeatedly calls `NextExternalFile`, and advances with `MakeScanCursorAfterFile`. The test deliberately calls `NextExternalFile` twice before advancing to ensure the cursor still points to the same file.

## State And Persistence Behavior
The test uses debug-version parsing, not actual manifest record replay. It models external object state through a deterministic object provider threshold.

## Dependencies And Integration Points
It integrates `ParseVersionDebug`, `L0Organizer`, `ScanCursor`, `objstorage` metadata, `base.UserKeyBounds`, and datadriven fixture `testdata/scan_cursor`.

## Risks And Test Signals
The test catches regressions in cursor advancement, external filtering, and L0/L1+ scan ordering. It does not cover object provider errors because the mock lookup always succeeds.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/scan_cursor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/table_metadata.go -->
# sources/storage-engines/pebble/internal/manifest/table_metadata.go

## Purpose
`table_metadata.go` defines the central metadata object for tables in Pebble versions. It separates logical physical/virtual SSTable metadata from backing file metadata, tracks bounds, sequence numbers, blob references, compaction state, statistics, and formatting/parsing/validation helpers.

## Important APIs, Types, And Functions
- `TableMetadata` stores table identity, size, sequence bounds, point/range bounds, blob references, virtual table parameters, synthetic transforms, compaction state, stats, and reference counts.
- `TableBacking` represents the physical backing file shared by a physical SSTable or one or more virtual SSTables.
- `TableBackingProperties`, `TableStats`, `TableInfo`, `RangeKeyKinds`, and `CompactionState` expose supporting metadata.
- Key methods include `Ref`, `Unref`, `InitPhysicalBacking`, `InitVirtualBacking`, `AttachVirtualBacking`, `ValidateVirtual`, `SetCompactionState`, `ExtendPointKeyBounds`, `ExtendRangeKeyBounds`, `Validate`, `DebugString`, and `ParseTableMetadataDebug`.
- Bound helpers include `Smallest`, `Largest`, `UserKeyBounds`, `UserKeyBoundsByType`, `ContainsKeyType`, `SmallestBound`, `LargestBound`, and `boundsMarker`.

## Control Flow
Bounds are extended through dedicated methods so point bounds, range bounds, combined overall bounds, `HasPointKeys`, `HasRangeKeys`, and `RangeKeyKinds` stay consistent. Refcount methods cascade from table references to backing references and report obsolete backings when counts reach zero. Virtual backing attachment builds `virtual.VirtualReaderParams` from final bounds. Validation checks bounds, key kinds, sequence ranges, backing presence, blob reference depth, and synthetic prefix/suffix invariants.

## State And Persistence Behavior
Most fields are reconstructed from MANIFEST version edits. `CompactionState`, `AllowedSeeks`, stats population flags, reference counts, and `LargestSeqNumAbsolute` restart behavior are in-memory concerns. Blob reference estimates are stable over a table lifetime because level aggregate sizes depend on them. Physical backing references determine when table files become obsolete.

## Dependencies And Integration Points
The file depends on `base`, `sstable`, `sstable/block`, `sstable/virtual`, invariant utilities, structured parsing, redaction, and blob metadata types. It is used by every manifest version, level, version edit, compaction, event, and object lookup path.

## Risks And Test Signals
Risks are high because this struct sits on most manifest paths. Particular hazards include virtual table backing invariants, range-key-only bounds, manifest backward compatibility, blob reference depth/value-size semantics, refcount underflow, and struct-size growth. `table_metadata_test.go` covers bound extension, debug parse roundtrips, statistic scaling, and expected struct sizes; version edit tests cover persisted encoding.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/table_metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/table_metadata_test.go -->
# sources/storage-engines/pebble/internal/manifest/table_metadata_test.go

## Purpose
This test file validates table metadata bound maintenance, debug parsing/formatting, virtual statistic scaling, and memory footprint constraints.

## Important APIs And Tests
- `TestExtendBounds` is datadriven and exercises `ExtendPointKeyBounds`, `ExtendRangeKeyBounds`, overall bound type selection, and `boundsMarker`.
- `TestTableMetadata_ParseRoundTrip` checks point-only, range-only, mixed point/range, whitespace-tolerant parsing, virtual tables, and blob references through `ParseTableMetadataDebug`, `Validate`, and `DebugString`.
- `TestTableMetadata_ScaleStatistic` verifies integer scaling for virtual SSTables, including invalid sizes and overflow-resistant cases.
- `TestTableMetadataSize` asserts `TableMetadata` and `TableBacking` byte sizes on amd64/arm64.

## Control Flow
The bound test parses scripted internal-key ranges, mutates one `TableMetadata`, and emits verbose state after every extension. Roundtrip tests parse debug strings, validate metadata invariants, and compare normalized debug output. Size tests use `unsafe.Sizeof`.

## State And Persistence Behavior
The tests primarily cover in-memory metadata, but debug strings mirror manifest test fixtures and parser behavior used by version debug tests. Virtual scaling indirectly protects persisted size semantics for virtual tables.

## Dependencies And Integration Points
The tests use datadriven fixture `testdata/file_metadata_bounds`, `base` key parsing/formatting, and `testify/require`. Struct-size checks are directly tied to manifest memory amplification.

## Risks And Test Signals
The strongest signals are around mixed point/range bounds and memory footprint. Tests do not exhaustively cover `Validate` corruption paths or refcounting; those are exercised indirectly through version application and release tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/table_metadata_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/version.go -->
# sources/storage-engines/pebble/internal/manifest/version.go

## Purpose
`version.go` defines a Pebble manifest `Version`: the complete in-memory set of tables and blob files visible in the LSM. It also implements version lists, ordering checks, overlap queries, range-key-set region tracking, reference release, and in-use key range calculation.

## Important APIs, Types, And Functions
- `Version` contains `Levels`, `L0SublevelFiles`, `RangeKeyLevels`, `BlobFiles`, `MarkedForCompaction`, `RangeKeySetRegions`, refcount/list links, and a comparer.
- Constructors include `NewInitialVersion`, `NewVersionWithFiles`, and `NewVersionForTesting`.
- Formatting/parsing includes `String`, `DebugString`, `DebugStringFormatKey`, `ParseVersionDebug`, and `describeSublevels`.
- Query and iteration APIs include `KeyRange`, `ExtendKeyRange`, `SortBySmallest`, `Contains`, `Overlaps`, `HasOverlap`, `AllLevelsAndSublevels`, and `AllTables`.
- Lifetime APIs include `Ref`, `Unref`, `UnrefLocked`, `unrefFiles`, `ObsoleteFiles`, and `VersionList`.
- `CalculateInuseKeyRanges`, `seekGT`, `CheckOrdering`, and blob invariant validation implement core correctness logic.

## Control Flow
Constructors build per-level B-trees and range-key subsets, populate range-key-set region trees, and initialize L0 organizer state. Overlap logic uses iterative expansion for whole L0 because L0 files can overlap transitively; L1+ uses key-sorted level slices. `CalculateInuseKeyRanges` descends levels, merging existing accumulated ranges with overlapping files and skipping files contained within already accumulated ranges. `CheckOrdering` applies relaxed legacy checks for whole L0 and strict sorted non-overlap checks for L1+ and L0 sublevels.

## State And Persistence Behavior
`Version` is the in-memory result of manifest replay and subsequent version edits. Reference counts keep table backings and blob files alive until no referenced version needs them. `RangeKeyLevels` and `RangeKeySetRegions` duplicate derived state for fast range-key queries. `L0SublevelFiles` must be populated by `L0Organizer` after `BulkVersionEdit.Apply`.

## Dependencies And Integration Points
The file integrates with level metadata, table metadata, blob metadata, virtual backing lifetime, L0 organizer, region trees, version edits, compaction picking, scan cursors, and event/debug tooling. It depends on `base`, `axisds/regiontree`, `strparse`, and Go `iter`/`slices` helpers.

## Risks And Test Signals
Major risks include L0 overlap expansion, range-key-only handling, version refcount release, blob file invariant drift, and ordering compatibility with older RocksDB/Pebble manifests. `version_test.go` covers key range union, overlaps, contains, unref/list removal, ordering datadriven cases, deterministic and randomized in-use range calculation, and zero-allocation iteration.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/version_edit.go -->
# sources/storage-engines/pebble/internal/manifest/version_edit.go

## Purpose
`version_edit.go` defines the MANIFEST edit record format and the machinery for decoding, encoding, accumulating, and applying edits to produce new `Version` instances. It is the main bridge between durable manifest records and in-memory version state.

## Important APIs, Types, And Functions
- Disk-format constants include LevelDB, RocksDB, and Pebble tags for logs, files, range keys, backing tables, blob files, excise records, and compaction marks.
- `VersionEdit` holds comparer/log/file-number state, deleted and new tables, backing table additions/removals, blob file changes, excise operations, and tables marked for compaction.
- Entry types include `DeletedTableEntry`, `DeletedBlobFileEntry`, `NewTableEntry`, `TableMarkedForCompactionEntry`, and `ExciseOpEntry`.
- `Decode` and `Encode` implement binary manifest serialization.
- `DebugString`, `String`, and `ParseVersionEditDebug` support test/debug text representations.
- `BulkVersionEdit` accumulates one or more edits and `Apply` creates a new `Version`.

## Control Flow
`Decode` reads uvarint tags until EOF, dispatching each tag to field-specific parsing. New table tags handle old point-only encodings, range-key encodings with bound markers, creation time, virtual backing file numbers, synthetic prefix/suffix, and blob references. `Encode` chooses the narrowest compatible new-file tag and emits custom fields when needed. `Accumulate` cancels add/delete pairs, resolves decoded virtual table backings, updates blob additions/deletions, and carries compaction marks. `Apply` clones current version state, updates blob files, removes deleted tables, inserts added tables with read-compaction seek counts and blob reference resolution, maintains range-key indexes/regions, and validates local ordering around edits.

## State And Persistence Behavior
This file directly owns persistent manifest semantics. Some state is intentionally absent from persistence, such as compaction state and table refcounts, while comparer name, log numbers, file numbers, sequence number upper bounds, table bounds, virtual/backing metadata, blob files, excise records, and compaction marks are encoded. Decoded virtual tables require backing resolution during accumulation.

## Dependencies And Integration Points
It depends on `base`, table/blob metadata, level metadata, version construction, L0 organizer callers, record log readers/writers outside this file, `sstable` synthetic transforms, and invariant checks. It also carries compatibility behavior for LevelDB/RocksDB tags and column family rejection.

## Risks And Test Signals
Compatibility and data-loss risks are high. Important hazards include custom tag ignore rules, range-key bound marker correctness, virtual backing lifecycle, blob reference `BackingValueSize` preservation, add/delete accumulation cancellation, and ordering validation after apply. `version_edit_test.go` provides roundtrip, decode fixture, last-sequence compatibility, datadriven apply, and debug parse roundtrip coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/version_edit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/version_edit_test.go -->
# sources/storage-engines/pebble/internal/manifest/version_edit_test.go

## Purpose
This test file validates manifest version edit serialization, decoding compatibility, virtual backing resolution, blob-reference persistence, edit application, and debug text parsing.

## Important APIs And Tests
- `checkRoundTrip` encodes and decodes a `VersionEdit` and diffs the result.
- `TestVERoundTripAndAccumulate` verifies virtual table backings are restored after decode plus `BulkVersionEdit.Accumulate`.
- `TestVERoundTripBackingValueSizeEqualValueSize` protects a regression where virtual blob reference `BackingValueSize` was lost when equal to `ValueSize`.
- `TestVersionEditRoundTrip` covers complete edits with log numbers, created/removed backings, deleted tables, point/range tables, and range-key kinds.
- `TestVersionEditDecode` uses `testdata/version_edit_decode` to encode/decode hex and quoted binary fixtures.
- `TestVersionEditEncodeLastSeqNum` locks RocksDB-compatible encoding of zero `LastSeqNum` when `ComparerName` is set.
- `TestVersionEditApply` datadriven-applies one or more edits to named versions.
- `TestParseVersionEditDebugRoundTrip` checks text parser/formatter normalization.

## Control Flow
The tests build representative `TableMetadata` objects, initialize physical or virtual backings, serialize edits, decode them, optionally accumulate to repair virtual backing pointers, and compare debug or structural output. The datadriven apply test seeds versions from debug text, splits multiple edits on a sentinel line, accumulates them into one bulk edit, applies them, and updates L0 sublevels.

## State And Persistence Behavior
These tests are directly about persistent MANIFEST behavior. They check binary encodings, decoded nil metadata/backing handling, persistent blob reference values, and compatibility fields that influence recovery.

## Dependencies And Integration Points
The file integrates `VersionEdit`, `BulkVersionEdit`, `TableMetadata`, `BlobFileMetadata`, `L0Organizer`, debug parsers, datadriven fixtures, binary hex fixtures, and `sstable` synthetic prefix/suffix types.

## Risks And Test Signals
The strongest signals cover manifest compatibility and virtual/blob edge cases. Remaining risk is that random map iteration can affect text order for paths not explicitly sorted, although the implementation sorts many debug outputs to stabilize tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/version_edit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/version_test.go -->
# sources/storage-engines/pebble/internal/manifest/version_test.go

## Purpose
This test file validates version-level queries, ordering checks, reference-list behavior, in-use key range calculation, and allocation behavior for table iteration.

## Important APIs And Tests
- `TestIkeyRange` checks `KeyRange` union behavior.
- `TestOverlaps` datadriven-tests `Version.Overlaps` with inclusive/exclusive bounds.
- `TestContains` validates exact file membership for overlapping L0 and non-overlapping L1.
- `TestVersionUnref` verifies last unref removes a version from `VersionList`.
- `TestCheckOrdering` runs datadriven ordering validation fixtures.
- `TestCalculateInuseKeyRanges` covers deterministic multi-level range merging cases.
- `TestCalculateInuseKeyRangesRandomized` checks generated non-overlapping levels over many random spans.
- `TestIterAllocs` asserts `LevelSlice.All` and `LevelMetadata.All` perform zero allocations.

## Control Flow
Tests construct versions from either explicit `TableMetadata` instances or debug strings, initialize L0 organizers, invoke version APIs, and compare returned slices/booleans/debug output. The randomized in-use test builds non-overlapping files per level and asserts every overlapping file span is contained within some calculated range.

## State And Persistence Behavior
Most tests use in-memory versions, but debug parsing mirrors manifest debug output. Reference tests cover version-list state and deletion callback flow.

## Dependencies And Integration Points
The tests depend on `NewVersionForTesting`, `ParseVersionDebug`, `L0Organizer`, `LevelMetadata`, `TableMetadata`, `base`, `testkeys`, datadriven fixtures, and `testing.AllocsPerRun`.

## Risks And Test Signals
Coverage is strong for overlaps, range merging, and ordering. Randomized tests log seeds to reproduce failures. The allocation test guards performance-sensitive iterator APIs used heavily by compaction and query planning.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/version_test.go -->
