# subset-b-008524 Research

Grouped research report for Pebble file cache tests, filename recovery tests, flush/flushable mechanics, format major version gates, point lookup, and SST ingestion. Each source section preserves the exact source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/file_cache_test.go -->
# sources/storage-engines/pebble/file_cache_test.go

## Purpose
Exercises Pebble's `FileCache` and `fileCacheHandle` behavior across table readers, blob file readers, shared cache ownership, virtual SSTable bounds, context cancellation, retry paths, leak detection, and fatal diagnostics. The tests fabricate many SST and blob objects in a memory filesystem and assert that the file cache opens files lazily, closes them exactly once, respects capacity, and remains correct under concurrent use.

## Important APIs, Types, And Functions
`fileCacheTestFS` wraps `vfs.FS` to count opens/closes, inject open errors, and delay opens. `fileCacheTestFile.Close` increments close counts. `fileCacheTest` owns a block cache handle and `FileCache`, builds test SST/blob objects through `objstorageprovider`, and constructs `fileCacheHandle`s with `newHandle`. `fileByIdx`, `validateOpenFiles`, `validateNoneStillOpen`, and `validateAndCloseHandle` are the main test helpers. Test coverage centers on `newIters`, `GetValueReader`, `Evict`, `findOrCreateTable`, `FileCache.Ref`, `FileCache.Unref`, and DB-level reads through `DB.newIters`/`DB.Get`.

## Control Flow
The shared fixture creates 200 SSTables and 100 blob files, then resets open/close counters before returning a cache handle. Random-access tests spawn or serialize thousands of iterator opens, verify `SeekGE("k")` finds the expected value length, and close iterators. Frequently-used tests repeatedly touch pinned files and rotating files, expecting pinned files to remain open. Eviction tests randomly read files and explicitly evict a small range, then compare average open counts for evicted versus safe files. Cancellation tests slow `Open`, run many goroutines with canceled, timed-out, or live contexts, and accept context errors only for callers whose contexts were canceled. Virtual-read tests manually replace a physical L6 table with two virtual table metadata entries and then verify point/range-delete/range-key reads through the file cache.

## State And Persistence Behavior
No production persistent state is intentionally created beyond in-memory DB/SST/blob files. The tests track transient cache state through reference counts, open/close maps, cached table/blob readers, reader iterator refs, and virtual table metadata. `TestVirtualReadsWiring` writes a manifest edit to replace one table with virtual SSTables and uses `checkVirtualBounds` to ensure metadata bounds match actual iterated keys. `TestFileCacheEvictClose` verifies object deletion events after compaction and close report no file-removal errors. `TestFileCacheNoSuchFileError` deletes an SST under an open DB and verifies the fatal message includes a useful directory summary.

## Dependencies And Integration Points
The file integrates `cache.Cache`, `FileCache`, `objstorageprovider`, `sstable.Writer`, `blob.FileWriter`, `manifest.TableMetadata`, virtual table backing metadata, `vfs.NewMem`, `base.MakeFilepath`, and DB operations such as `Open`, `Flush`, `Compact`, `NewIter`, and `Get`. It also exercises range-key and range-deletion iterator construction, table format handling, `block.InitFileReadStats`, corruption wrapping, and the event listener path for deleted tables.

## Risks And Edge Cases
The suite targets high-risk cache bugs: double-close or leaked file handles, use after all references are released, shared cache behavior with multiple DBs, iterator leaks during cache close, cached error poisoning after failed opens, context cancellation racing with shared initialization, bad magic number corruption messages, missing-table fatal diagnostics, and virtual SSTable bound mistakes. Several tests rely on timing/backoff or randomized access, so flakes may expose real races but can also require careful seed analysis.

## Test Signals
The file is itself the test signal. Strong signals are exact reference-count panics, `validateOpenFiles` capacity and close-count checks, leaktest failures, successful virtual reads over split metadata, expected injected-error retry behavior, accepted context cancellation outcomes, fatal logger capture for missing files, and benchmarks for iterator allocation and cache hot paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/file_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/filenames_test.go -->
# sources/storage-engines/pebble/filenames_test.go

