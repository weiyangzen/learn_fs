# subset-b-008621 research

Grouped research for RocksDB version edit and version builder files. Each file section is source-tree-aligned and delimited for reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/version_builder_test.cc -->
# sources/storage-engines/rocksdb/db/version_builder_test.cc

## Purpose

This file is a focused GoogleTest suite for RocksDB's `VersionBuilder` behavior. It constructs synthetic `VersionStorageInfo` state, applies `VersionEdit` objects, saves the resulting version state, and checks both successful materialization and corruption detection. The covered domain is manifest replay semantics for SST files and blob files: additions, deletions, dynamic-level layouts, blob garbage accounting, SST-to-blob link maintenance, L0 epoch ordering, and estimated active key accounting.

## Important APIs, types, and helpers

- `VersionBuilderTest` owns the test fixture state: `BytewiseComparator`, `InternalKeyComparator`, `Options`, `ImmutableOptions`, `MutableCFOptions`, `VersionStorageInfo`, FIFO options, and level compaction scratch state.
- `Add(...)` allocates a `FileMetaData`, fills key bounds, sequence bounds, file size, entry/deletion stats, `oldest_blob_file_number`, and `epoch_number`, then inserts it into the base `VersionStorageInfo`.
- `AddBlob(...)` creates `SharedBlobFileMetaData` and `BlobFileMetaData` with checksum, linked SSTs, and garbage counters, then inserts it into the base storage.
- `AddDummyFile(...)` and `AddDummyFileToEdit(...)` create small L0 table files used to make blob files reachable from SST metadata.
- `UpdateVersionStorageInfo(...)` runs `PrepareForVersionAppend` and `SetFinalized`, matching the state `VersionBuilder` expects before applying edits.
- `UnrefFilesInVersion(...)` mirrors fixture cleanup by decrementing `FileMetaData::refs` and deleting unreferenced files in temporary versions.

## Control flow and behavior covered

The tests generally follow a common flow: build a base `VersionStorageInfo`, finalize it, create one or more `VersionEdit`s, apply them through `VersionBuilder::Apply`, write to a fresh `VersionStorageInfo` with `SaveTo`, finalize the result, and assert derived state. The early tests validate table-file edits: additions increase level byte totals, deletes remove files, multiple additions are sorted into the saved version, dynamic level bytes do not break accounting, and add/delete combinations for the same file number produce the expected final file location.

The corruption tests verify `VersionBuilder::Apply` rejects deletes at the wrong level, deletes of files absent from the LSM tree, duplicate additions already present in the base version, and duplicate additions already staged by previous edits. Later tests cover blob-file operations: adding blob files, rejecting duplicate blob additions, applying blob garbage to base or newly added blob files, rejecting garbage for missing blob files, and rejecting garbage count/byte overflow.

The larger blob tests exercise `VersionBuilder::SaveTo` behavior. `SaveBlobFilesTo` verifies obsolete blob files are pruned when their linked SSTs disappear or they become entirely garbage. `SaveBlobFilesToConcurrentJobs` captures a concurrency pattern where a lower-numbered blob file can be added after a higher-numbered one already exists. `MaintainLinkedSstsForBlobFiles` checks that SST additions, deletions, trivial moves, and add-then-delete sequences correctly update `BlobFileMetaData::LinkedSsts` without unnecessarily recreating metadata objects.

The final consistency tests validate forced consistency checks: inconsistent SST/blob links, blob files that are entirely garbage but still linked, deleting the same file twice across versions, and invalid L0 ordering by `epoch_number`. `EstimatedActiveKeys` verifies sampled file stats drive the expected active-key estimate, subtracting deletions twice.

## State and persistence behavior

Although this file does not write real MANIFEST records, it models the in-memory result of manifest replay. `VersionEdit` instances represent persistent edit records, while `VersionBuilder` applies them to base `VersionStorageInfo` and emits a new version state. The tests manually manage `FileMetaData` references because temporary versions share metadata pointers with the base version. Blob-file tests are especially stateful: a blob file remains live only when linked SST metadata references it and its garbage counters have not consumed the whole file.

