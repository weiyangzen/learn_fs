# subset-b-008002 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestBlockDeletingService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestBlockDeletingService.java

Purpose: This is the main regression suite for `BlockDeletingService` and `BlockDeletingTask` behavior across container layouts and schema versions. It builds real `KeyValueContainer` instances on temporary `MutableVolumeSet`s, writes chunk files through `FilePerBlockStrategy` or `FilePerChunkStrategy`, inserts pending-delete state into schema-v1 deleting block keys or schema-v2/v3 delete transaction tables, and then drives the background service manually.

Important APIs and types: The tests use `ContainerTestVersionInfo.ContainerTest`, `KeyValueContainerData`, `BlockData`, `DeletedBlocksTransaction`, `DatanodeStoreSchemaTwoImpl`, `DatanodeStoreSchemaThreeImpl`, `BlockIterator`, `KeyPrefixFilter`, `ContainerChecksumTreeManager`, `BlockDeletingServiceMetrics`, `ContainerMetrics`, and a `BlockDeletingServiceTestImpl` helper. Helper methods `createToDeleteBlocks`, `createPendingDeleteBlocksSchema1`, `createPendingDeleteBlocksViaTxn`, `createTxn`, `putChunksInBlock`, `updateMetaData`, `getUnderDeletionBlocksCount`, and `assertDeletionsInChecksumFile` define the test data model.

Control flow: Setup enables `CodecBuffer` leak detection, configures metadata and datanode directories, initializes a `MutableVolumeSet`, and creates DB instances when needed. Test fixtures create closed containers, write committed chunks, store blocks, increment pending-delete counters, and persist metadata. Individual tests start the service, wait for `isStarted`, invoke `runDeletingTasks` or `runPeriodicalTaskNow`, and use `GenericTestUtils.waitFor` to observe task counts or state changes.

State and persistence behavior: The suite validates DB table state before and after deletion, including block records, metadata keys for block count, bytes used, pending-delete count, pending-delete bytes, schema-v2 long transaction keys, schema-v3 container-prefixed transaction keys, in-memory `KeyValueContainerData` counters, chunk files, and checksum tree files. It specifically tests stale pending-delete metadata reset, unrecorded block IDs in delete transactions, deletion retry after on-disk block files were already removed, and recording deleted blocks in the Merkle checksum file.

Dependencies and integration points: It integrates the container service layer with `KeyValueHandler`, `OzoneContainer` mocks, `ContainerDispatcher`, `BlockUtils` DB handles, volume selection, chunk managers, checksum persistence, `DatanodeConfiguration`, container deletion choosing policies, and the background service framework. The tests intentionally vary `OZONE_BLOCK_DELETING_SERVICE_INTERVAL`, block deletion limit, container limit, and max lock holding time.

Risks: These tests are timing-sensitive and rely on background task counters, waits, and log capture. They assume all containers are key-value containers and that schema-specific table semantics remain stable. Some paths skip schema-v1 or only assert schema-v2/v3 behavior. Tests that use random IDs and files depend on cleanup and DB cache shutdown to avoid cross-test leakage.

Test signals: Strong signals include exact DB record counts, pending-delete counters reaching zero, bytes used dropping by expected block space, metrics deltas, checksum-tree deleted flags, unrecorded chunk removal, service thread shutdown, timeout warning presence or absence, container throttle behavior, block throttle behavior, and lock-hold timeout log counts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestBlockDeletingService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestContainerCache.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestContainerCache.java

Purpose: This suite verifies `ContainerCache`, the singleton cache that opens and reuses container DB handles as `ReferenceCountedDB` instances. It focuses on eviction behavior, reference counting, concurrent opens, metrics, and recovery when the underlying RocksDB store has been closed.

Important APIs and types: The file uses `ContainerCache.getInstance`, `ContainerCache.clear`, `ContainerCache.getDB`, `ContainerCache.get`, `ContainerCacheMetrics`, `ReferenceCountedDB`, `DatanodeStoreSchemaTwoImpl`, and `VersionedDatanodeFeatures.SchemaV2.chooseSchemaVersion`. `createContainerDB` pre-creates schema-v2 container stores and stops them so the cache can reopen them.

Control flow: `testContainerCacheEviction` creates four DB directories with cache size two, opens repeated references to the same DB, closes selected references, adds more entries, and verifies that referenced entries are not evicted while zero-reference entries are eligible. `testConcurrentDBGet` submits two concurrent `getDB` calls against one path, then closes all references and cleans up. `testUnderlyingDBzIsClosed` manually closes the inner store and expects a later `getDB` to return a new wrapper, while subsequent gets share that new wrapper.

State and persistence behavior: The persistent object under test is an on-disk RocksDB directory. Runtime state is the cache map plus the reference counts. The tests verify cache size, object identity, reference count increments/decrements, cleanup, and the distinction between cached wrapper liveness and underlying store liveness.

