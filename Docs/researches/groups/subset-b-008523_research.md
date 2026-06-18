# subset-b-008523 Research

Grouped research report for Pebble download, error, event, excise, external iterator, and file cache sources. Each section preserves the exact source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/download.go -->
# sources/storage-engines/pebble/download.go

## Purpose
Implements `DB.Download`, a high-priority mechanism for making spans independent of external SSTable backing files. It repeatedly discovers external tables overlapping requested key ranges and drives download compactions until no external tables remain in the target spans.

## Important APIs, Types, And Functions
`DownloadSpan` carries `[StartKey, EndKey)` plus `ViaBackingFileDownload`, which selects rewrite compaction versus raw backing-file copy. `DB.Download`, `createDownloadTasks`, `waitForDownloadTasks`, and `removeDownloadTasks` manage the public operation. `downloadSpanTask`, `downloadBookmark`, `newDownloadSpanTask`, `tryLaunchDownloadForFile`, and `tryLaunchDownloadCompaction` implement task progress. `launchDownloadResult` distinguishes launched work, no work, and task completion.

## Control Flow
`Download` checks closed/read-only state, emits `DownloadBegin`, creates tasks from the current version, installs them in `d.mu.compact.downloads`, schedules compaction, and waits on each task channel. On success it restarts discovery, because concurrent ingests may have introduced new external tables; on no tasks it emits a done `DownloadEnd`. A task scans levels top-down and by start key using `manifest.ScanCursor`. Each discovered external or compacting file creates a bookmark. Bookmarks are revisited after launched compactions finish or after other compactions release files.

## State And Persistence Behavior
The method persists data indirectly through compaction output and manifest version edits performed by the normal compaction machinery. Local state is transient: task channels, scan cursors, bookmark ranges, launch counters, and the `d.mu.compact.downloads` queue. `ViaBackingFileDownload` changes whether the compaction rewrites keys or copies a backing file byte-for-byte.

## Dependencies And Integration Points
Depends on manifest scan cursors, `objstorage.IsExternalTable`, compaction picking, `newCompaction`, `d.compact`, event listener `DownloadInfo`, compaction scheduling, and DB format/object-provider state. It integrates with external ingestion, virtual SSTables, excise cancellation, and compaction concurrency.

## Risks And Edge Cases
The cursor/bookmark logic must not miss files that move between levels, shrink through excise, or are already compacting. Cancelled download compactions are not terminal and force bookmark rescanning. Context cancellation and non-cancel compaction errors remove pending tasks. Concurrent external ingestion can cause restarts and means the API is best effort at the instant it returns.

## Test Signals
Covered by `download_test.go` datadriven task tests. Integration signals are `DownloadBegin`/`DownloadEnd`, `DownloadCompactionsLaunched`, compaction errors, and absence of external tables in downloaded spans.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/download.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/download_test.go -->
# sources/storage-engines/pebble/download_test.go

## Purpose
Provides focused datadriven tests for the internal download task scanner and bookmark state machine without running full DB compactions.

## Important APIs, Types, And Functions
`TestDownloadTask` drives `newDownloadSpanTask` and `tryLaunchDownloadCompaction` with parsed manifest versions. `initDownloadTestProvider` builds an object provider with local table backings 1-99 and external backings 100-199. The test hook `downloadSpanTask.testing.launchDownloadCompaction` simulates successful or cancelled downloads.

## Control Flow
The datadriven commands define an LSM, mark tables compacting or not compacting, create a task over a span, and repeatedly attempt launches with a configurable concurrency limit. Simulated successful downloads mutate metadata from virtual/external to local by flipping `Virtual` and `DiskFileNum`; simulated failures return `ErrCancelledCompaction` to force bookmark rescans.

## State And Persistence Behavior
The test does not persist a real Pebble DB. It mutates in-memory `manifest.Version` metadata and object-provider catalogs to model local versus external backings. It prints bookmark cursors, end bounds, task cursor state, launched table numbers, and completion state.

