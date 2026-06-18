# subset-b-008005 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerTask.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerTask.java

Purpose: exercises `DiskBalancerService.DiskBalancerTask` container move behavior for key-value containers, including successful moves, rollback paths, delayed old-replica cleanup, committed-space release, and state validation. It builds a local two-volume `MutableVolumeSet`, a mocked `OzoneContainer`, a real `ContainerSet`, `KeyValueHandler`, and `DiskBalancerServiceTestImpl`.

Important APIs/types/functions: `DiskBalancerService.DiskBalancerTask.call()`, `DiskBalancerServiceTestImpl`, `KeyValueContainer`, `KeyValueContainerData`, `ContainerSet.updateContainer`, `KeyValueContainerUtil.removeContainer`, `ContainerID`, `HddsVolume` used/committed-space counters, `BackgroundTaskQueue`, and the nested `TestFaultInjector`. `ContainerTestVersionInfo.ContainerTest` runs most failure cases across schema/layout combinations, while `EnumSource` covers movable and invalid container states.

Control flow: `setup()` creates two data volumes, makes the first hot by incrementing used space, initializes container DBs, installs the key-value handler, enables disk balancer config, and installs a `KeyValueContainer` fault injector. `createContainer()` creates a closed/quasi-closed container on a selected source volume and manually updates used bytes. Tests poll one balancer task from `diskBalancerService.getTasks()` and call it synchronously or via `CompletableFuture` to assert behavior during specific race points. Fault cases inject IO exceptions during copy, force a non-empty destination directory before atomic move, spy `ContainerSet.updateContainer()` to fail after disk move, mock old-container deletion failure, remove the container before task execution, or mutate the container state between task selection and execution.

State and persistence behavior: successful moves mark the original in-memory container `DELETED`, create a new active container under the destination volume path, update `ContainerSet`, move container IDs between volume iterators, adjust source/destination used bytes, and release destination committed bytes. Rollback assertions ensure temp directories are deleted, pre-existing destination directories are preserved, source paths remain intact, destination paths are removed after in-memory update failure, `inProgressContainers` is cleared, metrics are updated, and source delta sizes are restored. Delayed deletion tests use `TestClock` to verify old replicas remain until the delay expires and that multiple same-deadline old replicas are queued without being overwritten.

Dependencies and integration points: depends on HDDS volume initialization, `MockSpaceUsageCheckFactory`, RocksDB/block DB cache via `BlockUtils`, container location helpers, static Mockito for `KeyValueContainerUtil`, Apache Commons `FileUtils`, and `GenericTestUtils` wait/log capture. It integrates disk balancing with key-value container creation/deletion, volume accounting, background task selection, delayed source cleanup, and schema-version toggles.

Risks and test signals: strong signals include explicit checks for no data loss on copy/atomic/in-memory-update failures, correct committed-space cleanup, and race-safe pending deletion queue behavior. Risk remains around timing-sensitive async tests that depend on temp-directory visibility and injected pause hooks; failures may indicate regressions in cleanup ordering, lock release, or volume accounting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerVolumeCalculation.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerVolumeCalculation.java

Purpose: validates defensive arithmetic in `DiskBalancerVolumeCalculation` and volume report utilization for empty, zero-capacity, and invalid volume-usage inputs.

Important APIs/types/functions: `DiskBalancerVolumeCalculation.getIdealUsage`, `calculateVolumeDataDensity`, `newVolumeFixedUsage`, `VolumeFixedUsage.getUtilization`, and `DiskBalancerService.buildVolumeReportProto`. The local `createVolume()` helper builds `HddsVolume` instances backed by `MockSpaceUsageSource.fixed()` and `MockSpaceUsageCheckFactory`.

Control flow: each test constructs one or more mock-backed volumes with synthetic capacity/available values, wraps them in `VolumeFixedUsage`, and checks calculations or expected exceptions. Zero-capacity tests assert zero ideal usage/utilization and that zero-capacity volumes do not affect density. Negative capacity/effective-used and effective-used-greater-than-capacity tests assert `IllegalArgumentException` with exact messages.

