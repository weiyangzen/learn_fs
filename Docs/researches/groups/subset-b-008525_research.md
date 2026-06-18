<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/ingest_test.go -->
# sources/storage-engines/pebble/ingest_test.go

## Purpose
This file is Pebble's broad ingest test suite. It exercises local SST ingestion, ingest-and-excise, shared and external tables, blob-backed value separation, flushable ingests, WAL recovery, file linking/copying, sequence-number rewriting, validation, cleanup, concurrent ingest/compaction races, and many-SSTable benchmarks.

## Important APIs, Types, And Functions
The tests call public APIs such as `DB.Ingest`, `DB.IngestWithStats`, `DB.IngestAndExcise`, `DB.IngestAndExciseWithBlobs`, `Download`, `Compact`, `Flush`, `ScanInternal`, and iterators. Test harness helpers include `testIngestSharedImpl`, `blockedCompaction`, `linkAndRemovePredicate`, `ingestCrashFS`, `noRemoveFS`, `fatalCapturingLogger`, and `testFileNumAllocator`.

## Control Flow
Datadriven tests build DBs and external files, ingest them, wait for flush or compaction state, and compare LSM/iterator/metric output. Regression tests construct precise races: pending commits before ingest target selection, flushable ingest WAL replay, concurrent compaction overlap, and crash-like file-number reuse after linking before manifest application.

## State And Persistence Behavior
The suite verifies manifest edits, file-number allocation, local link/copy behavior, remote/shared backing metadata, blob file mappings, L0 versus lower-level placement, ingest-as-flush persistence, WAL-disabled reopen semantics, and cleanup of linked table and blob objects on error.

## Dependencies And Integration Points
It integrates `vfs`, `errorfs`, `objstorageprovider`, `remote`, `sstable`, `valsep`, `manifest`, `keyspan`, `rangekey`, `record`, table filters, datadriven command helpers, and test comparers. The tests stress DB commit sequencing, memtable overlap detection, LSM overlap checking, validation jobs, event listeners, metrics, and object storage.

## Risks And Edge Cases
Coverage focuses on corrupt SST endpoints versus internal blocks, read-only errors, invalid excise spans, ingestion overlapping mutable/queued memtables and large batches, hidden link/remove errors, file reuse after crash, non-deterministic concurrent LSM placement, and stale blob mappings during WAL replay.

## Test Signals
This file is itself test coverage. It uses datadriven golden files plus direct assertions for returned stats, metrics, LSM descriptions, iterator output, value reads, manifest replay ordering, cleanup errors, and background/fatal error routing.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/ingest_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/ingest_with_blobs.go -->
# sources/storage-engines/pebble/ingest_with_blobs.go

## Purpose
This file defines the public local-ingest shape for SSTables that have associated blob files, and helper logic for opening those blob files as object-storage readables during ingestion.

## Important APIs, Types, And Functions
`LocalSSTables` is a slice of `LocalSST`; `TotalFiles` counts both SSTs and blob paths. `LocalSST` carries `Path` and `BlobPaths`. `closeReadables` combines close errors. `createBlobReadables` opens blob paths through `Options.FS` and wraps them with `objstorage.NewSimpleReadable`.

## Control Flow
For each blob path, `createBlobReadables` opens the file, builds an `objstorage.Readable`, appends it, and on any open/wrap error closes everything opened so far and combines errors.

## State And Persistence Behavior
The file does not persist metadata itself. It transfers local paths into readable handles for later ingest machinery, preserving ownership boundaries by closing partially initialized resources on failure.

## Dependencies And Integration Points
It depends on `Options.FS`, `objstorage.Readable`, and Cockroach errors. It is consumed by blob-aware ingest paths tested in `ingest_test.go`.

## Risks And Edge Cases
The main risk is resource leakage during partial failure. The code deliberately closes prior readables and combines errors, but callers must still close the returned readables after successful use.

## Test Signals
Blob ingest tests in `ingest_test.go` cover local blob ingestion, flushable blob ingests, WAL recovery, and cleanup of blob files.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/ingest_with_blobs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal.go -->
# sources/storage-engines/pebble/internal.go

