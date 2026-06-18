# subset-b-008087 research

This grouped report covers the Apache Ozone OM snapshot integration tests assigned to `subset-b-008087`. Each section preserves the source path and is intended to be split into the matching source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshot.java -->
## sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshot.java

Purpose: `TestOmSnapshot` is the large abstract integration-test base for Ozone Manager snapshot behavior. Concrete subclasses run this same suite under different `BucketLayout`, native RocksDB diff, filesystem path, and linked-bucket configurations. It validates snapshot point-in-time reads, snapshot diff semantics, deletion and retention behavior, RocksDB checkpoint/diff internals, upgrade-finalization gating, stream APIs, multipart upload visibility, and bucket/link-specific name resolution.

Important APIs/types/functions: The suite drives public client APIs through `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `OzoneSnapshot`, `OzoneSnapshotDiff`, `OzoneOutputStream`, `OzoneDataStreamOutput`, multipart APIs, and snapshot APIs such as `createSnapshot`, `deleteSnapshot`, `getSnapshotInfo`, `listSnapshot`, `snapshotDiff`, `cancelSnapshotDiff`, and `listSnapshotDiffJobs`. It also directly exercises OM internals through `OzoneManagerProtocol`, `OzoneManager`, `OmSnapshotManager`, `SnapshotInfo`, `KeyManagerImpl`, `RDBStore`, `RocksDatabase`, `RocksDBCheckpointDiffer`, `SnapshotDiffCleanupService`, and snapshot metadata readers. Helpers such as `createSnapshot`, `getSnapDiffReport`, `fetchReportPage`, `createFileKey`, `createStreamKey`, `createStreamFile`, MPU completion helpers, `flushKeyTable`, and `getOmKeyInfo` define most control-flow scaffolding.

Control flow: Construction calls `init()`, configures a MiniOzoneCluster, enables snapshots, chooses bucket layout and diff mode, creates the baseline volume/bucket, stops key deletion services to preserve test data, asserts snapshot operations are rejected before OM layout finalization, then finalizes the OM upgrade. Individual tests create isolated volumes/buckets/keys, create one or more snapshots, mutate active namespace state, and compare point-in-time listing or diff output. Snapshot diff tests poll until `SnapshotDiffResponse.JobStatus.DONE`, with explicit coverage for `IN_PROGRESS`, `CANCELLED`, invalid paging tokens, restart recovery, partial report pagination, and cancel cleanup. Tests that are too expensive or mode-specific use `assumeCanonicalConfig` or `assumeTrue` to run only under a relevant subclass.

State and persistence behavior: The suite waits for snapshot checkpoint directories under `OmSnapshotManager.getSnapshotPath(...)/CURRENT`, checks snapshot rows in the snapshot info table, validates that deleted snapshots eventually disappear when deletion services run, and verifies snapshot reads continue after active keys are deleted. It intentionally stops and restarts `KeyManagerImpl` to control asynchronous key/snapshot deletion timing. RocksDB state is inspected through live SST metadata, flushes, compaction listeners, compaction DAG contents, compaction log table rows, backup SST pruning, and snapshot DB options. Quota tests assert snapshot creation/deletion does not change volume or bucket namespace/byte consumption, while bucket deletion tests assert `CONTAINS_SNAPSHOT` prevents deleting a bucket with snapshots.

Dependencies and integration points: The tests depend on MiniOzoneCluster, OM metadata manager tables, RocksDB native tooling when native diff is enabled, Hadoop `FileSystem`/`OzoneFileSystem` for filesystem path coverage, Ozone ACL/object-tag APIs, OM upgrade finalization, snapshot deletion and cleanup services, and bucket layout resolution including linked buckets. They also touch feature flags such as `OZONE_FILESYSTEM_SNAPSHOT_ENABLED_KEY`, `OZONE_OM_SNAPSHOT_FORCE_FULL_DIFF`, `OZONE_OM_SNAPSHOT_DIFF_DISABLE_NATIVE_LIBS`, snapshot deleting intervals, SST filtering, snapshot cache cleanup, and compaction DAG pruning.

Risks and edge cases: The file is high-blast-radius because subclasses multiply the same test set across configurations. Timing risks appear wherever tests wait for async OM DB updates, checkpoint creation, deletion service passes, compaction pruning, or diff job completion. Linked bucket tests require careful source-bucket mapping; many assertions compare the source bucket name rather than the link name. Native diff tests can be skipped if RocksDB tooling is unavailable. Restart tests accept both `DONE` and fresh `IN_PROGRESS` after cleanup, reflecting possible job recovery races. Stream and MPU tests guard that invisible operations, partial uploads, aborts, metadata/tag modifications, replication changes, and overwrites produce the intended create/modify/delete/no-op diff entries.

Test signals: Key signals include exact `SnapshotDiffReport` entry lists for create/delete/rename/modify, empty diffs for no-op or invisible MPU lifecycle states, expected `OMException.ResultCodes` for invalid inputs, `CANCEL_*` messages for cancellation paths, snapshot checkpoint existence, no tracked non-target column families in the compaction DAG, snapshot DB auto-compaction and listener settings, preserved snapshot data after active deletion, successful snapshot reads through snapshot prefixes, and snapshot name reuse after purge.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotDisabled.java -->
## sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotDisabled.java

Purpose: This integration test verifies that snapshot RPCs are rejected when the filesystem snapshot feature flag is disabled. It focuses on the externally visible error contract for create and delete operations.

Important APIs/types/functions: The class uses `MiniOzoneHAClusterImpl`, `OzoneConfiguration`, `ObjectStore`, `OzoneClient`, `OzoneVolume`, `BucketLayout.LEGACY`, `OMConfigKeys.OZONE_FILESYSTEM_SNAPSHOT_ENABLED_KEY`, and `OMException.ResultCodes.FEATURE_NOT_ENABLED`. The only test method is `testExceptionThrown`; lifecycle methods are `init` and `tearDown`.

Control flow: `init` sets default bucket layout to legacy, sets DB profile to test, disables `OZONE_FILESYSTEM_SNAPSHOT_ENABLED_KEY`, builds a three-OM HA cluster, waits for readiness, and obtains an object-store client. The test creates a volume and bucket, then calls `store.createSnapshot` and `store.deleteSnapshot`, asserting each throws `OMException` with `FEATURE_NOT_ENABLED`.

State and persistence behavior: The test intentionally creates no snapshot state. Its state transition is negative: OM must reject snapshot mutations before any snapshot metadata or checkpoint can be created. Because it runs in HA mode, the feature-disabled path is checked through the same client-to-OM routing used in replicated deployments.

Dependencies and integration points: This test integrates with OM configuration parsing, snapshot request validation, client-side object-store RPCs, and HA MiniOzone startup. It also depends on DB test profile and legacy bucket layout to minimize unrelated layout complexity.

Risks and edge cases: The critical risk is accidentally allowing one snapshot operation while blocking another, or throwing a generic validation error instead of `FEATURE_NOT_ENABLED`. Since only create/delete are covered, list/diff/get-info behavior is covered by broader suites rather than here.

Test signals: Passing signal is exact exception result-code equality for both create and delete snapshot RPCs under a disabled feature flag.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotDisabled.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotDisabledRestart.java -->
## sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotDisabledRestart.java

Purpose: This unhealthy-marked integration test verifies startup protection when snapshot support is disabled after snapshots already exist. It asserts that an OM refuses to restart with the feature disabled while snapshot metadata remains.

Important APIs/types/functions: The class uses `MiniOzoneHAClusterImpl`, `ObjectStore`, `OzoneVolume`, `OZONE_FILESYSTEM_SNAPSHOT_ENABLED_KEY`, `cluster.shutdownOzoneManager`, `cluster.restartOzoneManager`, and AssertJ/JUnit assertions. The test is tagged `@Unhealthy("HDDS-8945")`.

Control flow: Setup enables snapshots and starts a three-node HA OM cluster. The test creates a volume, bucket, and snapshot. It then iterates over every OM, shuts the OM down, flips that OM configuration to disable snapshots, asserts restart fails with a `RuntimeException` containing `snapshots remaining`, re-enables the feature, and restarts successfully.

State and persistence behavior: The persistent state under test is pre-existing snapshot metadata and checkpoint state in OM DB. The test ensures configuration downgrade does not silently strand snapshots or boot into a mode unable to manage them. It validates both failure and recovery startup paths for each OM process.

Dependencies and integration points: This test integrates OM startup validation with snapshot metadata discovery, HA node lifecycle management, per-OM runtime configuration mutation, and existing snapshot state produced through public `ObjectStore` APIs.

Risks and edge cases: The test mutates OM configuration while cycling all HA nodes, so it is sensitive to leader election and restart timing. The asserted message is substring-based, so a behavior-preserving wording change around startup failure can still matter. The unhealthy tag indicates known instability or tracked issue context.

Test signals: A correct implementation throws on restart with disabled snapshots and remaining snapshot state, includes `snapshots remaining` in the failure, and restarts cleanly after the feature is enabled again.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotDisabledRestart.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotFileSystem.java -->
## sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotFileSystem.java

Purpose: `TestOmSnapshotFileSystem` is an abstract filesystem-facing snapshot test base. It verifies that Ozone snapshot prefixes work through `OzoneFileSystem` and object-store listings, especially for directory listing, file status, file reads, large paged directories, deleted snapshot access, and linked bucket/source bucket name handling.

Important APIs/types/functions: It uses `NonHATests.TestCase`, `OzoneFileSystem`, Hadoop `FileSystem`, `FileStatus`, `Path`, `ContractTestUtils`, `ObjectStore`, `OzoneBucket`, `OzoneManagerProtocol`, `SnapshotInfo`, `OmSnapshotManager`, `OpenKeySession`, and `OmKeyArgs`. Important helpers include `setupFsClient`, `deleteRootDir`, `createSnapshot`, `deleteSnapshot`, `createAndCommitKey`, `createKey`, `readkey`, `verifyFullTreeStructure`, and `checkKeyList`.

Control flow: `setupFsClient` temporarily enables filesystem paths on the OM, creates a test bucket with the configured layout and optional linked bucket, initializes the O3FS URI as `o3fs://bucket.volume/`, and lowers `OZONE_FS_ITERATE_BATCH_SIZE` to exercise pagination. Each test creates active filesystem or object-store keys, creates a snapshot through the OM protocol, waits for checkpoint creation, often deletes active root content, then lists or reads the snapshot path. `deleteRootDir` runs after each test to remove active namespace children.