## Purpose
Tests filename and marker-file crash recovery around `CURRENT`/MANIFEST updates, specifically ensuring temporary files left behind by a failed atomic marker rename are cleaned on the next successful `Open`. It also benchmarks filename formatting for table and blob file numbers.

## Important APIs, Types, And Functions
`TestSetCurrentFileCrash` is the primary test. `allTempFiles` lists the filesystem and filters entries through `base.ParseFilename` for `FileTypeTemp`. `renameErrorFS` injects rename failures by wrapping `vfs.FS.Rename`. `noFatalLogger` logs fatal messages to `testing.T` instead of aborting. `BenchmarkMakeFilename` repeatedly calls `base.MakeFilename` for table/blob file types.

## Control Flow
The test opens and closes a fresh DB to create an initial manifest, reopens through `renameErrorFS` with `MaxManifestFileSize` set tiny to force a manifest roll, expects the configured rename error, then checks that a temp file remains. A third open with the normal memory filesystem must succeed and remove the temp marker files before close.

## State And Persistence Behavior
All state lives in a `vfs.NewMem` filesystem. The test intentionally leaves a temporary file from a failed marker rename, then verifies open-time cleanup removes it. This covers persistence hygiene during manifest roll crashes: the durable DB state must still be recoverable, and stale temp files must not accumulate or confuse filename parsing.

## Dependencies And Integration Points
The file relies on Pebble `Open`/`Close`, manifest rolling through `MaxManifestFileSize`, `base.ParseFilename`, `base.MakeFilename`, `vfs.FS`, and logger behavior. It is adjacent to the atomic marker machinery used for `CURRENT` and format-version marker files.

## Risks And Edge Cases
The simulated crash is a rename failure in the middle of a marker update. If cleanup is incomplete, later opens may leave stale temp files, and if fatal logging panics the test cannot observe the intended recovery path. The benchmark also indirectly protects against avoidable allocation or formatting regressions in hot filename construction.

## Test Signals
Signals are the expected injected rename error, at least one temp file after the failed open, zero temp files after the normal reopen, no fatal panic through `noFatalLogger`, and benchmark performance for `base.MakeFilename`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/filenames_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/flush_test.go -->
# sources/storage-engines/pebble/flush_test.go

## Purpose
Provides focused tests for manual and asynchronous flushing, plus edge cases where flushed keys or range tombstone boundaries are empty byte slices. It validates that flushes update the current version and that empty keys are treated as real keys rather than nil sentinels.

## Important APIs, Types, And Functions
`TestManualFlush` drives `DB.Flush`, `DB.AsyncFlush`, `DB.NewBatch`, `Batch.Commit`, `runBatchDefineCmd`, and version string rendering through a datadriven file. `TestFlushDelRangeEmptyKey` writes `DeleteRange([]byte{}, "z")` then flushes. `TestFlushEmptyKey` writes `Set(nil, "hello")`, flushes, and reads the empty key through `Get`.

## Control Flow
`TestManualFlush` opens a DB with automatic compactions disabled and uses datadriven commands: `batch` builds and commits a batch, `flush` synchronously flushes and prints the current version, `async-flush` captures the current version, starts `AsyncFlush`, waits until the version pointer changes, and prints the new version, and `reset` reopens the DB. The empty-key tests perform direct DB operations and close after verification.

## State And Persistence Behavior
Flushes move mutable memtable contents into SSTables and update the version set/manifest state. The tests inspect the in-memory current version string after flushes and rely on persisted SST contents for `Get(nil)` after `Flush`. The range-delete empty-start case ensures an empty start key survives flush encoding and ordering invariants.

## Dependencies And Integration Points
The file depends on datadriven testdata, `vfs.NewMem`, `try` polling, DB version state under `d.mu`, batch command helpers, and public DB APIs. It integrates with flush scheduling, memtable rotation, version edit application, range tombstone flushing, and point lookup.

## Risks And Edge Cases
Manual and async flush behavior may regress if flush scheduling reports completion before a version update or if automatic compactions interfere with expected version strings. Empty keys are especially risky because nil and empty slices can be conflated in Go; these tests guard range deletion and point key invariant code against that confusion.