Dependencies and integration points: It uses the Ozone container cache configuration key `OZONE_CONTAINER_CACHE_SIZE`, schema-v2 store implementation, Apache commons file cleanup, Java executors, and cache metrics. It does not drive higher-level container operations; it isolates DB handle lifecycle.

Risks: The cache is singleton state, so failure to clear it can contaminate later tests. The concurrent test verifies no exception and final cache size, but does not assert precise reference counts from both worker threads until the final manual cleanup. The eviction test intentionally triggers an `IllegalArgumentException` through over-close behavior, so semantics of `ReferenceCountedDB.close` are part of the signal.

Test signals: Key assertions are cache misses and get-operation counts, stable object identity for repeated live handles, eviction exclusion for referenced entries, null or non-null cache lookups, new handle creation after inner DB close, and cache cleanup leaving no stale state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestContainerCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestContainerLayoutVersion.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestContainerLayoutVersion.java

Purpose: This compact test locks down the public enum-like contract of `ContainerLayoutVersion`. It verifies the currently supported layout count and the numeric IDs used by file-per-chunk and file-per-block layouts.

Important APIs and types: It imports `ContainerLayoutVersion`, `FILE_PER_CHUNK`, and `FILE_PER_BLOCK`. The tests call `ContainerLayoutVersion.getAllVersions()`, `getVersion()` on each constant, and JUnit `assertEquals`.

Control flow: The suite has three independent tests: `testVersionCount` asserts two known layout versions, `testV1` asserts `FILE_PER_CHUNK` has version 1, and `testV2` asserts `FILE_PER_BLOCK` has version 2.

State and persistence behavior: There is no filesystem or DB persistence. The only state is static layout metadata compiled into `ContainerLayoutVersion`.

Dependencies and integration points: These constants are used by chunk managers, container persistence, deletion service tests, YAML persistence, and parameterized layout tests elsewhere in this subset. This file provides a fast compatibility guard for serialization and upgrade-sensitive numeric layout IDs.

Risks: The version-count assertion must be updated deliberately if a new layout is added. A new layout addition would fail this test even if backward compatibility is preserved, which is useful as a prompt to update broader tests.

Test signals: Exact numeric equality for version count and per-layout IDs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestContainerLayoutVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestDatanodeLayOutVersion.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestDatanodeLayOutVersion.java

Purpose: This test verifies the visible contract of `HDDSVolumeLayoutVersion`, specifically the latest datanode volume layout version and its description string.

Important APIs and types: It calls `HDDSVolumeLayoutVersion.getLatestVersion()`, `getVersion()`, `getDescription()`, and `getAllVersions()`.

Control flow: A single JUnit test asserts latest version `1`, description `HDDS Datanode LayOut Version 1`, and performs a trivial equality assertion on the length returned by `getAllVersions()`.

State and persistence behavior: There is no persistence. The test protects static version metadata that is later written into datanode volume VERSION files and read by storage utility code.

Dependencies and integration points: It indirectly supports `DatanodeVersionFile`, `StorageVolumeUtil`, and volume formatting/read validation. The naming preserves the existing "LayOut" capitalization from the production class.

Risks: The final assertion comparing `getAllVersions().length` to itself has no behavioral value. If a new datanode layout is introduced, the latest-version and description assertions must change intentionally.

Test signals: Exact latest version and description values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestDatanodeLayOutVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestDatanodeStateMachine.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestDatanodeStateMachine.java

Purpose: This suite validates datanode state machine startup, INIT-to-RUNNING transitions, SCM endpoint RPC sequencing, failure-to-write ID handling, invalid SCM configuration handling, daemon stop, and thread priority ordering.

Important APIs and types: It uses `DatanodeStateMachine`, `DatanodeStateMachine.DatanodeStates`, `InitDatanodeState`, `RunningDatanodeState`, `EndpointStateMachine`, `SCMConnectionManager`, `ScmTestMock`, `SCMTestUtils`, `DatanodeLayoutStorage`, `HDDSLayoutFeature`, `ContainerUtils.writeDatanodeDetailsTo`, `CapacityVolumeChoosingPolicy`, Hadoop `RPC.Server`, and executor services from `HadoopExecutors`.

Control flow: `setUp` creates an Ozone config rooted in a temp directory, enables random IPC and Ratis ports, starts one mock SCM RPC server, and prepares a daemon executor. `testStartStopDatanodeStateMachine` starts the daemon, waits until one SCM connection is registered, then stops it. `testDatanodeStateContext` manually executes INIT and RUNNING tasks, verifies endpoint states moving through GETVERSION, REGISTER, and heartbeat paths, and checks mock RPC counts. Failure tests set the datanode ID directory read-only or provide malformed SCM names and expect SHUTDOWN. The priority test waits for command-processing thread creation and checks priority ordering.