## Purpose
This file re-exports selected internal Pebble primitives through the `pebble` package, mostly for tests, compatibility, and advanced callers that need file-format-visible key concepts.

## Important APIs, Types, And Functions
It aliases `SeqNum`, `InternalKeyKind`, `InternalKeyTrailer`, `InternalKey`, `KeyRange`, `internalIterator`, `topLevelIterator`, `AttributeAndLen`, `ShortAttribute`, `LazyFetcher`, and `CompressionCounters`. It exports internal key-kind constants, `MakeInternalKey`, `MakeInternalKeyTrailer`, `IsCorruptionError`, and deprecated `ErrCorruption`.

## Control Flow
There is no complex control flow: constructors delegate to `base.MakeInternalKey` and `base.MakeTrailer`, and corruption checks delegate to `base.IsCorruptionError`.

## State And Persistence Behavior
The constants are part of Pebble's file format and must remain stable. The aliases expose existing internal representations without storing state.

## Dependencies And Integration Points
The file integrates `internal/base` and `sstable/block` with the top-level Pebble package. Ingest, iterator, lazy-value, and corruption tests use these exported forms.

## Risks And Edge Cases
Changing constant values or alias semantics would be an on-disk compatibility break. `ErrCorruption` remains for compatibility but callers should prefer `IsCorruptionError`.

## Test Signals
Indirectly covered throughout Pebble tests that construct internal keys, key ranges, lazy values, compression counters, and corruption assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/ackseq/ackseq.go -->
# sources/storage-engines/pebble/internal/ackseq/ackseq.go

## Purpose
This package tracks monotonically allocated sequence numbers and advances an acknowledged base only when all lower sequence numbers are acknowledged.

## Important APIs, Types, And Functions
`S` stores atomic `next`, locked `base`, and a fixed bitmap window. `New` initializes the base and next number. `Next` atomically allocates a sequence number. `Ack` marks a number, detects invalid or duplicate acknowledgements, and returns the contiguous base-advance delta. `getLocked`, `setLocked`, and `clearLocked` manipulate bitmap bits.

## Control Flow
`Next` uses atomic increment. `Ack` locks, validates `seqNum` against `[base, base+windowSize)`, rejects already-set bits, sets the bit, and then repeatedly clears bits at `base` while advancing.

## State And Persistence Behavior
State is in memory only. The fixed window covers about one million pending acknowledgements using 128 KiB. Bits are reused modulo the window as the base advances.

## Dependencies And Integration Points
It uses `sync`, `sync/atomic`, and Cockroach errors. It is suitable for commit or scheduling pipelines that need out-of-order completion with in-order publication.

## Risks And Edge Cases
Acknowledging below base, too far beyond base, or twice before base advance returns errors. The caller must not allow more than `windowSize` unacknowledged allocated numbers ahead of base.

## Test Signals
`ackseq_test.go` covers in-order, reverse-order, double-ack before and after base advance, below-base, and beyond-window cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/ackseq/ackseq.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/ackseq/ackseq_test.go -->
# sources/storage-engines/pebble/internal/ackseq/ackseq_test.go

## Purpose
This file validates `ackseq.S` allocation and acknowledgement semantics.

## Important APIs, Types, And Functions
Tests call `New`, `Next`, and `Ack`, and assert returned deltas plus error text for invalid acknowledgements.

## Control Flow
`TestAckInOrder` expects every ack to advance by one. `TestAckOutOfOrder` allocates several numbers, acks high numbers first with zero delta, then acks the base and expects a full advance. Other tests exercise duplicate and range failures.

## State And Persistence Behavior
The tests focus on in-memory bitmap/base transitions. No persistent state is involved.

## Dependencies And Integration Points
It uses Go testing and `strings.Contains` for error classification.

## Risks And Edge Cases
The tests distinguish two duplicate-ack modes: already below base reports out-of-range, while still in-window reports already-acked. The beyond-window test acks a number that was never allocated, confirming range validation is based on base/window, not `next`.

## Test Signals
Together these tests give direct coverage of ordered and unordered acknowledgements, base advancement, bitmap clearing, and error boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/ackseq/ackseq_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/arena.go -->
# sources/storage-engines/pebble/internal/arenaskl/arena.go

