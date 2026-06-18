# sources/storage-engines/rocksdb/db/version_set.cc lines 1-6776

## Scope

This chunk covers the first 6,776 lines of RocksDB's `db/version_set.cc`. It implements the central in-memory and MANIFEST-facing version machinery for SST and blob-file metadata: file lookup helpers, point lookup and MultiGet file selection, level iterators over SSTs, table property/metadata APIs, blob value resolution, compaction scoring and file-priority bookkeeping, version lifetime management, and the first large part of `VersionSet` MANIFEST writer batching.

The chunk starts at includes and local read-path helpers and ends inside the public `VersionSet::LogAndApply()` overload after it validates multi-edit inputs. Later manifest recovery, manifest replay, full `LogAndApply()` wrapper control flow, WAL metadata helpers, and additional `VersionSet` utilities continue after this range and are intentionally out of scope for this chunk.

## Purpose

The code in this range maintains the immutable metadata view that readers, compactions, and recovery depend on:

- select the minimal set of SST files that might contain a key or key range;
- expose stable iterators over the current version's files, including range tombstone handling and MultiScan pruning;
- perform point lookups, MultiGet lookups, and blob-index materialization through table cache and blob source integration;
- expose table properties, column-family metadata, live-file metadata, live-size estimates, and debug summaries;
- compute compaction scores, compaction priorities, and special compaction candidate lists for TTL, periodic compaction, bottommost cleanup, forced blob GC, read-triggered compaction, and explicit table-property marks;
- prepare a `VersionStorageInfo` before it becomes current by deriving level briefs, file indexes, base-level byte targets, bottommost-file state, and file-location indexes;
- manage `Version` reference counts and obsolete file metadata transfer when old versions are released;
- batch and persist `VersionEdit`s through `VersionSet::ProcessManifestWrites()`, including atomic-group handling, manifest rotation, CURRENT-file installation, WAL metadata edits, and installing new `Version`s.

## Important APIs, Types, And Functions

- `FindFileInRange()`, public `FindFile()`, `AfterFile()`, `BeforeFile()`, and `SomeFileOverlapsRange()` are the low-level key-range predicates for sorted level files and unordered/overlapping L0 files.
- `MultiScanInternalKey()`, `MultiScanRangeOverlapsFile()`, `ForEachMultiScanOverlappingFile()`, and `GetMultiScanOverlappingFiles()` map bounded `MultiScanArgs` ranges to candidate SST file indexes, handling timestamp comparators by seeking with max timestamps.
- `DoGenerateLevelFilesBrief()` builds compact arena-backed `LevelFilesBrief` arrays from `FileMetaData`, copying encoded smallest/largest internal keys into contiguous arena storage.
- `FilePicker` is the single-key lookup planner. It walks levels from newest to oldest, uses `FileIndexer` fractional-cascading bounds for non-L0 levels, scans overlapping L0 files, and returns `FdWithKeyRange` candidates until no lower level can contain the key.
- `FilePickerMultiGet` extends the same idea for `MultiGetRange`, maintaining per-key search bounds, splitting a batch by file, skipping keys filtered out of a level, and preserving duplicate-key and key-spanning-next-file behavior.
- `LevelIterator` is an `InternalIterator` that lazily opens table iterators over non-overlapping level files. It supports seek/seek-for-prev/first/last/next/prev, table-cache iterator reuse, prepared MultiScan iterators, async prepare, lower/upper bound checks, sequential readahead state, pinned iterators, range tombstone iterators, and synthetic sentinel keys at file boundaries.
- `AddTableIteratorForLevel()`, `Version::AddIterators()`, `Version::AddIteratorsForLevel()`, and `Version::TEST_GetLevelIterator()` build child iterators for DB iterators. L0 gets one table iterator per file because files can overlap; lower levels usually get one `LevelIterator`.
- `Version::Get()`, `Version::MultiGet()`, coroutine-gated `Version::MultiGetAsync()`, and `Version::ProcessBatch()` implement SST-side point-read execution after memtables have been checked by higher layers.
- `Version::GetBlob()`, `Version::MultiGetBlob()`, `BlobFetcher`, `BlobIndex`, `BlobSource`, and `BlobFileMetaData` resolve integrated BlobDB blob references into user-visible values or wide-column default values.
- Table-property and metadata APIs include `GetTableProperties()`, `GetPropertiesOfAllTables()`, `GetPropertiesOfTablesInRange()`, `GetPropertiesOfTablesByLevel()`, `GetAggregatedTableProperties()`, `TablesRangeTombstoneSummary()`, `GetMemoryUsageByTableReaders()`, `GetColumnFamilyMetaData()`, `GetSstFilesSize()`, `GetSstFilesBoundaryKeys()`, and `GetCreationTimeOfOldestFile()`.
- `VersionStorageInfo` functions in this range include `PrepareForVersionAppend()`, `ComputeCompensatedSizes()`, `ComputeCompactionScore()`, `EstimateCompactionBytesNeeded()`, `UpdateFilesByCompactionPri()`, `CalculateBaseBytes()`, `GenerateLevelFilesBrief()`, `GenerateLevel0NonOverlapping()`, `GenerateBottommostFiles()`, `GenerateFileLocationIndex()`, `GetOverlappingInputs()`, `GetCleanInputsWithinInterval()`, `EstimateLiveDataSize()`, `RangeMightExistAfterSortedRun()`, `CalculateSSTWriteHint()`, and epoch recovery helpers.
- `VersionSet::ManifestWriter`, `AtomicGroupReadBuffer`, `VersionSet::VersionSet()`, `Close()`, `Reset()`, `UpdatedMutableDbOptions()`, `TuneMaxManifestFileSize()`, `AppendVersion()`, `ProcessManifestWrites()`, `WakeUpWaitingManifestWriters()`, and the start of `LogAndApply()` provide the manifest batching and version installation substrate.