State and persistence behavior: It writes a datanode ID file for the context test and initializes datanode layout storage before running SCM version negotiation. Runtime state includes state-machine context state, endpoint state, stored SCM version responses, RPC counts, and daemon thread lifecycle.

Dependencies and integration points: The tests integrate local RPC servers, datanode identity persistence, SCM connection manager, endpoint task scheduling, layout storage, volume choosing policy configuration, and thread management. They exercise real `DatanodeStateMachine` behavior rather than only mocks.

Risks: Timing is a key risk because waits depend on RPC server startup, endpoint transitions, and threads. File permission behavior for read-only directories can vary by environment. Invalid configuration coverage is table-driven but limited to selected malformed `OZONE_SCM_NAMES` strings.

Test signals: Strong signals include one connection manager entry, daemon stopped flag, expected INIT/RUNNING/SHUTDOWN states, endpoint GETVERSION and REGISTER states, non-null version response, exact mock RPC and heartbeat counts, default `CapacityVolumeChoosingPolicy`, and state-machine thread priority greater than command-processing thread priority.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestDatanodeStateMachine.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestDatanodeStoreCache.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestDatanodeStoreCache.java

Purpose: This test verifies basic operations of `DatanodeStoreCache`, a singleton cache for raw datanode DB stores used by schema-v3/shared DB paths.

Important APIs and types: The test uses `DatanodeStoreCache.getInstance`, `addDB`, `getDB`, `removeDB`, `shutdownCache`, `size`, `RawDB`, and `DatanodeStoreSchemaThreeImpl`.

Control flow: It creates two temporary DB directories, constructs two schema-v3 stores, adds both to the cache, verifies duplicate add does not increase size, gets one path back and checks it references the same underlying store object, removes one DB, tolerates removing a non-existent DB, and finally shuts down the cache.

State and persistence behavior: Persistent state is two created schema-v3 DB directories. Runtime cache state is the key-to-`RawDB` map. The test checks object identity with `assertSame` to ensure cached stores are reused rather than reopened.

Dependencies and integration points: It uses `OzoneConfiguration`, temp directories, schema-v3 metadata store implementation, and the raw DB wrapper used by container metadata code. It complements the more elaborate `ContainerCache` tests for per-container DB handles.

Risks: Because the cache is singleton state, `shutdownCache` is important for isolation. The test covers add/get/remove/shutdown but not concurrent access or closed-store recovery.

Test signals: Cache sizes 2, 2 after duplicate add, 1 after remove, and 0 after shutdown, plus same-object retrieval for `store1`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestDatanodeStoreCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestKeyValueContainerData.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestKeyValueContainerData.java

Purpose: This suite verifies `KeyValueContainerData` defaults, mutators, statistics, copy-constructor behavior, schema selection, replica index, pending-delete accounting, and data checksum state.

Important APIs and types: It uses `ContainerTestVersionInfo.ContainerTest`, `KeyValueContainerData`, `ContainerData.Statistics`, `ContainerLayoutVersion`, `ContainerProtos.ContainerDataProto.State`, mocked `HddsVolume`, `VersionedDatanodeFeatures.SchemaV3.chooseSchemaVersion`, and `StorageUnit.GB`.

Control flow: `initVersionInfo` sets the parameterized layout and schema into a fresh `OzoneConfiguration`. `testKeyValueData` constructs a container data object, verifies defaults, mutates state and paths, updates read/write/block stats, increments pending deletes, sets schema version and data checksum, then verifies the copy constructor resets volatile deletion counters while preserving replica index and schema. `testNeedsDataChecksum` checks the distinction between missing checksum and an explicitly set checksum value, including zero.

State and persistence behavior: There is no on-disk persistence in this test. It verifies in-memory metadata, statistics counters, pending-delete counters, delete transaction ID, replica index, origin IDs, schema version, and checksum sentinel behavior. The checksum test is important because `0` can mean either "not generated yet" or "generated hash is zero" depending on whether the setter has been called.

Dependencies and integration points: The class is a core data carrier for YAML persistence, block deletion metadata, container reports, schema-aware DB access, and checksum tree management. Parameterized execution gives coverage for all container layout/schema combinations exposed by `ContainerTestVersionInfo`.

Risks: The copy-constructor behavior intentionally does not preserve pending deletion counters and transaction ID; downstream code relying on copied objects must account for that. The test uses a mocked volume, so committed-space side effects are covered elsewhere.

Test signals: Exact defaults, statistic assertions, pending-delete counters, schema and checksum values, copy-constructor reset of pending deletion state, `needsDataChecksum` transitions, and negative checksum rejection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestKeyValueContainerData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestSchemaOneBackwardsCompatibility.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestSchemaOneBackwardsCompatibility.java

Purpose: This suite validates that schema-v1 RocksDB containers from test resources can be read and processed after upgrading to schema-v2 or schema-v3 code. It protects compatibility for the legacy single/default column-family encoding where metadata, regular blocks, deleting blocks, and deleted blocks coexist under prefixed keys.

Important APIs and types: It uses `ContainerDataYaml`, `KeyValueContainerUtil.parseKVContainerData`, `SchemaOneDeletedBlocksTable`, `BlockUtils.getDB`, `DatanodeStore` tables, `BlockIterator`, `BlockDeletingServiceTestImpl`, `KeyValueHandler`, `ContainerSet`, `MutableVolumeSet`, and a nested `TestDB` descriptor for the resource DB and `.container` file. The parameter source runs each test with target schema versions v2 and v3.

Control flow: `setup` copies the resource DB and container file into a temp folder, points metadata configuration at that folder, and prepares paths for mutation. `newKvData` reads the container file, fills temp-specific metadata/chunk paths, recomputes the container-file checksum, and parses DB metadata. Tests forbid direct table iteration, count regular/deleting/deleted blocks, read with and without metadata keys, run the block deleting service against pending v1 deleting keys, inspect deleted block chunk-info compatibility, and verify key decoding through tables and iterators.

State and persistence behavior: The persistent state is a copied legacy RocksDB directory plus `.container` YAML. Tests modify this copy by deleting metadata keys or running deletion. They verify metadata repair from scanning, key prefix removal on reads, deleted-block records whose old values cannot be decoded as `ChunkInfoList`, deleting-block records with `#deleting#` prefixes, and post-delete block counts. The block deleting path moves pending delete blocks into deleted-block state and updates metadata.

Dependencies and integration points: It integrates legacy DB codecs, table wrappers, block iterators, YAML checksums, key-value container parsing, deletion service, and schema upgrade selection. The suite is a compatibility anchor for upgrade and rollback behavior.

Risks: Resource DB contents are fixed and small, so coverage is representative rather than exhaustive. The deleting-service assertions account for mocked handler limitations around bytes-used updates. Direct table iteration being unsupported is an intentional schema-v1 guard and could break callers that assume all `Table` implementations are iterable.

Test signals: Unsupported direct iterators, exact counts for two deleted, two deleting, and two regular blocks, metadata values `KEY_COUNT`, `BYTES_USED`, and pending deletes, decoded key lists matching resource IDs, absence of visible deleted-key prefixes, successful metadata reconstruction after deleting keys, and deletion service reducing pending state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestSchemaOneBackwardsCompatibility.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestSchemaTwoBackwardsCompatibility.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestSchemaTwoBackwardsCompatibility.java

Purpose: This suite verifies that containers created under schema-v2 remain readable and deletable after schema-v3 is enabled. It models the upgrade assumption that schema-v2 containers are closed before upgrade and must continue to use their original DB layout.

Important APIs and types: It uses `ContainerTestUtils.disableSchemaV3` and `enableSchemaV3`, `KeyValueContainerData` with `SCHEMA_V2`, `BlockManagerImpl`, `FilePerBlockStrategy`, `DatanodeStoreSchemaTwoImpl`, `DeletedBlocksTransaction`, `BlockDeletingServiceTestImpl`, `BlockIterator`, `KeyValueHandler`, and mocked `OzoneContainer`/`ContainerDispatcher`.

Control flow: Setup disables schema-v3, initializes a volume set, block manager, file-per-block chunk manager, container set, handler, and ozone-container mock. `createTestContainer` creates a schema-v2 container, writes six blocks with two chunks each, and inserts two delete transactions of two blocks each while updating metadata. Tests then enable schema-v3 before reading or deleting. They verify DB file placement, block iteration and chunk lengths, metadata reads, and deletion via transaction processing.

State and persistence behavior: The suite persists schema-v2 DB state below the container path, not the shared schema-v3 DB. It writes real chunk files and block records, stores delete transactions in the schema-v2 transaction table keyed by long transaction ID, and updates metadata keys for latest delete transaction and pending delete count. After deletion, it checks in-memory and DB metadata for block count, pending-delete count, and bytes used.

Dependencies and integration points: It exercises upgrade-aware `BlockUtils.getDB`, schema detection, transaction table decoding, block manager writes, chunk manager filesystem writes, metadata table reads, and deletion service execution after the global config switches to schema-v3.

Risks: The test relies on file-per-block layout and fixed constants, so it does not cover file-per-chunk schema-v2 upgrade behavior here. The helper uses `startBlockID = txnID * DELETE_TXNS_PER_CONTAINER`, which matches current constants but would need review if transaction sizing changes.