## Purpose
This file implements the lock-free byte arena backing Pebble's concurrent arena skiplist.

## Important APIs, Types, And Functions
`Arena` holds an atomic allocation offset and backing buffer. `NewArena` reserves offset zero as nil. `Size`, `Capacity`, `alloc`, `getBytes`, `getPointer`, and `getPointerOffset` provide allocation and offset/pointer conversion. `ErrArenaFull`, `MaxArenaSize`, and `nodeAlignment` define limits.

## Control Flow
Allocation validates alignment under invariants, checks prior overflow, atomically adds padded size, verifies capacity plus overflow allowance, and returns an aligned offset.

## State And Persistence Behavior
All state is process-local. Failed allocation may push the internal counter beyond capacity; `Size` saturates to `MaxArenaSize`.

## Dependencies And Integration Points
It depends on `sync/atomic`, `unsafe`, `invariants`, and errors. `node.go` and `skl.go` allocate skiplist nodes from it.

## Risks And Edge Cases
Pointer arithmetic and offset truncation are load-bearing. Oversized buffers are truncated or panic under invariants. `alloc` requires power-of-two alignment and reserves overflow bytes for truncated node towers.

## Test Signals
`arena_test.go` checks overflow saturation, and `race_test.go` checks node allocation at arena boundaries under the race detector.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/arena.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/arena_test.go -->
# sources/storage-engines/pebble/internal/arenaskl/arena_test.go

## Purpose
This file tests arena allocation accounting around maximum sizes and overflow.

## Important APIs, Types, And Functions
`newArena` wraps `NewArena`. `TestArenaSizeOverflow` calls `alloc`, `Size`, and compares errors with `ErrArenaFull`.

## Control Flow
The test allocates under the limit, then attempts a `math.MaxUint32` allocation that would overflow with 32-bit arithmetic, then verifies subsequent allocations continue failing.

## State And Persistence Behavior
It checks only in-memory arena offset state and saturation of `Size`.

## Dependencies And Integration Points
It uses `math`, `testing`, and `testify/require`.

## Risks And Edge Cases
The key regression risk is offset accounting wrapping around after a failed oversized allocation. The test expects `Size` to saturate to `MaxArenaSize`.

## Test Signals
Direct assertions cover success under the limit, `ErrArenaFull` over the limit, and stable full-state behavior afterward.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/arena_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/flush_iterator.go -->
# sources/storage-engines/pebble/internal/arenaskl/flush_iterator.go

## Purpose
This file defines the specialized memtable flush iterator for arena skiplists.

## Important APIs, Types, And Functions
`flushIterator` embeds `Iterator` and implements `base.InternalIterator`. `String`, `First`, and `Next` are implemented; `SeekGE`, `SeekPrefixGE`, `SeekLT`, `NextPrefix`, and `Prev` panic with assertion failures because flush code only performs forward full scans.

## Control Flow
`First` delegates to `Iterator.First`. `Next` mirrors `Iterator.Next` but omits bounds and prefix checks for the flush path, advancing level-zero links, decoding the key, and returning an in-place value.

## State And Persistence Behavior
It reads immutable skiplist nodes during flush and exposes in-place values. It does not mutate or persist state.

## Dependencies And Integration Points
It depends on `base.InternalIterator` and `errors.AssertionFailedf`. `Skiplist.NewFlushIter` constructs it for memtable flush code.

## Risks And Edge Cases
Because `Next` intentionally mirrors `Iterator.Next`, drift between the two implementations can introduce flush-only bugs. Unsupported operations panic, so callers must respect the restricted iterator contract.

## Test Signals
Coverage is indirect through skiplist iteration tests and Pebble flush/ingest tests that flush memtables.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/flush_iterator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/iterator.go -->
# sources/storage-engines/pebble/internal/arenaskl/iterator.go

## Purpose
This file implements the arena skiplist `base.InternalIterator`, including forward/reverse seeks, bounds, strict-prefix iteration, and a small seek-using-next optimization.