## Test Signals
Datadriven output from `testdata/manual_flush` is the main signal for version layout. Additional signals are successful flush/close without invariant failures, `Get(nil)` returning `hello`, and leaktest completion.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/flush_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/flushable.go -->
# sources/storage-engines/pebble/flushable.go

## Purpose
Defines the flushable abstraction used by immutable memtables and flushable ingests, plus the concrete `ingestedFlushable` wrapper that makes already-on-disk ingested SSTables visible in the memtable queue before they are placed in the LSM. It also provides overlap-detection helpers and a combined blob-file mapping spanning the current version and pending flushable ingests.

## Important APIs, Types, And Functions
`flushable` requires point, flush, range deletion, and range key iterators; range-key presence; byte accounting; readiness; and cheap overlap checks. `flushableEntry` adds queue metadata: `flushed`, forced-flush flags, WAL/log numbers, log sequence number, reader refs, memory release, file unrefs, and deletion callbacks. `readerRef`, `readerUnref`, and `readerUnrefLocked` manage lifecycle. `ingestedFlushable` stores ordered table metadata, comparer, iterator constructors, immutable level slice, excise span/sequence number, and blob file map. Key methods include `newIterInternal`, `newItersV2`, `newRangeDelIter`, `newRangeKeyIter`, `containsRangeKeys`, `readyForFlush`, `computePossibleOverlaps`, `anyFileOverlaps`, `determineOverlapAllIters`, `determineOverlapPointIterator`, `determineOverlapKeyspanIterator`, and `combinedBlobFileMapping.Lookup`.

## Control Flow
Flushable queue consumers call iterator methods to merge memtables and pending ingests into read state. `newIngestedFlushable` verifies file non-overlap under invariants, converts virtual metadata to physical metadata for file access, builds a key-sorted `LevelSlice`, detects range-key presence, and records blob mappings. Point reads use a level iterator over the flushable-ingest layer. Range deletion and range key reads construct keyspan level iterators and optionally merge synthetic excise tombstones/deletes. Overlap checks for ingested files use metadata bounds only, deliberately avoiding I/O; generic overlap checks for in-memory flushables use iterators and panic if an infallible iterator errors.

## State And Persistence Behavior
`flushable.go` itself persists nothing, but its data structures mediate durability. `flushableEntry.logNum`, `logSize`, and `logSeqNum` connect queue entries to WAL lifecycle. Reader refs defer memory accounting release and table/blob unrefs until no read state or queue reference remains. `ingestedFlushable` represents SSTables already linked or attached to storage, with sequence numbers persisted later through a version edit when flushed. Excise spans are surfaced as synthetic range deletion/range-key delete entries so reads observe destructive excise semantics before manifest placement.

## Dependencies And Integration Points
The file integrates with `manifest.TableMetadata`, `manifest.LevelSlice`, `newLevelIter`, `iterv2`, `keyspanimpl.LevelIter`, `MergingIter`, `base.UserKeyBounds`, `KeyRange`, blob file metadata, DB read state, ingest handling, flush scheduling, obsolete-file cleanup, and table/blob file reference counting. `combinedBlobFileMapping` is used by blob value fetching when blob references may point to current-version blob files or pending ingested flushables.

## Risks And Edge Cases
Reference count mistakes can leak memory/files or delete files still visible to readers. `ingestedFlushable.newFlushIter` intentionally panics because ingested files are already on disk; callers must not treat it like a memtable. Excise spans must be copied and merged correctly into range deletion and range key iterators. Metadata-only overlap checks may produce false positives, which is acceptable for safety but affects ingest placement and flushing. Blob-file lookup must search pending flushables or reads of newly ingested blob values may fail before manifest application.

## Test Signals
Signals come from `flushable_test.go`, ingest tests, read-state tests, and file-cache/reference leak tests. Useful symptoms include correct datadriven point/range-key/range-delete output from ingested flushables, expected `readyForFlush`/`containsRangeKeys` values, absence of reference-count panics, and successful blob value reads during flushable ingest windows.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/flushable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/flushable_test.go -->
# sources/storage-engines/pebble/flushable_test.go