Test signals: Schema remains `SCHEMA_V2`, DB file parent path is the container ID, iterator returns six blocks with two 1024-byte chunks, metadata values match six blocks and four pending deletes, and deletion leaves two live blocks, zero pending deletes, and expected bytes used.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestSchemaTwoBackwardsCompatibility.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestStaleRecoveringContainerScrubbingService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestStaleRecoveringContainerScrubbingService.java

Purpose: This test verifies that `StaleRecoveringContainerScrubbingService` marks old RECOVERING containers UNHEALTHY while leaving CLOSED containers and non-stale RECOVERING containers unchanged.

Important APIs and types: It uses `StaleRecoveringContainerScrubbingService`, `ContainerSet`, `ContainerImplTestUtils.newContainerSet`, `TestClock`, `KeyValueContainerData`, `KeyValueContainer`, `HddsVolume`, `MutableVolumeSet`, `RoundRobinVolumeChoosingPolicy`, and `ContainerTestVersionInfo.ContainerTest`.

Control flow: `initVersionInfo` sets the active layout and schema, then `init` creates a formatted `HddsVolume` under a temp directory and mocks volume selection to return it. `createTestContainers` advances the test clock before each container, creates key-value containers in a requested state, persists them on the volume, and adds them to the container set. The main test creates closed containers, runs the scrubber, creates recovering containers, advances time beyond timeout, runs again, then increases the recovering timeout and proves newer recovering containers remain RECOVERING.

State and persistence behavior: The test persists actual container directories and uses `ContainerSet` creation timestamps driven by `TestClock`. State under test is container state transition from RECOVERING to UNHEALTHY based on age and timeout. It also exercises `ContainerSet.setRecoveringTimeout`.

Dependencies and integration points: It integrates container creation, volume formatting, clock-controlled container metadata, container set iteration, and the background scrubbing service's one-shot `runPeriodicalTaskNow` path. DB caches are shut down after each test.

Risks: The test depends on `newContainerSet(10, testClock)` honoring the injected clock. The service interval and timeout values are small and manually triggered, reducing but not eliminating timing coupling. It does not test service daemon start/stop.

Test signals: Container count remains unchanged, CLOSED containers remain CLOSED, stale RECOVERING containers become UNHEALTHY, and RECOVERING containers younger than the adjusted timeout remain RECOVERING.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestStaleRecoveringContainerScrubbingService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/helpers/TestBlockData.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/helpers/TestBlockData.java

Purpose: This helper test verifies `BlockData` chunk-list mutation, size accounting, `setChunks`, and string formatting for block identity.

Important APIs and types: It uses `BlockData`, `BlockID`, protobuf `ContainerProtos.ChunkInfo`, no-checksum data from `Checksum.getNoChecksumDataProto`, and JUnit assertions.

Control flow: `testAddAndRemove` starts with an empty `BlockData`, adds five random-length chunk protobufs while checking size and list equality after each add, then removes chunks in random order while rechecking. `testSetChunks` repeatedly replaces the full chunk list with an expanding expected list. `testToString` creates a `BlockID` with container ID, local ID, and BCS ID and checks the exact `BlockData.toString` output.

State and persistence behavior: There is no persistence. The state is the in-memory chunk list and derived block size. The tests ensure `BlockData.getSize()` is derived from current chunk lengths and remains consistent after remove and replace operations.

Dependencies and integration points: `BlockData` is persisted in RocksDB block tables, used by chunk managers, block manager reads/writes, and deletion service chunk cleanup. The exact string format is diagnostic but also a compatibility signal for logs and assertions.

Risks: Random chunk lengths and removal order should not affect determinism of expected comparisons, but they can make log output variable. Exact `toString` assertions are sensitive to formatting changes that may not affect behavior.

Test signals: Expected chunk list equality, sum-of-length size equality, empty-list handling, and exact string output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/helpers/TestBlockData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/helpers/TestContainerUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/helpers/TestContainerUtils.java

Purpose: This suite covers utility behavior in `ContainerUtils`: debug redaction, container tar-name round trips, datanode ID persistence and recovery, protobuf-to-YAML upgrade reads, malformed ID handling, IP validation behavior, and disk-space admission metrics around hard and soft spare-space limits.

Important APIs and types: It uses `ContainerUtils`, `DatanodeIdYaml` indirectly through read/write helpers, `DatanodeVersionFile`, `DatanodeDetails`, `MockDatanodeDetails`, `ContainerCommandRequestProto`, `ContainerCommandResponseProto`, `processForDebug`, `SpaceUsageSource.Fixed`, `HddsVolume`, `VolumeInfoMetrics`, and `StorageContainerException` with result `DISK_OUT_OF_SPACE`.

Control flow: Setup points metadata dirs at a temp directory. Redaction builds a read-chunk response containing known bytes and verifies the debug string keeps position while replacing data with the redacted string. ID persistence writes and reads `DatanodeDetails`, mocks DNS lookup to test persisted-vs-resolved IP handling, verifies cert serial and version fields, rejects missing and malformed files, and reads an older protobuf-format ID file. Recovery creates a VERSION file with a datanode UUID, creates an empty ID file, and expects `readDatanodeDetailsFrom` to reconstruct and rewrite it. Space tests mock volume free-space methods and metrics to cover soft-band, hard reject, equality boundaries, null metrics, zero-size writes, and disabled soft band.

State and persistence behavior: Persistent files include datanode ID YAML/protobuf files, malformed ID files, and VERSION files. Runtime state includes `DatanodeDetails` ports, IP validation, certificate serial ID, initial/current versions, and volume metrics counters. Disk-space tests do not use real disk state; they model available/capacity/used values through fixed usage objects and mocked spare-space methods.

Dependencies and integration points: These helpers are used during datanode startup, upgrade recovery, debugging logs, container archive naming, write-path disk admission, and metrics. The suite links configuration keys for metadata and datanode directories with storage volume VERSION recovery.

Risks: Mocked static DNS behavior must be scoped carefully. The recovery test assumes a specific `hdds/VERSION` layout under `HDDS_DATANODE_DIR_KEY`. Space admission tests encode strict less-than boundary semantics, so any intentional policy change must update several assertions.

Test signals: Redacted debug string position, tar name ID recovery, full datanode details equality including protobuf form, malformed/missing file exceptions, recovered UUID and rewritten ID file, `DISK_OUT_OF_SPACE` result on hard reject, correct metric increment paths, no null-metrics NPE, and no metric for zero-sized or exact-soft-boundary writes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/helpers/TestContainerUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/helpers/TestDatanodeIdYaml.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/helpers/TestDatanodeIdYaml.java

Purpose: This suite verifies YAML serialization and deserialization of `DatanodeDetails`, especially layout-version-gated port compatibility for Ratis datastream and web UI ports.

Important APIs and types: It uses `DatanodeIdYaml.createDatanodeIdFile`, `DatanodeIdYaml.readDatanodeIdFile`, `MockDatanodeDetails.randomDatanodeDetails`, `DatanodeLayoutStorage`, `HDDSLayoutFeature`, `DatanodeDetails.Port.Name`, and `OzoneConfiguration`.

Control flow: `testWriteRead` writes random datanode details to `datanode.yaml` and checks object equality and debug string equality. Two Ratis datastream tests initialize layout storage before or after `RATIS_DATASTREAM_PORT_IN_DATANODEDETAILS` and verify fallback-to-Ratis-port or preservation of the separate datastream port. Two web UI tests initialize layout storage before or after `WEBUI_PORTS_IN_DATANODEDETAILS` and verify HTTP/HTTPS omission or preservation.

State and persistence behavior: The tests persist YAML ID files and layout storage state under a temp metadata directory. The read path changes output depending on persisted layout version, not only YAML content. This protects upgrade compatibility where older layout versions did not persist newer ports.

Dependencies and integration points: Datanode startup and identity recovery depend on these files. The tests integrate identity serialization with datanode layout storage and HDDS upgrade features.

Risks: Random datanode details include several port values, so assertions focus on compatibility-sensitive ports. Behavior before layout features intentionally discards or aliases newer ports, which can surprise code expecting all random details to round-trip exactly.

Test signals: Full equality for normal read/write, datastream port fallback before its layout feature, exact datastream preservation after the feature, HTTP/HTTPS null before web UI feature, and exact HTTP/HTTPS preservation after the feature.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/helpers/TestDatanodeIdYaml.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/helpers/TestDatanodeVersionFile.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/helpers/TestDatanodeVersionFile.java

Purpose: This suite verifies creation, reading, and validation of datanode volume VERSION files through `DatanodeVersionFile` and `StorageVolumeUtil`.

Important APIs and types: It uses `DatanodeVersionFile`, `DatanodeVersionFile.readFrom`, `StorageVolumeUtil.getStorageID`, `getClusterID`, `getDatanodeUUID`, `getCreationTime`, `getLayOutVersion`, `HDDSVolumeLayoutVersion.getLatestVersion`, and `InconsistentStorageStateException`.

Control flow: `setup` creates a VERSION file in a temp folder with random storage ID, cluster ID, datanode UUID, current creation time, and latest layout version, then reads properties back. `testCreateAndReadVersionFile` verifies all fields. Negative tests rewrite invalid values or pass a mismatched expected cluster ID and assert validation exceptions with expected message fragments.

State and persistence behavior: The persistent artifact is a Java properties VERSION file. The tests validate that IDs, creation time, and layout version survive round trip and that invalid/mismatched fields are rejected by storage utilities rather than silently accepted.

Dependencies and integration points: VERSION files are consumed by volume formatting, datanode startup, ID recovery, and storage consistency checks. This file complements `TestDatanodeLayOutVersion` by checking the layout version in persisted form.

Risks: Exact error-message fragments are asserted, so wording changes in validation exceptions can fail tests. The invalid layout version `100` assumes the version registry remains below that value.

Test signals: File existence, exact property round trip, mismatched cluster ID exception, negative creation time exception, and invalid layout version exception.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/helpers/TestDatanodeVersionFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/ContainerImplTestUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/ContainerImplTestUtils.java

Purpose: This is a small test utility class for constructing `ContainerSet` instances backed by mocked `WitnessedContainerMetadataStore` objects. It is not itself a JUnit test but is used throughout this subset to avoid setting up a full metadata store.

Important APIs and types: It exposes `newContainerSet()`, `newContainerSet(long recoveringTimeout)`, `newContainerSet(long recoveringTimeout, WitnessedContainerMetadataStore)`, and `newContainerSet(long recoveringTimeout, Clock)`. It uses Mockito, `InMemoryTestTable`, `WitnessedContainerMetadataStore`, and `ContainerSet`.

Control flow: Default overloads create a mock metadata store, stub `getContainerCreateInfoTable()` to return an in-memory test table, and delegate to either `ContainerSet.newRwContainerSet` or the `ContainerSet` constructor with an injected `Clock`.

State and persistence behavior: No real persistence is used. The in-memory table stands in for container creation metadata, and the provided recovering timeout and optional clock configure runtime container-set behavior.

Dependencies and integration points: `TestBlockDeletingService`, schema compatibility tests, deletion choosing policy tests, stale recovering scrubbing tests, and persistence tests all rely on this helper to construct isolated container sets. The clock overload is important for deterministic stale-recovery tests.

Risks: Because the metadata store is mocked, tests using this helper may not catch bugs in the real witnessed metadata store. The helper must stay aligned with `ContainerSet` constructor and factory signatures.

Test signals: As a helper, its signal comes from downstream tests successfully adding, listing, and timing containers against the returned `ContainerSet`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/ContainerImplTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestContainerDataYaml.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestContainerDataYaml.java

Purpose: This suite verifies `.container` YAML creation and reading for `KeyValueContainerData`, backward-compatible parsing of files with additional fields, checksum verification, optional replica-index persistence, and exclusion of data checksum from the container file.

Important APIs and types: It uses `ContainerDataYaml.createContainerFile`, `readContainerFile`, `getYamlForContainerType`, `ContainerUtils.verifyContainerFileChecksum`, `KeyValueContainerData`, `ContainerLayoutTestInfo.ContainerTest`, `VersionedDatanodeFeatures.SchemaV2`, `ContainerLayoutVersion`, and resource files `incorrect.container`, `additionalfields.container`, and `incorrect.checksum.container`.

Control flow: `createContainerFile` builds a key-value container data object, sets DB type, paths, scan time, schema v2, replica index, and a data checksum, then writes YAML. `testCreateContainerFile` reads it back, checks all fields, updates metadata and state, rewrites, and rechecks. Other tests verify zero replica index is omitted from YAML, malformed enum data throws, additional unknown fields remain readable, container-file checksum validates, data checksum is not persisted in `.container`, checksum with replica index validates, incorrect checksum is detected, and checksum verification can be disabled by config.

State and persistence behavior: The persistent artifact is the `.container` YAML file. The tests distinguish container-file checksum from data checksum: file checksum is persisted and verified, while container data checksum lives elsewhere and should read as zero from YAML. Scan timestamps, state, metadata, paths, layout, schema, and replica index are persisted as appropriate.

Dependencies and integration points: This is central to container load, upgrade, rollback, checksum validation, and YAML compatibility. It integrates config-controlled checksum verification and layout-parameterized serialization.

Risks: Resource files encode compatibility expectations and must be maintained when YAML schema changes. Exact omission of `replicaIndex` when zero is a wire-format contract. The test recalculates paths in temp directories, so checksum behavior must account for path-sensitive fields.

Test signals: Field round trips, metadata update persistence, absence of `replicaIndex` for zero, `No enum constant` on bad enum, successful read of additional fields, checksum validation success/failure, disabled-checksum pass, and data checksum reading as zero from the container file.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestContainerDataYaml.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestContainerDeletionChoosingPolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestContainerDeletionChoosingPolicy.java

Purpose: This suite verifies container selection policies used by block deletion: random ordering, top-N ordering by pending delete blocks, and allowed container states for deletion.

Important APIs and types: It uses `BlockDeletingService.chooseContainerForBlockDeletion`, `BlockDeletingService.ContainerBlockInfo`, `RandomContainerDeletionChoosingPolicy`, `TopNOrderedContainerDeletionChoosingPolicy`, `ContainerDeletionChoosingPolicy`, `KeyValueContainerData`, `KeyValueContainer`, and `ContainerLayoutTestInfo.ContainerTest`.

Control flow: Each test configures the policy class, creates a `ContainerSet` via `newContainerSet`, populates `KeyValueContainerData` objects with pending delete counts and states, builds a mocked `OzoneContainer`, and invokes `chooseContainerForBlockDeletion`. The random policy test repeats selection up to 100 times and expects at least one shuffled order. The allowed-state test verifies CLOSED and QUASI_CLOSED are selected but OPEN and CLOSING are not. The top-N test creates containers with random pending counts plus one empty container, checks enough blocks are selected to satisfy a limit, and verifies descending order of pending counts.

State and persistence behavior: No real DB or chunk persistence is used. The state under test is in-memory container metadata: pending deletion block count, container state, and container map membership.

Dependencies and integration points: These policies feed `BlockDeletingService` and therefore control deletion fairness and throughput. The test integrates policy implementations with the service's selection layer and config key `OZONE_SCM_KEY_VALUE_CONTAINER_DELETION_CHOOSING_POLICY`.

Risks: The random test is probabilistic; it fails if two independently shuffled selections match for 100 attempts. Top-N uses random pending counts but derives expected order dynamically. The service object is built with mocked write channel and checksum manager, so only selection is covered.

Test signals: Total selected pending blocks meets or exceeds the limit, random ordering differs at least once, selected IDs include allowed states and exclude disallowed states, empty containers are skipped, and top-N results are non-increasing by pending block count.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestContainerDeletionChoosingPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestContainerPersistence.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestContainerPersistence.java

Purpose: This broad integration test validates creation, deletion, listing, reporting, chunk I/O, block I/O, metadata update, committed-space accounting, schema-v3 shared DB cleanup, and block commit sequence ID checks for key-value containers across layout and schema combinations.

Important APIs and types: It uses `ContainerTestVersionInfo.ContainerTest`, `KeyValueContainer`, `KeyValueContainerData`, `ContainerSet`, `MutableVolumeSet`, `StorageVolumeUtil`, `HddsVolume`, `BlockManagerImpl`, `ChunkManagerFactory`, `ChunkManager`, `BlockUtils`, `KeyValueContainerUtil`, `ContainerDataYaml`, `DatanodeStoreSchemaThreeImpl`, `ContainerChecksumTreeManager`, `KeyValueHandler`, `DispatcherContext`, checksum helpers, and result codes `UNKNOWN_BCSID` and `BCSID_MISMATCH`.

Control flow: Static setup configures datanode and metadata directories. Per-test setup creates a container set, initializes volumes, checks volume formatting, creates managers, and ensures storage directories exist. `addContainer` constructs metadata, creates the container on a volume, adds it to the set, and asserts committed bytes increased by max container size. Tests then cover duplicate add rejection, adding blocks after deletion, non-force deletion of non-empty containers, schema-v3 DB row removal, deletion with renaming through the volume deleted-container directory, container reports, paginated list, single and many chunk writes/reads, overwrite, chunk delete, put/get block, invalid BCS ID errors, many-chunk block put/get, metadata update with and without force, and block listing.

State and persistence behavior: The suite uses real container directories, chunk files, `.container` YAML files, per-container DBs for earlier schemas, and shared schema-v3 DB tables. It verifies committed-space reservation on container create and decrement on writes, bytes/statistics updates, block table contents, metadata table cleanup for schema-v3 container deletion, deleted container directory contents, YAML metadata updates, and chunk checksum preservation.

Dependencies and integration points: It connects volume initialization, container lifecycle, chunk manager layout behavior, block manager DB behavior, container set indexing/reporting, handler delete semantics, filesystem rename/delete paths, checksum computation, and schema-aware DB cleanup. It is one of the strongest integration signals in the subset.

Risks: The tests manipulate static temp directories and delete them after each test, so cache shutdown and cleanup ordering matter. Some tests intentionally skip schema-v3 or require schema-v3 because DB topology differs. The committed-space tests encode exact reservation/decrement policy and must change if accounting policy changes.

Test signals: Container paths and DB files exist, duplicate add throws, deleted-container DB open fails for old schemas, non-empty non-force delete throws, schema-v3 block/metadata rows are present then absent, deleted directory contents shrink as containers are removed, reports and paginated listings cover all IDs, chunk read checksums match, delete chunk makes read fail, BCS ID errors return exact result codes, YAML metadata persists updates, force update works on closed containers, and block listing returns sorted ranges with positive-count validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestContainerPersistence.java -->