## Control Flow

Point lookup flow starts in `Version::Get()`. A `GetContext` is constructed with comparator, merge operator, sequence/tombstone output pointers, optional blob fetcher, and tracing ID. `FilePicker` then returns potentially relevant SST files in newest-to-oldest semantic order. For each file, `table_cache_->Get()` searches the SST with level-specific filter skipping, histogram tracking, and sampled read accounting. The `GetContext` state controls whether lookup continues (`kNotFound`, `kMerge`) or returns immediately (`kFound`, `kDeleted`, corrupt states, unexpected blob index, merge-operator failure). If the final state is merge-in-progress after all files are exhausted, a full merge with no base value is attempted.

`MultiGet()` builds one `GetContext` per key, attaches those contexts to `MultiGetRange` entries, and then uses `FilePickerMultiGet` to group keys by current SST file. The synchronous path calls `MultiGetFromSST()` per file and dumps per-level index/filter/SST-read histograms. When coroutine support and async I/O are available, non-L0 work can batch multiple file tasks through `MultiGetFromSSTCoroutine()`, with `ProcessBatch()` splitting ranges into likely-in-level and leftover batches after filter checks. After SST reads, collected blob indexes are resolved in `MultiGetBlob()`, and remaining merge/not-found states are finalized per key.

Iterator construction distinguishes L0 from sorted lower levels. `Version::AddIteratorsForLevel()` adds each L0 file as an independent table iterator so overlap is merged by the parent. For levels greater than zero, it usually constructs one `LevelIterator` that binary-searches file ranges and lazily opens the relevant table iterator. With `MultiScanArgs`, the code first prunes to overlapping files; a single relevant lower-level file can use a direct table iterator, while multiple files use `LevelIterator` with per-file scan options.

`LevelIterator` seek flow finds the candidate file with `FindFile()`, initializes or reuses the file iterator through `InitFileIterator()`, seeks inside the table, handles async `TryAgain`, optionally stops at prefix exhaustion, creates range tombstone sentinel keys at file boundaries, and skips empty files forward/backward. Range tombstone integration is subtle: the parent merging iterator can observe sentinel keys so tombstone iterators remain alive across table-file transitions even when a file has no point keys.

Version preparation flow is `Version::PrepareAppend()` then `VersionStorageInfo::PrepareForVersionAppend()`. It may initialize bounded table-property stats, compute compensated file sizes, update the number of non-empty levels, calculate base-level target bytes, sort file priorities, generate file indexer and `LevelFilesBrief`, detect non-overlapping L0, compute bottommost files, and build a file-number to `(level, position)` index. `VersionSet::AppendVersion()` then computes compaction scores, finalizes the storage info, unrefs the old current version, sets the new current version, refs it, and links it into the CF's version list.

