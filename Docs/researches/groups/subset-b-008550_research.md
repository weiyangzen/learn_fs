# Research Group: subset-b-008550

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/writer_test.go -->
# sources/storage-engines/pebble/sstable/writer_test.go

## Purpose
This Go test file exercises Pebble's SSTable writer and rewriter behavior across table formats, writer modes, value-block encodings, blob-value handles, tiering histograms, block-property collectors, cache invalidation, and benchmarked write paths. It is a high-signal regression suite for the `sstable` package because the writer owns durable table bytes, metadata boundaries, range-key/range-delete blocks, table properties, block indexes, optional filters, and lazy value placement.

## Important APIs, Types, and Functions
The central entry points are `TestWriter`, `TestRewriter`, `runDataDriven`, `TestWriterWithValueBlocks`, `TestWriterWithBlobValueHandles`, `TestWriterWithTieringHistogram`, `TestWriterClearCache`, `TestWriterBlockPropertiesErrors`, `TestWriter_TableFormatCompatibility`, `TestWriterRace`, and the writer benchmarks. `tableFormatFile` binds datadriven fixture paths to `TableFormat` constants. `formatWriterMetadata` formats `WriterMetadata` bounds, sequence ranges, and selected properties. `discardFile` implements `objstorage.Writable` for fast writer tests and benchmarks without filesystem persistence. `testBlockPropCollector` injects failures at `AddPointKey`, `AddRangeKeys`, `FinishDataBlock`, `FinishIndexBlock`, and `FinishTable` to validate error propagation.

The datadriven harness exposes commands including `build`, `build-raw`, `open-writer`, `write-kvs`, `close`, `scan`, `scan-compaction`, `get`, `scan-range-del`, `scan-range-key`, `layout`, `decode-layout`, `rewrite`, and `props`. These commands integrate with helper functions from other test files such as `runBuildMemObjCmd`, `runBuildRawCmd`, `runBuildCmd`, `runRewriteCmd`, `ParseTestSST`, and `ParseTestKVsAndSpans`.

## Control Flow
`TestWriter` and `TestRewriter` iterate table formats Pebble v2 through v8 and dispatch into format-specific datadriven files. `runDataDriven` maintains one active `Reader`, `RawWriter`, and in-memory object, closing stale objects before rebuilds. Build commands create writer options with the testkeys comparer and selected table format, write fixture input, reopen readers over the produced object, and return normalized metadata. Scan commands use ordinary iterators, compaction iterators, raw range-delete iterators, and raw range-key iterators to render persisted content. Layout commands inspect block handles either through a reader or by decoding the raw object bytes.

The value-block tests build SSTables with optional block size and value-block disabling, then inspect both logical scans and "raw" row-block payloads by intentionally removing value-block readers from iterators. The blob-handle and tiering tests parse fixture KVs with `blobtest.Values`, configure short-attribute/tiering extractors, build max-format SSTables, and inspect layouts. Pool-clear tests allocate internal buffers/tasks, mutate state, call `clear`, and assert reusable fields are retained while owned pointers and estimates are reset. Error tests force low block sizes so block/index/table finish points are reached predictably.

## State and Persistence Behavior
The file tests persisted table bytes through in-memory objects, `vfs.NewMem`, and `objstorageprovider.NewFileWritable`. It verifies durable metadata: smallest/largest point keys, range deletion bounds, range key bounds, sequence number ranges, table properties, value-block property counts, blob separated-value counts, tiering histogram artifacts, and table layout. `TestWriterClearCache` is especially persistence-sensitive: it builds an SSTable, reads its block handles, poisons the cache entries for those offsets, rebuilds the table at the same file number, and confirms the writer cleared cache entries for all blocks it wrote.

The writer close path is treated as a durable lifecycle boundary. `TestDoubleClose` documents a compatibility expectation: a second `Close` returns `errWriterClosed` rather than succeeding. `TestParallelWriterErrorProp` reaches into the row writer's write queue to ensure asynchronous write errors are not lost by `Close`. The race test builds many tables concurrently and reopens the resulting bytes to ensure writer-local state is not shared unsafely.