`epoch_number` is treated as required ordering metadata for L0 tests. Files in L0 must be sorted newest-first by epoch, and overlapping files with the same epoch are corruption signals. Tests sometimes pass `EpochNumberRequirement::kMightMissing` to temporary `VersionStorageInfo` to avoid making unrelated metadata mandatory.

## Dependencies and integration points

The suite depends on `db/version_edit.h`, `db/version_set.h`, `VersionStorageInfo`, `VersionBuilder`, `FileMetaData`, `BlobFileMetaData`, `SharedBlobFileMetaData`, internal key formatting, RocksDB test harness macros, and checksum/unique-id constants. It is an integration-level unit test for the version-building layer rather than a pure unit test: it validates interactions among version edits, file metadata, blob metadata, level layout accounting, and consistency checking in `VersionStorageInfo`.

## Risks and edge cases

- Manual reference cleanup is easy to get wrong; missed `UnrefFilesInVersion` calls would leak metadata in tests or hide ownership assumptions.
- Several tests use `kUnknownEpochNumber` for non-L0 additions while newer code may tighten epoch requirements. Future changes must preserve the explicit `EpochNumberRequirement` intent.
- Blob metadata correctness depends on both directions of linkage: SST `oldest_blob_file_number` and blob `LinkedSsts`. The tests show corruption can be detected late at `SaveTo`, not only at `Apply`.
- Some tests intentionally mutate staged/new storage, such as corrupting L0 epoch order, to force consistency failures. These are valuable regression tests for invariants not normally violated by public APIs.

## Test signals

This file is itself the test signal. It exercises success and failure paths with `ASSERT_OK`, `ASSERT_NOK`, `ASSERT_TRUE(s.IsCorruption())`, and state assertions on level bytes, file locations, blob metadata fields, linked SST sets, L0 file ordering, and active-key estimates. Failure messages are checked with `std::strstr`, so user-visible corruption text is part of the tested contract.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/version_builder_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/version_edit.cc -->
# sources/storage-engines/rocksdb/db/version_edit.cc

## Purpose

This file implements the `VersionEdit` manifest codec and related metadata helpers for RocksDB. A `VersionEdit` is the durable unit of version-state change written to MANIFEST: it can carry DB-wide fields, column-family fields, SST additions/deletions, blob-file additions/garbage, WAL additions/deletions, atomic group markers, user-defined timestamp flags, and subcompaction progress snapshots. The implementation defines how those fields are encoded, decoded, debug-rendered, and merged for recovery.

## Important APIs, types, and functions

- `PinnedTableReader` implements copyable pin state for a table reader plus cache handle using acquire/release ordering around the atomic reader pointer.
- `PackFileNumberAndPathId` packs a file number and path ID into one integer, preserving the lower `kFileNumberMask` bits for the file number.
- `FileMetaData::UpdateBoundaries` updates smallest/largest internal keys, sequence bounds, and `oldest_blob_file_number` while scanning entries. It decodes `BlobIndex` values and wide-column blob references to maintain blob dependencies.
- `VersionEdit::EncodeTo` serializes a complete edit using stable manifest tags.
- `VersionEdit::EncodeToNewFile4` and `DecodeNewFile4From` implement the current SST-addition format, including custom tagged metadata fields.
- `VersionEdit::DecodeFrom` parses all supported historical and current tags, including old `kNewFile`, `kNewFile2`, `kNewFile3`, current `kNewFile4`, blob records, WAL records, and safe-ignore future tags.
- `DebugString` and `DebugJSON` render decoded edits for manifest dump tooling.
- `SubcompactionProgressPerLevel`, `SubcompactionProgress`, and `SubcompactionProgressBuilder` encode, decode, and merge compaction progress deltas.

## Control flow

