# sources/storage-engines/rocksdb/db/version_set.cc lines 6777-8568

## Scope

This chunk covers the tail of `VersionSet` in `db/version_set.cc`: manifest writer queue handling after `LogAndApply`, helpers for preparing `VersionEdit`s, manifest writer construction/reuse, normal and best-efforts MANIFEST recovery, column-family listing, level-count reduction, live-file checksum export, manifest dumping, file-number and WAL-retention counters, full-state MANIFEST snapshot writing, approximate range-size estimation, live/obsolete file metadata enumeration, column-family creation, aggregate live-version size accounting, SST metadata verification, and `ReactiveVersionSet` manifest tailing for secondary/follower instances.

The code is persistence-heavy. It owns how MANIFEST contents become in-memory `Version` state, how new MANIFESTs are compacted from current state, how file/WAL/blob metadata survives reopen, and how secondary instances safely switch to a primary's current MANIFEST.

## Purpose

- Serialize manifest updates so only the queue head performs `ProcessManifestWrites`, while later writers can be grouped, awakened, or failed consistently.
- Normalize `VersionEdit` metadata before commit: next file number, previous log number, last sequence, max column family ID for drops, and WAL-only edits that do not build a new `Version`.
- Reuse an existing MANIFEST on open when `reuse_manifest_on_open` is safe, otherwise fall back to creating a fresh MANIFEST on the next write.
- Recover a `VersionSet` from the current MANIFEST, including DB ID, per-CF log numbers, file metadata, epoch numbers, and optional table-reader loading.
- Support best-efforts recovery by scanning available MANIFESTs newest-first and retaining the latest consistent point-in-time state when the latest full state is unavailable.
- Emit utility views over MANIFEST state: list column families, dump a MANIFEST, export live-file checksum data, enumerate live metadata, and retrieve metadata for a file number.
- Rebuild a compact MANIFEST snapshot containing DB ID, current WAL additions/deletions, column-family descriptors, SST/blob metadata, compact cursors, per-CF WAL state, history timestamp low-watermark, last sequence, and compacted MANIFEST size.
- Provide size and offset approximations over LSM key ranges for DB properties, range tombstone compensation, and compaction accounting.
- Construct compaction input iterators over L0 and non-L0 inputs, including range tombstone iterators and optional ephemeral table readers.
- Track obsolete SST/blob/MANIFEST files while protecting pending outputs from premature deletion.
- Tail and switch MANIFEST readers in `ReactiveVersionSet` for secondary/follower DBs.

## Important APIs, Types, And Functions