## Dependencies and Integration Points
The tests depend on Pebble internals across `base`, `blobtest`, `cache`, `sstableinternal`, `testkeys`, `objstorage`, `objstorageprovider`, `block`, `rowblk`, `valblk`, `bloom`, and `vfs`. They also rely on Cockroach libraries `datadriven`, `leaktest`, and `errors`, plus `testify/require`. Integration coverage reaches reader iteration, compaction iteration, raw keyspan iterators, table layout decoding, cache handles, block-property collectors/filters, table format compatibility checks, and benchmarks that model compaction splitting by calling `EstimatedSize` before each write.

## Risks and Edge Cases
The most important risks covered are format regressions, missing error propagation from asynchronous block writes, stale cache entries after rewriting file numbers, incorrect lazy value ownership, value-handle decoding regressions, block-property lifecycle errors, race-prone writer buffer reuse, and feature usage below the minimum table format. The tests intentionally inspect internal iterator types in the value-block raw scan; that gives precise coverage but can require maintenance when iterator implementations change. Several tests depend on datadriven golden output, so benign formatting changes in metadata/property string output may require coordinated fixture updates.

## Test Signals
This file is itself the test signal for `sstable` writing. Passing it indicates tables can be built, rewritten, decoded, scanned, and benchmarked across supported formats. The most targeted signals are datadriven fixture diffs for table contents/layout/properties, cache poisoning failures in `TestWriterClearCache`, explicit injected errors in `TestWriterBlockPropertiesErrors`, and race detector value from `TestWriterRace`. Benchmarks provide performance trend signals across table formats, block sizes, filter enablement, and compression profiles.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/writer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/table_stats.go -->
# sources/storage-engines/pebble/table_stats.go

## Purpose
This file implements Pebble's asynchronous table-statistics loading and estimation machinery. Table statistics influence compaction picking, deletion compensation, delete-only compactions, metrics, and compression reporting, but loading them can require table and blob-file I/O. The implementation queues new tables, incrementally scans existing tables after `Open`, populates `TableMetadata` and blob metadata with loaded properties, and computes estimates for point and range tombstones.

## Important APIs, Types, and Functions
The scheduler entry points are `maybeCollectTableStatsLocked`, `updateTableStatsLocked`, `shouldCollectTableStatsLocked`, and `collectTableStats`. `collectedStats` couples `*manifest.TableMetadata` with `manifest.TableStats` until `DB.mu` can be reacquired for mutation. Loading/scanning functions include `loadNewFileStats`, `scanReadStateTableStats`, `scanBlobFileProperties`, `loadTableStats`, `loadTablePointKeyStats`, and `loadTableRangeDelStats`.

Estimation and helper functions include `seqNumRangeOfKind`, `estimateSizesBeneath`, `examineTablesBeneathTombstones`, `sanityCheckStats`, `estimateDiskUsageInTableAndBlobReferences`, `maybeSetStatsFromProperties`, `pointDeletionsBytesEstimate`, and `newCombinedDeletionKeyspanIter`. The file also defines manifest annotators: `deletionBytesAnnotator`, `tablePropsAnnotator`, and `blobCompressionStatsAnnotator`, with supporting `deletionBytes` and `aggregatedTableProps` types.

## Control Flow
New tables enter through `updateTableStatsLocked`, which checks whether any table lacks stats, appends entries to `d.mu.tableStats.pending`, and starts a collector if one is not already running. `collectTableStats` locks `DB.mu`, atomically claims the pending slice or initial-load scan work, marks `loading`, releases the mutex, loads a read state, performs I/O, unreferences the read state, then reacquires the mutex to populate metadata, broadcast waiters, possibly enqueue wide tombstones, and schedule compaction if tombstone compensation changed.