State and persistence behavior: Snapshot state is represented as paths prefixed by `/<.snapshot/...>` from `OmSnapshotManager.getSnapshotPrefix`, with physical checkpoint existence verified via `getSnapshotPath(...)/CURRENT`. Tests validate snapshot data remains readable after active data deletion, and that once `deleteSnapshot` is called the same snapshot paths fail with `FileNotFoundException` or `OMException` indicating the snapshot is no longer active. The suite also checks file metadata such as modification time is preserved between active and snapshot views.

Dependencies and integration points: This file connects OM snapshot checkpoints to the Hadoop filesystem adapter, object-store `listKeys`, OM key open/commit internals, linked bucket source-name resolution, FS default URI configuration, and client-side exception translation. It also covers path listing behavior influenced by `LISTING_PAGE_SIZE` and `OZONE_FS_ITERATE_BATCH_SIZE`.

Risks and edge cases: Snapshot filesystem reads depend on consistent path construction and exception mapping across Ozone client layers. Large directory listing tests are sensitive to pagination, duplicates, ordering, and immediate-child semantics. Linked buckets require expected error table keys to use the source bucket. The test modifies global OM config and restores it in `tearDown`, so cleanup correctness matters for surrounding tests.

Test signals: Signals include exact tree-ordered key lists, immediate-child counts from `listStatus`, correct handling of intermediate directories, successful `getFileStatus` for directories and files inside snapshots, byte-for-byte file reads from snapshots, large-directory result counts beyond one page, and expected failures after snapshot deletion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotFsoWithNativeLib.java -->
## sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotFsoWithNativeLib.java