State and persistence behavior: the file uses `@TempDir` to give each `HddsVolume` a filesystem root, but no durable container state is written. The significant state is the fixed space usage snapshot captured in each `HddsVolume` and optional effective-used adjustment map.

Dependencies and integration points: integrates disk balancer math with HDDS volume usage abstractions and the service's volume-report protobuf builder. It depends on mock space usage plumbing rather than real disk accounting.

Risks and test signals: high-value signals are edge-case protection against divide-by-zero, negative accounting, and over-capacity effective usage. Exact message assertions make validation precise but may be brittle if exception wording changes without behavioral change.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerVolumeCalculation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerWithConcurrentBackgroundTasks.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerWithConcurrentBackgroundTasks.java

Purpose: stress-tests races where disk balancer has swapped `ContainerSet` to a destination replica while concurrent background/RPC paths still hold stale source-container references. It proves delete, block deletion, mark-unhealthy, and close flows resolve the live container by ID and operate on the destination replica.

Important APIs/types/functions: `ContainerSet.getContainerWithWriteLock`, `ContainerSet.updateContainer`, `KeyValueHandler.deleteContainer`, `markContainerUnhealthy`, `closeContainer`, `BlockDeletingTask`, `BlockDeletingService.ContainerBlockInfo`, `DiskBalancerService.DiskBalancerTask`, and the nested `AfterInMemoryUpdateInjector`. Helpers persist quasi-closed state, seed/read pending-delete counters, choose hottest/coldest volumes, and create closed containers across `ContainerTestVersionInfo`.

Control flow: setup creates three volumes with controlled utilization so one is hot and one is cold, builds a real `KeyValueHandler` and mocked `OzoneContainer`, then starts a disk balancer service. Tests create a source replica on the hot volume, install an injector that pauses immediately after `ContainerSet.updateContainer`, run the move asynchronously, wait for the swap point, then start a concurrent operation using the stale source object/data. Once the concurrent operation makes observable progress, the test releases the balancer and asserts final state.

State and persistence behavior: the copied destination replica must own the live container ID, state transitions, DB counters, and chunk paths. Force-delete removes the destination map entry/path while disk balancer later deletes the old source path. Block deletion reads pending-delete counters copied into the destination DB and reduces them on the destination, not stale metadata. Mark-unhealthy changes the destination state to `UNHEALTHY`; close changes the destination from `QUASI_CLOSED` to `CLOSED`. Old source replicas are marked `DELETED` and removed by delayed cleanup.

Dependencies and integration points: depends on disk balancer hooks, `KeyValueHandler`, `BlockDeletingService`, `ContainerChecksumTreeManager`, `BlockUtils` DB access, YAML container-file persistence, volume usage ordering, `GenericTestUtils`, AssertJ, and `CompletableFuture`/latches. It directly protects integration between disk balancing and background services that may carry stale references.

Risks and test signals: the file gives strong concurrency-regression coverage for stale-reference bugs after map swap. Timing and latch coordination are deliberate; failures usually mean lock resolution, cleanup ordering, or state persistence changed. It assumes the injector remains positioned after `updateContainer` and before read-unlock, so moving that hook can invalidate test intent.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerWithConcurrentBackgroundTasks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerYaml.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerYaml.java

Purpose: verifies persistence and validation of datanode disk balancer YAML info files.

Important APIs/types/functions: `DiskBalancerYaml.createDiskBalancerInfoFile`, `readDiskBalancerInfoFile`, `DiskBalancerInfo`, `DiskBalancerRunningStatus`, `DiskBalancerConfiguration.DEFAULT_CONTAINER_STATES`, and `DiskBalancerVersion.DEFAULT_VERSION`. The `validYaml()` helper provides a baseline persisted document for mutation tests.