When there is pending work, `loadNewFileStats` skips tables that already have stats or are no longer live at the expected level. Otherwise, initial loading uses `scanReadStateTableStats`, bounded to 50 tables per scan, and then `scanBlobFileProperties`. Table scanning checks remote object sizes for non-shared, non-external remote files before reading stats. `loadTableStats` reads table backing properties only if needed, opens tables with `fileCache.withReader`, loads range deletion stats when range tombstones exist, and estimates point deletion bytes when point deletions exist.

Range deletion stats flow through `newCombinedDeletionKeyspanIter`, which merges defragmented range deletion spans with range-key delete spans. `loadTableRangeDelStats` estimates reclaimable bytes beneath each merged span, applies a bottommost-level heuristic for tombstones that may delete data within the same table, and records `tombspan.WideTombstone` candidates when lower tables could be dropped or excised. `estimateSizesBeneath` and `examineTablesBeneathTombstones` scan lower LSM levels to calculate average logical value sizes, compression ratios, full-overlap estimates, partial-overlap estimates, and delete-only compaction candidates.

## State and Persistence Behavior
The persistent inputs are MANIFEST metadata, table backing properties, SSTable range-deletion/range-key blocks, table sizes, blob references, and blob-file properties. The in-memory outputs are stored in `TableMetadata.PopulateStats`, `TableBacking.PopulateProperties`, and blob physical metadata `PopulateProperties`. The job is intentionally asynchronous and bounded: only one stats goroutine runs at a time through `d.mu.tableStats.loading`, and `loadedInitial` flips only after both table stats and blob properties are loaded for the current version.

The collector reads under a referenced read state and mutates shared metadata only after reacquiring `DB.mu` or under the single-collector invariant. It is resilient to concurrent DB close through `d.closed` and `bgCtx` checks. It may retry later by returning `moreRemain` or by re-triggering `maybeCollectTableStatsLocked`. Extreme deletion estimates are guarded by `sanityCheckStats`, which panics in invariant builds and rate-limits logging otherwise.

## Dependencies and Integration Points
This code integrates with `manifest.Version`, `manifest.TableMetadata`, `manifest.TableBackingProperties`, blob-file metadata, object provider lookup/size APIs, the table file cache, `sstable.Reader`, `block.ReadEnv`, range-key/range-delete keyspan iterators, `tombspan.WideTombstone`, compaction scheduling, event listeners, DB metrics annotations, and Pebble format-version gates such as `FormatVirtualSSTables`. It depends on `crmath` for scaled blob reference estimates, `crtime` for rate-limited logs, `invariants` for defensive checks, and `redact` for safe logging.

## Risks and Edge Cases
Important risks include expensive O(number of tables/files) scans, stale read states causing work on files that have moved or disappeared, remote object size mismatches, inaccurate deletion byte estimates from compression-ratio approximations, bottommost tombstone heuristics overestimating ingested tables, and L0 sublevel limitations noted in comments. `newCombinedDeletionKeyspanIter` is subtle: it assumes range deletion bounds are already valid for physical/virtual tables and uses bound assertions to catch old or migrated invalid tombstones. Blob-file property loading can lag table stats and impacts compression metrics until completed.

## Test Signals
`table_stats_test.go` supplies datadriven coverage for scheduling, initial load, metadata stats, range deletion iteration, and metrics after reopen. The file's own comments and guards signal operational expectations: no user-latency I/O under `DB.mu`, bounded work per scan, event listener notification on initial load, background error reporting for retryable failures, and compaction scheduling when deletion estimates create tombstone compensation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/table_stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/table_stats_test.go -->
# sources/storage-engines/pebble/table_stats_test.go

## Purpose
This test file validates the behavior implemented by `table_stats.go`. It covers asynchronous table-stat collection, datadriven database mutations, waiting for initial and pending stats, range deletion/range-key deletion span merging, and metric stability after reopening a database with table and blob compression properties.

