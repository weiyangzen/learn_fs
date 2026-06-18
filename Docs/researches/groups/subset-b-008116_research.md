# Research Report: subset-b-008116

This grouped report covers the subset-b-008116 source files. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/TestCompositeDeltaDiffComputer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/TestCompositeDeltaDiffComputer.java

## Purpose
`TestCompositeDeltaDiffComputer` validates the orchestration layer that chooses between RocksDB checkpoint DAG diffing and full SST comparison for OM snapshot diff delta-file discovery. It isolates `CompositeDeltaDiffComputer` with Mockito construction mocking so the tests can assert constructor choices, fallback rules, status reporting, close behavior, and non-native diff augmentation without invoking real RocksDB diff machinery.

## Important APIs, Types, and Functions
- `CompositeDeltaDiffComputer` is the system under test; it is constructed with `OmSnapshotManager`, active `OMMetadataManager`, a delta directory, a `Consumer<SubStatus>`, `fullDiff`, and `nonNativeDiff`.
- `RDBDifferComputer` is mocked as the preferred DAG-walk implementation when `fullDiff` is false.
- `FullDiffComputer` is mocked as the always-available fallback and as the direct implementation when `fullDiff` is true.
- `computeDeltaFiles(SnapshotInfo, SnapshotInfo, Set<String>, TablePrefixInfo)` returns `Optional<Map<Path, Pair<Path, SstFileInfo>>>`, where keys are source SST paths and values contain the linked delta path plus SST metadata.
- `SubStatus.SST_FILE_DELTA_DAG_WALK` and `SubStatus.SST_FILE_DELTA_FULL_DIFF` are asserted as progress signals.
- The non-native diff path uses `FullDiffComputer.getSSTFileSetForSnapshot`, `OmSnapshotManager.getActiveSnapshot`, `RDBStore.getDbLocation`, and inode checks via `IOUtils.getINode`.

## Control Flow
The constructor tests verify that `RDBDifferComputer` is built only in normal mode, while `FullDiffComputer` is built in both normal and full-diff-only modes. Success cases force the RDB differ mock to return maps with one, many, or zero SST files and confirm no fallback call occurs. Fallback cases force `Optional.empty()` or a runtime exception from the RDB differ and assert that full diff is invoked and its result is returned. Full-diff-only mode skips RDB construction entirely and reports only the full-diff status.

The non-native diff test first returns one RDB-differ SST and then mocks the from-snapshot database to expose two SSTs. With `nonNativeDiff=true`, the final result contains the RDB output plus from-snapshot files linked into the delta directory. With `nonNativeDiff=false`, only RDB output is returned.

## State and Persistence Behavior
The tests use `@TempDir` for delta and mock DB paths, creating concrete SST files to validate hard links. State is transient and cleaned by `close()`. Non-native mode has the most persistence relevance: it creates linked delta files for from-snapshot SSTs and asserts those links share inodes with the source files, which protects delete detection behavior when native RocksDB diffing is disabled.

## Dependencies and Integration Points
The file integrates with snapshot metadata (`SnapshotInfo`), OM snapshot lookup (`OmSnapshotManager` and `UncheckedAutoCloseableSupplier<OmSnapshot>`), RocksDB store metadata (`RDBStore`), table prefix filtering (`TablePrefixInfo`), and `SstFileInfo`. Mockito `mockConstruction` and `mockStatic` are critical to decouple the composite from concrete diff implementations and static SST scanning.

## Risks and Edge Cases
Important risks covered include accidentally constructing or invoking RDB diff in full-diff mode, treating an empty successful RDB result as a failure, missing status updates, failing to close child computers, and losing delete coverage in non-native mode by omitting from-snapshot SST files. A residual risk is that constructor argument propagation to child diff computers is mostly inferred from construction count rather than captured argument inspection.

## Test Signals
The test suite is a strong behavioral signal for fallback semantics, status sequencing, and link-based non-native diff output. It does not run real RocksDB checkpoint traversal; those semantics are delegated to companion tests for `RDBDifferComputer` and `FullDiffComputer`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/TestCompositeDeltaDiffComputer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/TestFileLinkDeltaFileComputer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/TestFileLinkDeltaFileComputer.java

## Purpose
`TestFileLinkDeltaFileComputer` validates the abstract base behavior for delta-file computers that materialize hard links into a temporary delta directory. It uses a concrete inner subclass to expose protected behavior and stub `computeDeltaFiles`.

## Important APIs, Types, and Functions
- `FileLinkDeltaFileComputer` supplies delta-directory lifecycle, hard-link creation, snapshot/local-data accessors, activity updates, and public `getDeltaFiles`.
- `TestableFileLinkDeltaFileComputer` overrides `computeDeltaFiles` and allows tests to inject an `Optional<Map<Path, Pair<Path, SstFileInfo>>>`.
- `createLink(Path)` creates unique hard links under the delta directory while preserving source file extensions.
- `getDeltaFiles(...)` fetches `TablePrefixInfo` from the active metadata manager and converts the internal map to a collection of `(deltaPath, SstFileInfo)` pairs.

## Control Flow
Constructor tests assert that a missing or existing delta directory is handled. Link tests create real files, then verify link existence, extension preservation, content visibility, unique naming across multiple links, and retry behavior when a next numeric link name already exists. Accessor tests validate delegation to `OmSnapshotLocalDataManager.getOmSnapshotLocalData`, `OmSnapshotManager.getActiveSnapshot`, and `getActiveMetadataManager`. `getDeltaFiles` tests assert success when the abstract compute method returns a map and `IOException` when it returns `Optional.empty()`.

## State and Persistence Behavior
The class creates and deletes a filesystem directory under `@TempDir`. The tests verify that `close()` removes the directory both when empty and when populated with links, and that closing a missing directory is harmless. Hard-link tests imply shared persistence with source files: content written to the source is visible through the link.

## Dependencies and Integration Points
The base class depends on OM snapshot manager APIs, active metadata table prefix calculation, snapshot local data providers, and `SstFileInfo` metadata. The activity reporter bridges file-link delta work to snapshot diff progress reporting through `SubStatus`.