## Important APIs, Types, And Functions
`Iterator` stores the skiplist, split function, current node, bounds, cached bound nodes, prefix, and current KV. Important methods include `SeekGE`, `SeekPrefixGE`, `SeekLT`, `First`, `Last`, `Next`, `NextPrefix`, `Prev`, `SetBounds`, `Close`, `decodeKey`, and `seekForBaseSplice`.

## Control Flow
Seek methods descend skiplist levels through `seekForBaseSplice`, then decode and bound-check the landing node. `TrySeekUsingNext` can walk a few `Next` calls before falling back to a full seek. Prefix mode is set by `SeekPrefixGE` and enforced by `Next`.

## State And Persistence Behavior
Iterator state is pooled through `sync.Pool`. Values are returned as in-place references to arena memory. Bounds cache arbitrary nodes outside range to avoid repeated comparisons after exhaustion.

## Dependencies And Integration Points
It integrates `base.InternalIterator`, `base.Split`, seek flags, `treesteps`, and `Skiplist` link accessors. It is used by memtables and tests with both default and MVCC-like comparers.

## Risks And Edge Cases
The iterator assumes callers honor lower-bound checks for `SeekGE`/`First` and upper-bound checks for `SeekLT`/`Last`. Prefix exhaustion must still update `kv.V` to avoid stale values when a later `TrySeekUsingNext` returns the cached KV.

## Test Signals
`skl_test.go` covers basic iteration, strict-prefix behavior, prefix-exhausted fast path, bounds, seek directions, and concurrent access.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/iterator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/node.go -->
# sources/storage-engines/pebble/internal/arenaskl/node.go

## Purpose
This file defines the arena-resident skiplist node layout and node allocation helpers.

## Important APIs, Types, And Functions
`MaxNodeSize` computes worst-case memory. `links` stores atomic next/prev offsets. `node` stores key offset/size, internal trailer, value size, padding, and a tower. `newNode`, `newRawNode`, `getKeyBytes`, `getValue`, and CAS offset methods manage node content and links.

## Control Flow
`newNode` validates height and key/value sizes, allocates raw node memory, stores the trailer, and copies key/value bytes. `newRawNode` truncates unused tower memory based on height and asks the arena to reserve overflow bytes.

## State And Persistence Behavior
Nodes live in arena memory and store offsets rather than Go pointers, reducing GC interaction. Keys and values are immutable after insertion.

## Dependencies And Integration Points
It depends on `base.InternalKey`, atomics, `unsafe`-compatible arena allocation, and Cockroach errors. `skl.go` links nodes concurrently.

## Risks And Edge Cases
The node struct must not contain heap pointers before arena type-casting. Size overflow, incorrect tower truncation, or bad offset CAS would corrupt skiplist order or crash under the race detector.

## Test Signals
`skl_test.go` checks no-pointer layout and ordering; `race_test.go` checks arena-boundary node allocation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/race_test.go -->
# sources/storage-engines/pebble/internal/arenaskl/race_test.go

## Purpose
This race-build-only test validates node allocation at the end of small arenas, targeting pointer alignment issues detected by Go's race detector.

## Important APIs, Types, And Functions
`TestNodeArenaEnd` repeatedly calls `newArena` and `newNode` with increasing arena sizes.

## Control Flow
The loop expects `ErrArenaFull` until the arena is large enough. Once allocation succeeds, the test stops; race detector instrumentation would report boundary/alignment problems during the attempts.

## State And Persistence Behavior
Only transient arena memory is involved.

## Dependencies And Integration Points
It is guarded by `//go:build race`, uses `testify/require`, and depends on helper constructors from `skl_test.go`.

## Risks And Edge Cases
The targeted risk is a node's truncated tower or overflow reservation straddling the arena boundary in a way unsafe instrumentation observes as invalid memory.

## Test Signals
It provides specialized race-detector coverage not exercised in normal builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/race_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/skl.go -->
# sources/storage-engines/pebble/internal/arenaskl/skl.go

## Purpose
This file implements Pebble's concurrent arena-backed skiplist used by memtables.

## Important APIs, Types, And Functions
`Skiplist` owns the arena, comparer, head/tail nodes, height, and testing flag. `Inserter` caches splices for sequential insertion. Key methods include `NewSkiplist`, `Reset`, `Add`, `Inserter.Add`, `NewIter`, `NewFlushIter`, `newNode`, `randomHeight`, `findSplice`, `findSpliceForLevel`, `keyIsAfterNode`, `getNext`, and `getPrev`.

