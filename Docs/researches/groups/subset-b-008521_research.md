# subset-b-008521 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/db.go -->
## sources/storage-engines/pebble/db.go

### Purpose
`db.go` defines Pebble's central `DB` type and much of the public runtime surface for a concurrent, persistent ordered key/value store. It binds the public `Reader` and `Writer` APIs to the internal write path, iterator construction, snapshot creation, manual compaction, flushing, metrics, SSTable inspection, memtable allocation, WAL rotation, and close-time cleanup. The file is the main coordination point between application-facing operations and the lower-level version, manifest, WAL, memtable, table cache, compaction, blob, and object-storage subsystems.

### Important APIs, types, and functions
The `Reader` interface exposes `Get`, `NewIter`, `NewIterWithContext`, and `Close`, with explicit lifetime ownership for returned value closers. The `Writer` interface exposes `Apply`, `Set`, `Delete`, `DeleteSized`, `SingleDelete`, `DeleteRange`, `Merge`, `LogData`, and range-key methods. The `DB` struct implements both and contains the core mutable state: atomics for memtable and WAL metrics, options and comparer functions, object provider and file cache handles, commit pipeline, read-state pointer, close context, delete pacer, compaction scheduler, and the large `mu` protected state block for format versions, job IDs, version set, WAL manager/writer, memtable queue, compaction queues, snapshots, table stats, and validation.

Public single-operation write helpers such as `Set`, `Delete`, `DeleteSized`, `SingleDelete`, `DeleteRange`, `Merge`, `LogData`, `RangeKeySet`, `RangeKeyUnset`, and `RangeKeyDelete` each allocate a temporary batch, add one operation, call `Apply`, and close the batch only on success. `Apply` and `ApplyNoSyncWait` delegate to `applyInternal`, which validates closed state, batch reuse, read-only mode, WAL requirements, format major version requirements, range-key comparer support, batch sizing, large-batch conversion, and commit-pipeline execution.

`commitWrite` and `commitApply` are the hooks used by the commit pipeline. `commitWrite` reserves space in the current memtable or rotates through `makeRoomForWrite`, writes the WAL record unless WALs are disabled, and handles large flushable batches specially by writing them to the pre-rotation WAL. `commitApply` applies normal batches to a memtable, schedules delayed flushes for range deletions or range keys when configured, and schedules a flush after writer references drain.

Iterator-related types include `iterAllocCommon`, `iterAlloc`, `iterV2Alloc`, `snapshotIterOpts`, `batchIterOpts`, and `newIterOpts`. `newIter` captures the read state or snapshot version, chooses V1 or V2 iterator stack allocation, installs batch state, bounds, tracing/profile state, and calls `Iterator.finishInitializingIter`. `finishInitializingIter` constructs point and range-key stacks, supports lazy combined iteration for sparse range keys, trims memtables newer than the snapshot sequence, and arms the V2 trigger iterator when range-key lazy switching is possible. `constructPointIter` builds the V1 merging iterator over batch, memtables, L0 sublevels, and L1+ levels. `constructPointIterV2` builds the analogous V2 stack with interleaving iterators for range deletes and trigger support.

Lifecycle and storage APIs include `NewBatch`, `NewIndexedBatch`, `NewIter`, `NewSnapshot`, `NewEventuallyFileOnlySnapshot`, `Close`, `Compact`, `Flush`, `AsyncFlush`, `Metrics`, `SSTables`, `SetCreatorID`, `ScanStatistics`, `ObjProvider`, `DebugString`, and `DebugCurrentVersion`. `SSTables` supports options for properties, key-range filtering, and approximate span bytes, and enriches manifest metadata with virtual/backing information and object-storage placement. `ScanStatistics` scans obsolete and live internal keys over a range, optionally rate-limited, to count key kinds, latest keys, snapshot-pinned keys, and bytes read.