Control flow: parameterized round-trip tests write `DiskBalancerInfo` to the default info filename under `@TempDir`, read it back, and compare equality. Missing and explicit-null `containerStates` tests hand-write YAML and assert defaulting. Invalid cases mutate version, operational state, threshold, bandwidth, parallel thread count, or container states and assert `IOException` messages include the expected validation reason.

State and persistence behavior: this is a pure YAML file test. It checks backward-compatible defaults for older/malformed persisted beans and rejects unsupported or invalid persisted configuration before disk balancer resumes from it.

Dependencies and integration points: integrates SnakeYAML-backed disk balancer persistence with config validation and protobuf running-status enums. It uses Java NIO file writes and JUnit parameter sources.

Risks and test signals: strong signal for persisted-info compatibility and safety. Exact substring checks avoid binding to whole exception text but still catch missing validation. Gaps include no explicit malformed YAML syntax case or future-version migration path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerYaml.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/ContainerLayoutTestInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/ContainerLayoutTestInfo.java

Purpose: provides reusable test parameters and helpers for key-value container chunk layout implementations.

Important APIs/types/functions: enum values `DUMMY`, `FILE_PER_CHUNK`, and `FILE_PER_BLOCK`; `createChunkManager(boolean, BlockManager)`, `validateFileCount(File,long,long)`, `getLayout()`, `updateConfig(OzoneConfiguration)`, and the composite `@ContainerTest` annotation sourcing `ContainerLayoutVersion.getAllVersions`.

Control flow: each enum value constructs the matching `ChunkManager` implementation and asserts expected files under the chunks directory. `DUMMY` disables persisted data with `HDDS_CONTAINER_PERSISTDATA=false` and expects zero files. `FILE_PER_CHUNK` sets layout config and expects one file per chunk. `FILE_PER_BLOCK` sets layout config and expects one file per block.

State and persistence behavior: this helper controls whether tests write chunk data to disk and how many files should appear for a given block/chunk count. `updateConfig()` mutates the supplied `OzoneConfiguration` to align production code paths with the selected layout.

Dependencies and integration points: used by container integrity, mark-unhealthy, and reconciliation tests to run the same behavior over layout variants. It binds tests to `FilePerChunkStrategy`, `FilePerBlockStrategy`, `ChunkManagerDummyImpl`, and layout config keys.

Risks and test signals: centralizing layout setup keeps broad tests consistent. Because file-count assertions inspect only direct children, layout changes that add sidecar files in chunks directories would require updating this contract.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/ContainerLayoutTestInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/ContainerTestVersionInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/ContainerTestVersionInfo.java

Purpose: defines the cross-product of container metadata schema versions and chunk layout versions used by many parameterized key-value container tests.

Important APIs/types/functions: `SCHEMA_VERSIONS` includes `null`, `SCHEMA_V1`, `SCHEMA_V2`, and `SCHEMA_V3`; static `layoutList`; constructor/getters; `toString()`; `getLayoutList()`; `setTestSchemaVersion(String,OzoneConfiguration)`; and composite `@ContainerTest` sourcing this class.

Control flow: the static initializer iterates all `ContainerLayoutVersion.getAllVersions()` and every schema entry, appending a `ContainerTestVersionInfo` for each pair. Tests annotated with `@ContainerTest` receive each pair. `setTestSchemaVersion()` enables schema V3 only when the requested schema matches V3; all other values disable schema V3.

State and persistence behavior: instances are immutable parameter values. The mutable state is the static list and the supplied `OzoneConfiguration`, which is toggled to choose schema V3 shared-DB behavior versus older per-container DB behavior.

Dependencies and integration points: integrates JUnit parameterization with Ozone schema toggles in `ContainerTestUtils` and schema comparison in `KeyValueContainerUtil`. It is used heavily by disk balancer, iterator, container, scanner, metadata-inspector, and reconciliation tests.

Risks and test signals: ensures broad compatibility coverage across layouts and schema versions, including default/null schema behavior. Adding a schema version or layout automatically multiplies test coverage, which is useful but can increase runtime or expose assumptions in older tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/ContainerTestVersionInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestContainerCorruptions.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestContainerCorruptions.java

