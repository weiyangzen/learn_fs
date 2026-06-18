# subset-b-008612 Research

Grouped research report for RocksDB external SST file ingestion implementation and tests. Each section preserves the exact source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/external_sst_file_basic_test.cc -->
# sources/storage-engines/rocksdb/db/external_sst_file_basic_test.cc

## Purpose
`external_sst_file_basic_test.cc` is the broad regression suite for RocksDB external SST creation and ingestion. It validates `SstFileWriter`, `DB::IngestExternalFile`, and `DB::IngestExternalFiles` across normal ingestion, checksum metadata, copy/link behavior, global sequence-number assignment, range tombstones, corruption handling, atomic replacement, file temperature, manifest persistence, snapshot visibility, and column-family concurrency.

The file is not only a unit test for the public external SST APIs. It also pins several internal invariants of `ExternalSstFileIngestionJob`: whether files are copied or linked, when an ingestion must flush memtables, which sequence numbers are assigned, which level receives each file, what metadata survives reopen, and how standalone range deletion files interact with compaction.

## Important APIs, Types, And Functions
The fixture `ExternalSSTFileBasicTest` extends `DBTestBase` and is parameterized by `(write_global_seqno, verify_checksums_before_ingest)`. It creates an external SST directory, probes `RandomRWFile` support, and provides helpers:

- `DeprecatedAddFile` builds legacy ingestion options with global seqno disabled and blocking flush disabled.
- `AddFileWithFileChecksum` exercises the multi-file `IngestExternalFiles` argument path with caller-provided checksums and checksum function names.
- `GenerateAndAddExternalFile` writes point keys, merges, deletions, and range deletions into an external SST, updates an expected map, and ingests the result.
- `VerifyInputFilesInternalStatsForOutputLevel` checks compaction stats for filtered or skipped input files after ingestion-triggered compactions.

`ChecksumVerifyHelper`, `VariousFileChecksumGenerator`, and `VariousFileChecksumGenFactory` model checksum generation, requested checksum function matching, and intentionally varying checksum names. `CompactionJobStatsCheckerForFilteredFiles` observes compaction completion events to verify filtered file counts and skipped bytes.

The main test cases cover basic `SstFileWriter` metadata, aligned buffered writes, CRC32C and custom file checksums, no-copy/move ingestion, global seqno choices for overlapping data, mixed value types, fadvise, sync failures, checksum readahead, range tombstones, corrupted blocks/properties, overlapping input files, standalone range deletion compactions, file temperature, full and partial atomic replacement, bottommost-level constraints, checksum verification after ingest, SST unique IDs, stable snapshots during manifest logging, concurrent column-family drop, and large key/value limits.

## Control Flow
Most tests follow a common pattern: configure `Options`, create one or more external SSTs through `SstFileWriter`, call an ingestion API with a chosen `IngestExternalFileOptions` or `IngestExternalFileArg`, then inspect DB reads, live file metadata, level counts, sequence numbers, filesystem state, or event/stat counters.

The parameterized tests repeatedly call `ChangeOptionsForFileIngestionTest()` so the same ingestion semantics are checked under multiple RocksDB option combinations. They compare `dbfull()->GetLatestSequenceNumber()` to expected increments. Non-overlapping external files can preserve sequence number zero, while files that overwrite DB state, overlap range tombstones, or are ingested while snapshots exist require new global sequence numbers.

Range-deletion tests write tombstone-only or mixed SSTs, then verify inclusive/exclusive boundary behavior, out-of-order tombstone handling, memtable overlap flush decisions, target level placement, and final key visibility. Atomic replacement tests build existing LSM shapes, ingest replacement files with `atomic_replace_range`, and assert rejection for unsupported one-sided ranges, uncovered input files, partial overlap with existing files, memtable overlap when blocking flush is disabled, and snapshot-consistency combinations that are not supported.

Failure tests use `FaultInjectionTestEnv`, `SpecialEnv`, and sync points to disable filesystem syncs, tamper with block checksums, corrupt data/properties blocks, or observe manifest logging. These paths ensure ingestion returns errors when pre-ingest checksum verification is enabled, ignores `SyncFile` not-supported cases where allowed, and cleans up state without exposing partial ingestion.

## State And Persistence Behavior
The tests verify both transient and durable state. Transient state includes the external SST directory, whether source files remain after copy versus move/link ingestion, random-read counters during checksum verification, sync point callbacks, generated expected maps, and parameterized sequence-number expectations.