- `VersionSet::LogAndApply(...)` is the public multi-CF manifest update entry. In this chunk it validates grouped edits, creates `ManifestWriter` queue nodes, waits until the first local writer reaches the queue head, rejects updates for dropped CFs, invokes an optional `pre_cb`, and delegates to `ProcessManifestWrites`.
- `ManifestWriter` instances in `manifest_writers_` carry a CF pointer, edit list, condition variable, completion status, and completion callback. The queue serializes manifest writers under the DB mutex.
- `LogAndApplyCFHelper()` prepares column-family add/drop edits, including persisting `max_column_family` on drops so IDs are not reused after recovery.
- `LogAndApplyHelper()` prepares non-CF edits and applies them to a `VersionBuilder` unless the edit is WAL-only.
- `GetFileOptionsForManifestWrite()` and `CreateManifestWriter()` centralize MANIFEST file options, preallocation, checksum handoff classification, listener plumbing, and log block offset setup for fresh or reopened MANIFEST writers.
- `ReopenManifestForAppend()` implements the `reuse_manifest_on_open` path. It requires a known `manifest_last_valid_record_end_`, rejects best-efforts recovery, tail-size mismatches, direct writes, reopen failures, and reopened-size mismatches, and constructs `descriptor_log_` positioned at the existing file tail.
- `Recover()` reads `CURRENT`, opens the referenced MANIFEST through `SequentialFileReader` and `log::Reader`, replays it with `VersionEditHandler`, stores `manifest_file_size_`, recovers epoch numbers, logs recovered CF state, and optionally reopens the MANIFEST for append.
- `ManifestPicker`, `TryRecover()`, and `TryRecoverFromOneManifest()` implement best-efforts recovery over all descriptor files in reverse file-number order using `VersionEditHandlerPointInTime`.
- `RecoverEpochNumbers()` asks each initialized, non-dropped `ColumnFamilyData` to fill missing file epoch numbers and recover the next CF epoch counter.
- `ListColumnFamilies()` and `ListColumnFamiliesFromManifest()` parse MANIFEST records through `ListColumnFamiliesHandler` without constructing a full DB.
- `ReduceNumberOfLevels()` creates a temporary `VersionSet`, recovers the default CF, rewrites `VersionStorageInfo` level arrays when files can be collapsed into the new last level, updates file-location indexes, and persists the change with `LogAndApply`.
- `GetLiveFilesChecksumInfo()` walks current versions for all initialized, non-dropped CFs and inserts SST plus blob file checksum records into `FileChecksumList`.
- `DumpManifest()` first discovers CF names in the MANIFEST, merges them with supplied descriptors, then uses `DumpManifestHandler` to print verbose/hex/JSON decoded records.
- `MarkFileNumberUsed()` and `MarkMinLogNumberToKeep()` monotonically update recovered file-number and WAL-retention state.
- `WriteCurrentStateToManifest()` writes a compact snapshot to a `log::Writer`: DB ID, WAL additions, rolled-over WAL deletions, each live CF descriptor, all SST file metadata, compact cursors, blob file metadata and garbage, per-CF log number, default-CF min-log-to-keep, full-history timestamp low, last sequence, and approximate compacted MANIFEST size.
- `ApproximateSize()` and `ApproximateOffsetOf()` estimate bytes in key ranges by combining level metadata, `FindFileInRange`, file-size shortcuts, and table-cache `ApproximateOffsetOf`/`ApproximateSize`.
- `RemoveLiveFiles()` and `AddLiveFiles()` iterate all live `Version` nodes for each initialized CF, with a defensive fallback if `current()` is not linked into the version list.
- `MakeInputIterator()` builds the iterator set consumed by compaction: individual table iterators for L0 inputs and `LevelIterator`s for sorted non-L0 levels, then wraps them in `NewCompactionMergingIterator`.
- `GetMetadataForFile()` searches initialized current versions for a table file number and returns its level, `FileMetaData`, and owning CF.
- `GetLiveFilesMetaData()` populates public `LiveFileMetaData` fields from current SST metadata, including CF/path, bounds, sequence numbers, reads sampled, compaction state, entry/delete counts, blob ancestry, checksums, temperature, times, and epoch number.
- `GetObsoleteFiles()` drains obsolete SST/blob/MANIFEST queues, holding back files whose numbers are at or above `min_pending_output`.
- `CreateColumnFamily()` constructs a new `ColumnFamilyData`, dummy version list, current `Version`, memtable, and CF log number after a persisted CF-add edit commits.
- `GetNumLiveVersions()`, `GetTotalSstFilesSize()`, and `GetTotalBlobFileSize()` summarize version-list and unique-file storage usage.
- `VerifyFileMetadata()` compares on-disk SST size with MANIFEST metadata and, when configured, opens the table through `TableCache::FindTable()` so table-derived unique ID verification can run.
- `ReactiveVersionSet` overrides normal writable behavior. Its `Recover()`, `ReadAndApply()`, and `MaybeSwitchManifest()` use `ManifestTailer` and `log::FragmentBufferedReader` to replay primary MANIFEST updates and switch readers when `CURRENT` changes.

## Control Flow

`LogAndApply` starts with a mutex-held edit list. Empty updates return OK. Multi-edit batches are debug-checked to ensure they do not include CF manipulation or dummy no-write edits. It creates local `ManifestWriter` objects, appends their addresses to `manifest_writers_`, and waits until the first local writer is at the queue head. If an earlier grouped writer already completed this writer, it returns the completed status. Otherwise it counts undropped CFs, runs `pre_cb` only when this invocation has exclusive writer ownership, removes queued writers on early failure, signals the next queue head, or calls `ProcessManifestWrites`.

For ordinary recovery, `Recover` resolves `CURRENT` to a MANIFEST path, opens it for sequential reading, constructs a checksummed `log::Reader`, and lets `VersionEditHandler` replay all records into this `VersionSet`. On success it records the consumed reader offset as `manifest_file_size_`, copies the DB ID, runs `RecoverEpochNumbers`, and logs recovered file/log/CF state. If the DB is writable and `reuse_manifest_on_open` is enabled, it calls `ReopenManifestForAppend`; failure to reopen is intentionally converted into OK fallback in that helper so the next write rotates to a new MANIFEST.

Best-efforts recovery has a different flow. `ManifestPicker` parses file names in the DB directory, keeps descriptor files, sorts them by descending file number, and returns full paths one at a time. `TryRecover` attempts `TryRecoverFromOneManifest`, and after a failed attempt resets in-memory state before trying the next older MANIFEST. `TryRecoverFromOneManifest` uses `VersionEditHandlerPointInTime` with incomplete valid versions allowed and reports whether table files were missing.