Manifest write flow is centered on `VersionSet::ProcessManifestWrites()`. The caller holds the DB mutex. The first queued `ManifestWriter` can group compatible subsequent writers, except column-family manipulation and no-manifest dummy edits. The function builds per-CF `VersionBuilder`s, applies `VersionEdit`s in memory via `LogAndApplyHelper()`, adjusts atomic-group `remaining_entries_` when dropped CF edits are skipped, saves builders into new `Version`s, and verifies atomic-group shape in debug builds. It then decides whether to rotate the MANIFEST, releases the DB mutex for table-handler loading and filesystem writes, optionally writes a new full-state MANIFEST snapshot, appends encoded edits, syncs, installs CURRENT for a new descriptor file, reacquires the mutex, applies WAL metadata edits, updates I/O status and quarantine state, installs new versions or CF add/drop effects, updates descriptor sequence/manifest numbers, and wakes grouped writers.

## State And Persistence Behavior

`Version` objects are immutable once finalized and ref-counted. Releasing the last reference unlinks the version and decrements every referenced `FileMetaData`; metadata with no remaining refs is moved to `VersionSet::obsolete_files_` with enough context for table-cache release and eventual deletion. Live versions therefore define the set of SST and blob files that must not be purged.

`VersionStorageInfo` owns per-level `FileMetaData*` vectors, blob file metadata, arena-backed file briefs, compaction-priority arrays, compaction scores, bottommost-file lists, file-location maps, accumulated stats, estimated pending compaction bytes, compact cursors, and epoch-number requirements. It copies some accounting from a previous storage info so stats and cursors persist across version transitions.

MANIFEST persistence is done by encoded `VersionEdit`s appended to `descriptor_log_`, with rotation when size exceeds the tuned threshold or no descriptor exists. New MANIFEST files are populated with current CF state and WAL additions before appending the current edit batch, then installed through `CURRENT`. On failures, new versions are deleted, the current descriptor is reset so the next update creates a fresh MANIFEST, and a newly created MANIFEST may be deleted only when the manifest I/O itself failed rather than when CURRENT installation had ambiguous remote-filesystem semantics.

Atomic manifest groups are represented by `VersionEdit::IsInAtomicGroup()` and `remaining_entries_`. `AtomicGroupReadBuffer` collects group entries during replay and rejects size mismatches or normal edits mixed into an unfinished group. `ProcessManifestWrites()` preserves group structure during batching and adjusts remaining counts if dropped-column-family edits are omitted.

Blob-file state is sorted by blob file number and stored alongside SST state. Blob reads validate that referenced blob file metadata exists and that the blob index is neither TTL nor inlined. Forced blob GC candidate computation uses blob-file garbage ratios and the linked SST set from the oldest eligible blob metadata to mark SST files for compaction.

Compaction state is derived, not directly persisted here, but it controls future persistent edits. Scores account for compaction style, L0 file count and size, dynamic base levels, FIFO size/TTL/temperature triggers, incoming downcompact bytes, unnecessary dynamic levels, and compensated deletion sizes. Candidate lists are populated for explicit marks, bottommost cleanup after snapshot advancement, TTL expiry, periodic compaction, forced blob GC, and read-triggered compaction.

Epoch-number recovery updates file metadata and CF epoch counters. If epoch numbers are missing or force recovery is requested, all files in each non-L0 level receive one epoch per level from bottom to top, while L0 files receive distinct epochs in reverse file order. In ingest-behind mode, the reserved ingest-behind epoch number is consumed first.

## Dependencies And Integration Points

This chunk is tied to many RocksDB subsystems:

- table access through `TableCache`, `TableReader`, `InternalIterator`, table properties, table open options, range tombstone iterators, and block-cache tracing;
- read semantics through `LookupKey`, `GetContext`, `MergeContext`, `MergeHelper`, merge operators, wide columns, snapshots, read callbacks, pinned iterators, and `ReadOptions` bounds/timestamps;
- compaction through `CompactionStyle`, `FileIndexer`, `CompactionPicker` priorities, compaction boundaries, file temperature age thresholds, FIFO options, TTL, periodic compaction, and read-triggered compaction sampling;
- blob storage through `BlobIndex`, `BlobSource`, `BlobFileMetaData`, blob read request batching, blob garbage metadata, and linked SST tracking;
- MANIFEST persistence through `VersionEdit`, `VersionBuilder`, `BaseReferencedVersionBuilder`, `log::Writer`, `WritableFileWriter`, descriptor/CURRENT filenames, `SyncManifest()`, and `SetCurrentFile()`;
- column families through `ColumnFamilyData`, `ColumnFamilySet`, mutable/immutable options, per-CF log numbers, full-history timestamp lows, table cache, internal stats, and file metadata cache reservation managers;
- filesystem and observability through `Env`, `FileSystem`, `FSDirectory`, file checksums, random/sequential file readers, event listeners, `IOStatus`, statistics tickers/histograms, perf context, sync points, and info logging.