Persistent state includes table files placed into RocksDB data directories, MANIFEST entries for file checksum, checksum function name, file temperature, unique ID, smallest/largest sequence numbers, and level placement. Reopen checks in `IngestWithTemperature`, `VerifySstUniqueId`, and `StableSnapshotWhileLoggingToManifest` confirm that ingested metadata and sequence advancement survive DB restart.

The suite explicitly checks that `move_files=true` removes the original file only on successful ingestion, failed overlap leaves source files intact, bottommost or atomic replace failures leave existing data unchanged, and full-column-family atomic replacement deletes old files while preserving only newly ingested files. It also validates snapshot isolation while `VersionSet::LogAndApply` writes the manifest: a snapshot taken during manifest logging continues to see the old value, while post-reopen reads see the ingested value and later writes receive higher sequence numbers.

## Dependencies And Integration Points
The file depends on RocksDB test infrastructure (`DBTestBase`, `testharness`, `testutil`, sync points), public APIs (`SstFileWriter`, `IngestExternalFileOptions`, `IngestExternalFileArg`, `ExternalSstFileInfo`, `ColumnFamilyMetaData`, `LiveFileMetaData`), internal metadata (`ColumnFamilyData`, `InternalStats`, `VersionEdit`), environment wrappers (`FaultInjectionTestEnv`, `SpecialEnv`, `FileTemperatureTestFS`), checksum helpers, merge operators, compaction listeners, snapshots, and column-family handles.

It integrates directly with the implementation in `external_sst_file_ingestion_job.cc`: tests assert behavior for file linking/copying and directory sync, random-write global seqno update, checksum generation before and after global seqno mutation, `allow_global_seqno`, `write_global_seqno`, `verify_checksums_before_ingest`, `allow_blocking_flush`, `snapshot_consistency`, `ingest_behind`, `fail_if_not_bottommost_level`, `allow_db_generated_files`-adjacent behavior, file temperature, range conflict registration, and atomic replace deletion edits.

## Risks And Edge Cases
Important covered risks include stale reads after ingestion into universal compaction layouts, bad sequence ordering when files are moved between levels, range tombstone end-key exclusivity, out-of-order range deletions expanding file bounds, incomplete checksum vectors, wrong checksum function names, checksum recomputation after writing global seqno, unsupported random write for seqno patching, sync failure during linked-file ingestion, corruption that is only detected when checksum verification is requested, and file-temperature hints that may be missing or wrong.

Atomic replacement has especially sharp edges. The tests document that one-sided replace ranges are unsupported, upper-bound handling is currently not as exclusive as `DeleteRange` semantics, snapshot consistency with atomic replace is not supported, and partial overlap with existing files is rejected because the implementation does not synthesize tombstone files to split existing SSTs.

The large key/value test is gated by `test::HasBigMem()` because it intentionally approaches 32-bit size limits. Concurrent ingestion and column-family drop is racy by design; the accepted signal is that each operation either ingests and reads the key or fails cleanly without leaving the key visible.

## Test Signals
Primary signals are `ASSERT_OK`/`ASSERT_NOK` status checks, exact `Get` results, `GetLatestSequenceNumber()` deltas, `FilesPerLevel()` and `NumTableFilesAtLevel()` shapes, source-file existence, `LiveFileMetaData` checksum and temperature fields, `ColumnFamilyMetaData` persistence across reopen, compaction event counters, internal compaction stats, sync point callback observations, random-read counts under readahead, and `VerifyChecksum()`.

The executable is registered through the local RocksDB test harness with a `main` that installs the stack trace handler, initializes GoogleTest, registers custom objects, and runs all tests. The parameter instantiation covers all four combinations of writing global seqno and verifying checksums before ingestion.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/external_sst_file_basic_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/external_sst_file_ingestion_job.cc -->
# sources/storage-engines/rocksdb/db/external_sst_file_ingestion_job.cc

## Purpose
`external_sst_file_ingestion_job.cc` implements the internal job that turns caller-supplied external SST files into RocksDB version edits. It reads and validates table metadata, copies or links files into DB-owned paths, verifies or generates checksums, decides whether input files overlap, batches overlapping input files, assigns target levels and global sequence numbers, updates on-disk global seqno fields when requested, constructs `FileMetaData`, records equivalent compactions for range conflict checks, updates stats/events, and cleans up files on success or failure.

This file is the transactional core under `DB::IngestExternalFile(s)`. The caller is responsible for higher-level write-thread coordination and manifest application; the job prepares durable files and a `VersionEdit` that can be applied to make ingestion visible.