`WriteCurrentStateToManifest` is invoked from the new-MANIFEST path in `ProcessManifestWrites` after current per-CF mutable state has been captured under the DB mutex. It does not hold the mutex itself. It writes standalone records in a careful order: DB ID first, WAL additions, a rolled-over WAL-deletion watermark, then per-CF descriptor and file-state records. It writes the compacted MANIFEST size record last because that estimate depends on the current writer file size.

`ApproximateSize` scans levels in `[start_level, end_level)`. L0 files are all treated as boundary candidates because they are not sorted. For sorted levels it binary-searches start and end files, sums full intermediate file sizes exactly, saves first/last boundary files, and either approximates boundary contribution as half the intersecting size when within the configured error margin or asks table readers for offsets.

`MakeInputIterator` allocates an array sized for the number of compaction input streams. L0 files get one table iterator each after optional start/end filtering based on user keys without timestamps. Non-L0 levels get one `LevelIterator` per input level. Range tombstone iterator ownership or pointer slots are tracked beside each child iterator so the final compaction merging iterator can see file-local tombstones.

`ReactiveVersionSet::MaybeSwitchManifest` checks `CURRENT` on every recover/read cycle. If the current reader already points at that MANIFEST, it keeps tailing. If not, it verifies the path exists, opens a new sequential file, replaces the fragment-buffered reader, logs the switch, and asks the existing tailer to prepare for a new MANIFEST. Races where the primary switches and deletes the old/new MANIFEST become `Status::TryAgain`.

## State And Persistence Behavior

- `next_file_number_`, `prev_log_number_`, `descriptor_last_sequence_`, `manifest_file_number_`, `manifest_file_size_`, `min_log_number_to_keep_`, and `column_family_set_->GetMaxColumnFamily()` are persisted or reconstructed through MANIFEST edits.
- CF drops persist `max_column_family` so recovery never reuses a previously allocated CF ID.
- `reuse_manifest_on_open` depends on `manifest_last_valid_record_end_`, which represents the exact byte offset consumed by the recovery reader. The reopened writer uses that offset for both `WritableFileWriter` size accounting and the `log::Writer` block offset, preventing record framing corruption after appending.
- `best_efforts_recovery` intentionally disables MANIFEST reuse because it rebuilds MANIFEST/CURRENT from salvaged state rather than trusting a possibly stale tail.
- New compacted MANIFEST snapshots include WAL addition state and a WAL-deletion watermark. This prevents a later WAL-addition record in the new MANIFEST from making an already-deleted WAL appear live again.
- SST metadata persistence is broad: file number, path ID, size, smallest/largest internal keys, sequence bounds, marked-for-compaction flag, temperature, blob ancestry, oldest ancestor/file creation times, epoch number, checksums, unique ID, range-deletion compensation, tail size, and user-defined timestamp metadata.
- Blob file metadata in the MANIFEST includes total blob count/bytes, checksum method/value, and garbage count/bytes when nonzero.
- Compact cursors and `full_history_ts_low` are written per CF, preserving compaction progress and history-trimming boundaries across reopen.
- `last_compacted_manifest_file_size_` and manifest tuning state are updated when a new descriptor log is installed and later used to tune maximum MANIFEST size.
- Obsolete SST/blob queues are drained only for numbers below `min_pending_output`, protecting files that may still be written or referenced by pending operations.
- `ReactiveVersionSet` is read-only with respect to normal `LogAndApply`; its persistent state arrives by replaying primary MANIFEST records.

## Dependencies And Integration Points

- MANIFEST IO uses `FileSystem`, `FSSequentialFile`, `FSWritableFile`, `SequentialFileReader`, `WritableFileWriter`, `log::Reader`, `log::FragmentBufferedReader`, and `log::Writer`.
- Version replay and printing depend on `VersionEditHandler`, `VersionEditHandlerPointInTime`, `ManifestTailer`, `ListColumnFamiliesHandler`, and `DumpManifestHandler`.
- Version construction depends on `ColumnFamilySet`, `ColumnFamilyData`, `Version`, `VersionBuilder`, `VersionStorageInfo`, `MutableCFOptions`, and `MutableCFState`.
- Table validation and approximation depend on `TableCache`, `TableReader`, `TableCacheOpenOptions`, `TableReaderCaller`, `InternalKeyComparator`, `FdWithKeyRange`, `LevelFilesBrief`, and `FindFileInRange`.
- Compaction iterator creation integrates with `Compaction`, `RangeDelAggregator`, `TruncatedRangeDelIterator`, `LevelIterator`, and `NewCompactionMergingIterator`.
- Public/admin surfaces include `DB::GetLiveFilesMetaData`, `DB::GetLiveFilesChecksumInfo`, `ldb` checksum/manifest commands, `ReduceNumberOfLevels`, and manifest dump tooling.
- Recovery/open integration is through `DBImpl::Open`, best-efforts recovery, read-only opens, secondary/follower implementations, and `CURRENT` file management.
- Observability and fault-injection rely on `ROCKS_LOG_*`, `TEST_SYNC_POINT`, `TEST_SYNC_POINT_CALLBACK`, and random kill points around MANIFEST writes.