Purpose: enumerates reusable corruption injectors for container scanner tests, mapping each filesystem mutation to the expected `ContainerScanError.FailureType`.

Important APIs/types/functions: enum constants for missing chunks/metadata/container dirs, missing `.container` file, missing/corrupt/truncated block files, corrupt/truncated container file; `applyTo(Container<?>)`, `applyTo(Container<?>, long)`, `assertLogged(...)`, `getExpectedResult()`, `getAllParamsExcept(...)`, and `getBlock(...)`.

Control flow: each enum constant wraps a `BiConsumer<Container<?>,Long>` that deletes directories/files or mutates file content using `ContainerTestHelper.corruptFile`/`truncateFile`. `getBlock()` locates either the first `.block` file for negative IDs or a specific `<localID>.block` file under the chunks directory. Log assertions compile multiline regexes to verify scanner log output includes the expected failure type and container ID.

State and persistence behavior: mutations operate directly on the container's on-disk directory tree. Truncated block behavior intentionally maps to `MISSING_CHUNK` because a fully emptied file causes scanner chunk lookups to report all chunks missing.

Dependencies and integration points: used by `TestKeyValueContainerCheck` and reconciliation helpers. It depends on key-value file-per-block layout conventions, Apache Commons `FileUtils`, AssertJ, JUnit assertions, and `ContainerScanError`.

Risks and test signals: gives clear, reusable scan-corruption fixtures. The comment notes current support is file-per-block focused; tests using file-per-chunk or future layouts must avoid incompatible cases or extend lookup logic.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestContainerCorruptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestContainerReconciliationWithMockDatanodes.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestContainerReconciliationWithMockDatanodes.java

Purpose: simulates three datanodes with local key-value container replicas and verifies checksum/Merkle-tree reconciliation repairs missing blocks and corrupt chunks, even when one peer fails during protocol calls.

Important APIs/types/functions: `DNContainerOperationClient`, static mocks of `ContainerProtocolCalls.getContainerChecksumInfo/getBlock/readChunk`, `ContainerChecksumTreeManager`, `OnDemandContainerScanner`, `KeyValueHandler.reconcileContainer`, `MockDatanode`, `FailureLocation`, `corruptionValues()`, and helpers for checksum uniqueness and scan-count waiting.

Control flow: `@BeforeAll` creates three `MockDatanode` instances, each with a closed 15-block container containing deterministic chunk data, performs an initial scan to write Merkle trees, records the healthy data checksum, resets scan metrics, and installs protocol mocks that route "network" calls to the local peer objects. Main reconciliation tests corrupt two replicas differently, rescan, verify divergent checksums, reconcile each datanode against its peers, wait for reconciliation-triggered scans, and assert all data checksums return to the original healthy value. Peer-failure tests inject IO exceptions at checksum-info, block, or chunk-read stages for one healthy peer and assert the corrupted node still repairs from the other peer. A scan-failure test spies checksum reads to throw and asserts reconciliation propagates `IOException` while still triggering on-demand scans.

State and persistence behavior: `MockDatanode.addContainerWithBlocks()` creates real container directories, block files, DB metadata, and checksum files. Corruption removes block DB rows and files or overwrites bytes at chunk offsets. Reconciliation reads peer checksum trees, fetches missing/corrupt block/chunk data, writes repairs locally, and runs on-demand scans to refresh persisted checksum trees.

Dependencies and integration points: integrates `KeyValueHandler`, block/chunk managers, container scanner, checksum tree manager, HDDS pipeline protocol call static APIs, mocked datanode details, volume setup, RocksDB metadata, and file corruption helpers. It avoids a real network/cluster but exercises production reconciliation call paths.

Risks and test signals: strong end-to-end signal for reconciliation correctness across many corruption counts and partial peer failures. Risks include static mock lifecycle sensitivity and test cost from real file/DB operations. The TODO notes unsupported broader corruption combinations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestContainerReconciliationWithMockDatanodes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueBlockIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueBlockIterator.java