## Important APIs, Types, and Functions
The exported test functions are `TestTableStats`, `TestTableRangeDeletionIter`, and `TestStatsAfterReopen`. `TestTableStats` creates an in-memory DB with automatic compactions disabled, a test comparer, minimum supported format, a custom `TableStatsLoaded` listener, and a test logger. It delegates most operations to existing datadriven helpers including `runDBDefineCmd`, `runBatchDefineCmd`, `runBuildCmd`, `runIngestCmd`, `runWaitForTableStatsCmd`, `runCompactCmd`, `runMetadataCommand`, `runSSTablePropertiesCmd`, and `runIngestAndExciseCmd`.

`TestTableRangeDeletionIter` builds raw SSTables with `sstable.NewRawWriter`, encodes `keyspan.ParseSpan` input, synthesizes `manifest.TableMetadata` bounds from writer metadata, and opens the resulting SSTable to call `newCombinedDeletionKeyspanIter`. `TestStatsAfterReopen` uses randomized options and workload generation to compare JSON-rendered table and blob compression metrics before close and after reopen plus `waitTableStats`.

## Control Flow
`TestTableStats` drives `testdata/table_stats` commands. `define` recreates a DB from a datadriven description and returns current version text. `disable` and `enable` toggle `DisableTableStats`, with enable calling `maybeCollectTableStatsLocked`. Mutation commands write batches, flush, build/ingest SSTables, ingest-and-excise, or compact ranges, returning LSM or error text. Wait commands block on `d.mu.tableStats.cond` until pending stats or initial loading complete. Metadata and property commands inspect current-version SSTable state.

`TestTableRangeDeletionIter` has a two-phase flow: `build` creates `tmp.sst` in memory from text spans and records bounds on a manifest metadata object; `spans` reopens the table, constructs the combined deletion iterator, and prints every merged span or `(none)`. This directly tests the span merge/defragmentation semantics that feed range deletion byte estimates and wide tombstone discovery.

`TestStatsAfterReopen` constructs many flushed SSTables with random keys/values, occasionally compacts random ranges, then snapshots metrics. After close and reopen, it waits for asynchronous stats loading and asserts that table/blob compression metrics match exactly. The workload forces many small tables by using small block and target file sizes and raises thresholds to avoid stop-write interference.

## State and Persistence Behavior
The tests use `vfs.NewMem` to keep persistence deterministic but still exercise real MANIFEST/table/blob metadata flows across close and reopen. `loadedInfo` is protected by `d.mu` and validates that the event listener fires when initial stats are loaded. The datadriven tests explicitly close snapshots before DB reset, close/reopen the DB, and inspect the current manifest version. The reopen metrics test ensures compression metrics derived from in-memory annotations are reconstructed from persisted table/blob properties after the async collector finishes.

## Dependencies and Integration Points
Dependencies include `datadriven`, `leaktest`, `testify/require`, `manifest`, `keyspan`, `testkeys`, `testutils`, `objstorage`, `objstorageprovider`, `sstable`, `colblk`, and `vfs`. The tests integrate table stats with Pebble DB operations: batching, flushing, ingestion, compaction, manual excision, metrics collection, event listeners, and raw SSTable range-key/range-delete blocks.

## Risks and Edge Cases
The datadriven suite is sensitive to scheduler timing and must explicitly wait on `tableStats.cond` to avoid races. Randomized options in `TestStatsAfterReopen` increase coverage but can make failures need seed/log inspection. Range deletion iterator tests rely on manually constructed `TableMetadata` bounds matching writer metadata; this is valuable for isolating iterator logic, but it does not exercise the whole DB ingestion path. Metrics equality after reopen is a strict signal and may require updates if metric serialization or compression accounting intentionally changes.

## Test Signals
Passing tests signal that stats can be disabled/enabled, pending and initial loads complete, `TableStatsLoaded` is emitted, metadata properties are populated, deletion iterator merging matches expected datadriven output, and compression metrics are stable across reopen. Failures usually point to either async scheduler state, manifest/table property reconstruction, range tombstone span logic, or metric annotation cacheability.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/table_stats_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/testdata/Makefile -->
# sources/storage-engines/pebble/testdata/Makefile