## Dependencies And Integration Points
Depends on `datadriven`, `manifest.ParseVersionDebug`, `manifest.L0Organizer`, `objstorageprovider`, in-memory local and remote object storage, and `testdata/download_task`. It validates the implementation in `download.go` at the manifest/task layer.

## Risks And Edge Cases
The tests focus on files overlapping the left edge of a span, compacting files that cannot launch immediately, cancelled downloads, cursor advancement, and max-concurrent bookmark limiting. They do not validate real compaction output, event listener behavior, or end-to-end external ingestion.

## Test Signals
The output is the signal: deterministic printed cursors/bookmarks show whether the scanner advances, stalls, retries, or completes at the expected point.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/download_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/error_iter.go -->
# sources/storage-engines/pebble/error_iter.go

## Purpose
Defines sentinel iterator implementations that expose a fixed error or empty result while satisfying Pebble internal iterator interfaces. They are useful when callers need a non-nil iterator object even though iteration cannot produce keys.

## Important APIs, Types, And Functions
`errorIter` implements `internalIterator`; all positioning methods return nil, `Error` and `Close` return the stored error, `String` returns `"error"`, and `TreeStepsNode` exposes diagnostic tree-step metadata. `errorKeyspanIter` implements `keyspan.FragmentIterator`; all seek/navigation methods return nil plus the stored error, while `Close` is a no-op.

## Control Flow
There is no complex flow. Callers construct these iterators with an error, then all reads fail deterministically by returning nil data and the stored error through the iterator's error-returning API. `SeekPrefixGE` delegates to `SeekPrefixGEStrict` for interface consistency.

## State And Persistence Behavior
The only state is the immutable `err` field. These iterators do not hold files, buffers, bounds, or context, and they do not persist anything.

## Dependencies And Integration Points
Depends on `base.InternalKV`, seek flag types, `keyspan.FragmentIterator`, `context`, and `treesteps`. `file_cache.go` uses nil-error instances as `emptyIter` and `emptyKeyspanIter`, letting `iterSet.Point`, `RangeDeletion`, and `RangeKey` return non-nil empty iterators.

## Risks And Edge Cases
`errorKeyspanIter.Close` intentionally discards the stored error because its interface has no error return. Callers must check operation errors. A nil stored error makes these iterators behave as empty iterators, so misuse can hide a missing real iterator if the caller expected data.

## Test Signals
There are no direct tests in this file. Coverage is indirect through iterator construction, file cache `iterSet` behavior, and any code path that uses empty or error iterators for absent key kinds.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/error_iter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/error_test.go -->
# sources/storage-engines/pebble/error_test.go

## Purpose
Exercises Pebble's error propagation and crash recovery behavior under injected filesystem failures, read corruption, WAL rotation crashes, and compaction-time crash scenarios.

## Important APIs, Types, And Functions
`panicLogger` converts fatal logging into panics so tests can observe fatal paths. `corruptFS` and `corruptFile` mutate bytes returned by `Read`/`ReadAt`. `expectLSM` checks manifest layout. Tests include `TestErrors`, `TestRequireReadError`, `TestCorruptReadError`, `TestDBWALRotationCrash`, and `TestDBCompactionCrash`.

## Control Flow
`TestErrors` repeatedly runs open, set, flush, compact, iterate, and close with an injected error at successive operation indices until a clean run occurs, then checks expected fatal manifest errors appeared. Read tests build a controlled LSM with range deletion and point data, enable read error or corruption injection, iterate, and require any injected read failure to surface through iterator close or operation errors. Crash tests use crashable MemFS clones to simulate unsynced writes being lost and then reopen/continue.

## State And Persistence Behavior
The tests stress durable metadata, WALs, flushed SSTables, compaction output, and recovery from partially persisted filesystem state. They intentionally clone crash states and reopen DBs to verify persisted state is recoverable or that errors are reported rather than silently ignored.

## Dependencies And Integration Points
Uses `vfs`, `errorfs`, `leaktest`, test key generators, format versions, compaction options, and Pebble public APIs. The cases exercise Open/Close, WAL management, flush, compaction, iterator reads, checksums, and manifest update paths.