Purpose: verifies `BlockIterator<BlockData>` behavior over key-value container metadata tables across schema/layout variants and schema V3 key-separator settings.

Important APIs/types/functions: `db.getStore().getBlockIterator(containerID)`, filtered `getBlockIterator(containerID, KeyPrefixFilter)`, `BlockIterator.hasNext`, `nextBlock`, `seekToFirst`, `KeyValueContainerData.getDeletingBlockKeyFilter`, `containerPrefix`, and helper `createContainerWithBlocks`.

Control flow: `provideTestData()` duplicates the full `ContainerTestVersionInfo` matrix for empty and configured schema V3 key separators. `initTest()` toggles schema and separator config, then `setup()` creates a container and opens its DB. Tests populate block table rows with unprefixed, deleting, and synthetic second-prefix keys. They assert default iteration skips deleting-prefixed blocks, repeated `hasNext()` is idempotent, `seekToFirst()` resets iteration, `nextBlock()` throws a specific `NoSuchElementException` at EOF, deleting filters return only deleting blocks, and arbitrary future prefixes work.

State and persistence behavior: the file writes `BlockData` rows directly into the container's RocksDB block table. It does not write chunk files; block rows contain minimal `ChunkInfo`. Prefix construction includes `containerData.containerPrefix()` so schema-specific key formats are exercised.

Dependencies and integration points: depends on `MutableVolumeSet`, `BlockUtils`, `DatanodeConfiguration`, Ozone constants for deleting-key prefix, metadata key filters, and JUnit parameterization. It protects store iterator behavior that scanner, deletion, and listing code depend on.

Risks and test signals: strong signal for iterator cursor semantics and prefix filtering in RocksDB-backed stores. HashMap iteration is used when creating prefix groups, but expected IDs are tracked by prefix and sorted insertion per prefix, so tests focus on filter correctness rather than global key ordering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueBlockIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueContainer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueContainer.java

Purpose: broad unit coverage for `KeyValueContainer` lifecycle, metadata persistence, import/export, DB options, schema compatibility, checksum files, committed-space reservation, and error cleanup.

Important APIs/types/functions: `KeyValueContainer.create/delete/close/update/markContainerUnhealthy/exportContainerData/importContainerData/populatePathFields`, `KeyValueContainerData`, `TarContainerPacker`, `CopyContainerCompression`, `KeyValueContainerUtil.removeContainer/parseKVContainerData`, `BlockUtils.getDB`, `ContainerChecksumTreeManager`, `DatanodeStoreCache`, `StorageVolumeUtil`, `DatanodeDBProfile`, and helper methods `init`, `populate`, `populateWithoutBlock`, `checkContainerFilesPresent`, and `testMixedSchemaImport`.

Control flow: `init()` configures a reusable `OzoneConfiguration`, enables leak detection, sets RocksDB/compaction knobs, creates a checked `HddsVolume`, mocks volume selection, and constructs a container data object for each schema/layout parameter. Tests cover basic creation, retrying a second volume after metadata creation failure, duplicate and disk-full errors, deletion semantics, close/update/report behavior, concurrent export from 20 threads, import/export round trips for empty, unhealthy, populated, and empty-Merkle-tree containers, failed import cleanup, protobuf conversion, RocksDB cache/profile behavior, schema V2/V3 mixed import, empty-state calculation after import, auto-compaction for many schema V3 imports, and committed-space reservation during creation.

State and persistence behavior: tests write actual container directories, `.container` YAML files, chunks directories, DB rows, checksum files, and tar archives. Import/export asserts metadata, layout, max size, state, block counts, bytes used, DB type, data checksum, and container-file checksum survive. Deletion differs by schema: schema V3 shared DB may remain while older per-container DB files are removed. Failed import moves partial data to a temp deleted-container directory before cleanup attempts. Mixed-schema import preserves the exported replica schema and pending-delete counters regardless of target volume schema setting.

Dependencies and integration points: integrates key-value containers with volume choosing, HDDS volume formatting, RocksDB stores, DB profile/cache configuration, tar packing/compression, checksum tree validation, container util parsing, disk checker exceptions, Mockito spies, and JUnit assumptions. It is a central regression suite for many production container surfaces.

Risks and test signals: high-value signals include import/export invariants, cleanup on failure, schema migration compatibility, and memory leak detection via `CodecBuffer.assertNoLeaks()`. Risks are runtime/flake potential in the auto-compaction test because it imports 200 containers and sleeps for compaction, and the static `CONF` means tests intentionally share some option-cache state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueContainer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueContainerCheck.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueContainerCheck.java

Purpose: validates `KeyValueContainerCheck` scanner behavior for metadata failures, data corruption aggregation, checksum-tree diffs, normal containers, corrupted chunks, and containers marked for deletion.

Important APIs/types/functions: extends `TestKeyValueContainerIntegrityChecks`; uses `KeyValueContainerCheck.fastCheck/fullCheck`, `DataScanResult`, `ContainerScannerConfiguration`, `DataTransferThrottler`, `ContainerChecksumTreeManager.updateTree/diff`, `ContainerDiffReport`, and `TestContainerCorruptions`. Parameter sources exclude unsupported file-per-chunk corruption injection for fault-injection cases.

Control flow: metadata-error tests create a valid container, verify a clean full scan, inject one metadata corruption and optionally a later data corruption, then assert scan exits after the metadata error only. Data-error aggregation creates six blocks, captures a healthy Merkle tree, corrupts one block, deletes one block, truncates another, runs full scan, checks ordered failure types, writes the new corrupted tree, and verifies diff reports corrupt chunks, missing chunks, and missing blocks. Sanity tests cover clean open/closed scans and a manually truncated chunk failure. Deleted-container tests show missing internals are errors before `markContainerForDelete()` and become deleted/non-error scan results after deletion marking.

State and persistence behavior: tests create real block files, DB metadata, container YAML, and checksum tree updates. Corruption mutates files/directories on disk; scans read metadata first and then data files. Marking a container for delete changes scan semantics so missing directories are treated as expected deletion state.

Dependencies and integration points: integrates scanner config, throttling/cancel APIs, checksum tree manager, block iterator, layout file resolution, and reusable corruption enum. It protects both scan error reporting and reconciliation diff inputs.

Risks and test signals: strong signals for scanner stop/continue policy: metadata errors short-circuit, data errors accumulate. The expected duplicate corrupt-chunk and all-chunks-missing behavior encodes current scanner interpretation and may need adjustment if scanner granularity changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueContainerCheck.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueContainerIntegrityChecks.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueContainerIntegrityChecks.java

Purpose: shared base fixture for key-value container integrity and metadata-inspector tests, with helpers to create containers containing normal and deleting blocks plus optional on-disk chunk data.

Important APIs/types/functions: `initTestData(ContainerTestVersionInfo)`, private `setup()`, `teardown()`, `getChunkLayout()`, `getConf()`, and `createContainerWithBlocks(long,int,int,boolean)`. Constants define `UNIT_LEN`, `CHUNK_LEN`, and `CHUNKS_PER_BLOCK`.

Control flow: `initTestData()` configures schema V3 state, maps layout versions to `ContainerLayoutTestInfo.FILE_PER_BLOCK` or `FILE_PER_CHUNK`, then sets up datanode and metadata directories. `createContainerWithBlocks()` creates a `KeyValueContainer`, opens its DB, generates deterministic block/chunk metadata, optionally writes and commits chunk bytes through the selected `ChunkManager`, and stores normal block keys first followed by deleting block keys.

State and persistence behavior: when `writeToDisk` is true, chunks are physically written using checksummed random ASCII bytes and file-count assertions validate layout-specific persistence. Block metadata is stored in RocksDB under normal or deleting key prefixes. Container max size is derived from total block/chunk bytes, with a minimum of 1 for empty containers.