Encoding starts by writing optional scalar fields in a stable order: DB ID, comparator, log numbers, next file number, max column family, min log number to keep, last sequence, compact cursors, and deleted files. New SST files are encoded as `kNewFile4`; the caller must provide timestamp size when there are new files. The encoder rejects invalid file boundaries or missing epoch numbers by returning `false`. Blob additions, blob garbage, WAL additions/deletions, column-family markers, atomic group state, full-history timestamp lower bound, persist-user-defined-timestamp flag, subcompaction progress, and last compacted manifest size follow.

`EncodeToNewFile4` writes level, file number, file size, encoded key bounds, sequence bounds, then a custom-field sequence ending in `kTerminate`. Custom fields include path ID, compaction mark, min-log-number hack, oldest blob file number, oldest ancestor time, creation time, epoch number, checksums, temperature, unique ID, compensated range deletion size, tail size, user-defined timestamp persistence, min/max timestamps, and file-open metadata. File boundaries are stripped of user-defined timestamps when `user_defined_timestamps_persisted` is false.

Decoding loops over varint tags until input is exhausted or malformed. Unknown tags with the safe-ignore mask are skipped by length; unknown unmasked tags produce corruption. Historical file formats populate progressively less metadata, while `kNewFile4` delegates custom-field parsing to `DecodeNewFile4From`. Decode errors are returned as `Status::Corruption` or the status from nested blob/WAL/subcompaction decoders.

Subcompaction progress uses nested tagged custom fields. Per-level progress persists only the delta of output files since `last_persisted_output_files_count_`, preventing quadratic manifest growth as progress is snapshotted repeatedly. The builder merges multiple decoded delta edits by replacing scalar progress fields and appending output-file deltas.

## State and persistence behavior

The file defines durable manifest wire compatibility. Tag numbers are persistent and cannot be changed. Safe-ignore masks allow downgrade/forward compatibility when the reader can skip unknown length-prefixed fields. Critical custom fields without a safe-ignore bit intentionally fail recovery. New SST files added to a `VersionEdit` are also recorded in `files_to_quarantine_` so failed manifest commits can avoid deleting files that may have become durable.

`VersionEdit::ShouldEmitPerColumnFamilyRecoveryEdit` decides whether a recovery edit contains enough state to be worth writing for a column family. `VersionEdit::Clear` resets the object by assigning a fresh default. `AddFile` updates `last_sequence_` to the file's largest sequence number when needed, so file additions advance recovery sequence state.

## Dependencies and integration points

This implementation depends on RocksDB internal coding utilities (`PutVarint*`, `GetVarint*`, length-prefixed slices), internal key encoding, blob index decoding, wide-column serialization, WAL edit codecs, table unique-id helpers, `JSONWriter`, and test sync points. Its output is consumed by manifest readers such as `VersionEditHandler`, `VersionSet`, manifest dump tooling, and best-effort recovery/tailing paths.

## Risks and edge cases

- Manifest wire compatibility is fragile: changing tag values or field encoding would break recovery and downgrade behavior.
- `EncodeTo` requires `ts_sz` for new files and asserts in debug builds; callers must pass timestamp size whenever SST additions are present.
- `DecodeNewFile4From` handles non-safe custom fields strictly. A future critical field will intentionally make older readers fail.
- `PinnedTableReader` copy semantics are explicitly fragile: callers must avoid double releases after copying pinned handles.
- Subcompaction progress merging assumes all processed edits belong to the same subcompaction; the builder does not validate identity and can silently mix unrelated progress.
- The min-log-number-to-keep custom field is described as a compatibility hack embedded inside `kNewFile4`, so it is a known maintenance hazard.

## Test signals

This file contains sync points used by tests around oldest ancestor time, file creation time, unique ID, custom field encoding, and ignored tags. Broader behavior is covered by version-edit, manifest, recovery, and version-builder tests elsewhere. The adjacent `version_builder_test.cc` validates many downstream invariants produced after decoded edits are applied.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/version_edit.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/version_edit.h -->
# sources/storage-engines/rocksdb/db/version_edit.h

## Purpose

This header declares RocksDB's version-edit data model: the persistent tags used in MANIFEST records, file metadata structures used by versions, subcompaction progress structures, and the `VersionEdit` API for describing changes to DB and column-family state. It is a central contract between manifest writing, manifest replay, version building, table loading, blob tracking, WAL tracking, recovery, and debugging.