## Risks And Edge Cases
Important coverage includes retried background write errors, mandatory foreground read-error reporting, checksum/corruption detection when the FS returns successful reads with bad bytes, crash points during WAL rotation, concurrent compactions with random latency, and Windows-specific timing avoidance.

## Test Signals
Signals are absence of unexpected non-injected errors, expected injected-error messages, iterator close errors when reads fail, corruption errors for modified bytes, and successful reopen after simulated crashes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/error_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/event.go -->
# sources/storage-engines/pebble/event.go

## Purpose
Defines Pebble's event payloads, formatting, default event listener behavior, logging listener, listener teeing, low disk space reporting, and corruption reporting metadata.

## Important APIs, Types, And Functions
Important exported payloads include `DataCorruptionInfo`, `LevelInfo`, `BlobFileCreateInfo`, `BlobFileDeleteInfo`, `BlobFileRewriteInfo`, `BlobFileInfo`, `CompactionInfo`, `FlushInfo`, `DownloadInfo`, manifest/table/WAL events, `TableIngestInfo`, `WriteStallBeginInfo`, `LowDiskSpaceInfo`, and `PossibleAPIMisuseInfo`. `EventListener` contains callback fields for all event types. `EnsureDefaults`, `MakeLoggingEventListener`, `TeeEventListener`, `lowDiskSpaceReporter.Report`, `DB.reportCorruption`, and `ExtractDataCorruptionInfo` are the main behavior.

## Control Flow
Event producers populate an info struct and call the configured listener synchronously. Formatting paths implement `redact.SafeFormatter` so log output is safe by default. `EnsureDefaults` fills nil callbacks, using logger-backed background errors and fatal corruption reporting when possible. `MakeLoggingEventListener` logs every callback. `TeeEventListener` forwards to two listeners after defaulting both. `lowDiskSpaceReporter` emits when disk availability crosses descending thresholds or after a repeat interval.

## State And Persistence Behavior
The file does not mutate durable DB state. It carries event state to users and logs. `reportCorruption` enriches corruption errors with object path, remote locator, user-key bounds, details, and corrupt block data, then joins a hidden carrier error so callers can later extract the payload.

## Dependencies And Integration Points
Integrates with compactions, flushes, blob rewriting, ingestion, downloads, manifests, WALs, table stats, validation, write stalls, disk health checks, low disk monitoring, and corruption detection. It depends on `manifest`, `base`, `objstorage`, `remote`, `vfs`, humanizers, `redact`, and CockroachDB errors.

## Risks And Edge Cases
Callbacks are synchronous and can block DB work if user code is slow. Some callbacks run on hot read or disk-health paths and must not perform blocking I/O. Redaction must distinguish safe local paths from potentially unsafe remote paths. Formatting divides by duration for rates, so callers should provide sensible durations. `PossibleAPIMisuse` includes false-positive caveats for SingleDelete under delete-only compactions.

## Test Signals
Covered by event listener datadriven tests, redaction tests, callback default coverage, low disk reporter tests, block-data hex formatting tests, and corruption event tests for SSTables and blobs.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/event.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/event_listener_test.go -->
# sources/storage-engines/pebble/event_listener_test.go

## Purpose
Validates event listener logging, callback defaulting, listener teeing, redaction, write stall events, low disk space events, and corruption event payload propagation.

## Important APIs, Types, And Functions
`TestEventListener` is a datadriven scenario over open, close, flush, compact, checkpoint, file deletion toggles, ingest, metrics, and SSTable listing. `TestWriteStallEvents`, `redactLogger`, `mockLogger`, `testAllCallbacksSetInEventListener`, `TestLowDiskReporter`, `mockDiskUsageFS`, `TestSSTCorruptionEvent`, and `TestBlobCorruptionEvent` cover narrower event behavior.

## Control Flow
The datadriven test wraps a memory FS with logging and uses `MakeLoggingEventListener`, overriding timing-sensitive fields for deterministic output. Write-stall tests block table creation at strategic points to force memtable or L0 stalls, then wait for stall-end callbacks. Corruption tests create data, remove or mutate SST/blob files, read keys, and compare emitted `DataCorruptionInfo` to the payload extracted from the returned error.