## Control Flow
Insertion finds per-level splices, allocates a random-height node, raises list height with CAS, and inserts bottom-up by CASing next offsets before prev offsets. On races it helps repair stale prev links and recomputes the affected splice.

## State And Persistence Behavior
State is in arena memory and atomic offsets. Nodes are immutable after insertion; deletion is represented by higher-level tombstones, not physical removal. The inserter cache is caller-local and invalidated on concurrent interference.

## Dependencies And Integration Points
It depends on `base.Compare`, arena/node internals, `math/rand/v2`, atomics, runtime scheduling for race amplification, and skiplist iterators. Pebble memtables rely on it for ordered internal keys.

## Risks And Edge Cases
Concurrent insertion has an intermediate state where forward and backward links disagree. Duplicate internal keys return `ErrRecordExists`. Correct ordering depends on user-key compare plus descending trailer order.

## Test Signals
`skl_test.go` covers empty/full lists, duplicates, concurrency, iterator behavior, bounds, strict-prefix iteration, splice correctness, and benchmarks.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/skl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/skl_bench_test.go -->
# sources/storage-engines/pebble/internal/arenaskl/skl_bench_test.go

## Purpose
This external-package benchmark measures `SeekPrefixGE` performance on Cockroach-style MVCC keys.

## Important APIs, Types, And Functions
`BenchmarkCockroachKeysSeekPrefixGE` builds an `arenaskl.Skiplist` with `cockroachkvs.Compare`, generates random KVs, computes prefixes with `cockroachkvs.Split`, and benchmarks skip distances with and without `TrySeekUsingNext`.

## Control Flow
The benchmark fills a 64 MiB arena until full, then for skip distances 1, 2, 4, 8, and 16 repeatedly seeks to later keys, optionally enabling the next-based fast path and disabling it on wraparound.

## State And Persistence Behavior
State is benchmark-local skiplist memory; no persistence.

## Dependencies And Integration Points
It integrates `cockroachkvs`, `arenaskl`, `base.SeekGEFlags`, and Go benchmarking.

## Risks And Edge Cases
Performance is sensitive to key distribution, shared-prefix density, and whether the seek direction actually satisfies the `TrySeekUsingNext` contract.

## Test Signals
Benchmark results signal regressions in prefix seeking over realistic MVCC-key shapes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/skl_bench_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/skl_test.go -->
# sources/storage-engines/pebble/internal/arenaskl/skl_test.go

## Purpose
This file tests arena skiplist correctness, concurrency, iterator semantics, splice caching, and performance.

## Important APIs, Types, And Functions
Helpers construct keys, values, inserter add functions, lengths, random skiplists, and value extraction. Tests include `TestNoPointers`, `TestEmpty`, `TestFull`, `TestBasic`, concurrent add/read tests, iterator seek/bounds/prefix tests, `TestSkiplistFindSplice`, and benchmarks for read/write, ordered write, iteration, and `SeekPrefixGE`.

## Control Flow
Tests build skiplists with default or testkeys comparers, insert keys in varied orders, seek and iterate forward/backward, and run concurrent goroutines with `testing` delay mode to expose link races.

## State And Persistence Behavior
Only in-memory arena state is tested. Sequence-number ordering is represented through `base.InternalKey` trailers.

## Dependencies And Integration Points
It uses `base`, `testkeys`, `testutils`, `require`, random generators, sync primitives, and the skiplist public/internal APIs.

## Risks And Edge Cases
The file targets duplicate insertion, empty/nil keys, arena full behavior, concurrent one-key races, stale `TrySeekUsingNext` values after prefix exhaustion, lower/upper bound caching, and splice tightness under cached inserters.

## Test Signals
Direct assertions plus benchmarks provide strong coverage of ordering, concurrent safety, prefix iteration correctness, and expected fast paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/skl_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/ascii/table/examples_test.go -->
# sources/storage-engines/pebble/internal/ascii/table/examples_test.go

## Purpose
This file provides a Go example for the generic ASCII table renderer.