Purpose: This concrete subclass runs the shared `TestOmSnapshot` suite for file-system-optimized buckets with RocksDB native diff tooling enabled. It is the native-diff FSO matrix entry.

Important APIs/types/functions: The class extends `TestOmSnapshot`, uses `BucketLayout.FILE_SYSTEM_OPTIMIZED`, and is gated by `@EnabledIfSystemProperty(named = ROCKS_TOOLS_NATIVE_PROPERTY, matches = "true")`. Its constructor calls `super(FILE_SYSTEM_OPTIMIZED, false, false, false, false)`.

Control flow: JUnit only instantiates this class when the native tools system property is true. Construction delegates all setup and tests to `TestOmSnapshot`, with filesystem paths disabled, full diff disabled, native diff enabled, and linked bucket creation disabled.

State and persistence behavior: The state behavior comes from the inherited suite: FSO directory/file tables, snapshot checkpoint creation, native RocksDB checkpoint differ and compaction DAG behavior, and snapshot diff outputs across FSO namespace mutations.

Dependencies and integration points: This subclass depends on native RocksDB tools availability and the shared MiniOzone setup in `TestOmSnapshot`. It is the canonical class for native-only heavyweight tests such as compaction DAG coverage when `assumeCanonicalConfig(true)` is used.

Risks and edge cases: If the system property is not set, this matrix entry does not run. If native libraries fail to load after the property gate, inherited assumptions skip native-dependent paths. The subclass itself is intentionally minimal, so constructor argument drift would silently change a large inherited test surface.