### Control flow and state behavior
Writes flow through a batch into the commit pipeline. The fast path prepares the current mutable memtable while holding the commit pipeline mutex. If the memtable lacks room or the batch is large, `makeRoomForWrite` acquires `DB.mu` with the required lock ordering, may induce write stalls, rotates the WAL, turns the mutable memtable immutable, appends a new mutable memtable, updates read state, and schedules flushes. Large flushable batches are appended to the flushable queue and associated with the preceding WAL/memtable flush group, preserving the SingleDelete no-duplication invariant described in the `Writer.SingleDelete` comment.

Reads and iterators use `readState` references to provide a point-in-time view while preventing referenced files and memtables from deletion. Snapshots store a visible sequence number in `DB.mu.snapshots`; eventually-file-only snapshots can reference versions for file-only consistency over selected ranges. Iterator construction merges batch, memtable, L0 sublevel, lower-level, range-delete, range-key, and blob value sources, using `seqNum` and bounds to constrain visibility.

Persistence is coordinated through the WAL manager/writer, memtable queue, version set, MANIFEST, format-version marker, object provider, table/blob metadata annotators, and obsolete-file deletion queues. `rotateWAL` closes the previous WAL before creating the new one to avoid recovery treating both logs as corrupt. `rotateMemtable` updates the flushable queue and read state atomically with the visible memory state. `Close` sets the closed marker, cancels background I/O, waits for compactions, downloads, flushes, stats loading, and validation, closes WAL/manifest/object/cache resources, unreferences read state and memtables, schedules obsolete-file deletion, checks leaked iterators/snapshots/memtable reservations/zombie files, and returns the first accumulated error.

Manual compaction first flushes overlapping memtables, then enqueues one or more `manualCompaction` records per level. With `parallelize`, `splitManualCompaction` uses in-use key ranges to create non-overlapping compaction spans. Context cancellation removes pending manual compactions, but already-started compactions are allowed to finish.

### Dependencies and integration points
This file integrates heavily with `internal/base`, `arenaskl`, `cache`, `deletepacer`, `inflight`, `invalidating`, `iterv2`, `keyspan`, `manifest`, `manual`, `problemspans`, `tombspan`, `metrics`, `objstorage`, `remote`, `rangekey`, `sstable`, `blob`, `block`, `atomicfs`, `wal`, and `tokenbucket`. It depends on options and event listeners for logging, tracing, write-stall notifications, compaction scheduling, file cache behavior, object storage placement, table format selection, and WAL failover. It also shares assumptions with batching, flush, compaction, ingestion, snapshot, iterator, table-cache, and version-set code outside this file.

### Risks and invariants
The largest correctness risks are lock ordering around `commitPipeline.mu` and `DB.mu`, WAL/memtable rotation atomicity, large-batch flush-group semantics, and iterator/snapshot reference leaks. Operations on a closed DB panic with `ErrClosed`, so callers and tests must distinguish panics from returned errors. `ApplyNoSyncWait` exposes a durability-sensitive mode that requires explicit `Batch.SyncWait`. The `SingleDelete` API has strict workload assumptions and depends on Pebble avoiding internal write duplication. Iterator pool reuse relies on zeroing checks in invariant builds. Lazy combined iteration must be disabled whenever batches or memtables contain range keys. `Close` is intentionally not safe concurrently with arbitrary DB methods, and compaction cancellation does not stop compactions already running.

### Test signals
`db_test.go` provides broad coverage for this file: basic reads/writes, random writes, large-batch WAL placement and L0 output, no-cache reads, merge ordering and merger closer lifetimes, WAL-only log data, SingleDelete behavior with flushes and snapshots, iterator and shared-cache leak detection, memtable reservation/recycling and leak errors, cache eviction after compaction, empty flushes, MANIFEST rollover and preservation, closed-DB panics, concurrent commit/compact/flush, compact/close races, mismatched batch application panics, cleaner/close races, SSTables options including virtual SSTables and approximate span bytes, tracing, memtable-ingest inversion regression coverage, WAL failover write-stall behavior, deterministic concurrent sequencing, and load-block semaphore enforcement.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/db.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/db_internals.go -->
## sources/storage-engines/pebble/db_internals.go

### Purpose
`db_internals.go` contains the small internal job ID utility used to identify asynchronous or background jobs such as flushes, compactions, and file ingestions. Job IDs are diagnostic and observability identifiers, not persisted correctness state.

### Important APIs, types, and functions
`type JobID int` is the exported identifier passed to event listener notifications and logs. `(*DB).newJobIDLocked` returns the current `d.mu.nextJobID` and increments it, requiring `DB.mu` to already be held. `(*DB).newJobID` is the locking wrapper for callers that do not already hold `DB.mu`.

### Control flow and state behavior
The control flow is intentionally simple: job ID allocation is serialized by `DB.mu`, and IDs are monotonically incremented in memory. There is no persistence across process restarts and no attempt to encode job identity into on-disk metadata.

### Dependencies and integration points
The functions depend on the `DB` struct's `mu.nextJobID` field defined in `db.go`. Allocated IDs are consumed by event listener calls, logging, WAL creation, flush scheduling, compaction scheduling, deletion jobs, and ingestion paths elsewhere in Pebble.

### Risks and invariants
The main invariant is that `newJobIDLocked` must only be called while holding `DB.mu`; otherwise duplicate or skipped IDs could occur under concurrency. Since IDs are not persisted or correctness-critical, overflow or restart reuse would mainly affect logs and event correlation, not data correctness.

### Test signals
There is no dedicated test in this file. Indirect coverage comes from tests in `db_test.go` that observe event listener behavior, tracing, compaction/flush scheduling, WAL rotation, and deletion cleanup. Those tests would expose severe job-ID allocation races mostly through inconsistent event correlation or unexpected panics.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/db_internals.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/db_test.go -->
## sources/storage-engines/pebble/db_test.go

### Purpose
`db_test.go` is a broad behavioral and regression suite for Pebble's core DB implementation. It validates the public read/write API, batch application, WAL and memtable rotation, flushing, compaction, close-time cleanup, iterator and memtable reference accounting, SSTable introspection, tracing, WAL failover, determinism under reordered execution, and read concurrency limiting.

### Important APIs, types, and functions
`try` is a test helper that retries a condition with exponential backoff. `verifyGet` and `verifyGetNotFound` centralize `Reader.Get` assertions. The main tests exercise `Open`, `Set`, `Delete`, `SingleDelete`, `Merge`, `LogData`, `Apply`, `Flush`, `AsyncFlush`, `Compact`, `Ingest`, `Excise`, `SSTables`, `NewIter`, `NewSnapshot`, `NewBatch`, `NewIndexedBatch`, `Metrics`, and `Close`.

Test-only helper types include `closableMerger`, which verifies that merge value closers are propagated; `testTracer`, which records tracing events; `sstAndLogFileBlockingFS`, which blocks WAL or SST creation to force stall/failover scenarios; `testLogManager`, which can dynamically elevate write-stall thresholds; ordering tree types (`sequential`, `reorder`, `parallel`, `leaf`) for deterministic reruns; and `readTrackFS`/`readTrackFile`, which count concurrent SST reads for semaphore enforcement.

### Control flow and state behavior
The early tests validate basic persisted state by opening staged testdata directories, applying direct and batched writes, and comparing reads against an expected in-memory map. Random write tests force memtable churn with small memtables. `TestLargeBatch` validates the special large-batch path: a value larger than the configured threshold is written to the pre-existing WAL, triggers WAL rotation, leaves the new WAL empty, and eventually produces the expected L0 files.

Merge and SingleDelete tests validate subtle internal-key semantics across memtables and flushes, including a snapshot case where an older value must remain visible to a snapshot while the DB observes deletion. Leak tests intentionally leave iterators or memtable refs open and require `Close` to report leaked versions or reservations. Manifest tests force frequent MANIFEST rollover, check the current descriptor, and verify preservation of the configured number of previous manifests. Close tests assert that closed DB operations panic with `ErrClosed`.

Concurrency tests stress `Set`, `Compact`, `Flush`, and `AsyncFlush` in parallel, close while compactions are active, and race file cleaning with DB close. SSTable tests validate property loading, key-range filtering, approximate span-byte estimation, and virtual SSTable metadata after excise. Tracing is datadriven and covers gets plus iterators over DB, snapshot, and indexed-batch views. `TestMemtableIngestInversion` constructs a complex sequence of blocked compactions, blocked flushes, ingests, range deletes, and memtable writes to guard against a historical L0 sublevel/sequence-number inversion bug.

The WAL failover tests use blocking filesystems and a fake log manager to ensure write stalls are avoided or unblocked when failover elevation applies. `TestDeterminism` records a datadriven sequence and reruns it under sequential, reordered, parallel, and latency-injected schedules to ensure output stability. `TestLoadBlockSema` confirms `LoadBlockSema` bounds concurrent SST reads during parallel `Get` workloads.

### Dependencies and integration points
The tests use `vfs.NewMem`, `errorfs`, `wal`, `sstable`, `objstorageprovider`, `cache`, `testkeys`, `testutils`, `datadriven`, `leaktest`, `require`, and numerous Pebble test helpers from other files such as `runBatchDefineCmd`, `runBuildCmd`, `runCompactCmd`, `runDBDefineCmd`, `runExciseCmd`, and ingestion helpers. They intentionally reach into `d.mu`, version metadata, WAL manager internals, and metrics, so they are package-level tests tightly coupled to core internals.

### Risks and invariants
Because these tests inspect internal strings, file numbers, and version layouts, they can be sensitive to legitimate compaction, manifest, or formatting changes. Several tests rely on timing, blocking filesystems, or background scheduling; they include timeouts and semaphores, but slow or highly contended environments could expose flakes. The determinism harness is powerful but only covers operations expressed in its datadriven command set. Tests that accept randomized options must account for option-dependent behavior.

### Test signals
This file itself is the test signal for `db.go` and related components. Its benchmarks also signal performance-sensitive areas: delete versus single-delete, iterator construction and close cost under high read amplification, and repeated memtable rotation for large memtables.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/db_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/disk_usage.go -->
## sources/storage-engines/pebble/disk_usage.go

### Purpose
`disk_usage.go` implements disk usage estimation for a user-key range and table/blob metadata annotators that aggregate usage by storage placement. It supports both simple total estimates and estimates split into local, remote/shared, and external-backed storage.

### Important APIs, types, and functions
`(*DB).EstimateDiskUsage(start, end)` returns a total byte estimate for SSTable data overlapping the inclusive range `[start, end]`, delegating to `EstimateDiskUsageByBackingType`. `(*DB).EstimateDiskUsageByBackingType` returns total bytes, remote bytes, external bytes, and an error. It checks closed state, validates inclusive bounds, references the current read state, and obtains a version range annotation from `d.tableDiskUsageAnnotator`.

`TableUsageByPlacement` wraps `metrics.ByPlacement[TableDiskUsage]` and can accumulate local, shared, and external usage. `TableDiskUsage` tracks physical table count/bytes, virtual table count/estimated bytes, and referenced blob bytes. `TotalBytes` sums all byte fields, and `Accumulate` merges another usage value.

`singleTableDiskUsage` builds a placement-keyed usage value for one table using `objstorage.Placement`. `makeTableDiskSpaceUsageAnnotator` creates a `manifest.TableAnnotator` that computes full-table and partial-overlap usage, including estimated referenced blob bytes. `makeBlobFileDiskSpaceUsageAnnotator` creates a blob-file annotator that accumulates physical blob file sizes by placement.

### Control flow and state behavior
Usage estimation is read-only. It obtains a referenced `readState` so concurrent compactions cannot delete the underlying version while annotations are computed. Fully contained tables contribute full table size plus estimated referenced blob size. Partially overlapping tables call `d.fileCache.estimateSize` for the overlapping table bytes, then scale the table's estimated referenced blob size by the overlap fraction. Virtual tables are counted separately from physical tables but included in byte totals. `EstimateDiskUsageByBackingType` treats external bytes as part of remote bytes, and remote bytes as part of total bytes.

The annotators are intended to be cached by manifest annotation indexes. The table annotator returns cacheable values for full-table metadata and computes best-effort values for partial overlaps. The blob annotator computes live blob-file usage independently from table-referenced blob bytes.

### Dependencies and integration points
This code depends on `internal/base` for user-key bounds and file types, `internal/manifest` for table and blob annotation infrastructure, `metrics` for count/size and placement aggregation, `objstorage` for placement classification, and `fileCache.estimateSize` for partial SSTable overlap estimates. The resulting annotators are used by `DB.Metrics` in `db.go` and by range-level estimation APIs.

### Risks and invariants
The API excludes WAL bytes for unflushed keys, so callers must treat estimates as SSTable/blob-oriented rather than full end-to-end storage accounting. Partial overlap estimation may overcount blocks when block boundaries or abbreviated index keys prevent exact overlap detection. If `fileCache.estimateSize` returns an error inside the partial-overlap annotator, the code returns an empty usage value, which can undercount silently. Blob referenced bytes are scaled by table overlap fraction, an approximation that may diverge from actual value distribution. The range is inclusive, unlike many Pebble APIs that use end-exclusive bounds, so callers must pass the intended end key carefully.

### Test signals
`disk_usage_test.go` verifies closed-DB panics and uses datadriven tests for open/close, batches, flushes, built tables, ingests, remote builds, external ingests, compactions, total estimates, and backing-type estimates. It asserts `external <= remote <= total`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/disk_usage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/disk_usage_test.go -->
## sources/storage-engines/pebble/disk_usage_test.go

### Purpose
`disk_usage_test.go` validates the disk-usage estimation APIs in `disk_usage.go`, including closed-DB behavior and datadriven scenarios involving local, remote, external, ingested, flushed, and compacted files.

### Important APIs, types, and functions
`TestEstimateDiskUsageClosedDB` opens an in-memory DB, writes a key, closes it, and asserts both `EstimateDiskUsage` and `EstimateDiskUsageByBackingType` panic after close. `TestEstimateDiskUsageDataDriven` interprets `testdata/disk_usage` commands. It supports `open`, `close`, `batch`, `flush`, `build`, `ingest`, `build-remote`, `ingest-external`, `compact`, `estimate-disk-usage`, and `estimate-disk-usage-by-backing-type`.

### Control flow and state behavior
The datadriven test maintains a shared in-memory filesystem, a remote in-memory storage object, and a current `*DB`. The `open` command resets any existing DB and configures `FormatExciseBoundsRecord`, disables automatic compactions, and installs a simple remote-storage factory with an external locator. Build and ingest commands create local, remote, or external SSTables through shared Pebble test helpers. Estimate commands default to range `a` through `z` unless two command arguments provide explicit start and end keys.

For backing-type estimates, the test checks the returned hierarchy before printing it: external usage must be less than or equal to remote usage, and remote usage must be less than or equal to total usage. Compaction commands return the LSM state after compacting, allowing expected files and placement behavior to be encoded in the datadriven output.

### Dependencies and integration points
The file depends on `leaktest`, `datadriven`, `remote.NewInMem`, `remote.MakeSimpleFactory`, `vfs.NewMem`, and `require`. It also depends on test helpers defined elsewhere for parsing DB options, defining batches, building SSTables, ingesting local/remote/external files, compacting, and rendering the LSM.

### Risks and invariants
The test assumes closed DB methods should panic rather than return errors, matching the core DB closed-state convention. The datadriven parser uses positional command arguments for ranges, so malformed test input can accidentally fall back to defaults or produce unexpected ranges. Since size estimates are approximate, expected output must tolerate implementation-defined estimates where partial overlap or blob-reference scaling changes. Remote and external storage setup must match object-provider placement semantics for the hierarchy assertions to remain meaningful.

### Test signals
The strongest signal is coverage across local, remote, and external placement plus compaction and ingestion. The tests do not directly assert exact behavior for `fileCache.estimateSize` errors or WAL-exclusion behavior, so those remain residual risk areas.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/disk_usage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/docs/js/app.js -->
## sources/storage-engines/pebble/docs/js/app.js