## State And Persistence Behavior
The tests create temporary in-memory DB state, external SSTables, blob files, and low disk usage snapshots. They intentionally alter filesystem contents to verify corruption reporting rather than normal persistence.

## Dependencies And Integration Points
Uses datadriven testdata, `vfs.WithLogging`, in-memory object provider, `sstable.Writer`, event listeners, disk usage APIs, value separation, and error/corruption helpers. It exercises the event API through real DB operations instead of only direct formatting calls.

## Risks And Edge Cases
Determinism is managed by overriding durations, input bytes, and table-stats behavior. Tests guard that all listener constructors set every callback, redaction hides unsafe error contents, low disk notices respect threshold/frequency rules, and corruption details survive wrapping.

## Test Signals
Signals are exact log output, reflected non-nil callbacks, callback invocation counts, expected stall reason strings, stored low disk info, corruption classification, bounds/path correctness, and equality between event payload and extracted error payload.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/event_listener_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/event_test.go -->
# sources/storage-engines/pebble/event_test.go

## Purpose
Tests `DataCorruptionInfo.FormatBlockDataAsHex`, the helper that renders captured corrupt block bytes for diagnostic logs.

## Important APIs, Types, And Functions
`TestFormatBlockDataAsHex` uses datadriven input. It strips whitespace from hex input, decodes bytes, constructs `DataCorruptionInfo{CorruptedBlockData: data}`, and returns `FormatBlockDataAsHex`.

## Control Flow
Each `format` command feeds arbitrary hex into the formatter. Invalid hex fails the test. The formatter behavior under empty input, grouping, offsets, line breaks, and truncation is captured in `testdata/format_block_data_as_hex`.

## State And Persistence Behavior
No DB state or files are used. The test is pure data formatting.

## Dependencies And Integration Points
Depends on `encoding/hex`, `strings`, `datadriven`, and the event payload defined in `event.go`. It supports corruption logging tests by keeping hex output stable.

## Risks And Edge Cases
The key edge cases are empty data, non-multiple-of-line-size data, 8-byte grouping, 64-byte rows, and the maximum dump limit. Since corruption diagnostics may be copied into logs, stable formatting matters for operational debugging.

## Test Signals
The datadriven output is the signal: exact byte offsets and hex group layout must match expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/event_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/example_test.go -->
# sources/storage-engines/pebble/example_test.go

## Purpose
Provides a package example for basic Pebble usage through the public API.

## Important APIs, Types, And Functions
`Example` calls `pebble.Open`, `DB.Set`, `DB.Get`, closer `Close`, and `DB.Close`, using `vfs.NewMem` and `pebble.Sync`.

## Control Flow
The example opens an in-memory DB, writes key `"hello"` with value `"world"`, reads it back, prints key and value, closes the value closer, and closes the DB. The `// Output:` block makes it an executable Go example.

## State And Persistence Behavior
State is held only in a memory filesystem. The write is synchronous with respect to the configured in-memory FS, and the read value remains valid until the returned closer is closed.

## Dependencies And Integration Points
This file is in package `pebble_test`, so it demonstrates external-package usage instead of privileged internals. It integrates with Go's example test runner and validates basic API ergonomics.

## Risks And Edge Cases
The example intentionally avoids advanced options, iteration, batches, and persistence to disk. It demonstrates the important closer lifetime on `Get`, which users must honor to release resources.

## Test Signals
The exact printed output `hello world` is checked by `go test`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/excise.go -->
# sources/storage-engines/pebble/excise.go

## Purpose
Implements `DB.Excise`, which atomically removes all data overlapping a key span, including data visible to snapshots, by applying an ingest/excise operation and splitting affected SSTables into virtual remnants.

## Important APIs, Types, And Functions
`DB.Excise` validates read/write state, unsuffixed bounds, and `FormatVirtualSSTables`. `exciseBoundsPolicy` selects tight, loose, or local-only tight bounds. `exciseTable` creates left/right virtual `TableMetadata` around the excised span. Helpers include `exciseOverlapBounds`, loose/tight bound calculators, `determineExcisedTableSize`, `determineExcisedTableBlobReferences`, and `applyExciseToVersionEdit`.