## Important APIs, Types, And Functions
`ExternalSstFileIngestionJob::Prepare` is the pre-manifest phase. It calls `GetIngestedFileInfo` for each path, validates column-family IDs and non-empty/correct key ranges, handles `atomic_replace_range`, rejects unsupported overlapping input modes, copies or links files, fsyncs files/directories, performs checksum generation/verification, and calls `DivideInputFilesIntoBatches`.

`Run` is the manifest-edit construction phase. It checks memtable state when the caller flushed before run, enforces no remaining flush need in debug builds, determines whether snapshots force global seqnos, deletes existing files for `atomic_replace_range`, assigns levels/seqnos per batch, and creates equivalent compactions.

Other key functions are `NeedsFlush`, `MergeForSameColumnFamily`, `ComputeFilesOverlap`, `AssignLevelsForOneBatch`, `AssignLevelAndSeqnoForIngestedFile`, `CheckLevelForIngestedBehindFile`, `AssignGlobalSeqnoForIngestedFile`, `GenerateChecksumForIngestedFile`, `GetIngestedFileInfo`, `SanityCheckTableProperties`, `ResetTableReader`, `GetSeqnoBoundaryForFile`, `IngestedFileFitInLevel`, `CreateEquivalentFileIngestingCompactions`, `RegisterRange`, `UnregisterRange`, `UpdateStats`, `Cleanup`, and `DeleteInternalFiles`.

## Control Flow
Preparation starts by scanning every external path. For each file, the job creates a DB file descriptor, opens a `TableReader`, validates external SST version/global seqno properties, validates comparator and user-defined timestamp compatibility, optionally computes existing DB-generated seqno boundaries, verifies checksums, obtains smallest/largest point keys, expands bounds with range tombstones, derives user-key overlap bounds, and extracts a unique ID.

After input metadata is collected, the job detects input-file overlap by sorting range pointers and checking adjacent ranges with `ExternalFileRangeChecker`. Overlap affects batching and sequence-number assignment. Overlapping files cannot be ingested behind, require global seqnos unless DB-generated files are allowed, and are disallowed for user-defined timestamp column families.

The copy/link phase places every file at its final DB table filename. `move_files` or `link_files` first try `LinkFile`; unsupported links can fall back to copy if configured. Linked files are explicitly synced because applications may not have synced the source. Copied files use `CopyFile`, which also syncs and may change the destination temperature based on write or last-level temperature options. Data directories are fsynced after files are added.

Checksum handling has two phases. During `Prepare`, if a DB checksum factory exists, the job either trusts complete caller-provided checksums when verification is disabled or generates checksums and compares them to caller input when verification is enabled. If `write_global_seqno` will mutate the file later, final manifest checksum generation is deferred. During `Run`, after global seqno assignment, `GenerateChecksumForIngestedFile` recomputes checksum metadata for the manifest when needed.

`Run` uses current `SuperVersion` storage info. For atomic replace, it emits `DeleteFile` edits for fully covered existing files and rejects pending compaction overlap or partial overlap. For each batch, `AssignLevelAndSeqnoForIngestedFile` walks levels from top toward the allowed boundary, checks pending compactions and existing file overlap, chooses the lowest fitting level, and assigns `last_seqno + 1` when snapshots, input overlap, L0/FIFO placement, or DB overlap require ordering. Each ingested file becomes a `FileMetaData` added to the `VersionEdit`.

## State And Persistence Behavior
The job owns transient vectors of `IngestedFileInfo`, `FileBatchInfo`, equivalent `Compaction` objects, and temporary `FileMetaData` allocations. It also accumulates persistent intent in `edit_`: delete edits for atomic replacement and add edits for ingested files.

On disk, `Prepare` creates or links internal SST files in DB data paths and fsyncs files/directories. `AssignGlobalSeqnoForIngestedFile` may open the internal file as `FSRandomRWFile`, write the encoded sequence number at the table property offset, and sync the modified file. `Cleanup` deletes internal files on failure; on success with `move_files`, it deletes original external links. Successful ingestion persists metadata only when the caller later applies `edit_` to the manifest.

File metadata carries level, file number/path ID/size, internal key bounds, smallest/largest sequence numbers, temperature, epoch number, checksum and checksum function name, unique ID, tail size, timestamp persistence flag, min/max timestamp properties, file-open metadata when fast SST open is enabled, and a marked-for-compaction bit for standalone range deletion files.