## Purpose
This small Makefile regenerates Pebble test fixture databases under `sources/storage-engines/pebble/testdata`. It provides a single `rebuild` target that removes and recreates four staged database directories using `make-db.go`.

## Important APIs, Types, and Functions
The relevant Make targets are `all` and `.PHONY: rebuild`. `all` aliases to `rebuild`. The `rebuild` recipe loops over stages `1 2 3 4`, removes `db-stage-<stage>`, and runs `go run make-db.go <stage>`.

## Control Flow
Running `make` or `make rebuild` performs a shell loop. Each iteration deletes the previous fixture directory with `rm -fr db-stage-$$stage` and invokes the Go fixture generator for that stage. The Makefile depends on `make-db.go`, so changes to the generator are the explicit reason to rebuild.

## State and Persistence Behavior
The Makefile's only persistent state is the `db-stage-1` through `db-stage-4` fixture directories. It destructively replaces those directories in the testdata tree. The resulting contents are Pebble databases at successive mutation stages and are intended to be checked or consumed as deterministic test fixtures.

## Dependencies and Integration Points
It depends on a working Go toolchain, module resolution for Pebble imports, and the local `make-db.go` program. It integrates with tests or tooling that read the staged `db-stage-*` directories.

## Risks and Edge Cases
The recipe is intentionally destructive for matching fixture names. If run from the wrong directory or with a modified generator, it can rewrite fixture data. It does not set `set -e` explicitly, but the chained `&&` within each loop iteration prevents `go run` after a failed removal and causes make to stop on command failure. Whitespace is minimal; portability assumes POSIX shell behavior.

## Test Signals
The Makefile itself has no tests. A successful `make rebuild` signal is creation of all four `db-stage-*` directories by `make-db.go` without Go runtime errors. Downstream tests that consume these fixtures provide the real validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/testdata/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/testdata/make-db.go -->
# sources/storage-engines/pebble/testdata/make-db.go

## Purpose
This standalone Go program generates deterministic staged Pebble database fixtures for testdata. It accepts a stage number from 1 to 4, opens `db-stage-<stage>` with a fixed format major version, performs mutations up to that stage, and exits with a database representing that lifecycle point.

## Important APIs, Types, and Functions
The file defines `const version = pebble.FormatFlushableIngest`, `usage`, and `main`. It uses `pebble.Open`, `DB.Set`, `DB.Delete`, `DB.Close`, and `pebble.Sync`. Standard library dependencies are `fmt`, `log`, `os`, and `strconv`.

## Control Flow
`main` validates exactly one argument and parses it as an integer in `[1,4]`. Stage 1 opens an empty DB and returns if the requested stage is less than 2. Stage 2 writes `foo=one`, `bar=two`, `baz=three`, overwrites `foo=four`, and deletes `bar`. Stage 3 closes and reopens the DB, which the comments say forces a compaction. Stage 4 writes `foo=five`, writes `quux=six`, and deletes `baz`. A deferred close protects normal exits while setting `db = nil` around the explicit reopen avoids double close.

## State and Persistence Behavior
Each invocation writes a separate Pebble directory named by stage. All mutations use `pebble.Sync`, so fixture creation exercises synced WAL/table state rather than unsynced transient updates. The fixed `FormatMajorVersion` stabilizes on-disk format expectations across generator runs. Reopen at stage 3 persists a lifecycle transition that tests can use to inspect post-open or post-compaction behavior.

## Dependencies and Integration Points
The program is invoked by the adjacent Makefile and depends on the Pebble module itself. It integrates with tests that need small real database directories rather than in-memory DBs. Because it imports the package under test, changes to Pebble format constants, option semantics, or compaction-on-open behavior can affect the generated fixtures.

## Risks and Edge Cases
The generator exits with `log.Fatal` on any Pebble error, so partial fixture directories may remain after failures. It assumes the target directory is already removed by the caller; running it over an existing directory may open and mutate existing state. The "forces a compaction" behavior is implicit rather than asserted by this program. Fixture stability depends on the chosen Pebble format version and any default option changes that influence physical layout.