### Purpose
`docs/js/app.js` implements the client-side D3 application used by Pebble's benchmark dashboard. It parses benchmark data, renders YCSB time-series charts, supports global or per-chart maxima, overlays optional detail series, synchronizes zoom and hover state across charts, displays annotations and commit SHA hints, loads write-throughput summary data, and persists selected chart options in query parameters.

### Important APIs, types, and functions
Date helpers include `parseDateStr`, which accepts `YYYYMMDD` or `YYYYMMDD-sha`, and `parseTime`, which returns only the date. Formatting and geometry helpers include `formatTime`, `dateBisector`, `styleWidth`, `styleHeight`, `pathGetY`, `humanize`, `dirname`, and `equalDay`.

Data shaping functions include `computeSegments`, which splits a series into contiguous daily runs, and `computeGaps`, which creates dashed gap segments between non-contiguous runs and from the last datum to the dashboard max date. `initData` parses the global `data` object's CSV rows into objects with date, sha, ops/sec, read/write bytes, and read/write amplification, computes global and per-chart maxima, then fetches `writeThroughputSummaryURL()` and merges summary records. `initDateRange`, `initAnnotations`, `initQueryParams`, `setQueryParams`, `setDetail`, `toggleDetail`, and `toggleLocalMax` initialize or update UI state.

`renderChart` is the main renderer. It clears an SVG chart, computes dimensions and scales, draws axes, handles no-data charts, creates clip paths, renders annotations, splits and draws solid and dashed line segments, optionally renders a second detail axis and line, installs synchronized D3 zoom behavior, and creates hover overlays for date, value, marker, and short SHA. `renderYCSB` applies `renderChart` to every `.chart.ycsb` element. `window.onload`, `window.onpopstate`, and the resize listener bootstrap and refresh the dashboard.

### Control flow and state behavior
The script uses module-level mutable state: `minDate`, `max`, `usePerChartMax`, `detail`, `detailName`, `detailFormat`, and `annotations`. On page load, it wires toggle links, loads and parses data, initializes date range and annotations, restores query params, renders YCSB charts and write-throughput panels, sets the "last updated" text, and then toggles local-max mode by default.

Charts share zoom state by broadcasting the active D3 transform to all `.chart` nodes with an `updateZoom` function. Hover state is similarly broadcast with `updateMouse`, causing all charts to show the closest datapoint for the same date. The detail series is selected globally through query parameters and can be read bytes, write bytes, read amplification, or write amplification. Annotations are read from DOM nodes with class `.annotation` and rendered as green markers/vertical lines; hovering near an annotation temporarily replaces the chart title with the annotation message.

### Dependencies and integration points
The file assumes D3 is globally available and uses D3 v5-era APIs such as `d3.event` and `d3.mouse`. It assumes global variables and functions from surrounding documentation scripts: `data`, `writeThroughputSummaryURL`, `renderWriteThroughputSummary`, `writeThroughputWorkload`, and `bisectAndRenderWriteThroughputDetail`. HTML integration depends on `.chart.ycsb` SVG elements, `.toggle` controls, `#localMax`, `.annotation` elements with `data-date`, and `.updated` targets.

### Risks and invariants
Several functions assume non-empty data arrays. `computeGaps` indexes the last segment and will fail if a chart has an empty series. `dirname` assumes a slash exists in the path. `initData` uses `for (key in data)` without declaring `key`, creating or reusing a global. The write-throughput merge path replaces parsed dates with `d.date.split("-")[0]`, a string, while the charting logic expects `Date` objects; this is safe only if downstream write-throughput functions do not feed those records back into YCSB chart paths that require dates. `pathGetY` operates on the first rendered path node for a series, so hover-series selection can be inaccurate when data is split into multiple segments. Query parameter updates push history entries for each toggle. The script is tied to older D3 event APIs and would need changes for D3 v6+.

### Test signals
There are no local tests for this JavaScript file in the researched set. Practical validation would require loading the docs page with representative `data`, annotations, and write-throughput summary responses, then checking rendering, zoom synchronization, hover values, detail toggles, query params, resize behavior, empty-chart behavior, and SHA display.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/docs/js/app.js -->