## Dependencies And Integration Points
The implementation depends on `VersionSet`, `ColumnFamilyData`, `SuperVersion`, `VersionStorageInfo`, `TableReader`, table factories, `SstFileWriter` external properties, `FileSystem`, `Directories`, `CopyFile`, checksum generators, `IOTracer`, `EventLogger`, internal stats, compaction picker, `RangeOverlapWithCompaction`, `OverlapWithLevelIterator`, `SnapshotList`, user-defined timestamp utilities, unique-ID helpers, sync points, and RocksDB logging/status APIs.

It integrates with write-thread orchestration through mutex/write-thread preconditions on `Run`, `RegisterRange`, `UnregisterRange`, and `UpdateStats`. Equivalent compactions are registered with the compaction picker so ingestion ranges conflict with concurrent compactions. `MergeForSameColumnFamily` supports combining prepared handles for a single column family while preserving user-specified file order and higher-seqno-wins semantics.

## Risks And Edge Cases
Range comparison is built on internal keys and comments warn the `sstableKeyCompare` approach with user comparators is fragile. Range tombstones require special bound updates, and user-defined timestamps require comparing user keys without timestamp bytes by constructing max/min timestamp versions.

Correct sequence-number behavior is central. Files with existing nonzero sequence numbers are rejected unless `allow_db_generated_files` is enabled. DB-generated files may not overlap existing DB data because the job will not rewrite their seqnos. Snapshot consistency, overlapping input files, L0/FIFO placement, pending compaction overlap, and existing-level overlap all force assigned seqnos. If `allow_global_seqno` is false, those cases fail.

Atomic replacement is conservative: full-CF replacement fails while any compaction is in progress; ranged replacement rejects pending compaction overlap, partial file overlap, unsupported one-sided ranges upstream, and files outside the replace range. The code comments note that synthesizing tombstone files for partial overlap is a future possibility.

Filesystem behavior is another risk surface. Linking can fail or be unsupported; syncing linked files can fail except `NotSupported` is ignored for some filesystems; random-write support controls whether global seqno can be physically written; checksum generation reads whole files and TODOs mention rate limiting and IO activity plumbing. Cleanup logs deletion failures but cannot guarantee all artifacts are removed if the filesystem fails.

## Test Signals
This file is heavily exercised by `external_sst_file_basic_test.cc` and related ingestion tests. Useful signals are successful ingestion plus correct DB reads, expected `InvalidArgument`, `TryAgain`, `NotSupported`, or `Corruption` failures, manifest file metadata matching checksum/temperature/unique ID/seqno expectations, no leaked internal files after failed ingestion, source-file deletion after successful move ingestion, level counts after overlapping batches, internal stats/event logger updates, and sync point paths around file sync, directory sync, random write, seqno sync, overlap detection, and seqno-boundary file scans.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/external_sst_file_ingestion_job.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/external_sst_file_ingestion_job.h -->
# sources/storage-engines/rocksdb/db/external_sst_file_ingestion_job.h

## Purpose
`external_sst_file_ingestion_job.h` declares the data structures and job API used to ingest external SST files into a RocksDB column family. It defines range metadata, file metadata collected from external tables, batching metadata for overlapping inputs, and the `ExternalSstFileIngestionJob` class that prepares files, checks flush needs, creates version edits, registers range conflicts, updates stats, and cleans up.

The header captures the contract between DB ingestion orchestration and the implementation file. It makes clear which methods require the DB mutex, which operations are thread-safe, and which state is prepared before the final manifest edit is applied.

## Important APIs, Types, And Functions
`KeyRangeInfo` stores smallest and largest `InternalKey` bounds. Its `unset()` helper treats unset internal keys as invalid or unbounded sentinel values.

`ExternalFileRangeChecker` wraps a user comparator and supplies ordering, overlap, containment, and range-extension helpers. `operator()` sorts `KeyRangeInfo` pointers by smallest internal key. `Overlaps` supports a fast path when sorted ranges are known ordered. `Contains` validates range containment. `MaybeUpdateRange` expands a `KeyRangeInfo` with new start/end internal keys.

`IngestedFileInfo` extends `KeyRangeInfo` with external path, timestamp-aware user-key overlap bounds, original and assigned sequence numbers, global seqno offset, file size, entry and range deletion counts, column-family ID, table properties, external file version, destination `FileDescriptor`, internal path, picked level, copy/link decision, checksum metadata, temperature, unique ID, user-defined timestamp persistence flag, and seqno boundaries for DB-generated files.

`FileBatchInfo` extends `KeyRangeInfo` and groups `IngestedFileInfo*` values. Its `track_batch_range` flag controls whether `AddFile` maintains the batch's aggregate range. Non-overlapping inputs can skip range tracking in a single default batch; overlapping inputs use tracked batches to preserve order while avoiding overlap within a batch.