## Control Flow
The public method delegates to `d.ingest` with an excise span. For each overlapping table, `exciseTable` first drops tables fully contained in the span. Partial overlaps create virtual left and/or right tables. Tight mode opens point, range deletion, and range key iterators to find precise remaining bounds; loose mode uses sentinel bounds without reading remote data. Valid remnants attach the original backing, estimate size, copy scaled blob references, validate metadata, and are added to a version edit while the original is deleted.

## State And Persistence Behavior
Durable changes are manifest edits: delete original tables, optionally record created backing-table metadata, and add new virtual tables referencing existing backing files. Excise does not rewrite table contents in this file; it changes the LSM's metadata view. Blob references are conservatively copied and scaled to preserve value-separation accounting.

## Dependencies And Integration Points
Depends on ingest machinery, manifest metadata, virtual SSTable format, iterators from the file cache, object-storage locality checks, eventually file-only snapshots, range deletion/key iterators, and format-major-version gates. It interacts with download because excised external files may cancel or reshape download compactions.

## Risks And Edge Cases
Inclusive upper bounds require tight bounds and reject truncating point/range data at the inclusive end. Loose remote bounds may create broader virtual files and estimated sizes. Empty remnants must be discarded. EFOS protected ranges can extend overlap work. Size estimation can return zero, so the code forces size one to avoid later divide-by-zero behavior.

## Test Signals
Covered by `excise_test.go` datadriven excise, concurrent excise, and bounds tests. Signals include LSM debug output, iterator results, backing pointer confirmation, metrics, table stats, and dry-run version edits.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/excise.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/excise_test.go -->
# sources/storage-engines/pebble/excise_test.go

## Purpose
Provides datadriven coverage for excise behavior across local, remote, shared, flushable, and concurrent scenarios, plus direct tests of tight and loose excised table bounds.

## Important APIs, Types, And Functions
`TestExcise` drives a single DB with commands for building/ingesting SSTables, external ingestion, file-only snapshots, iteration, metrics, dry-run excise, and backing confirmation. `TestConcurrentExcise` coordinates two DBs over shared remote storage and blocked compactions. `TestExciseBounds` builds SSTables and calls `determineLeftTableBounds`, `determineRightTableBounds`, and loose-bound helpers directly.

## Control Flow
The main datadriven harness resets an in-memory FS and remote storage, opens a DB with virtual/flushable ingest excise support, and executes commands from `testdata/excise`. Concurrent tests switch between two DBs, replicate key spans through `ScanInternal` and `IngestAndExcise`, block selected compactions through event callbacks, and wait for errors/unblocks. Bounds tests build raw SSTables, open raw iterators, and print calculated metadata.

## State And Persistence Behavior
Tests create real Pebble manifests, virtual SSTables, remote object catalog state, shared backing files, blob references, eventually file-only snapshots, and flushable ingest metrics. They check persistence across reopen and confirm virtual fragments can share one `TableBacking`.

## Dependencies And Integration Points
Uses testkey comparer, block property collectors, remote in-memory storage, object provider, raw SST writers, keyspan encoders, datadriven helper commands, event listener synchronization, and table stats wait helpers.

## Risks And Edge Cases
Coverage targets range deletions, range keys, masking filters, tiny blocks, remote object movement, memtable flush interaction, EFOS protected ranges, concurrent compaction cancellation, shared-SST replication, inclusive-bound assertions, and loose bounds for remote files.

## Test Signals
Signals include exact iterator output, `get` results, LSM layouts, version edit dry-runs, metrics, table stats completion, compaction error messages, backing equality, and printed tight-versus-loose bounds.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/excise_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/external_iterator.go -->
# sources/storage-engines/pebble/external_iterator.go

## Purpose
Implements `NewExternalIter`, which builds a normal Pebble `Iterator` over externally supplied SSTable files without opening a DB.