## Purpose
Datadriven sanity coverage for `ingestedFlushable`, verifying that SSTables loaded through the ingest metadata path can be exposed through the `flushable` API for point iteration, range deletion iteration, range key iteration, excise handling, and readiness/range-key introspection.

## Important APIs, Types, And Functions
`TestIngestedSSTFlushableAPI` owns the whole file. The `reset` helper opens a DB over a memory filesystem with newest internal format, debug level checks, high L0 thresholds, and automatic compactions disabled. `loadFileMeta` reuses `ingestLoad`, `setSeqNumInMetadata`, `ingestSortAndVerify`, and `ingestLinkLocal` to build metadata and link SSTables. The test constructs `newIngestedFlushable` and calls `newIter`, `newRangeKeyIter`, `newRangeDelIter`, `readyForFlush`, and `containsRangeKeys`.

## Control Flow
Datadriven commands build SSTables, construct a flushable from named local SST paths plus an optional `excise` range, then print point iterator keys, range key spans, range deletion spans, or boolean API results. The sequence number counter is advanced per ingested file and excise so synthetic tombstones and file keys have realistic ordering. Linked files are fsynced before use to mirror ingest durability ordering.

## State And Persistence Behavior
The test writes temporary local SSTables into `vfs.NewMem`, hard-links/copies them into the DB's object provider, and increments table backing references to satisfy file-cache expectations even though the files are not installed in a version. It synthesizes sequence numbers in metadata rather than rewriting table contents. Excise spans become synthetic in-memory range deletion/range-key delete state inside the flushable.

## Dependencies And Integration Points
The test depends on datadriven testdata `testdata/ingested_flushable_api`, `runBuildCmd`, `LocalSSTables`, ingest metadata loading/linking functions, `manifest.TableMetadata`, `vfs`, DB object provider sync, file cache iterators, and the comparer/range-key stack. It is a focused bridge between the ingest pipeline and the flushable read interface.

## Risks And Edge Cases
The setup reuses production ingest helpers while bypassing actual manifest installation, so table backing refs and directory sync are important to avoid false test failures. Excise sequence numbering must match production conventions. Range key and range deletion iterators may be nil, and the test handles nil iterators explicitly to catch incorrect non-nil typed nil behavior.

## Test Signals
Expected datadriven output for point keys, range deletion spans, range key spans, `readyForFlush`, and `containsRangeKey` is the primary signal. Debug checks and file-cache behavior add secondary signals for metadata validity and linked-file readability.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/flushable_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/format_major_version.go -->
# sources/storage-engines/pebble/format_major_version.go

## Purpose
Defines Pebble's durable format-major-version system: version constants for backward-incompatible on-disk changes, table/blob format capability mapping, marker-file lookup and writing, runtime ratcheting, and migrations that mark or compact files before enabling newer invariants. It is the central gate that prevents older binaries from opening databases written with newer durable formats.

## Important APIs, Types, And Functions
`FormatMajorVersion` implements `String` and `SafeValue`. Constants run from `FormatDefault` through `FormatNewest`/`internalFormatNewest`, with `FormatMinSupported` set to `FormatFlushableIngest` and shared-object support starting at `FormatVirtualSSTables`. Methods include `resolveDefault`, `MaxTableFormat`, `MinTableFormat`, `MaxBlobFileFormat`, `DB.FormatMajorVersion`, `DB.TableFormat`, `DB.BlobFileFormat`, `DB.shouldCreateShared`, `DB.RatchetFormatMajorVersion`, `ratchetFormatMajorVersionLocked`, `finalizeFormatVersUpgrade`, `writeFormatVersionMarker`, `compactMarkedFilesLocked`, `findFilesRowblk`, and `markFilesForCompactionLocked`. `formatMajorVersionMigrations` maps each supported version to an idempotent migration closure.