## Risks and Edge Cases
Covered risks include name collisions in concurrent link creation, leaking temporary delta directories, treating absent delta computation as success, and extension loss. The tests do not verify cross-filesystem hard-link failure behavior, permissions errors, or cleanup failure handling.

## Test Signals
This file provides the foundational contract for the concrete diff computers: any successful diff returns linked files under a managed delta directory, and failure is represented by an absent optional that `getDeltaFiles` converts to `IOException`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/TestFileLinkDeltaFileComputer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/TestFullDiffComputer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/TestFullDiffComputer.java

## Purpose
`TestFullDiffComputer` validates full SST-file diffing between two OM snapshots. It ensures that full diff identifies SST files that may contain changes for selected tables and bucket prefixes, and that returned files are hard-linked through the common file-link delta mechanism.

## Important APIs, Types, and Functions
- `FullDiffComputer.computeDeltaFiles` compares live SST metadata from source and target snapshots.
- `FullDiffComputer.getDeltaFiles` goes through the public base API and verifies inode identity for linked outputs.
- `SstFileInfo` carries file name, key range, and column family.
- `TablePrefixInfo` filters diff candidates by table-to-prefix mapping.
- The helper `createMockSnapshot` builds mocked `OmSnapshot`, `OMMetadataManager`, `RDBStore`, `RocksDatabase`, `ManagedRocksDB`, and `RocksDB` chains and creates real hard links at snapshot DB paths.

## Control Flow
A parameterized method supplies multiple source/target SST metadata maps, table prefix maps, expected diff files, and lookup table sets. For each case, temporary source SST files are created, mock snapshots expose corresponding RocksDB live metadata, and `computeDeltaFiles` is invoked. The expected result is normalized to snapshot directory paths and compared against actual `SstFileInfo` values. The public `getDeltaFiles` path is then called to ensure delta links point to the same inodes as the selected source files.

## State and Persistence Behavior
The test creates real filesystem directories and hard links under `@TempDir`. Snapshot DB locations are represented by `snapDirectory/snapshotName`, and SST file paths are linked to shared underlying files. `close()` is expected to delete the delta directory. No durable OM metadata is written; persistence is simulated through RocksDB metadata and file paths.

## Dependencies and Integration Points
The test integrates with RocksDB live-file metadata (`LiveFileMetaData`), HDDS Rocks DB wrappers, snapshot handles, active snapshot lookup, and OM table-prefix filtering. It models the behavior needed by snapshot diff report generation when checkpoint differ traversal is unavailable or disabled.

## Risks and Edge Cases
The cases cover equal sets, source-only and target-only files, invalid key prefixes, multiple tables, and lookup-table filtering. Key risks are false positives from unrelated tables, false negatives when a file range crosses a bucket prefix, and incorrect link paths. The mock RocksDB layer means compaction timing and real RocksDB metadata quirks are not exercised.

## Test Signals
This is the main test signal for full-diff correctness. It verifies both logical diff selection and physical link identity, which together protect the downstream merge/report stage from missing required SST data.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/TestFullDiffComputer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/TestRDBDifferComputer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/TestRDBDifferComputer.java

## Purpose
`TestRDBDifferComputer` validates the delta-file computer that delegates snapshot diff discovery to `RocksDBCheckpointDiffer`. It checks constructor behavior, snapshot-local-data conversion to differ inputs, version mapping, hard-link creation, resource closure, and error propagation.

## Important APIs, Types, and Functions
- `RDBDifferComputer` is constructed from `OmSnapshotManager`, active `OMMetadataManager`, delta path, and activity reporter.
- `RocksDBCheckpointDiffer.getSSTDiffListWithFullPath` is the core integration point; it receives `DifferSnapshotInfo` objects, a version map, `TablePrefixInfo`, and lookup tables.
- `OmSnapshotLocalDataManager.ReadableOmSnapshotLocalDataProvider` supplies current and previous `OmSnapshotLocalData`.
- `OmSnapshotLocalData.VersionMeta` and `getVersionSstFileInfos` drive version ancestry mapping for the differ.

## Control Flow
The constructor tests assert that the active store and checkpoint differ are obtained, but a null differ still allows object construction. Success tests configure snapshot local data, mock differ output, invoke `computeDeltaFiles`, and confirm every returned source SST is linked into the delta directory. Empty differ output and null differ both return `Optional.empty()`. Version mapping tests capture the map passed to the differ and assert the expected mapping from current versions to previous versions. Error tests cover missing version metadata and `IOException` from the differ.

## State and Persistence Behavior
The test uses real temporary SST files and verifies hard-link inode equality. Snapshot-local-data providers are explicitly verified as closed, including when the differ throws. The metadata manager's persistent delegation is mocked; the state under test is local-data version metadata and transient delta links.

## Dependencies and Integration Points
This file connects OM snapshot-local metadata, RocksDB checkpoint differ, table prefix filtering, and file-link output. It is the unit boundary between Ozone snapshot management and the lower-level `org.apache.ozone.rocksdiff` package.

## Risks and Edge Cases
Covered risks include absent checkpoint differ, empty differ result, multiple table output, corrupt or empty version metadata, propagated I/O failure, unclosed local data providers, and repeated synchronized differ calls. The synchronization test calls sequentially rather than with real threads, so race protection is inferred from repeated safe invocations.

## Test Signals
The tests are strong indicators for correct differ wiring and cleanup. They do not prove RocksDB differ algorithm correctness, but they verify Ozone's adapter supplies the right metadata and handles failures in the expected fallback-friendly form.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/TestRDBDifferComputer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/filter/AbstractReclaimableFilterTest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/filter/AbstractReclaimableFilterTest.java

## Purpose
`AbstractReclaimableFilterTest` is a shared fixture for reclaimable snapshot garbage-collection filter tests. It builds mocked Ozone Manager, snapshot chain, bucket metadata, locks, snapshot cache, and RocksDB surfaces so concrete tests can focus on reclaimability decisions for keys, directories, and rename entries.