## Important APIs, Types, And Functions
`NewExternalIter` and `NewExternalIterWithContext` are the public constructors. `externalIterState` owns opened `sstable.Reader`s and a block buffer pool. `validateExternalIterOpts`, `createExternalPointIter`, `finishInitializingExternal`, and `openExternalTables` handle option validation, point/range iterator construction, and reader opening.

## Control Flow
The constructor rejects unsupported iterator options, opens every provided file as an `sstable.Reader`, allocates an `Iterator`, attaches `externalIterState`, applies bounds, and initializes point and optional range-key iteration. Point iteration creates one merging level per file, assigning synthetic sequence numbers so earlier input subarrays shadow later ones. Range keys are merged through range-key iterator configuration and interleaved with points when requested. Initialization errors close already-opened readers.

## State And Persistence Behavior
The iterator is read-only and owns only transient readers, buffer pool memory, iterator stats, and synthetic sequence transforms. It does not mutate or persist DB metadata. `Close` releases all readers and the buffer pool.

## Dependencies And Integration Points
Depends on public `Options`/`IterOptions`, `objstorage.ReadableFile`, `sstable.Reader`, merging iterators, range key interleaving, block buffer pools, and table reader options. It is useful for ingest/replication/tooling paths that need Pebble semantics over raw SSTables.

## Risks And Edge Cases
Input ordering is a contract: subarrays are reverse chronological, files within subarrays are sorted and non-overlapping for points. External iterators do not support block-property filters, table filters, guaranteed durable reads, L6 filter options, or blob references. Error cleanup during initialization is important because partially opened readers otherwise leak.

## Test Signals
Covered by datadriven external iterator tests, flaky initialization error tests, blob-reference rejection, masking/bounds cases, and scan benchmarks.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/external_iterator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/external_iterator_test.go -->
# sources/storage-engines/pebble/external_iterator_test.go

## Purpose
Tests and benchmarks `NewExternalIter` over standalone SSTables, including initialization failures and scan performance.

## Important APIs, Types, And Functions
`TestExternalIterator` builds SSTables in an in-memory FS and iterates them with optional bounds, mask suffixes, and file lists. `testExternalIteratorInitError` wraps files in `flakyFile` to force intermittent `ReadAt` failures. `BenchmarkExternalIter_NonOverlapping_Scan` measures scan throughput over varying key and file counts.

## Control Flow
Datadriven commands reset the FS, build SSTables, run initialization-error loops, or create an external iterator and feed it to shared iterator test helpers. The flaky test retries many constructor calls, requiring either a surfaced `"flaky file"` error or a successfully closable iterator. The benchmark builds sorted SSTables, repeatedly opens file handles, constructs an iterator, and scans with `NextPrefix`.

## State And Persistence Behavior
All state is temporary in-memory SSTables and opened file handles. No DB manifest is used. Blob test values may be used while building to validate unsupported blob-reference behavior.

## Dependencies And Integration Points
Uses `datadriven`, `testkeys`, `sstable`, `objstorageprovider`, `blobtest`, `vfs`, and shared build/iterator helpers from Pebble tests. It directly validates `external_iterator.go`.

## Risks And Edge Cases
The most important edge case is constructor cleanup when reader initialization fails after some files have opened. Other covered areas include range-key masking, lower/upper bounds, unsupported blob values, and correct ordering across multiple external files.

## Test Signals
Signals are datadriven iterator output, expected constructor errors, absence of panics during flaky initialization, and benchmark key-count validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/external_iterator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/external_test.go -->
# sources/storage-engines/pebble/external_test.go

## Purpose
Contains broader external/package tests and benchmarks for read error propagation, separated-value lookup performance, restart safety, read-only recovery, and `Options.Clone` independence.

## Important APIs, Types, And Functions
`TestIteratorErrors` uses Pebble metamorphic tests with random read-operation error injection. `BenchmarkPointLookupSeparatedValues` and `buildSeparatedValuesDB` construct value-separation workloads. `TestDoubleRestart`, `getKVs`, and `checkKVs` validate quick close/reopen safety. `TestReadOnlyRecovery` ensures read-only open does not mutate a crash clone. `TestOptionsClone`, `mangle`, and `genVal` fuzz clone isolation.