## Control Flow
Opening a DB uses `lookupFormatMajorVersion` to locate the atomic `format-version` marker, parse the decimal version string, and reject unknown or unsupported versions. Ratcheting checks read-only state, version direction, unknown versions, and concurrent ratchets, then walks one version at a time. Each migration runs under `DB.mu`, performs any prerequisite work, and must call `finalizeFormatVersUpgrade`, which moves the marker, stores the new in-memory version atomically, and emits the format-upgrade event. Some migrations are simple finalizers; others compact already-marked files or mark row-block tables for compaction before finalizing.

## State And Persistence Behavior
The active format version is durable in an atomic marker named `format-version`, encoded as a stable decimal string. `d.mu.formatVers.vers` mirrors that durable state in memory. Ratcheting can mutate the MANIFEST by marking files for compaction through `VersionEdit.TablesMarkedForCompaction`, can wait for compactions to rewrite marked files, and can trigger event listeners. `findFilesRowblk` reads table formats through the file cache and identifies non-columnar data blocks for migration marking.

## Dependencies And Integration Points
This file depends on `atomicfs.Marker`, `vfs`, `manifest.VersionEdit`, compaction scheduling/conditions, file-cache reader access, `sstable.TableFormat`, `blob.FileFormat`, remote shared-object policy, block format inspection, and DB event listeners. Its gates are consumed by ingest, WAL writing, table writing, blob value separation, virtual SSTables, excise bounds records, shared objects, and compaction picking.

## Risks And Edge Cases
Format constants must never be renumbered because marker values are persisted. `FormatDefault` must not be written to disk. `MinTableFormat` is intentionally conservative for CockroachDB raft-log ingestion compatibility. Migrations that wait for compaction drop `DB.mu` through condition waits and must handle DB closure. `markFilesForCompactionLocked` requires `FormatMarkForCompactionInVersionEdit`; ordering of migrations is therefore significant. Unknown future versions and unsupported old versions must fail loudly to avoid corruption.

## Test Signals
`format_major_version_test.go` checks stable numeric values, migration coverage, ratcheting through all versions, persisted marker reopen behavior, unknown marker rejection, and table/blob format mappings. Integration signals include successful opens at requested formats, correct table/blob writer formats, format-upgrade event firing, and compaction of marked files during migrations.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/format_major_version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/format_major_version_test.go -->
# sources/storage-engines/pebble/format_major_version_test.go

## Purpose
Validates the durable format-major-version contract: stable numeric values, complete migration definitions, ratcheting at open and while open, persisted marker behavior, rejection of unknown future versions, and exhaustive mappings from format major versions to supported table/blob formats.

## Important APIs, Types, And Functions
Tests include `TestFormatMajorVersionStableValues`, `TestFormatMajorVersion_MigrationDefined`, `TestRatchetFormat`, `testBasicDB`, `TestFormatMajorVersions`, `TestFormatMajorVersions_TableFormat`, `TestFormatMajorVersions_BlobFileFormat`, and `TestFormatMajorVersions_MaxTableFormat`. They call `Open`, `DB.RatchetFormatMajorVersion`, `DB.FormatMajorVersion`, `DB.TableFormat`, `FormatMajorVersion.MinTableFormat`, `MaxTableFormat`, `MaxBlobFileFormat`, and `atomicfs.LocateMarker`.

## Control Flow
Stable-value tests compare each exported/current format constant against explicit numbers. Migration coverage iterates from `FormatMinSupported` through `FormatNewest`. Ratchet tests open a memory DB, write data, ratchet through every version, close/reopen to verify persistence, then manually move the marker to `999999` and expect open failure. Exhaustive version tests create DBs at each version, run basic set/flush/compact/iteration operations, and use crash clones to test upgrade-at-open and upgrade-while-open without mutating the original filesystem. Format mapping tests iterate valid ranges and assert expected min/max table and blob formats, including panic checks for invalid versions.

## State And Persistence Behavior
The tests exercise real marker persistence in a memory filesystem and crash-cloned filesystems. `testBasicDB` writes and flushes data, compacts the full key range, and iterates through the resulting version, ensuring each format can sustain basic persistent operations. Marker tampering tests verify persisted unknown versions block open with a precise error.

## Dependencies And Integration Points
The file depends on `vfs.NewMem`, `vfs.NewCrashableMem`, `atomicfs`, `sstable.TableFormat`, `blob.FileFormat`, Pebble open/flush/compact/iterator APIs, and test logging. It provides direct coverage for the format gates used by table writing, blob file writing, ingest validation, WAL/manifest compatibility, and migrations.

## Risks And Edge Cases
Adding a new format version requires updating both stable-value expectations and mapping tables; otherwise tests fail. Crash clones are used to isolate upgrade permutations, reducing cross-test contamination. Invalid-version panic checks protect `resolveDefault` and format mapping code. The explicit marker move to an unknown version verifies Pebble does not silently downgrade or ignore future durable state.

## Test Signals
Signals include exact numeric constant equality, every supported version having a migration closure, successful basic DB operations across all versions and upgrade paths, persisted upgraded version after reopen, exact unknown-version error text, expected table/blob format mappings, and expected panics for unsupported mappings.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/format_major_version_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/get.go -->
# sources/storage-engines/pebble/get.go

## Purpose
Implements the public point lookup API `DB.Get` and its shared internal helper. It performs a snapshot-consistent prefix seek through Pebble's iterator stack and returns a value slice whose lifetime is tied to the returned iterator closer.

## Important APIs, Types, And Functions
`DB.Get(key []byte) ([]byte, io.Closer, error)` delegates to `getInternal` with no batch or snapshot. `getInternal(key, b, s)` checks `d.closed`, selects a sequence number from the provided `Snapshot` or `visibleSeqNum`, builds an iterator with optional batch and `categoryGet`, uses `SeekPrefixGE`, compares the found key with `Comparer.Equal`, calls `ValueAndErr`, and returns the iterator as the `io.Closer`.

## Control Flow
The function panics if the DB is closed, constructs a read iterator at the desired snapshot sequence number, seeks to the key prefix, and treats a missing seek result or unequal key as `ErrNotFound` after closing the iterator. If value retrieval errors, it combines the value error with iterator close error. On success, it deliberately leaves the iterator open and returns it to the caller as the closer that pins the returned value bytes.

## State And Persistence Behavior
`Get` is read-only. It observes the current visible sequence number or a snapshot sequence number and may merge state from a batch, memtables, flushable ingests, and SSTables through `newIter`. The returned value slice is backed by iterator-owned resources, so caller closure is required to release memory/cache references.

## Dependencies And Integration Points
The code depends on `DB.newIter`, `Iterator.SeekPrefixGE`, `Iterator.Key`, `Iterator.ValueAndErr`, `Iterator.Close`, `Snapshot.seqNum`, `Batch`, `base.SeqNum`, comparer equality, `ErrNotFound`, and iterator category accounting. It is the simple public wrapper over the same read stack used by scans and internal lookups.

## Risks And Edge Cases
The main contract risk is leaking the returned closer, which pins iterator resources. Empty keys are valid and must flow through comparer/iterator logic, as covered by flush tests. Prefix seek must be followed by exact equality to avoid returning the next key. Error handling must close iterators on not-found and combine errors on failed value retrieval without closing on success.

## Test Signals
Direct and indirect signals include point lookup tests throughout the repository, `TestFlushEmptyKey`, snapshot and batch read tests, leak detection for unclosed iterators, and errors surfaced from iterator close or value retrieval.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/get.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/ingest.go -->
# sources/storage-engines/pebble/ingest.go

## Purpose
Implements Pebble SST ingestion: validating local SSTables, attaching shared/external remote SSTables, assigning sequence numbers, optionally representing overlapping local ingests as flushable queue entries, selecting target LSM levels, performing excise and ingest-time virtual splits, applying manifest edits, cleaning up inputs, emitting stats/events, and optionally validating ingested table checksums.