## Important APIs and types

- `enum Tag` defines on-disk MANIFEST tags. Values are persistent and include base LevelDB fields, RocksDB-specific file formats, column-family manipulation, atomic groups, blob files, WAL edits, user-defined timestamp fields, subcompaction progress, and last compacted manifest size.
- `enum NewFileCustomTag` defines extensible fields inside `kNewFile4`, including path ID, oldest blob file, time metadata, checksums, temperature, timestamp bounds, unique ID, epoch number, range-deletion compensation, tail size, UDT persistence, and file-open metadata.
- `PinnedTableReader` carries a `TableReader*` and cache handle with concurrency-aware access.
- `FileDescriptor` stores packed file number/path ID, file size, and sequence range, plus optional pinned table reader.
- `FileSampledStats` holds atomic read-sampling counters used for compaction/read statistics.
- `FileMetaData` is the rich in-memory description of an SST: descriptor, key range, stats, sizes, refcount, compaction flags, temperature, blob linkage, time metadata, epoch, checksum, unique ID, tail size, UDT fields, timestamp bounds, and file-open metadata.
- `FdWithKeyRange` and `LevelFilesBrief` provide compact read-path representations of files per level.
- `SubcompactionProgressPerLevel`, `SubcompactionProgress`, and `SubcompactionProgressBuilder` model persisted compaction progress and delta merging.
- `VersionEdit` exposes setters/getters and mutation APIs for manifest edits: file add/delete, blob file add/garbage, WAL add/delete, column family add/drop, compact cursors, full-history timestamp lower bound, atomic group state, and debug output.

## Control flow and API usage

Writers construct a `VersionEdit` by setting DB/CF scalar fields and adding mutation entries. `AddFile` creates or copies `FileMetaData`, appends it with its target level, records the file for quarantine-on-commit-failure, and updates `last_sequence_` from the file's largest sequence number. `DeleteFile` records a level/file-number pair in a set. Blob additions and WAL additions are separate vectors; WAL addition and deletion are asserted to be mutually exclusive at the edit level.

Column-family add/drop operations assert that the edit contains no file/blob/WAL entries and that add/drop are not mixed. Atomic group state is represented by `MarkAtomicGroup` and remaining-entry count. `EncodeTo` and `DecodeFrom` bridge the in-memory edit to the manifest wire format. Debug APIs provide human-readable and JSON dump forms.

`FileMetaData` boundary helpers are used while generating table metadata. `UpdateBoundaries` expects keys in sorted order and updates largest key with each call, while `UpdateBoundariesForRange` accepts unordered range tombstones and compares through `InternalKeyComparator`. Timestamp/time helper methods try local metadata first and fall back to pinned table properties.

## State and persistence behavior

This header is explicit about persistent compatibility. Tag values are written to disk and must remain stable. Safe-ignore masks separate forward-compatible unknown fields from critical fields. `kFileNumberMask` reserves high bits for path ID packing. Unknown time and epoch constants are represented as zero, while `kReservedEpochNumberForFileIngestedBehind` reserves epoch one for ingest-behind behavior.

`FileMetaData` owns mutable recovery and compaction state that survives through version building: refcounts, `being_compacted`, `marked_for_compaction`, stats initialization, blob references, checksums, user-defined timestamp persistence, and file-open metadata. `ApproximateMemoryUsage` must be updated when new string fields are added, which is noted as a maintenance warning.

Subcompaction progress deliberately persists output-file deltas rather than the full accumulated output list every time. The builder reconstructs complete progress from a sequence of edits, but its comments state that callers must ensure all inputs refer to the same subcompaction.

## Dependencies and integration points

The header depends on blob addition/garbage records, DB internal format, WAL edit definitions, arena and malloc utilities, advanced cache/options APIs, table readers, unique-id helpers, and sync points. It is included by `version_edit.cc`, `version_edit_handler`, `version_builder`, `version_set`, manifest dump utilities, recovery code, tests, and blob/compaction components that need file metadata.