## Control Flow
Iterator error testing first generates a random DB with write operations, reopens it read-only under an error-injecting FS, then steps through random read operations and requires injected errors to appear in operation output. Double restart builds a metamorphic DB, clones its FS, records golden KVs, then repeatedly opens/closes/reopens independent clones under random latency and checks KVs. Read-only recovery compares filesystem string state before and after open/close.

## State And Persistence Behavior
The tests stress persisted WAL, manifest, SSTable, blob/value-separation, and crash-clone state. Read-only recovery specifically asserts no filesystem mutation. Clone tests ensure option structs do not share mutable Pebble-owned fields after `Clone`.

## Dependencies And Integration Points
Uses package `pebble_test`, metamorphic workload generation, Cockroach key schema, bloom filters, value separation, `vfs`, `errorfs`, random latency, and public APIs. It validates external-user behavior rather than package internals.

## Risks And Edge Cases
Coverage includes silent read-error swallowing, WAL deletion before flush safety, large-batch recovery under small memtables, unsynced crash clones, read-only recovery side effects, and shallow-copy bugs in nested options.

## Test Signals
Signals include injected-error text in operation output, exact KV equality with a golden DB, unchanged FS state after read-only open, absence of restart data loss, and stable option string after mutating a clone.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/external_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/file_cache.go -->
# sources/storage-engines/pebble/file_cache.go

## Purpose
Implements Pebble's shared open-file cache for SSTable and blob readers, plus the DB-specific handle that creates point/range iterators, supplies blob/value-block readers, tracks iterator leaks, and reports file-cache metrics.

## Important APIs, Types, And Functions
Important types include `FileCacheMetrics`, `tableNewIters`, `fileCacheHandle`, `FileCache`, `fileCacheKey`, `fileCacheValue`, `tableCacheShardReaderProvider`, `iterSet`, and `iterKinds`. Key functions include `NewFileCache`, `FileCache.Ref/Unref`, `fileCacheHandle.newHandle`, `Close`, `openFile`, `findOrCreateTable`, `findOrCreateBlob`, `Evict`, `Metrics`, `withReader`, `GetValueReader`, `newIters`, `newPointIter`, `SetupBlobReaderProvider`, `newRangeDelIter`, `newRangeKeyIter`, and `getTableProperties`.

## Control Flow
`NewFileCache` initializes a sharded generic cache with an init function that opens object-storage files and constructs either an `sstable.Reader` or `blob.FileReader`, and a release function that closes readers and decrements counts. A DB creates a handle with object provider, block cache handle, reader options, and corruption callback. Iterator construction finds or creates the table reader, installs corruption reporting in read env, applies virtual/shared-ingest transforms, creates requested range-key, range-deletion, and point iterators, and pins the cache value until the point iterator close hook runs.

## State And Persistence Behavior
The cache holds process-local reader objects, refcounts, per-type counts, iterator counts, race-build stack traces for leaked refs, block-cache file entries, and per-handle filter metrics. It does not persist data, but it controls access to persisted SSTable/blob files and must evict block-cache state when files are evicted.

## Dependencies And Integration Points
Integrates with object storage, block cache, generic cache, manifest table metadata, virtual SSTables, value separation, blob readers, range deletion/key span iterators, compaction iterators, block property filters, IO tracing, and corruption reporting from `event.go`.

## Risks And Edge Cases
Reference ownership is subtle: point iterators pin cache values, range iterators generally do not, and value-block/blob reader providers hold their own refs. Leaked iterators make handle close fail and can panic on eviction. Virtual metadata must be initialized before reads. Shared ingested SSTables with synthetic seqnums hide obsolete points. Range-key filtering is disabled when range-key deletions exist to avoid surfacing deleted lower-level keys.

## Test Signals
Signals are broad and indirect through iterator, compaction, value-separation, corruption, excise size-estimation, and file-cache tests. Metrics (`Size`, `TableCount`, `BlobFileCount`, hits, misses), iterator leak errors, and corruption callbacks are important runtime indicators.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/file_cache.go -->