## Important APIs, Types, And Functions
Public APIs are `DB.Ingest`, `DB.IngestWithStats`, `DB.IngestExternalFiles`, `DB.IngestAndExciseWithBlobs`, and `DB.IngestAndExcise`. Exposed data types include `IngestOperationStats` and `ExternalFile`; local/shared input types come from neighboring files. Key helpers include `ingestValidateKey`, `ingestSynthesizeShared`, `ingestLoad1External`, `rangeKeyIngestValidator`, `ingestLoad1`, `constructBlobFileMetadataForIngestedTable`, `ingestLoad`, `ingestSortAndVerify`, `ingestCleanup`, `ingestLinkLocal`, `ingestAttachRemote`, `findExistingBackingsForExternalObjects`, `ingestUnprotectExternalBackings`, `setSeqNumInMetadata`, `ingestUpdateSeqNum`, `ingestTargetLevel`, `newIngestedFlushableEntry`, `handleIngestAsFlushable`, `ingest`, `ingestSplit`, `ingestApply`, `maybeValidateSSTablesLocked`, `shouldValidateSSTablesLocked`, and `validateSSTables`.

## Control Flow
Ingestion first rejects read-only or format-incompatible calls, allocates file numbers while loading metadata, validates table formats/key schemas/key sequence numbers, handles blob references, and elides empty SSTables. It sorts and verifies non-overlap, links/copies local tables and blobs into the object provider, attaches shared/external remote objects, syncs the provider, and enters the commit pipeline. During sequence-number allocation, `prepare` checks overlap with queued flushables and excise-protected ranges. If there is no overlap, it writer-refs the mutable memtable so later writes cannot flush ahead of the ingest. If overlap exists and flushable ingest is allowed, it writes an ingest record to the WAL, appends an `ingestedFlushable`, rotates WAL/memtable state, and returns before manifest installation. Otherwise it forces/waits for the overlapping flushable to flush. `apply` updates sequence numbers, waits as needed, and calls `ingestApply` to select levels and write the manifest edit.

## State And Persistence Behavior
Local ingest durability depends on linking/copying files into the DB object provider and syncing before any manifest edit references them. Sequence numbers are persisted in table metadata written to the manifest, not by rewriting SST contents. Flushable ingests are persisted first as WAL records and later reconstructed on replay or installed through flush. Shared/external ingests create or reuse virtual table backings; reused external backings are protected during the operation and unprotected afterward. Excise operations mutate the LSM by replacing overlapping tables with virtual left/right fragments and may write `ExciseBoundsRecord` entries when the format permits. Successful local ingests remove original input table/blob paths after linking/copying.

## Dependencies And Integration Points
The file is tightly integrated with `sstable.Reader`, table properties, key schema registry, blob file readers and reference blocks, `objstorage.Provider`, remote object attachment, `manifest.TableMetadata`, version edits, virtual table backings, file/blob refcounts, `overlapChecker`, compaction in-progress tracking, commit pipeline sequence allocation, WAL rotation, memtable/flushable queue management, flush scheduling, excise helpers, event listeners, table validation, and format major version gates such as `FormatVirtualSSTables`, `FormatSyntheticPrefixSuffix`, `FormatFlushableIngest`, `FormatFlushableIngestExcises`, `FormatIngestBlobFiles`, and `FormatExciseBoundsRecord`.

## Risks And Edge Cases
Ingest is high risk because it crosses filesystem durability, manifest atomicity, sequence-number visibility, read-state publication, compaction concurrency, and remote object lifetime. Inputs with non-zero sequence numbers, invalid keys, unsupported table/blob formats, unknown columnar key schemas, mismatched blob files, overlapping local/external ranges, shared files outside the excise span, external level inconsistency, and suffixed range-key boundaries are rejected. Flushable ingests are disabled for remote files and constrained by queue size, WAL settings, format version, and excise support. Ingest-time splits and excises must cancel conflicting compactions and avoid producing overlapping virtual files. Validation can fatal on corruption and retries transient checksum validation failures.

## Test Signals
Signals come from ingest unit/datadriven tests, flushable ingest tests, excise/virtual SST tests, format-version tests, blob ingest tests, event listener assertions, and table validation behavior. Runtime signals include `TableIngested`, `TableCreated`, `BlobFileCreated`, `TableValidated`, background errors, ingest stats per level, `MemtableOverlappingFiles`, cleanup error logs, and fatal corruption reports from checksum validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/ingest.go -->