Test signals: Passing signals are inherited from `TestOmSnapshot`, especially native diff and compaction DAG assertions under FSO layout.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotFsoWithNativeLib.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotFsoWithoutNativeLib.java -->
## sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotFsoWithoutNativeLib.java

Purpose: This concrete subclass runs the shared snapshot suite for file-system-optimized buckets while forcing native snapshot diff libraries off. It validates the fallback/full-Java diff path for FSO buckets.

Important APIs/types/functions: The class extends `TestOmSnapshot`, uses `BucketLayout.FILE_SYSTEM_OPTIMIZED`, and calls `super(FILE_SYSTEM_OPTIMIZED, false, false, true, false)`.

Control flow: Construction delegates to the abstract base with filesystem paths disabled, force-full-diff disabled, `disableNativeDiff` true, and linked bucket creation disabled. The inherited suite then skips native-only assumptions and exercises fallback snapshot diff behavior.

State and persistence behavior: The inherited tests cover FSO file/directory table checkpoint state, snapshot reads, deletion, restart, stream file/key operations, MPU diff behavior, and snapshot reuse without native RocksDB diff acceleration.

Dependencies and integration points: This subclass integrates the inherited snapshot suite with the `OZONE_OM_SNAPSHOT_DIFF_DISABLE_NATIVE_LIBS` configuration. It is also the canonical non-native FSO entry for heavy tests guarded by `assumeCanonicalConfig(false)`.

Risks and edge cases: Because this mode bypasses native diff, result ordering and performance-sensitive paths can diverge from the native implementation. The subclass is constructor-only, so the main maintenance risk is accidental argument mismatch against the intended matrix.

Test signals: Correctness is shown by inherited snapshot diff, deletion, restart, quota, tag, stream, and MPU assertions passing with native libraries disabled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotFsoWithoutNativeLib.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotFsoWithoutNativeLibWithLinkedBuckets.java -->
## sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotFsoWithoutNativeLibWithLinkedBuckets.java

Purpose: This subclass runs the shared `TestOmSnapshot` suite for FSO buckets with native diff disabled and linked bucket creation enabled. It targets source-bucket resolution and linked-bucket snapshot semantics.

Important APIs/types/functions: The class extends `TestOmSnapshot`, uses `BucketLayout.FILE_SYSTEM_OPTIMIZED`, and calls `super(FILE_SYSTEM_OPTIMIZED, false, false, true, true)`.

Control flow: All test execution is inherited. The key constructor difference is `createLinkedBucket=true`, causing `TestOmSnapshot.createBucket` and initial bucket setup to create source buckets plus linked buckets and to maintain a link-to-source map for assertions and OM key resolution.

State and persistence behavior: Snapshot table keys, bucket names returned by snapshot info, and OM key lookups are expected to refer to the source bucket where appropriate. The inherited suite validates that snapshot operations through the linked bucket preserve point-in-time data and resolve to the correct underlying bucket.

Dependencies and integration points: This subclass depends on `TestDataUtil.createLinkedBucket`, linked bucket metadata, FSO key/file tables, and the non-native diff path. It integrates link resolution with snapshot create/delete/diff/list behavior.

Risks and edge cases: Linked bucket tests are prone to mismatches between visible bucket name and source bucket name, especially in snapshot table keys and `OzoneSnapshot.getBucketName`. Since native diff is disabled, this subclass does not cover linked buckets with native SST diff.

Test signals: Inherited assertions pass while using linked bucket mappings for snapshot info, key lookups, bucket deletion, quota handling, and diff outputs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotFsoWithoutNativeLibWithLinkedBuckets.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotObjectStore.java -->
## sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotObjectStore.java

Purpose: This concrete subclass runs the shared snapshot suite for `OBJECT_STORE` bucket layout. It covers snapshot behavior when keys are treated as object-store keys rather than FSO directory/file entries.