`ExternalSstFileIngestionJob` exposes `Prepare`, `NeedsFlush`, `SetFlushedBeforeRun`, `Run`, `RegisterRange`, `UnregisterRange`, `UpdateStats`, `Cleanup`, `edit`, `files_to_ingest`, `MaxAssignedSequenceNumber`, and `MergeForSameColumnFamily`.

## Control Flow
The public lifecycle is:

1. Construct the job with version-set, column-family, immutable/mutable DB options, env options, snapshot list, ingestion options, directories, event logger, and IO tracer.
2. Call `Prepare` with external paths, optional checksum vectors, optional atomic replace range, temperature hint, next file number, and `SuperVersion`. This fills `files_to_ingest_`, copies or links files into DB storage, validates input metadata, and forms file batches.
3. Call `NeedsFlush` as needed to decide whether memtables overlap the ingested ranges or atomic replace range. If a flush is performed, call `SetFlushedBeforeRun`.
4. Under the DB writer/mutex protocol, call `Run` to assign levels/seqnos and populate `edit_`.
5. Register equivalent compaction ranges before manifest application when needed, then unregister on destruction or explicit cleanup.
6. Call `UpdateStats` after success and `Cleanup` with the final status to delete temporary internal files on failure or remove original moved files on success.

Private helpers in the class declaration show the major implementation phases: table-reader reset, table-property sanity checks, ingested-file metadata extraction, overlap batching, level and seqno assignment, ingest-behind validation, global seqno writing, checksum generation, level fit checks, syncing, DB-generated seqno boundary scanning, equivalent compaction creation, and failed-file deletion.

## State And Persistence Behavior
Most fields are borrowed pointers or references to DB-owned state: `VersionSet`, `ColumnFamilyData`, comparators, options, snapshots, directories, and event logger. Job-owned mutable state includes `files_to_ingest_`, `file_batches_to_ingest_`, `atomic_replace_range_`, `edit_`, `job_start_time_`, `max_assigned_seqno_`, `files_overlap_`, `need_generate_file_checksum_`, `flushed_before_run_`, and vectors holding equivalent compaction objects.

The header documents that `MaxAssignedSequenceNumber` has two interpretations. With normal external files, assigned global seqnos follow `versions_->LastSequence()` when global seqno assignment is needed. With `allow_db_generated_files=true`, files already carry sequence numbers, so the max is the largest seqno observed in the ingested files.

Persistent effects are not applied directly by the header API, but the job prepares them through `edit_` and DB-owned internal file paths. `Cleanup` semantics are part of the public contract: failed jobs delete internal files; successful move ingestion removes original paths.

## Dependencies And Integration Points
The header depends on RocksDB internal DB metadata (`column_family.h`, `internal_stats.h`, `snapshot_impl.h`, `version_edit.h`), filesystem tracing and file-system abstractions, event logging, DB options, public `rocksdb/db.h` and `rocksdb/sst_file_writer.h`, and `autovector`.

`ExternalSstFileIngestionJob` is integrated into DB ingestion code that owns write serialization, super-version lifetime, manifest application, sequence-number advancement, and column-family lifetime. It also integrates with compaction conflict tracking by creating `Compaction` objects equivalent to the ingestion's output ranges and registering them with the column family's compaction picker.

## Risks And Edge Cases
The range checker works on internal keys and asserts that ranges are set and legal. Bad unset handling can silently return false in release builds after an assertion path, so callers must validate table key bounds before overlap checks.

`IngestedFileInfo` carries two sets of range concepts: internal key bounds for manifest metadata and `start_ukey`/`limit_ukey` for overlap checks without user-defined timestamp bytes. Mixing those fields would break UDT ingestion and overlap detection. The default `copy_file=true` is intentional to avoid undefined behavior before options decide copy versus link.

Batching order matters for overlapping inputs: later files are meant to win by receiving higher sequence numbers. `MergeForSameColumnFamily` also preserves append order for this reason. Atomic replace range, ingest-behind, bottommost-level requirements, and DB-generated file ingestion all restrict which helper paths are legal.

## Test Signals
The header's contract is indirectly validated by the external SST ingestion tests. Relevant signals include correct `files_to_ingest()` metadata after prepare, `NeedsFlush` decisions for point and range-tombstone overlaps, `edit()` containing expected add/delete file edits, `MaxAssignedSequenceNumber()` matching sequence advancement, range registration preventing compaction conflicts, successful cleanup behavior, and compile-time enforcement of method signatures used by DB ingestion orchestration.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/external_sst_file_ingestion_job.h -->