Dependencies and integration points: depends on `ContainerLayoutTestInfo`, `ContainerTestVersionInfo`, `MutableVolumeSet`, `BlockUtils`, checksum computation, `ChunkManager` strategies, and `ContainerTestUtils` write/commit stages. Subclasses reuse it for scanner and metadata repair coverage.

Risks and test signals: provides consistent fixture generation across schema/layout variants. It assumes all non-file-per-block layouts in this suite should use file-per-chunk behavior; adding a new layout may require updating the mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueContainerIntegrityChecks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueContainerMarkUnhealthy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueContainerMarkUnhealthy.java

Purpose: tests `KeyValueContainer.markContainerUnhealthy()` state transitions and persistence for every container layout version.

Important APIs/types/functions: `KeyValueContainer.markContainerUnhealthy`, `markContainerForClose`, `close`, `quasiClose`, `ContainerDataYaml.readContainerFile`, `HddsVolume.format/createWorkingDir`, mocked `MutableVolumeSet`, and `ContainerLayoutTestInfo.ContainerTest`.

Control flow: `initTestData()` selects a layout and calls `setup()`, which creates an HDDS volume under `@TempDir`, mocks volume choosing to return it, builds `KeyValueContainerData`, assigns a metadata path, and constructs a `KeyValueContainer`. Tests mark open, closed, quasi-closed, and closing containers unhealthy, and assert closing an already unhealthy container throws `StorageContainerException`.

State and persistence behavior: marking unhealthy updates in-memory `KeyValueContainerData` state and, for created containers, the `.container` file. Closed/quasi-closed tests create the container first to avoid close/quasi-close sync/compaction null paths. The open-container test reads the container YAML back to verify persisted `UNHEALTHY`.

Dependencies and integration points: integrates state-machine transitions with volume setup and container YAML persistence. Uses AssertJ and JUnit exception assertions.

Risks and test signals: focused signal for unhealthy transition permissiveness and close rejection. It does not test handler-level ICR/report side effects; those are covered elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueContainerMarkUnhealthy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueContainerMetadataInspector.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueContainerMetadataInspector.java

Purpose: verifies `KeyValueContainerMetadataInspector` activation, read-only/repair modes, JSON report content, and DB counter repair for block count, bytes used, and pending-delete block counts.

Important APIs/types/functions: extends `TestKeyValueContainerIntegrityChecks`; uses `KeyValueContainerMetadataInspector.SYSTEM_PROPERTY`, `Mode.INSPECT`, `Mode.REPAIR`, `ContainerInspectorUtil.load/unload`, `KeyValueContainerUtil.parseKVContainerData`, `BlockUtils.getDB`, schema two/three delete transaction tables, and nested `DeletedBlocksTransactionGeneratorForTesting`.

Control flow: activation tests clear/set the system property and assert inspector load/read-only behavior. Correct-container tests create containers with matching DB counters and assert no report in inspect or repair mode. Incorrect-total tests mutate DB metadata counts and run `inspectThenRepairOnIncorrectContainer()`, which captures JSON in inspect mode, validates errors without mutation, runs repair mode, validates `repaired=true`, then verifies DB metadata was corrected. Delete-count tests compare pending-delete count keys against the number of local IDs in delete transaction tables for schema 2 and schema 3 store implementations.

State and persistence behavior: tests directly mutate RocksDB metadata table values for block count, bytes used, pending delete count, and delete transaction rows. Inspector output is captured from its report logger as raw JSON. Repair mode writes corrected metadata values back to DB; inspect mode must not mutate DB. Container state and chunks directory file count are included in reports.

Dependencies and integration points: integrates container parsing, inspector plugin loading, log4j capture, Jackson JSON validation, schema-specific datanode store transaction tables, and inherited real container/chunk fixture generation.

Risks and test signals: strong signal for operational repair safety: disabled by default, inspect is read-only, repair is explicit. Exact JSON field assertions protect report contract but can be brittle for schema changes. The tests depend on global system properties and inspector load state, so cleanup is important.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueContainerMetadataInspector.java -->