## Test Signals
Successful execution for stages 1 through 4 is the direct signal. Downstream fixture consumers validate whether the produced database state still matches expected behavior. The printed `Stage N` lines are simple progress diagnostics, not a formal output contract.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/testdata/make-db.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/blob.go -->
# sources/storage-engines/pebble/tool/blob.go

## Purpose
This file implements the `pebble tool blob` command group, currently focused on introspecting blob files and printing their physical layout. It provides command wiring, blob-file opening, reader construction, argument traversal, and layout rendering.

## Important APIs, Types, and Functions
`blobT` holds the Cobra root command, the `layout` subcommand, and shared `*pebble.Options`. `newBlob` constructs the command tree. `newReader` converts a `vfs.File` into an `objstorage.Readable`, derives reader/cache options from Pebble options, and opens a `blob.FileReader`. `foreachBlob` delegates path/file traversal to the shared `processFiles` helper for `.blob` files. `runLayout` is the Cobra command implementation.

## Control Flow
`newBlob` creates a root command named `blob` and a subcommand `layout <blob files>` requiring at least one argument. When `layout` runs, `runLayout` obtains stdout/stderr from Cobra, calls `foreachBlob`, prints each path, calls `r.Layout`, and prints either the layout or an error. `foreachBlob` wraps the callback and reader close function and passes them into `processFiles`, allowing individual file paths or directories to be handled uniformly.

`newReader` first wraps the opened VFS file with `objstorage.NewSimpleReadable`. It builds `ReaderOptions` through `b.opts.MakeReaderOptions`, populates cache options if a cache handle is provided, and parses the filename for a file number to improve cache keying. If `blob.NewFileReader` fails, it combines the open error with closing the readable.

## State and Persistence Behavior
The command is read-only with respect to blob files. It opens files, reads blob layout metadata, and closes readers through `processFiles`. Cache state may be used through `CacheOpts` if the surrounding tool configuration supplies a cache handle; file-number parsing makes cache entries stable for recognized Pebble filenames.

## Dependencies and Integration Points
Dependencies include Cobra, `pebble.Options`, `base.ParseFilename`, `cache.Handle`, `sstableinternal.CacheOptions`, `objstorage`, `blob.FileReader`, and `vfs`. The file integrates with the broader Pebble debug tool framework through `processFiles` and with blob-file internals through `blob.FileReader.Layout`.

## Risks and Edge Cases
The command relies on filename parsing only opportunistically; unrecognized names still open but may lack a useful cache file number. Directory traversal and per-file error behavior are delegated to `processFiles`, so UX consistency depends on that shared helper. `context.TODO()` is used for reader creation, which is acceptable for a command-line debug tool but does not expose cancellation at this layer. Layout errors are printed per file and do not stop processing subsequent files.

## Test Signals
`tool/blob_test.go` runs datadriven tests matching `testdata/blob_*`, which likely exercise command output and errors. Additional signal comes from manual use: `blob layout` should print a path line followed by the decoded layout for each `.blob` input.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/blob.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/blob_files.go -->
# sources/storage-engines/pebble/tool/blob_files.go

## Purpose
This file provides manifest-derived blob-file mapping support for Pebble debug tooling. SSTables that reference separated values do not directly encode every physical blob file detail needed for reading; this helper loads manifests to map table numbers to blob references and blob file IDs to physical disk file numbers, then exposes a `sstable.TableBlobContext`.

## Important APIs, Types, and Functions
The main type is `blobFileMappings`, containing `references`, `physicalFiles`, a `blob.ValueFetcher`, a `debugReaderProvider`, and stderr for warnings. Public-style methods are `LoadValueBlobContext`, `Lookup`, and `Close`. The constructor `newBlobFileMappings` reads a list of manifest `fileLoc` values and builds all mappings.

`LoadValueBlobContext` returns `sstable.TableBlobContext{ValueFetcher, References}` for a table number. `Lookup` implements `base.BlobFileMapping`, returning a `base.ObjectInfoLiteral` for the newest physical file associated with a blob file ID. `Close` combines cleanup for the value fetcher and object provider.