## Important APIs, Types, and Functions
- `initializeFilter(...)` is the abstract factory implemented by subclasses.
- `setup(...)` creates mock OM state, snapshot chain state, bucket layout, and the concrete `ReclaimableFilter`.
- `mockSnapshotChain` creates `SnapshotInfo` lists per volume/bucket and stubs `SnapshotUtils.getSnapshotInfo`, `getPreviousSnapshot`, and `getLatestSnapshotInfo`.
- `mockOmSnapshotManager` constructs a real `OmSnapshotManager` while mocking `ManagedRocksDB.open`, `SnapshotDiffManager`, `SnapshotCache`, `OmSnapshotLocalDataManager`, transaction table state, and RocksDB iterators.
- Accessors expose `reclaimableFilter`, `snapshotInfos`, `snapshotChainManager`, `omSnapshotManager`, `keyManager`, lock IDs, volumes, and buckets.

## Control Flow
`setup` constructs the mock OM, chain manager, key manager, and a lock that records acquired snapshot IDs and asserts release symmetry. It builds a configurable grid of volumes and buckets, creates a snapshot chain for each bucket, stubs bucket lookup and volume IDs, then initializes and spies the concrete filter. The selected `currentSnapshotInfo` may be null to represent the active object store rather than a specific snapshot.

## State and Persistence Behavior
The fixture creates a temporary metadata directory and mocks transaction info as flushed through `TransactionInfo.valueOf(0, 10)`. Snapshot status and last transaction info can be modified via a supplied `Function<SnapshotInfo, SnapshotInfo>` to test inactive or unflushed snapshots. The lock ID `AtomicReference` is the key state assertion for GC lock correctness.

## Dependencies and Integration Points
The fixture ties together `OzoneManager`, `OmMetadataManagerImpl`, `OmSnapshotManager`, `SnapshotChainManager`, `SnapshotUtils`, `SnapshotCache`, `SnapshotDiffManager`, `OmSnapshotLocalDataManager`, RocksDB wrappers, bucket manager, key manager, and `IOzoneManagerLock`. It is tightly coupled to snapshot GC internals.

## Risks and Edge Cases
The helper's heavy mocking can hide integration drift, especially constructor changes in `OmSnapshotManager` or metadata manager behavior. It does, however, guard important edge cases: inactive snapshots, unflushed transaction info, nonexistent volumes/buckets, and lock release ID mismatches.

## Test Signals
This fixture is the backbone for all reclaimable filter tests. Its strongest signal is consistent setup of snapshot-chain windows and GC read-lock acquisition for the snapshots consulted by a filter.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/filter/AbstractReclaimableFilterTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/filter/TestReclaimableDirFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/filter/TestReclaimableDirFilter.java

## Purpose
`TestReclaimableDirFilter` validates whether deleted directory entries can be reclaimed based on their presence and identity in the immediately previous snapshot.

## Important APIs, Types, and Functions
- `ReclaimableDirFilter` is created with one previous snapshot in scope.
- `KeyManager.getPreviousSnapshotOzoneDirInfo(volumeId, bucketInfo, dirInfo)` supplies previous directory metadata.
- `OmKeyInfo` represents the current deleted directory entry, while `OmDirectoryInfo` represents the previous snapshot's directory entry.
- The helper `testReclaimableDirFilter` wires previous snapshot key managers and asserts filter output.

## Control Flow
Each parameterized test varies the number of snapshots and active index. The helper resolves the previous snapshot, mocks its `KeyManager` if present, stubs current directory volume/bucket names, and applies the filter. A directory with the same object ID in the previous snapshot is not reclaimable; absent previous info or a different object ID is reclaimable.

## State and Persistence Behavior
No durable state is written. The relevant state is snapshot chain position and object ID continuity across snapshots. The base fixture also ensures the GC read lock is acquired for consulted snapshots.

## Dependencies and Integration Points
This test integrates with bucket metadata, volume ID lookup, previous snapshot handles from `OmSnapshotManager`, and `KeyManager` previous-snapshot lookup APIs. It exercises filesystem-optimized directory reclamation behavior.

## Risks and Edge Cases
The test covers no-previous-snapshot and object-ID mismatch cases. It does not cover failures from `getPreviousSnapshotOzoneDirInfo`, malformed directory names, or multiple previous snapshots because directory reclamation only needs one prior state here.

## Test Signals
The test is a focused signal that directory reclamation depends on identity continuity, not merely name presence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/filter/TestReclaimableDirFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/filter/TestReclaimableFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/filter/TestReclaimableFilter.java

## Purpose
`TestReclaimableFilter` validates the base `ReclaimableFilter` snapshot-chain initialization, bucket/volume validation, locking behavior, active-object-store behavior, and failure handling for inactive or unflushed snapshots.

## Important APIs, Types, and Functions
- An anonymous `ReclaimableFilter<Boolean>` implementation extracts volume and bucket from a slash-separated key and treats `null` or `true` values as reclaimable.
- `testSnapshotInitAndLocking` asserts the filter return value, previous snapshot info list, previous `OmSnapshot` handles, and recorded lock IDs.
- Parameter providers generate combinations of previous snapshot count, actual chain length, and current index.
- `SnapshotUtils` static methods are stubbed by the base class and adjusted in dynamic snapshot-addition tests.

## Control Flow
The main parameterized test applies the filter to valid volume/bucket entries and asserts previous snapshot window initialization. Invalid volume and invalid bucket cases represent active object store mode and expect reclaimability to default true when the object cannot be resolved. Bucket/volume mismatch cases throw when a current snapshot is bound but the key belongs to another bucket. Snapshot-addition tests simulate new latest snapshots during `isReclaimable`. Inactive and unflushed snapshot tests modify specific chain entries and assert failures only when the problematic snapshot falls inside the consulted previous-window range.

## State and Persistence Behavior
State is mostly in-memory but models persistent snapshot metadata: `SnapshotInfo.SnapshotStatus`, last transaction info, transaction table value, and snapshot chains. Lock state is persisted in `AtomicReference<List<UUID>>` during each application and checked against expected previous-plus-current snapshot IDs.