## Risks and edge cases

- `PinnedTableReader` is copyable but not movable; copy assignment relies on caller discipline around cache-handle lifetime.
- Many fields have persistence defaults. Missing or incorrectly defaulted fields, especially epoch number, timestamp persistence, or checksum fields, can cause recovery errors or subtle metadata loss.
- `FileMetaData::UpdateBoundaries` requires sorted keys; misuse would corrupt smallest/largest bounds.
- `FileMetaData::ApproximateMemoryUsage` is manually maintained for string fields.
- `VersionEdit::IsWalManipulation` and edit-entry counts rely on booleans and vector sizes; mixed WAL/file edits are constrained by assertions but still require disciplined callers.
- Subcompaction progress builder can silently merge unrelated subcompactions.

## Test signals

The header exposes test-only hooks such as `PinnedTableReader::TEST_SetReader` and `SubcompactionProgressPerLevel::TEST_ClearOutputFiles`, plus sync points in constructors and tail-size calculation. Its behavior is indirectly exercised by version-edit codec tests, manifest recovery tests, and `version_builder_test.cc`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/version_edit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/version_edit_handler.cc -->
# sources/storage-engines/rocksdb/db/version_edit_handler.cc

## Purpose

This file implements MANIFEST replay handlers built around `VersionEdit`. It reads logical records from a MANIFEST log, decodes edits, handles atomic-group buffering, applies edits to column families and version builders, loads table metadata, verifies file availability, maintains replay parameters, supports point-in-time recovery, supports manifest tailing for secondary/follower instances, and provides manifest dump output.

## Important APIs, classes, and functions

- `VersionEditHandlerBase::Iterate` is the generic replay loop over `log::Reader`.
- `ListColumnFamiliesHandler::ApplyVersionEdit` tracks column-family add/drop records to list live CF names.
- `FileChecksumRetriever` builds a file-number to checksum map across SST and blob file additions, removing entries on file deletion or CF drop.
- `VersionEditHandler` implements normal recovery replay into a `VersionSet`, including CF creation/drop, WAL changes, non-CF file edits, global manifest parameters, table loading, and final version installation.
- `VersionEditHandlerPointInTime` extends replay to maintain the latest valid point-in-time version when the end state may reference missing files.
- `ManifestTailer` extends point-in-time handling for secondary/follower catch-up, including repeated reads and mode switching from recovery to catch-up.
- `DumpManifestHandler` prints individual edits and final column-family/version state for diagnostic tools.

## Control flow

`VersionEditHandlerBase::Iterate` initializes the handler, then reads records until the reader reaches `max_manifest_read_size_`, returns EOF, hits a read status error, or a handler status fails. Each record is decoded into a `VersionEdit`, the end offset is stored as `last_valid_record_end_`, and the edit is fed into `AtomicGroupReadBuffer`. Atomic-group edits are only replayed when the buffer is full; non-atomic edits are applied immediately. On corruption, the handler appends the MANIFEST filename to the error state.

Normal `VersionEditHandler::ApplyVersionEdit` dispatches by edit type: column-family add, column-family drop, WAL addition, WAL deletion, or regular CF operation. CF add checks whether the CF is already open or intentionally not opened, handles the persistent stats CF specially, and creates a `ColumnFamilyData` plus `BaseReferencedVersionBuilder` when appropriate. CF drop removes builders and marks the CF dropped. WAL operations update `version_set_->wals_`. Regular CF operations validate CF presence, pad stripped user-defined timestamp file boundaries when needed, and call `MaybeCreateVersionBeforeApplyEdit`.

At end of iteration, `CheckIterationResult` validates required manifest globals: log number, next file number, and last sequence. It rejects unopened column families in normal mode, updates max CF/min log/file-number accounting, checks builder level consistency, loads table handlers unless configured to skip, creates final versions for all live CFs, updates manifest read offsets and valid-record offsets, advances sequence-number atomics, and stores previous log number.

Point-in-time replay wraps builder save points around each edit. It saves a version when a valid state is about to become invalid or when a valid state is explicitly forced. It suppresses table-loading failures caused by missing files and uses atomic update buffering so multi-CF atomic groups only become visible all at once. Manifest tailing reuses recovery initialization for the first pass, then in catch-up mode rebuilds builders from current live versions and tracks changed CFs.

## State and persistence behavior

The handlers transform durable MANIFEST records into live `VersionSet` state. `version_edit_params_` accumulates persistent manifest parameters such as DB ID, log numbers, next file, max CF, min log number to keep, last sequence, and last compacted manifest size. `last_valid_record_end_` records the byte offset after the last fully decoded logical edit, allowing recovery/tailing to distinguish durable valid data from a torn or partial tail.

Column-family state is split among `builders_` for opened CFs and `do_not_open_column_families_` for CFs present in MANIFEST but not requested by the caller. Read-only or tailing modes can tolerate unopened CFs differently from normal DB open. User-defined timestamp state is also persistent: if enabling UDT is detected for a CF, existing SST boundaries are padded and files are marked as not having persisted UDTs so in-memory boundaries match the running comparator.

Point-in-time state is held in `versions_` and `atomic_update_versions_`. Incomplete atomic groups are discarded rather than partially applied. `HasMissingFiles` delegates to version builders so callers can detect best-effort recovery outcomes.

## Dependencies and integration points

This file integrates with `log::Reader`, `AtomicGroupReadBuffer`, `VersionEdit`, `VersionSet`, `ColumnFamilySet`, `ColumnFamilyData`, `BaseReferencedVersionBuilder`, `VersionBuilder`, table cache loading, blob sources/readers, WAL state, persistent stats CF options, user-defined timestamp utilities, `IOTracer`, RocksDB logging, and manifest dump stdout tooling.

## Risks and edge cases

- Atomic-group handling must preserve all-or-nothing visibility. Incomplete or nested groups produce corruption or discarded buffered versions.
- `CheckIterationResult` performs many finalization actions; failures after partial builder state exists must avoid installing invalid versions.
- Missing table files are conditionally tolerated depending on `no_error_if_files_missing_`, `paranoid_checks`, point-in-time mode, and best-effort recovery settings.
- `MaybeHandleFileBoundariesForNewFiles` assumes all new files in one edit have consistent `user_defined_timestamps_persisted` unless existing SSTs are being marked no-UDT. Mixed values are corruption.
- `FileChecksumRetriever::ApplyVersionEdit` returns `NotFound` when deleting an unknown checksum entry, so it is stricter than some recovery paths.
- `ManifestTailer::OnColumnFamilyAdd` ignores new CFs not already present during catch-up, which is intentional but important for secondary/follower semantics.
- Blob verification opens blob files but has a TODO for checksum verification.

## Test signals

The implementation exposes sync points around `Iterate` finish, load-table skipping, and point-in-time version creation. It is exercised by manifest recovery tests, secondary/tailing tests, WAL tracking tests, checksum retrieval tests, dump-manifest tests, and downstream version-builder tests. The explicit corruption strings in this file form part of recovery diagnostics.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/version_edit_handler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/version_edit_handler.h -->
# sources/storage-engines/rocksdb/db/version_edit_handler.h

## Purpose

This header declares the MANIFEST replay handler hierarchy for RocksDB version edits. It defines the base iteration interface, specialized handlers for listing column families and retrieving checksums, the main `VersionEditHandler` used during DB recovery, point-in-time recovery support, manifest tailing for secondary/follower instances, and a dump handler for diagnostic output.

## Important APIs and types