Public-facing behavior supported by this file includes `DB::Get`, `MultiGet`, iterators, MultiScan, table-property APIs, column-family metadata APIs, approximate live-size/file-size introspection, compaction scheduling, manifest write durability, and obsolete-file protection.

## Risks And Edge Cases

- File range comparisons must consistently strip or preserve user-defined timestamps. MultiScan and file-overlap code compare without timestamps where appropriate but seeks use synthetic max-timestamp internal keys.
- L0 ordering and overlap are special. `FilePicker` and `FilePickerMultiGet` scan L0 files rather than relying on sorted disjoint ranges; treating L0 like lower levels can miss newer overlapping data.
- Fractional-cascading bounds from `FileIndexer` reduce lower-level search cost but must be reset when a level is empty, a key falls beyond the right bound, or a key is skipped for the next level.
- `LevelIterator` has three validity states: valid table key, invalid table iterator, and sentinel key. Mistakes around `to_return_sentinel_`, range tombstone iterator lifetime, or prefix exhaustion can hide tombstones or make iterators step across prefix boundaries incorrectly.
- Prepared MultiScan iterators are stored by file index and consumed on first `InitFileIterator()`. Reusing or leaking them would affect async scans and memory ownership.
- `Get()` may stop early when `max_covering_tombstone_seq` is set, because lower levels can only contain covered keys. Incorrect tombstone propagation would produce false not-found or stale value returns.
- Blob resolution converts blob indexes into values after SST lookup. Invalid blob file numbers, TTL/inlined blob indexes, `kBlockCacheTier` incomplete reads, and value-size soft-limit aborts all have separate status behavior.
- Compaction score scaling changes priority without changing the 1.0 trigger threshold. Dynamic-level score changes, L0-size boosting, unnecessary-level draining, FIFO temperature changes, and incoming downcompact bytes can interact in non-obvious ways.
- `ComputeCompensatedSizes()` mutates `FileMetaData` only when `compensated_file_size` is zero; changing this invariant could race with readers sharing file metadata.
- Bottommost compaction marking is gated by oldest snapshot sequence, optional delay, ingest-behind mode, and user-defined timestamp history low. Ignoring timestamp max checks can create futile or repeated compactions.
- Forced blob GC assumes blob files are ordered and that the oldest metadata has linked SSTs. Corrupt or stale blob-to-SST linkage would mark wrong SSTs for compaction.
- Manifest rotation has ambiguous failure cases on remote filesystems. The code intentionally keeps a newly written MANIFEST if CURRENT installation status is ambiguous, because deleting it could make a DB unrecoverable if the remote rename actually succeeded.
- `ProcessManifestWrites()` releases the DB mutex during file I/O after constructing in-memory state. Any new state captured before unlock, such as current CF log numbers and full-history timestamp lows for a new MANIFEST, must be complete and immutable enough for the write window.
- Dropped column families inside atomic groups require adjusting `remaining_entries_`; otherwise recovery would see a corrupted atomic group even though the omission is intentional.

## Test Signals

Expected coverage for this chunk should come from tests around:

- point lookup ordering across L0 and lower levels, merge operands, covering range tombstones, blob indexes, wide columns, and filter-skipping on bottommost hits;
- MultiGet batch splitting, duplicate keys, keys spanning file boundaries, coroutine async I/O, per-level read histograms, and soft value-size aborts;
- iterator seek/next/prev behavior across empty files, prefix exhaustion, lower/upper bounds, range tombstone sentinel keys, and `ignore_range_deletions`;
- MultiScan pruning with bounded ranges, timestamp comparators, L0 overlapping files, standalone range tombstone files, and async prepared iterators;
- table-property fallback reads when table cache returns `Incomplete`, range tombstone summary output, metadata APIs, memory usage by table readers, and blob file metadata reporting;
- compaction scoring for level, universal, FIFO, dynamic-level bytes, TTL, periodic compaction, file-temperature changes, read-triggered compaction, bottommost cleanup, and forced blob GC;
- version lifetime and obsolete-file cleanup under iterators/readers holding old versions;
- epoch-number recovery with missing epochs, forced restart, L0 ordering, non-L0 level grouping, and ingest-behind reserved epoch behavior;
- MANIFEST batching, atomic group replay, dropped-CF atomic groups, manifest rotation, CURRENT installation, manifest sync failures, WAL addition/deletion edits, no-manifest dummy edits, and callback/waiter wakeup behavior;
- close-time MANIFEST verification paths that read back descriptor records and rewrite or report corruption on validation failure.