## Dependencies and Integration Points
The test exercises base filter interactions with `OzoneManager`, `BucketManager`, `SnapshotChainManager`, `OmSnapshotManager`, `SnapshotUtils`, `TransactionInfo`, `IOzoneManagerLock`, and `SnapshotInfo` lifecycle fields.

## Risks and Edge Cases
It covers invalid buckets/volumes, mismatched snapshot scope, dynamic snapshot addition, deleted snapshots, and unflushed snapshots. A risk is reliance on exact exception message text. Another is that the test's synthetic key parser is simpler than production key encodings.

## Test Signals
This is the broadest signal for reclaimable filter correctness: before concrete filters decide on an entry, the base class must load, validate, lock, and release the correct snapshot context.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/filter/TestReclaimableFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/filter/TestReclaimableKeyFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/filter/TestReclaimableKeyFilter.java

## Purpose
`TestReclaimableKeyFilter` validates deleted-key reclamation and exclusive-size accounting across current, previous, and previous-to-previous snapshots.

## Important APIs, Types, and Functions
- `ReclaimableKeyFilter` is initialized with two previous snapshots in scope.
- `KeyManager.getPreviousSnapshotOzoneKeyInfo(volumeId, bucketInfo, keyInfo)` retrieves prior key versions.
- `SnapshotUtils.isBlockLocationInfoSame` is mocked to distinguish same-object/same-block continuity from changed block locations.
- `getExclusiveSizeMap` and `getExclusiveReplicatedSizeMap` expose per-snapshot retained-size accounting.

## Control Flow
The helper resolves two prior snapshots, attaches mock key managers to them, wires previous-key lookups, and applies the filter. A key is not reclaimable when the previous snapshot contains the same object ID and equivalent block locations. It is reclaimable when there is no prior key, a different object ID, or different block IDs. Size-accounting tests apply the filter multiple times while changing previous-to-previous block equivalence to verify when the previous snapshot's exclusive size should accumulate.

## State and Persistence Behavior
The main state under test is the filter's in-memory maps keyed by previous snapshot ID. They accumulate data size and replicated size for keys retained exclusively by a snapshot. Snapshot metadata and previous-key tables are mocked; no durable store is mutated.

## Dependencies and Integration Points
This test integrates with key manager previous-snapshot lookup, bucket info, volume ID mapping, snapshot handles, and `SnapshotUtils` block comparison. It protects the snapshot GC accounting path that reports storage exclusive to snapshots.

## Risks and Edge Cases
Covered risks include reclaiming a key that is still referenced by prior snapshots, failing to reclaim changed object/block versions, and incorrect exclusive-size accounting when the same key exists farther back in the chain. The tests use mocked `OmKeyInfo`; real multipart/block-list complexity is represented only through `isBlockLocationInfoSame`.

## Test Signals
The file provides strong coverage for key identity and retained-byte accounting. It is especially useful for regressions that would over-delete snapshot-protected blocks or undercount exclusive snapshot usage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/filter/TestReclaimableKeyFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/filter/TestReclaimableRenameEntryFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/filter/TestReclaimableRenameEntryFilter.java

## Purpose
`TestReclaimableRenameEntryFilter` validates reclaimability of rename-table entries by checking whether their target key or directory still exists in the previous snapshot.

## Important APIs, Types, and Functions
- `ReclaimableRenameEntryFilter` is initialized with one previous snapshot.
- Rename table values are strings that point to prior key/directory entries.
- `OMMetadataManager.splitRenameKey` parses the rename key into volume/bucket/object components.
- Previous snapshot `OMMetadataManager.getKeyTable(bucketLayout)` and `getDirectoryTable` are mocked to simulate object-store and filesystem-optimized layouts.

## Control Flow
The helper resolves the previous snapshot, wires its metadata manager to mocked key and directory tables, configures the current key manager metadata manager to split the rename key, and applies the filter. For object-store buckets, presence in the previous key table makes the entry non-reclaimable except at index zero. For FSO buckets, absence from both key and directory tables makes it reclaimable; presence in either file or directory table makes it non-reclaimable when a previous snapshot exists.

## State and Persistence Behavior
State is represented by mocked table contents. `getMockedTable` returns table values from maps; `getFailingMockedTable` protects layout-specific paths by throwing if an irrelevant table is queried. No persistent state changes occur.