- `VersionEditHandlerBase` owns replay status, read options, `AtomicGroupReadBuffer`, `last_valid_record_end_`, and the `Iterate` entry point. Subclasses implement `ApplyVersionEdit` and can hook initialization, atomic-group begin/end, and final iteration checks.
- `ListColumnFamiliesHandler` maintains a map from CF ID to name, initialized with the default CF, and applies only CF add/drop edits.
- `FileChecksumRetriever` scans edits up to a bounded manifest size and exposes `FetchFileChecksumList`.
- `VersionEditHandler` is the normal recovery handler. It owns requested column-family descriptors, a `VersionSet`, per-CF version builders, unopened-CF tracking, replayed version parameters, missing-file behavior flags, IO tracing, table-load skipping, UDT boundary state, and epoch-number requirements.
- `VersionEditHandlerPointInTime` adds maps of saved `Version*` objects and atomic-update buffers so recovery can retain the most recent valid version when later manifest edits point at missing files.
- `ManifestTailer` adds recovery/catch-up mode, changed-CF tracking, new-manifest preparation, and intermediate-file collection.
- `DumpManifestHandler` wraps normal replay while printing each edit and final CF/version state.

## Control flow and extension points

Users create a concrete handler, pass it a MANIFEST `log::Reader` via `Iterate`, then inspect `status()` and handler-specific results. `VersionEditHandler` subclasses customize behavior by overriding `VerifyFile`, `VerifyBlobFile`, `OnColumnFamilyAdd`, `MaybeCreateVersionBeforeApplyEdit`, `LoadTables`, `MustOpenAllColumnFamilies`, or `CheckIterationResult`.

The normal handler's protected methods break replay into clear phases: initialize the default CF, classify CF IDs, create/drop CFs, handle WAL changes, handle non-CF edits, apply version edits through builders, load tables, extract replay parameters, and adjust UDT file boundaries. Point-in-time subclasses override the version-creation and table-loading pieces to save valid intermediate states instead of requiring the final manifest state to be complete.

## State and persistence behavior

The header exposes recovery state that mirrors durable MANIFEST content. `VersionEditParams` tracks replayed DB-wide manifest values. `builders_` hold per-CF edit accumulation. `do_not_open_column_families_` records manifest CFs omitted from the caller's open list. `last_valid_record_end_` is the persistence boundary for fully decoded records. For best-effort and tailing modes, `versions_` stores candidate recoverable versions and `atomic_update_versions_` delays visibility until all affected CFs have valid versions.

The flags `track_found_and_missing_files_`, `no_error_if_files_missing_`, `skip_load_table_files_`, `allow_incomplete_valid_version_`, and `epoch_number_requirement_` make the same replay machinery usable for normal open, read-only open, best-effort recovery, manifest dump, file checksum retrieval, and secondary catch-up.

## Dependencies and integration points

The declarations depend on `version_builder.h`, `version_edit.h`, `version_set.h`, `ColumnFamilyDescriptor`, `ColumnFamilyData`, `Version`, `VersionBuilder`, `FileChecksumList`, `IOTracer`, `ReadOptions`, and blob metadata types. These handlers are integration points between manifest log reading and the rest of DB recovery, including table-cache loading, blob-file verification, WAL lifecycle tracking, and diagnostic tooling.

## Risks and edge cases

- The classes are explicitly not thread-safe when shared; external synchronization is required.
- Subclass contracts are subtle: overriding `LoadTables`, `MaybeCreateVersionBeforeApplyEdit`, or `MustOpenAllColumnFamilies` changes recovery semantics significantly.
- Point-in-time recovery owns raw `Version*` pointers in maps and must delete or append them exactly once.
- Atomic update buffering assumes CF additions/drops inside an atomic group are unsupported and should become corruption.
- `ManifestTailer::PrepareToReadNewManifest` resets initialization and atomic read buffering; callers must use it before switching manifest files.
- `DumpManifestHandler` can print debug strings containing non-terminating null characters, so it writes with `fwrite` rather than C-string APIs.

## Test signals

The header declares testable behaviors through virtual methods and mode-specific APIs: `GetLastValidRecordEnd`, `HasMissingFiles`, `GetUpdatedColumnFamilies`, `GetAndClearIntermediateFiles`, and dump output. Implementation tests should cover normal recovery, read-only/unopened CF handling, missing-file tolerance, atomic groups, tailing mode transitions, checksum retrieval, and dump output.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/version_edit_handler.h -->