## Important APIs, Types, And Functions
`ExampleDefine` uses `table.Define`, `String`, `Int`, `Div`, `Render`, `RenderOptions`, and `ascii.Make`.

## Control Flow
The example defines a struct, creates a table layout with dividers, renders rows into an ASCII board, and prints the board.

## State And Persistence Behavior
No persistent state exists; rendering mutates only the in-memory board.

## Dependencies And Integration Points
It demonstrates the public table package from an external test package and its integration with `internal/ascii`.

## Risks And Edge Cases
As an executable example, output changes are API-visible for docs and tests. It also demonstrates widening beyond the initial board width.

## Test Signals
The `// Output:` block is checked by `go test`, validating exact rendered layout.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/ascii/table/examples_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/ascii/table/table.go -->
# sources/storage-engines/pebble/internal/ascii/table/table.go

## Purpose
This file implements a generic ASCII table layout and rendering helper over `ascii.Board`.

## Important APIs, Types, And Functions
`Define`, `Layout`, `HorizontalDividers`, `MakeHorizontalDividers`, `RenderOptions`, `Render`, `Element`, `Field`, `Div`, `Literal`, alignment constants, `String`, `Int`, `Int64`, `StringWithTupleIndex`, `AutoIncrement`, `Count`, `Bytes`, `Float`, `makeFuncField`, and `humanizeFloat` define the table API.

## Control Flow
`Render` filters tuples, renders fields column by column, inserts one-space separators, draws dividers and horizontal lines, widens columns for long values, pads by alignment, and returns the cursor after the rendered table.

## State And Persistence Behavior
`Layout` stores field definitions and optional filter function. Rendering only mutates the supplied `ascii.Board`.

## Dependencies And Integration Points
It depends on `internal/ascii`, humanized count/byte formatting, constraints, and Cockroach errors for assertions.

## Risks And Edge Cases
Header width is enforced at `Define` time, but data values can widen columns. Negative horizontal divider indexes count from the end after filtering. Multi-byte strings use rune counts for padding.

## Test Signals
`table_test.go` uses datadriven tests for alignment, dividers, filtering, tuple indexes, and widening; `examples_test.go` checks documented output.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/ascii/table/table.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/ascii/table/table_test.go -->
# sources/storage-engines/pebble/internal/ascii/table/table_test.go

## Purpose
This file datadriven-tests the ASCII table renderer.

## Important APIs, Types, And Functions
`TestTable` constructs `Layout` values with `Define`, `String`, `StringWithTupleIndex`, `Int`, and `Div`, toggles `RenderOptions.HorizontalDividers`, and renders into `ascii.Board`.

## Control Flow
Each datadriven command chooses a layout, parses alignment and divider args, optionally filters odd rows, resets the board, renders the table, and returns board text.

## State And Persistence Behavior
The board is reused across commands through `Reset`; no persistent state exists.

## Dependencies And Integration Points
It uses `datadriven`, `strconv`, `testing`, and `internal/ascii`.

## Risks And Edge Cases
Coverage targets tuple-index preservation after filtering, long values exceeding declared widths, no-divider layout, left/right/center alignment, and negative/explicit horizontal dividers.

## Test Signals
Golden datadriven output catches layout regressions, spacing changes, and divider placement changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/ascii/table/table_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/ascii/whiteboard.go -->
# sources/storage-engines/pebble/internal/ascii/whiteboard.go

## Purpose
This file implements a simple growable rune board for rendering ASCII/text diagrams.

## Important APIs, Types, And Functions
`Board` holds a rune buffer and width. `Make`, `At`, `NewLine`, `String`, `Render`, `Reset`, `write`, `repeat`, `growWidth`, `lines`, and `row` manage board storage. `Cursor` provides `Offset`, `Down`, `Right`, row/column setters, `SetCarriageReturnPosition`, `Printf`, `WriteString`, `Repeat`, and `NewlineReturn`.

## Control Flow
Board access grows rows lazily. Writes grow width if needed, handle multi-rune strings, and newline handling returns to a configurable carriage-return column.

## State And Persistence Behavior
State is an in-memory mutable rune grid. `Render` trims trailing spaces per row and prefixes indentation.