## Risks And Edge Cases

- Manifest writer queue entries are addresses of local `ManifestWriter` objects. Correctness relies on all queued local writers being completed or removed before `LogAndApply` returns.
- `pre_cb` is intentionally delayed until the call owns the manifest writer slot; moving it earlier could execute side effects for work that later gets grouped or rejected.
- `ReopenManifestForAppend` returns OK on many fallback cases. Callers must interpret OK with `descriptor_log_ == nullptr` as "create a fresh MANIFEST later", not successful reuse.
- Appending to an existing MANIFEST is unsafe if physical size differs from the last valid record end, if direct writes remain enabled, or if the reopened handle reports a different size. These guards protect log record framing.
- `WriteCurrentStateToManifest` runs without the DB mutex. Its inputs must be stable snapshots captured before mutex release; adding new per-CF mutable fields needs the same treatment.
- The compacted MANIFEST snapshot record order matters for recovery interpretation and for the final compacted-size estimate.
- `ReduceNumberOfLevels` mutates internal `VersionStorageInfo` arrays and `file_locations_` directly, so it is only safe under its strict condition that at most one old high level contains files.
- `ApproximateSize` assumes internal key ordering and non-overlap properties for sorted levels. Range-boundary comparisons, timestamped comparators, or inclusive/exclusive mistakes can overcount or undercount.
- `MakeInputIterator` allocates raw iterator arrays and transfers tombstone iterator ownership into the merging iterator setup. Leaks or dangling tombstone pointers are plausible risks if constructor contracts change.
- `GetLiveFilesMetaData` falls back to the last CF path when a file path ID exceeds configured paths. That protects metadata generation but can mask inconsistent path IDs outside debug builds.
- `VerifyFileMetadata` only performs unique-ID verification when `verify_sst_unique_id_in_manifest` is enabled; size mismatch is always checked, but checksum verification is elsewhere.
- `ReactiveVersionSet::MaybeSwitchManifest` handles races by returning `TryAgain`, but non-POSIX filesystems may still require extra care because the primary can delete a MANIFEST while a secondary is opening or reading it.

## Test Signals

- `db_basic_test.cc` exercises `reuse_manifest_on_open`, including default-disabled behavior, reopening for append, block-offset/size accounting after reuse, close/recovery marker interactions, and fallback cases.
- `version_set_test.cc` covers best-efforts recovery through `TryRecover`/`TryRecoverFromOneManifest`, point-in-time recovery, atomic-group handling, and `ReactiveVersionSet` recover/read-and-apply behavior for valid, incomplete, corrupted, and incorrectly sized atomic groups.
- `db_secondary_test.cc` uses the `ReactiveVersionSet::MaybeSwitchManifest` sync points to test races while a secondary observes `CURRENT` and switches MANIFESTs.
- `external_sst_file_basic_test.cc`, `db_compaction_test.cc`, and `compaction_service_test.cc` observe `VersionSet::MakeInputIterator:NewCompactionMergingIterator`, especially around compaction input counts and external/remote compaction paths.
- `db_range_del_test.cc` exercises `VersionSet::ApproximateSize` for compensated range tombstone sizes, including assertions around valid start/end ordering.
- `db_etc2_test.cc` and `ldb_cmd_test.cc` validate live-file checksum extraction from MANIFEST state through `GetLiveFilesChecksumInfo`.
- SST unique-ID recovery tests route through `VersionEditHandlerPointInTime::VerifyFile()` into `VersionSet::VerifyFileMetadata`, checking both mismatch corruption and backward-compatible missing-ID behavior.
- Useful failure signatures in this chunk include manifest corruption on reopen, file-number reuse, lost CF IDs after drop/recreate, WAL deletion/addition inconsistencies after MANIFEST rotation, stale or missing live-file checksum data, compaction iterator input-count mismatches, secondary `TryAgain` loops, and incorrect live/obsolete file deletion decisions.