## Dependencies and Integration Points
The test integrates bucket layout selection, rename-key parsing, previous snapshot metadata tables, and base reclaimable snapshot chain locking. It covers both `BucketLayout.OBJECT_STORE` and `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

## Risks and Edge Cases
The tests cover file versus directory entries and ensure non-FSO logic does not query directory tables. Risks not covered include malformed rename keys, RocksDB iterator behavior, and exceptions from relevant tables beyond the deliberate failing-table guard.

## Test Signals
This is a targeted signal that rename entries are only safe to reclaim after the object they point to is absent from the relevant previous-snapshot table.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/filter/TestReclaimableRenameEntryFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/util/TestTableMergeIterator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/util/TestTableMergeIterator.java

## Purpose
`TestTableMergeIterator` validates `TableMergeIterator`, a utility that iterates a caller-provided key stream and returns the values for each key across multiple tables in fixed table order.

## Important APIs, Types, and Functions
- `TableMergeIterator<K,V>` is constructed from `Iterator<K> keysToFilter`, an optional prefix, and one or more `Table<K,V>` instances.
- `next()` returns `Table.KeyValue<K, List<V>>` where the list index corresponds to the input table index and missing values are `null`.
- `StringInMemoryTestTable` supplies simple in-memory table behavior.
- `close()` is expected to be safe and idempotent enough for test usage.

## Control Flow
Tests cover constructor creation, `hasNext` delegation, single-key lookup in all tables, partial table hits, no hits, multiple sequential keys, empty tables, `NoSuchElementException` after exhaustion, prefix usage, single-table operation, null keys, large 100-key iteration, and sparse requested keys. A dedicated test asserts that the returned values list is mutable and reused across `next()` calls.

## State and Persistence Behavior
State is in-memory only. The iterator maintains the current key and a reusable values list, which is an explicit behavior: callers must not retain the list expecting immutability or snapshot isolation across iterations.

## Dependencies and Integration Points
The utility depends on the HDDS `Table` abstraction and `KeyValue` return type. It is relevant to snapshot table-merge workflows where a candidate key list must be compared across active and snapshot tables.

## Risks and Edge Cases
The test covers null keys and absent values but does not simulate table I/O exceptions during `get`, concurrent table mutation, or prefix mismatch filtering beyond a matching prefix case. The reusable list behavior is a notable integration risk for callers that cache results.

## Test Signals
The file establishes deterministic merge ordering and missing-value semantics, both essential for callers that compare per-key state across multiple metadata tables.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/util/TestTableMergeIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/MockOmRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/MockOmRequest.java

## Purpose
`MockOmRequest` is a minimal test fixture used to validate layout-version annotations on OM request classes and aspect interception of request pre-execution.

## Important APIs, Types, and Functions
- The class is annotated with `@BelongsToLayoutVersion(INITIAL_VERSION)`.
- `preExecute(OzoneManager om)` is intentionally shaped like real `OMClientRequest.preExecute` methods so `OMLayoutFeatureAspect.beforeRequestApplyTxn` can inspect the target and first argument.

## Control Flow
The method body is empty; tests do not rely on behavior inside `preExecute`. Instead, the class provides an annotation target and a method signature compatible with the aspect.

## State and Persistence Behavior
There is no state or persistence behavior. The class exists only for reflective and aspect-oriented tests.

## Dependencies and Integration Points
It depends on `OzoneManager`, `BelongsToLayoutVersion`, and `OMLayoutFeature.INITIAL_VERSION`. It integrates with `TestOMLayoutFeatureAspect`.

## Risks and Edge Cases
The fixture must remain compatible with the aspect's assumption that request `preExecute` receives `OzoneManager` as its first argument. If production request signatures change, this mock can hide or reveal aspect drift depending on whether it is updated.

## Test Signals
The class signals that request-level layout gating is annotation driven and can be tested without a full request implementation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/MockOmRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/OMLayoutFeatureUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/OMLayoutFeatureUtil.java

## Purpose
`OMLayoutFeatureUtil` is a test utility for method-level layout gating. It supplies one disallowed annotated API, one basic API, and a mocked layout version manager provider for the aspect.

## Important APIs, Types, and Functions
- `ecMethod()` is annotated with `@DisallowedUntilLayoutVersion(INITIAL_VERSION)` and returns `"ec"` if allowed.
- `basicMethod()` returns `"basic"` and has no gating annotation.
- `getOmVersionManager()` returns a mocked `LayoutVersionManager` whose `isAllowed(String)` returns false first and true second, and whose `getFeature(String)` resolves to `INITIAL_VERSION`.

## Control Flow
The aspect test calls `ecMethod` through a mocked `JoinPoint`. The utility's version manager causes the first gate check to fail, producing an `OMException`. The second allowed return value supports tests that may invoke again after finalization.

## State and Persistence Behavior
No durable state exists. The only state is Mockito's ordered return behavior for the mocked version manager.

## Dependencies and Integration Points
The utility depends on layout annotations, `LayoutVersionManager`, Mockito, and `OMLayoutFeature.INITIAL_VERSION`. It integrates with `OMLayoutFeatureAspect` tests.

## Risks and Edge Cases
Because it returns a new mock manager on each call, it is not a full lifecycle simulation of layout finalization. It is intentionally narrow and should not be used as a production-like version manager.

## Test Signals
The file signals that method-level feature restrictions can be enforced independently from business logic through annotations and aspect lookup of an owning version manager.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/OMLayoutFeatureUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/TestOMLayoutFeatureAspect.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/TestOMLayoutFeatureAspect.java

## Purpose
`TestOMLayoutFeatureAspect` validates the AspectJ-based layout feature gate that blocks APIs or request pre-execution before a layout feature is finalized.

## Important APIs, Types, and Functions
- `OMLayoutFeatureAspect.checkLayoutFeature(JoinPoint)` checks method-level `@DisallowedUntilLayoutVersion`.
- `OMLayoutFeatureAspect.beforeRequestApplyTxn(JoinPoint)` checks class-level `@BelongsToLayoutVersion` on request objects.
- `OMLayoutFeatureUtil.ecMethod` and `MockOmRequest.preExecute` are fixture targets.
- `OMLayoutVersionManager.isAllowed` and `getFeature` drive allow/deny decisions.

## Control Flow
The method-level test builds a mocked join point whose target is `OMLayoutFeatureUtil` and whose method signature points to `ecMethod`. The aspect throws `OMException` containing a finalization message. The request-level test builds a mocked `OzoneManager` whose version manager denies `INITIAL_VERSION`, passes it as the first join-point argument, and asserts the same failure shape.

## State and Persistence Behavior
No persistent state is used. Temporary metadata configuration is created in setup but not materially used by the assertions. The relevant state is the mocked layout manager's denied feature status.

## Dependencies and Integration Points
The tests depend on AspectJ `JoinPoint` and `MethodSignature`, OM layout annotations, `OMException`, `OzoneManager`, and `OMLayoutVersionManager`. They protect upgrade gating at both utility-method and OM-request boundaries.

## Risks and Edge Cases
The tests assert denial paths only; allowed execution paths are mostly represented by utility behavior elsewhere. They also depend on exact annotation discovery through mocked signatures rather than woven aspect execution in a running container.

## Test Signals
The file confirms that layout gates fail closed when a feature is not finalized and that error messages explain the finalization requirement.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/TestOMLayoutFeatureAspect.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/TestOMUpgradeFinalizer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/TestOMUpgradeFinalizer.java

## Purpose
`TestOMUpgradeFinalizer` validates OM layout finalization status reporting, client ownership/takeover behavior, execution of upgrade actions, storage layout version advancement, and failure handling.

## Important APIs, Types, and Functions
- `OMUpgradeFinalizer.finalize(clientId, OzoneManager)` starts finalization.
- `reportStatus(clientId, takeover)` reports finalization status and enforces client ownership unless takeover is requested.
- `OMLayoutVersionManager` supplies upgrade state, `needsFinalization`, and `unfinalizedFeatures`.
- `OMLayoutFeature.action()` may provide an `OmUpgradeAction`.
- `OMStorage.setLayoutVersion` persists finalized layout versions.

## Control Flow
Already-finalized state returns `ALREADY_FINALIZED`. Required-finalization setup supplies mocked feature iterables and expects `STARTING_FINALIZATION`, then later `FINALIZATION_DONE`. Report status from a different client fails unless takeover is true. Action tests attach an upgrade action to the first feature, assert it calls `OzoneManager.getVersion`, and verify both feature layout versions are written. Failure tests throw from the first action and assert an `UpgradeException` with `LAYOUT_FEATURE_FINALIZATION_FAILED`, with no storage version updates.

## State and Persistence Behavior
Persistent state is modeled through `OMStorage.setLayoutVersion` and an in-test `storedLayoutVersion` field. The finalizer also holds client ownership and completion status in memory. Messages accumulated by finalization are expected to be non-empty after completion/failure.

## Dependencies and Integration Points
The test uses `UpgradeFinalization.Status`, `UpgradeException`, `LayoutFeature`, `OMLayoutFeature`, `OmUpgradeAction`, `OzoneManager`, and `OMStorage`. It protects the transition point from feature-level actions to durable OM layout version storage.

## Risks and Edge Cases
Covered risks include incorrect already-finalized behavior, unknown client status polling, missing takeover support, action execution order, and version persistence after failure. The current test notes that finalization runs synchronously; if behavior becomes background/state-machine-driven, in-progress status tests must be updated.

## Test Signals
This is the primary unit signal for finalization sequencing and failure atomicity: failed feature actions must not advance stored layout versions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/TestOMUpgradeFinalizer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/TestOMVersionManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/TestOMVersionManager.java

## Purpose
`TestOMVersionManager` validates OM layout version manager invariants: initial feature allowance, unsupported version rejection, monotonic layout versions, aspect compatibility with request pre-execution, and upgrade action registration.

## Important APIs, Types, and Functions
- `OMLayoutVersionManager` manages metadata layout version and feature allowance.
- `OMLayoutFeature` enum values must have consecutive `layoutVersion()` values.
- `OMClientRequest.preExecute` must have `OzoneManager` as its first parameter for aspect compatibility.
- `registerUpgradeActions(OM_UPGRADE_CLASS_PACKAGE)` discovers `@UpgradeActionOm` classes.
- Nested `MockOmUpgradeAction` executes by calling `OzoneManager.getVersion`.

## Control Flow
The tests instantiate default and explicit-version managers, assert initial allowance, and verify an unsupported version greater than the latest feature throws `OMException` with `NOT_SUPPORTED_OPERATION`. The enum ordering test iterates every feature and asserts versions increase by one. It also attaches and executes an action on the last feature. The compatibility test reflectively inspects `OMClientRequest.preExecute`. The registration test mocks an old metadata layout version and ensures `INITIAL_VERSION` gains the nested action.

## State and Persistence Behavior
No durable state is written. Feature action registration mutates static/enum-associated action state for `OMLayoutFeature`, which can affect test ordering if not carefully controlled by the manager's registration semantics.

## Dependencies and Integration Points
The file depends on layout feature enums, annotation scanning, OM request base class reflection, `OMException`, and `OzoneManager`. It is a guard for upgrade framework metadata consistency.

## Risks and Edge Cases
The tests cover monotonic version numbering and registration when metadata layout is behind. They do not validate every real upgrade action's side effects. Because enum action state can be mutable, tests must avoid assumptions that actions are always absent after registration in the same JVM.

## Test Signals
The file provides high-value regression protection against accidental layout version gaps and preExecute signature changes that would break aspect gating.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/TestOMVersionManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/TestOzoneManagerPrepareState.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/TestOzoneManagerPrepareState.java

## Purpose
`TestOzoneManagerPrepareState` validates OM prepare-state lifecycle and its marker-file persistence. Prepare mode blocks normal OM write requests during upgrade preparation and must survive restart only when the marker file is valid for the applied transaction index.

## Important APIs, Types, and Functions
- `OzoneManagerPrepareState.enablePrepareGate`, `finishPrepare`, `cancelPrepare`, `restorePrepareFromFile`, `requestAllowed`, and `getState` are tested.
- `PrepareStatus` values include `NOT_PREPARED`, `PREPARE_GATE_ENABLED`, and `PREPARE_COMPLETED`.
- `getPrepareMarkerFile` exposes the marker file containing the prepare transaction index.
- `Type.Prepare` and `Type.CancelPrepare` are the only request types allowed while the gate is up.

## Control Flow
Tests cover starting prepare, finishing as follower and leader, repeated finish, cancel after start/finish/cancel, request gating, restore with correct index, restore with marker index behind OM transaction index, garbage marker content, empty marker, missing marker, gate-only in-memory state, and repeated restores. Assertion helpers centralize status, index, marker presence, and request allowance checks.

## State and Persistence Behavior
The marker file is durable state. `finishPrepare(TEST_INDEX)` writes the index, and restore reads and validates it. `cancelPrepare` removes the marker and drops the gate. Invalid marker content or stale marker index raises `OMException` with `PREPARE_FAILED`, while preserving in-memory gate state for gate-only restore failure.

## Dependencies and Integration Points
The test uses `OzoneConfiguration` with `OZONE_METADATA_DIRS`, OM protocol `Type`, prepare status protos, and file I/O. It protects upgrade prepare behavior that coordinates OM request admission with Ratis-applied transaction indexes.

## Risks and Edge Cases
Covered risks include accepting stale marker files, mishandling corrupt or empty files, dropping gate state on failed restore, and allowing disallowed request types during prepare. The helper `assertPrepareFailedException` only rethrows non-prepare failures, so callers must rely on follow-up state assertions to ensure failure occurred.

## Test Signals
This file is the main signal for prepare-state durability and gate semantics. It confirms that once prepare begins, only prepare/cancel requests pass until cancellation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/TestOzoneManagerPrepareState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/protocolPB/TestOzoneManagerRequestHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/protocolPB/TestOzoneManagerRequestHandler.java

## Purpose
`TestOzoneManagerRequestHandler` validates selected read/write request handling behavior in the protobuf-facing OM request handler: list response sizing, light-key encryption propagation, audit logging on write failures, and snapshot diff method routing for optional native/full diff flags.

## Important APIs, Types, and Functions
- `OzoneManagerRequestHandler.handleReadRequest` handles `ListKeys`, `ListKeysLight`, `ListStatus`, and `SnapshotDiff` requests.
- `handleWriteRequestImpl` is tested for exception audit logging with an `ExecutionContext`.
- `OmConfig.setMaxListSize` sets the server-side cap.
- `BasicOmKeyInfo.fromOmKeyInfo` preserves encryption state into light key responses.
- `OzoneManager.snapshotDiff` has overloaded forms: one with `forceFullDiff`/`disableNativeDiff` booleans and one report-only legacy form.

## Control Flow
Parameterized list tests vary result sizes and request counts, mock corresponding OzoneManager list methods, and assert response sizes are capped by both server max and request count. The encryption test builds encrypted and non-encrypted `OmKeyInfo` instances and asserts `BasicKeyInfo.isEncrypted`. The write audit test intentionally leaves OM metrics null so create-volume cache update throws, then captures the audit message and checks transaction index and command type. Snapshot diff routing builds a request with explicit optional booleans and expects the boolean overload, then clears invocations and sends a report-only request without those fields and expects the shorter overload.

## State and Persistence Behavior
No durable OM state is written. The write test exercises transient audit message generation during a failing write path. List tests use in-memory mocked result lists.

## Dependencies and Integration Points
The test integrates protobuf request/response types, OM list APIs, `OmConfig`, replication configs, encryption metadata, audit logging, performance metrics, Ratis `TermIndex`, and layout version checks for snapshot diff.

## Risks and Edge Cases
Covered risks include over-returning list entries, losing encryption flags in light listings, missing transaction/command audit context on failed writes, and invoking the wrong snapshot diff overload based on optional flag presence. The tests do not validate every request type handled by `OzoneManagerRequestHandler`.

## Test Signals
The file provides high-signal coverage for API compatibility and response shaping at the protocol boundary, especially around optional-field backward compatibility for snapshot diff.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/protocolPB/TestOzoneManagerRequestHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/S3SecretStoreMap.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/S3SecretStoreMap.java

## Purpose
`S3SecretStoreMap` is a simple in-memory test implementation of `S3SecretStore` backed by a concurrent map.

## Important APIs, Types, and Functions
- Constructor copies an initial `Map<String, S3SecretValue>`.
- `storeSecret` inserts or replaces a secret by Kerberos ID.
- `getSecret` returns the stored `S3SecretValue` or null.
- `revokeSecret` removes a secret.
- `batcher()` returns null because batch semantics are not needed in these tests.

## Control Flow
The implementation is direct map delegation with no validation or transformation. It is used by S3 authentication tests through `S3SecretManagerImpl` and locking wrappers.

## State and Persistence Behavior
State is held in a `ConcurrentHashMap` for test-thread safety. There is no persistence, batching, or transactional behavior.

## Dependencies and Integration Points
It implements `org.apache.hadoop.ozone.om.S3SecretStore` and stores `S3SecretValue` objects. It integrates with `S3SecretManagerImpl`, `S3SecretLockedManager`, and `OzoneDelegationTokenSecretManager` S3 auth validation tests.

## Risks and Edge Cases
Returning null from `batcher()` is acceptable for current tests but would be unsafe for code paths expecting batch operations. The store does not simulate persistence failures, serialization, or lock contention.

## Test Signals
The class is a lightweight fixture signal: S3 auth tests can focus on signature validation and token behavior without requiring a real OM metadata-backed secret store.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/S3SecretStoreMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/SecretKeyTestClient.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/SecretKeyTestClient.java

## Purpose
`SecretKeyTestClient` is a test implementation of `SecretKeyClient` that supplies rotating HMAC managed secret keys for delegation token signing and verification tests.

## Important APIs, Types, and Functions
- `rotate()` generates a new `ManagedSecretKey` and stores it by UUID.
- `getCurrentSecretKey()` returns the active key.
- `getSecretKey(UUID)` returns a historical key by ID.
- `generateKey()` creates an `HmacSHA256` `SecretKey` and wraps it in `ManagedSecretKey` with one-hour validity.

## Control Flow
The constructor immediately rotates so a current key is always available. Each rotation creates a random UUID and a fresh key, updates `current`, and preserves prior keys in `keysMap`.

## State and Persistence Behavior
State is an in-memory `HashMap` and current-key reference. There is no persistence or expiration cleanup; validity timestamps are embedded in the `ManagedSecretKey`.

## Dependencies and Integration Points
The class depends on Java Cryptography Architecture `KeyGenerator`, `SecretKey`, and HDDS `ManagedSecretKey`/`SecretKeyClient`. It is used by `TestOzoneDelegationTokenSecretManager` for symmetric token signatures.

## Risks and Edge Cases
The implementation is not thread-safe and does not simulate key service failures except when spied in tests. It throws a runtime exception if `HmacSHA256` is unavailable, which is effectively impossible on supported JVMs.

## Test Signals
The class provides deterministic API behavior with real cryptographic keys, making token signature tests more meaningful than byte-array stubs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/SecretKeyTestClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/TestAWSV4AuthValidator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/TestAWSV4AuthValidator.java

## Purpose
`TestAWSV4AuthValidator` validates AWS Signature Version 4 request signature checking against known positive and negative vectors.

## Important APIs, Types, and Functions
- `AWSV4AuthValidator.validateRequest(stringToSign, signature, accessKey)` returns a boolean validation result.
- The parameter provider `data()` supplies canonical string-to-sign values, expected signatures, secret access keys, and expected outcomes.

## Control Flow
The parameterized test passes each tuple to `validateRequest` and asserts the boolean result. Two cases are valid signatures and one differs by the final hex character to assert rejection.

## State and Persistence Behavior
No state or persistence is involved. Inputs are immutable strings.

## Dependencies and Integration Points
The validator is used by S3 authentication paths, including `OzoneDelegationTokenSecretManager` when token type is `S3AUTHINFO`. This test keeps a direct unit signal for the HMAC derivation logic.

## Risks and Edge Cases
The vectors cover positive and one invalid-signature case but do not cover malformed credential scope, unsupported algorithms, date parsing errors, or whitespace/canonicalization issues. Those may be covered at higher S3 request layers.

## Test Signals
The file confirms that the low-level AWS V4 validator matches known HMAC outputs and rejects altered signatures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/TestAWSV4AuthValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/TestOmCertificateClientInit.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/TestOmCertificateClientInit.java

## Purpose
`TestOmCertificateClientInit` validates `OMCertificateClient.init()` behavior for all combinations of private key, public key, and certificate presence on disk.

## Important APIs, Types, and Functions
- `OMCertificateClient.init()` returns `InitResponse` values `GETCERT`, `FAILURE`, or `SUCCESS`.
- `KeyStorage.storePrivateKey` and `storePublicKey` prepare key files.
- `CertificateCodec.writeCertificate` prepares the certificate file.
- `OzoneSecurityUtil.checkIfFileExist` asserts key files exist after non-failure initialization.

## Control Flow
Setup creates a temp metadata directory, `SecurityConfig`, generated key pair, self-signed certificate, mocked `OMStorage`, OM details proto, `OMCertificateClient`, and component key directory. The parameterized test deletes or writes private key, public key, and certificate files based on booleans, calls `init()`, asserts the expected response with a special case for both keys present but no cert, and verifies key files exist for non-failure responses.

## State and Persistence Behavior
This test writes actual key and certificate files under the temp security directory and deletes missing-case files with `FileUtils.deleteQuietly`. It verifies initialization can generate or preserve key material depending on present artifacts.

## Dependencies and Integration Points
The test integrates `SecurityConfig`, `HDDSKeyGenerator`, `KeyStorage`, `CertificateCodec`, `OMStorage`, `OzoneManager.getOmDetailsProto`, and Java `X509Certificate` generation via `KeyStoreTestUtil`.

## Risks and Edge Cases
Covered risks include partial key/cert states and ensuring successful init leaves both key files present. The test does not validate certificate chain trust, CSR submission, or SCM interaction because those are outside local init artifact handling.

## Test Signals
The file is a strong matrix test for local OM certificate-client bootstrap behavior and prevents regressions in key/cert artifact recovery.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/TestOmCertificateClientInit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/TestOzoneDelegationTokenSecretManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/TestOzoneDelegationTokenSecretManager.java

## Purpose
`TestOzoneDelegationTokenSecretManager` validates OM delegation token creation, password retrieval, renewal, cancellation, signature verification, expired secret-key handling, leader checks, and S3 auth token validation.

## Important APIs, Types, and Functions
- `OzoneDelegationTokenSecretManager.Builder` wires configuration, token lifetimes, service address, OM, S3 secret manager, certificate client, OM service ID, and secret key client.
- `createToken`, `renewToken`, `cancelToken`, `retrievePassword`, `createIdentifier`, `verifySignature`, and `updateToken` are tested.
- `OzoneTokenIdentifier` carries owner, renewer, real user, token type, secret key ID, certificate serial ID, S3 signature fields, and service ID.
- `SecretKeyTestClient` provides symmetric signing keys; an overridden `OMCertificateClient` provides asymmetric signing and certificate lookup.
- `S3SecretLockedManager` plus `S3SecretStoreMap` provide S3 access secrets.

## Control Flow
Setup creates a temp OM metadata path, security config, certificate client with generated RSA key/cert path, secret key client, mocked OM with metadata manager and layout manager, and an S3 secret manager seeded with test users. Tests then cover: wrapping OM leadership exceptions in `InvalidToken`; creating a token and validating its signature; behavior when secret key IDs cannot be resolved and expired tokens are removed from the delegation token table; renew success with and without secret-manager restart; renew failure for wrong renewer, max lifetime expiry, and renewal interval expiry; empty identifier creation; cancel success and authorization failure; symmetric and asymmetric signature verification; invalid certificate serial failure; and S3AUTHINFO success/failure.

## State and Persistence Behavior
The test uses a real `OmMetadataManagerImpl` backed by the temp metadata path and writes delegation token entries into the delegation token table through `addToTokenStore`. Secret manager restart reloads state from metadata. Expired-token handling deletes stale rows from the delegation token table. Certificate and key material are local in-memory/temporary test artifacts.

## Dependencies and Integration Points
This file integrates security config, certificate codecs, Java cert paths, OM metadata tables, layout version gating, S3 secret managers, leader status checks, Hadoop `Token`, `SecretManager.InvalidToken`, access-control exceptions, Ratis peer IDs, and log capture. It is a broad integration-style unit test for OM token security.

## Risks and Edge Cases
Covered risks include accepting operations on non-leader OMs, losing renewability across restart, allowing unauthorized renew/cancel users, accepting expired tokens, failing to clean expired rows when keys are missing, incorrect symmetric/asymmetric signature validation, and S3 signature validation against absent/invalid secrets. Timing-based tests use sleeps and short lifetimes, which can be sensitive on slow CI.

## Test Signals
This is the strongest security test in the subset. It verifies both cryptographic paths and persisted token table interactions, while also confirming S3 auth delegates to stored S3 secrets and AWS V4 signature logic.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/TestOzoneDelegationTokenSecretManager.java -->