## Dependencies And Integration Points
It depends on `bytes`, `fmt`, `slices`, and `strings`. The table renderer builds on `Cursor`.

## Risks And Edge Cases
Width growth must preserve existing rows. Rune indexing avoids byte-width bugs for UTF-8 text, but visual display width is still rune-based, not terminal-cell-width aware.

## Test Signals
`whiteboard_test.go` covers datadriven board commands and newline carriage-return behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/ascii/whiteboard.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/ascii/whiteboard_test.go -->
# sources/storage-engines/pebble/internal/ascii/whiteboard_test.go

## Purpose
This file tests the ASCII board and cursor write behavior.

## Important APIs, Types, And Functions
`TestASCIIBoardDatadriven` exercises `Make`, `At`, and `WriteString` through testdata commands. `TestASCIIBoard` checks `Printf`, `Reset`, `SetCarriageReturnPosition`, and cursor row/column results.

## Control Flow
The datadriven harness creates boards and writes parsed lines at row/column positions. The direct test writes multi-line strings and verifies rendered output.

## State And Persistence Behavior
Only in-memory board mutation is covered. `Reset` clears the buffer while preserving reusable capacity.

## Dependencies And Integration Points
It integrates datadriven, `crstrings`, `strparse`, and `testify/require`.

## Risks And Edge Cases
The tests focus on automatic row growth, newline handling, and carriage-return column preservation during repeated newlines.

## Test Signals
Golden outputs and direct assertions catch changes in trimming, row growth, and returned cursor positions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/ascii/whiteboard_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/cleaner.go -->
# sources/storage-engines/pebble/internal/base/cleaner.go

## Purpose
This file defines obsolete-file cleanup strategies for Pebble.

## Important APIs, Types, And Functions
`Cleaner` is the cleanup interface. `NeedsFileContents` marks cleaners requiring file contents. `DeleteCleaner` removes files. `ArchiveCleaner` moves log, manifest, table, and blob files into an `archive` directory and removes other file types.

## Control Flow
`DeleteCleaner.Clean` calls `fs.Remove`. `ArchiveCleaner.Clean` switches on `FileType`, creates an archive directory for persistent file types, renames the file there, or removes unsupported types.

## State And Persistence Behavior
This file directly affects filesystem state: deletion or rename into an archive sibling directory. `ArchiveCleaner` advertises that it needs file contents.

## Dependencies And Integration Points
It depends on `vfs.FS` and base `FileType`. Options and object storage cleanup code select a cleaner policy.

## Risks And Edge Cases
Archive behavior for secondary FS log files is noted as a TODO. Rename failures, directory creation failures, and platform-specific file semantics propagate as errors.

## Test Signals
Coverage is indirect through DB/file cleanup tests, including ingest cleanup and obsolete file handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/cleaner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/close_helper.go -->
# sources/storage-engines/pebble/internal/base/close_helper.go

## Purpose
This file provides an idempotent wrapper around `io.Closer`.

## Important APIs, Types, And Functions
`CloseHelper` returns a `closeHelper` containing the original closer. `closeHelper.Close` closes once, nils the stored closer, and returns nil on later calls.

## Control Flow
`Close` snapshots the closer, returns nil if already nil, otherwise clears the field before invoking the underlying `Close`.

## State And Persistence Behavior
State is only the wrapper's pointer to the closer. It prevents duplicate close side effects in error/defer paths.

## Dependencies And Integration Points
It depends only on `io`. It can wrap files, readers, writers, or cleanup resources throughout Pebble.

## Risks And Edge Cases
The helper is not synchronized; concurrent `Close` calls on the same wrapper can race. It is intended for single-goroutine cleanup paths.

## Test Signals
No direct test in this subset; behavior is simple and likely exercised indirectly by callers that rely on idempotent cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/close_helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/compaction_grant_handle.go -->
# sources/storage-engines/pebble/internal/base/compaction_grant_handle.go

## Purpose
This file defines interfaces and small types used by compactions to report resource usage to a scheduler.