## Control Flow
`newBlobFileMappings` opens an object storage provider for the DB directory, initializes maps, initializes the `blob.ValueFetcher` with the mapping object and a cached reader count from `blob.SuggestedCachedReaders(5)`, then iterates over manifest files. Each manifest is opened through the VFS, wrapped in `record.NewReader`, decoded record-by-record as `manifest.VersionEdit`, and inspected for `NewTables` and `NewBlobFiles`. New table entries populate table-number-to-blob-references mapping. New blob file entries append unique physical file numbers per blob file ID.

Errors while reading a manifest are written to stderr and do not abort construction. The comments explain why: a manifest rotation may leave some manifests unreadable while other manifests still provide enough information for debug reads.

## State and Persistence Behavior
This code is read-only against manifests and object storage, but it builds in-memory state that must be closed. The `physicalFiles` map intentionally accumulates every physical file number ever observed for each logical blob file ID rather than only the latest manifest state. `Lookup` returns the last physical file number in that accumulated slice and warns if multiple physical files were seen.

## Dependencies and Integration Points
Dependencies include `manifest.VersionEdit`, `manifest.BlobReferences`, `base.BlobFileID`, `base.ObjectInfoLiteral`, `objstorageprovider`, `record.Reader`, `sstable.TableBlobContext`, `blob.ValueFetcher`, `block.ReadEnv`, and `vfs`. The mapping is used by SSTable debug/read tooling that needs to fetch blob-separated values while scanning tables.

## Risks and Edge Cases
The main correctness risk is stale or ambiguous blob file identity. The file chooses the last physical file when several are observed and logs a warning, but it does not verify file existence or bounds. Manifest read failures are deliberately non-fatal, which helps debugging live/rotating DBs but can leave missing mappings. The cached reader count of 5 is arbitrary and may not match large manifests or high read amplification, though this is acceptable for a debug tool. `Close` must be called to release object provider and fetcher resources.

## Test Signals
Direct tests are not in this file, but `tool/blob_test.go` may exercise separated-value reads indirectly if datadriven blob fixtures require manifest mapping. Runtime warning output for multiple physical files or manifest read errors is an important diagnostic signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/blob_files.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/blob_test.go -->
# sources/storage-engines/pebble/tool/blob_test.go

## Purpose
This file registers datadriven tests for the Pebble blob debug tool. It is intentionally small: its role is to connect the generic tool test runner to all blob-related fixture files.

## Important APIs, Types, and Functions
The only test is `TestBlob(t *testing.T)`, which calls `runTests(t, "testdata/blob_*")`. The implementation of `runTests` lives elsewhere in the `tool` package and provides command execution, fixture parsing, and output comparison.

## Control Flow
When the Go test runner executes `TestBlob`, the shared datadriven harness expands the glob `testdata/blob_*` and runs each matching fixture. Those fixtures are expected to invoke the `blob` command tree, including commands from `blob.go`, and compare stdout/stderr against golden output.

## State and Persistence Behavior
This file does not create state directly. Any persistent or in-memory state comes from the datadriven fixtures and shared harness. Because blob tooling reads real blob files and possibly manifests, the fixtures can validate layout rendering and blob-file mapping behavior without additional test code here.

## Dependencies and Integration Points
It depends on Go's `testing` package and the local `runTests` helper. It integrates with `newBlob`, `blobT.runLayout`, `blobFileMappings`, and other tool package command registration through the shared test harness.

## Risks and Edge Cases
The broad glob keeps the test file low maintenance but can hide which blob behaviors are covered unless the fixture names and contents are inspected. If no files match the glob, coverage depends on how `runTests` reports that condition. The test's precision is entirely determined by datadriven fixture quality.

## Test Signals
Passing `TestBlob` means all `testdata/blob_*` fixtures produce expected command output. Failures should be investigated in the fixture diff first, then in command wiring, blob layout decoding, or manifest-derived blob mapping.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/blob_test.go -->