Important APIs/types/functions: The class extends `TestOmSnapshot`, imports `BucketLayout.OBJECT_STORE`, and calls `super(OBJECT_STORE, false, false, false, false)`.

Control flow: The inherited suite builds a MiniOzoneCluster with object-store bucket layout, native diff enabled if libraries load, filesystem paths disabled, and no linked buckets. Object-store-specific behavior appears in inherited conditional assertions, such as directory entries and filesystem API assumptions.

State and persistence behavior: Snapshot state is stored and diffed through the object-store key table. Directory-like names are treated differently from FSO, and inherited tests account for ordering and missing explicit directory entries.

Dependencies and integration points: This subclass integrates object-store bucket layout with snapshot create/read/list/delete/diff, RocksDB key table SST filtering, object tag and metadata modification, stream key APIs, and MPU lifecycle tests.

Risks and edge cases: Filesystem-specific tests are skipped where object-store semantics do not support them. Directory ordering and rename semantics differ from FSO, so inherited assertions branch on bucket layout. Constructor-only drift would change the entire object-store matrix.

Test signals: Passing inherited assertions demonstrate that object-store snapshots preserve data, produce expected diff entries, reject invalid operations, and handle restart/deletion/MPU/tag cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotObjectStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotWithoutBucketLinkingLegacy.java -->
## sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotWithoutBucketLinkingLegacy.java

Purpose: This concrete subclass runs the shared snapshot suite for legacy bucket layout without linked buckets. It preserves regression coverage for pre-FSO bucket semantics.

Important APIs/types/functions: The class extends `TestOmSnapshot`, imports `BucketLayout.LEGACY`, and calls `super(LEGACY, false, false, false, false)`.

Control flow: The inherited suite runs with legacy layout, filesystem paths disabled, full diff disabled, native diff enabled if available, and linked buckets disabled. Legacy-specific behavior is handled by `bucketLayout` branches in the base test.

State and persistence behavior: Snapshot state is represented through the legacy/key-table model rather than FSO file and directory tables. Tests cover point-in-time reads, diff operations, deletion protection, quota neutrality, tag/metadata modifications, stream key behavior, and MPU behavior under that layout.

Dependencies and integration points: This subclass connects the base snapshot suite with legacy bucket metadata, OM key table diffing, object-store-style listing, and MiniOzone cluster setup.

Risks and edge cases: Legacy layout may differ from FSO in directory materialization and diff ordering. The subclass name emphasizes no bucket linking; linked-bucket edge cases are covered elsewhere.

Test signals: Passing inherited tests confirm legacy snapshot behavior remains compatible with create/list/read/delete/diff, restart, and mutation scenarios.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotWithoutBucketLinkingLegacy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOzoneManagerHASnapshot.java -->
## sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOzoneManagerHASnapshot.java

Purpose: This class tests snapshot behavior in a three-OM HA deployment. It focuses on leader restart/failover, snapshot metadata consistency across OM nodes, snapshot chain restoration, snapshot deletion service ownership after failover, follower double-buffer ordering, and in-flight snapshot counters.

Important APIs/types/functions: The suite uses `MiniOzoneHAClusterImpl`, `OzoneManager`, `ObjectStore`, `OzoneBucket`, `SnapshotInfo`, `OmMetadataManagerImpl`, `OzoneManagerDoubleBuffer`, `RDBCheckpointUtils`, `SnapshotDiffResponse`, and `SnapshotUtils`. Important methods include `testSnapshotDiffWhenOmLeaderRestart`, `testSnapshotIdConsistency`, `testSnapshotNameConsistency`, `testSnapshotChainManagerRestore`, `testSnapshotDeletingServiceDuringOMFailover`, `testKeyAndSnapshotDeletionService`, `testSnapshotInFlightCount`, `createSnapshot`, and `checkSnapshotIsPurgedFromDB`.

Control flow: `staticInit` enables snapshots and fast delete-service intervals, builds a three-OM HA cluster, creates a shared test bucket, and stores shared client handles. Tests create snapshots and keys, then deliberately restart leaders, shut down leaders to force failover, suspend deletion services, pause follower double buffers, or inspect each OM metadata table. Polling with `await` or `GenericTestUtils.waitFor` handles replication and async cleanup.