## Important APIs, Types, And Functions
`CompactionGrantHandleStats` currently carries cumulative write bytes. `CompactionGrantHandle` requires `Started`, `MeasureCPU`, `CumulativeStats`, and `Done`. `CompactionGoroutineKind` identifies primary SST/blob worker goroutines. `CPUMeasurer` abstracts CPU measurement, and `NoopCPUMeasurer` is a no-op implementation.

## Control Flow
There is no implementation flow besides `NoopCPUMeasurer.MeasureCPU` doing nothing. Comments define lifecycle ordering: `Started` first, frequent measurement/stat calls, and `Done` after version install without locks.

## State And Persistence Behavior
The file stores no state and persists nothing. It defines contracts for runtime scheduling.

## Dependencies And Integration Points
Compaction code and schedulers use these contracts to pace disk/CPU work and schedule follow-up compactions.

## Risks And Edge Cases
Callers must avoid holding locks across `Done` because it may synchronously schedule more work. Missing `MeasureCPU` calls can undercount resource use.

## Test Signals
No direct tests in this subset; expected coverage is through compaction scheduler tests elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/compaction_grant_handle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/comparer.go -->
# sources/storage-engines/pebble/internal/base/comparer.go

## Purpose
This file defines Pebble's key comparison contract, default bytewise comparer, formatting helpers, comparer assertion wrapper, and comparer validation suite.

## Important APIs, Types, And Functions
Core function types include `Compare`, `Equal`, `AbbreviatedKey`, `Separator`, `Successor`, `ImmediateSuccessor`, `Split`, `CompareRangeSuffixes`, `ComparePointSuffixes`, `FormatKey`, `FormatValue`, and `ValidateKey`. `Comparer` groups them; `EnsureDefaults`, `Prefix`, `HasPrefix`, `DefaultComparer`, `MinUserKey`, `FormatBytes`, `MakeAssertComparer`, and `CheckComparer` implement behavior and checks.

## Control Flow
`EnsureDefaults` validates required fields and fills split, compare, equality, suffix comparison, and formatting defaults. `DefaultComparer` implements bytewise abbreviated keys, separators, successors, and immediate successors. `CheckComparer` sorts suffixes, validates split and key validity, and exhaustively checks compare/equal/prefix/suffix consistency.

## State And Persistence Behavior
Comparer name is persisted in the DB format; opening with a different comparer name is invalid. The rest is runtime behavior over keys.

## Dependencies And Integration Points
Comparers are central to memtables, SSTables, bloom prefixes, range keys, suffix ordering, and tests. The file depends on bytes, binary encoding, random sampling, formatting, slices, UTF-8, and Cockroach errors.

## Risks And Edge Cases
Incorrect compare/split/suffix relationships can corrupt ordering. Separator/successor must return valid keys. Range suffix comparison may be stricter than point suffix comparison, and assertion comparers depend on `ValidateKey` being correct.

## Test Signals
`comparer_test.go` covers default separator/successor outputs, default comparer validation, default filling, abbreviated key ordering, and benchmarking.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/comparer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/comparer_test.go -->
# sources/storage-engines/pebble/internal/base/comparer_test.go

## Purpose
This file tests the default comparer and abbreviated-key helper.

## Important APIs, Types, And Functions
Tests exercise `DefaultComparer.Separator`, `DefaultComparer.Successor`, `CheckComparer`, `Comparer.EnsureDefaults`, and `DefaultComparer.AbbreviatedKey`. `BenchmarkAbbreviatedKey` measures the abbreviated-key path.

## Control Flow
Separator and successor tests run table-driven cases. Default comparer and default-filling tests call `CheckComparer`. Abbreviated-key testing generates random keys, sorts them by comparer, and ensures abbreviated keys never invert ordering.

## State And Persistence Behavior
No persistent state is involved; tests validate runtime ordering helpers that affect persisted table layout elsewhere.

## Dependencies And Integration Points
It uses Go testing, random generation, slices sorting, time seeding, and formatting to keep benchmark values live.

## Risks And Edge Cases
Cases cover prefix relationships, byte increment behavior, `0xff` runs, empty successor input, and equality handling for abbreviated keys.

## Test Signals
The tests provide direct regression coverage for bytewise comparer shortening and ordering invariants.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/base/comparer_test.go -->