State and persistence behavior: The tests validate snapshot IDs and generated names converge across all OM metadata tables, snapshot chain manager state can be restored after leader restarts and deletions, deleted snapshot rows are purged from `SnapshotInfoTable`, and snapshot directories exist before tests proceed. The double-buffer test simulates a lagging follower receiving key purge and snapshot purge transactions in the same batch and verifies both leader and follower purge the snapshot consistently.

Dependencies and integration points: The file integrates snapshot diff jobs with HA leader election, Ratis/double-buffer flush mechanics, snapshot deleting service, key deleting service, snapshot chain manager, OM metadata tables, and checkpoint filesystem state. It uses HA cluster node lifecycle methods such as `shutdownOzoneManager`, `restartOzoneManager`, and `waitForLeaderOM`.

Risks and edge cases: These tests are timing-sensitive by design: leader election, async delete service runs, Ratis replication, double-buffer flushes, and snapshot diff job completion can race. `testSnapshotNameConsistency` is marked flaky. The deletion-service failover test must restore the old leader in a `finally` block to protect later tests.

Test signals: Signals include correct diff size after leader restart, identical snapshot IDs/names across OMs, non-corrupt snapshot chain after restart/deletion sequences, purged snapshot DB rows on new leaders and lagging followers, reset in-flight snapshot count after leader change, and successful cluster restoration after failover scenarios.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOzoneManagerHASnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOzoneManagerSnapshotAcl.java -->
## sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOzoneManagerSnapshotAcl.java

Purpose: This class verifies snapshot authorization behavior with native Ozone ACLs enabled. It tests read access to snapshot-prefixed keys, ACL inheritance/prefix behavior, and snapshot management permissions for bucket owners versus users with read/list permissions or no permissions.

Important APIs/types/functions: The suite uses `MiniOzoneCluster`, `ObjectStore`, `OzoneManager`, `UserGroupInformation`, `OzoneAcl`, `OzoneObjInfo`, `BucketLayout`, `BucketArgs`, `VolumeArgs`, `OmKeyArgs`, `SnapshotInfo`, and `RDBCheckpointUtils`. Main tests cover `lookupKey`, `getKeyInfo`, `listStatus`, `lookupFile`, `listKeys`, `getAcl`, prefix ACL lookup, and management APIs `createSnapshot`, `renameSnapshot`, `deleteSnapshot`, `listSnapshot`, `getSnapshotInfo`, `snapshotDiff`, `listSnapshotDiffJobs`, and `cancelSnapshotDiff`.

Control flow: `init` sets the login user to an admin UGI, enables test authorization and native ACLs, enables snapshot rename, starts a one-OM HA builder cluster, stops key deletion services, and stores shared clients. Per-test `setup` logs in as `UGI1`, creates a volume/bucket/key, assigns baseline ACLs, creates a snapshot, then changes active key and bucket ACLs. Tests switch `UserGroupInformation.setLoginUser` or use `doAs` clients to assert allowed and denied behavior.

State and persistence behavior: Snapshot creation captures key ACL state before later active ACL changes. The important state distinction is that a user can be allowed against the active key after ACL updates while still denied against the snapshot key because snapshot access uses the captured snapshot ACL view. Snapshot checkpoint existence is explicitly awaited through `RDBCheckpointUtils.waitForCheckpointDirectoryExist`.

Dependencies and integration points: The file integrates OM snapshot path handling with native ACL authorizer behavior, volume/bucket/key/prefix ACL resources, default ACL inheritance, bucket ownership checks, OFS default URI setup, and direct OM methods that bypass higher-level filesystem adapters. It parameterizes over every `BucketLayout` and selected list-status recursion/partial-prefix combinations.

Risks and edge cases: Because tests mutate global login user, isolation depends on each setup path resetting identity and ACLs. Prefix ACL tests include a flaky marker for one denial case. The intentional contrast between snapshot and active ACL evaluation can regress if snapshot metadata starts resolving current ACLs instead of checkpointed ACLs. `listKeys` is notable because denied user assertions expect no throw in both snapshot and active paths, documenting its current permission model.

Test signals: Signals include `PERMISSION_DENIED` for disallowed snapshot reads, no exception for allowed users, active namespace access still allowed after ACL changes, snapshot management denied for non-owners, read/list/diff/cancel operations allowed for a bucket-read user, all snapshot operations denied for a user with no permissions, and correct behavior across object-store, FSO, and legacy bucket layouts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOzoneManagerSnapshotAcl.java -->
