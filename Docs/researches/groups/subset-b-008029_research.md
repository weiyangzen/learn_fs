# Research: subset-b-008029

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/rocksdiff/TestRocksDBCheckpointDiffer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/rocksdiff/TestRocksDBCheckpointDiffer.java

Purpose: This JUnit 5 class is the main regression suite for `RocksDBCheckpointDiffer`, covering SST diff calculation with and without a live RocksDB instance, compaction DAG construction from both legacy log lines and persisted `CompactionLogEntry` rows, SST backup pruning, value pruning, table-prefix filtering, and column-family filtering.

Important APIs and types: The test exercises `RocksDBCheckpointDiffer.getSSTDiffList`, `internalGetSSTDiffList`, `processCompactionLogLine`, `addToCompactionLogTable`, `loadAllCompactionLogs`, `pruneSstFiles`, `pruneSstFileValues`, and `shouldSkipCompaction`. It constructs `DifferSnapshotInfo`, `DifferSnapshotVersion`, `SstFileInfo`, `CompactionLogEntry`, `CompactionFileInfo`, `CompactionNode`, and `TablePrefixInfo`. It also directly uses managed RocksDB wrappers such as `ManagedRocksDB`, `ManagedCheckpoint`, `ManagedSstFileReader`, and `RDBSstFileWriter`.

Control flow: `init` creates clean active DB, metadata, compaction-log, and SST-backup directories, mocks configuration, installs a read/write lock callback, initializes the differ, opens RocksDB with tracked column families, and loads existing logs. Parameterized no-DB tests build synthetic compaction histories, mock snapshot SST sets, call internal DAG expansion, and compare same/different SST sets plus the public filtered diff list. The DB-backed flaky test writes 250k keys, checkpoints periodically, traverses the compaction graph, compares all snapshot diffs to deterministic expectations, verifies backup links, and waits for inflight compactions to drain.

State and persistence behavior: Test state includes temporary RocksDB directories, checkpoint directories, active column-family handles, a compaction log table, and backup SST files. The suite verifies that compaction records survive through the differ's table-backed load path, that pruned SST backups are removed or rewritten, that compaction log files are deleted after pruning, and that `PRUNED_SST_FILE_TEMP` is cleaned up after successful value pruning.

Dependencies and integration points: This file integrates with RocksDB JNI, Ozone managed DB wrappers, compaction log codecs, Guava graphs, Mockito static/construction mocking, and Ozone configuration keys for compaction DAG and pruning behavior. It validates the contract between the differ, RocksDB compaction callbacks, snapshot metadata, and SST file readers.

Risks: Many scenarios depend on exact SST names and compaction order, so DB-backed assertions can be flaky when RocksDB behavior changes. Large row counts make the test expensive. Prefix and column-family filtering are risk-sensitive because unknown metadata intentionally falls back to conservative inclusion. Lock tests guard prune operations from racing with DAG bootstrap.

Test signals: Strong coverage comes from the parameterized compaction-log cases, prefix-filtered DAG traversal cases, pruning metrics assertions, `shouldSkipNode` edge cases, and `shouldSkipCompaction` column-family cases. `testDifferWithDB` is marked flaky but remains the highest-fidelity integration signal for real RocksDB checkpoints and compactions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/rocksdiff/TestRocksDBCheckpointDiffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/rocksdiff/TestRocksDiffUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/rocksdiff/TestRocksDiffUtils.java

Purpose: This focused test class verifies the static filtering helpers in `RocksDiffUtils`, especially prefix-range detection and mutation of SST metadata maps to retain only relevant SST files.

Important APIs and types: It calls `RocksDiffUtils.isKeyWithPrefixPresent` and `RocksDiffUtils.filterRelevantSstFiles`. Test data uses `SstFileInfo`, `TablePrefixInfo`, Guava immutable maps/sets, and `getLexicographicallyHigherString` to place prefixes relative to SST key ranges.

Control flow: `testFilterFunction` checks whether a table prefix may exist between the smallest and largest keys of an SST range. `testFilterRelevantSstFilesMap` iterates several table lookup sets, builds a map containing one relevant, one irrelevant, and one untracked SST file, runs the filter, and asserts that matching tracked files plus untracked metadata remain.

State and persistence behavior: There is no persisted state. The important behavior is in-place mutation of the input `Map<String, SstFileInfo>`, which callers must expect.

Dependencies and integration points: These helpers are used by the checkpoint differ to narrow SST diffs by table and key prefix. `TablePrefixInfo` supplies table-to-prefix mappings, while absent SST metadata is treated conservatively and retained.

Risks: Lexicographic edge conditions are subtle: equal start/end keys, adjacent prefixes, and bucket names that are prefixes of other bucket names must not be confused. Unknown column family or key-range metadata can reduce pruning precision because the safe behavior is to keep the file.

Test signals: The suite gives direct regression coverage for positive, negative, boundary, multi-table, and untracked SST cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/rocksdiff/TestRocksDiffUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/dev-support/findbugsExcludeFile.xml

Purpose: This SpotBugs/FindBugs exclude filter suppresses static-analysis findings for generated protocol classes under `org.apache.hadoop.hdds.protocol.proto`.

Important APIs and types: The file contains a single `<FindBugsFilter>` with one `<Match>` by package name. It is referenced by the `spotbugs-maven-plugin` configuration in the server-scm Maven module.

Control flow: During the module's SpotBugs execution, findings matching the generated protobuf package are excluded before the analysis result is reported.

State and persistence behavior: There is no runtime state. The file is build metadata that changes quality-gate behavior.

Dependencies and integration points: It integrates with Maven SpotBugs and the generated protobuf sources used by SCM. The server-scm `pom.xml` points `excludeFilterFile` to this path.

Risks: A broad package-level exclusion can hide real issues if handwritten classes are ever placed in the excluded package. The narrow generated-proto package makes the risk acceptable, but changes to proto package naming or generated-source layout should revisit it.

Test signals: The signal is build-time: SpotBugs should complete without reporting generated-code findings from the excluded package, while still checking the rest of the SCM module.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/pom.xml

Purpose: This Maven POM defines the `hdds-server-scm` jar module, its runtime and test dependencies, test resources, annotation processors, static-analysis configuration, web/docs resource unpacking, and protobuf test generation.

Important APIs and types: Key build plugins are `maven-compiler-plugin` with Ozone config and replication annotation processors, `maven-enforcer-plugin` with a local override for banned imports, `maven-dependency-plugin` to unpack shared web assets and docs, `spotbugs-maven-plugin` using `dev-support/findbugsExcludeFile.xml`, and `protobuf-maven-plugin` for test proto compilation.

Control flow: Normal compilation includes annotation processing for generated config files and replicated methods. During `prepare-package`, shared static web assets from `hdds-server-framework` and docs from `hdds-docs` are unpacked into output directories. During `generate-test-sources`, test protobuf files are compiled.

State and persistence behavior: The POM does not affect runtime state directly, but it controls generated sources, packaged web resources, and analysis behavior that become part of the built SCM artifact.

Dependencies and integration points: The module depends on Ozone HDDS modules for common code, container service, interfaces, managed RocksDB, server framework, and docs; Hadoop, Ratis, protobuf, Jackson, Jetty, BouncyCastle, Guava, and servlet APIs; plus test jars from Hadoop and Ozone modules. This mirrors SCM's role as a central server integrating storage, HA, security, protocol, and web layers.

Risks: Several compile dependencies are present because they are transitively needed from other modules despite test-scope comments; changing scopes may break runtime packaging. Annotation processor configuration is important for Ratis replication annotations. Resource unpacking can silently affect the SCM web UI artifact.

Test signals: Maven compile, test-compile, SpotBugs, and packaging tasks are the primary signals. Any SCM source that uses `@Replicate` or config annotations depends on this POM keeping the processors enabled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/FetchMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/FetchMetrics.java

Purpose: `FetchMetrics` is a JMX-to-JSON adapter used to fetch platform MBean metrics and serialize them into a JSON document.

Important APIs and types: Public API is `getMetrics(String qry)`, where a null query defaults to `*:*`. Internals use `ManagementFactory.getPlatformMBeanServer`, `ObjectName`, `MBeanInfo`, `MBeanAttributeInfo`, Jackson `JsonFactory`/`JsonGenerator`, `CompositeData`, and `TabularData`.

Control flow: `getMetrics` creates a UTF-8 JSON generator, starts an object, resolves the query, calls `listBeans`, closes the generator, and returns the buffer. `listBeans` queries matching MBeans, writes one JSON object per bean with `name` and `modelerType`, then iterates readable attributes. `writeAttribute` skips unsafe attribute names and handles common JMX exceptions. `writeObject` recursively serializes nulls, arrays, numbers, booleans, composite data, tabular data, and string fallbacks.

State and persistence behavior: The class holds transient references to the MBean server and JSON factory. It persists nothing and reflects live JVM MBean state at call time.

Dependencies and integration points: This code integrates with the JVM management subsystem and likely SCM/admin metric endpoints. It depends on Jackson core only for streaming JSON, not databind.

Risks: A malformed query or IO failure returns null after logging, so callers need null handling. Attribute getters can be expensive or throw runtime exceptions; the class logs and skips failed attributes. `Number` values are written from string form, which depends on Jackson's parsing of numeric text. Querying `*:*` can be large.

Test signals: Useful tests would register synthetic MBeans with scalar, array, composite, and tabular attributes, then assert JSON shape and exception-skipping behavior. The current file itself has no tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/FetchMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/PipelineChoosePolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/PipelineChoosePolicy.java

Purpose: `PipelineChoosePolicy` defines the strategy interface for choosing an existing pipeline from a candidate list.

Important APIs and types: The interface exposes `init(NodeManager)`, `choosePipeline(List<Pipeline>, PipelineRequestInformation)`, and `choosePipelineIndex(List<Pipeline>, PipelineRequestInformation)`. The default `init` is a no-op, and the default index chooser returns `-1` for null/empty lists or `0` otherwise.

Control flow: Implementations may initialize against `NodeManager`, choose a concrete `Pipeline`, and optionally expose the selected index. Callers can use the index method when they need list-position semantics rather than the pipeline object.

State and persistence behavior: The interface has no state. Implementations may hold node-manager-derived state after `init`.

Dependencies and integration points: It connects SCM pipeline allocation code to pluggable selection policies and request metadata represented by `PipelineRequestInformation`.

Risks: The default index method is intentionally simple and can be inconsistent with a custom `choosePipeline` unless implementations override both. A null return from `choosePipeline` is allowed when no candidate can be selected.

Test signals: Implementation tests should verify initialization, empty-list behavior, selected pipeline/index consistency, and policy-specific filtering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/PipelineChoosePolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/PlacementPolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/PlacementPolicy.java

Purpose: `PlacementPolicy` is the SCM contract for choosing datanodes and evaluating or repairing container replica placement.

Important APIs and types: It defines overloaded `chooseDatanodes`, `validateContainerPlacement`, `replicasToCopyToFixMisreplication`, and `replicasToRemoveToFixOverreplication`. Inputs include used, excluded, and favored datanodes; metadata and data space requirements; replica lists; and `ContainerReplica` sets.

Control flow: The default five-argument `chooseDatanodes` forwards to the six-argument form with an empty used-node list. Implementations select datanodes, validate placement status, choose replicas to copy for misreplication, and choose replicas to delete for overreplication.

State and persistence behavior: The interface is stateless. Implementations typically consult `NodeManager`, network topology, node health, and storage reports.

Dependencies and integration points: This interface is consumed by SCM container placement, pipeline/container allocation, and replication manager repair logic. `ContainerPlacementStatus` is the result contract for validation.

Risks: The default overload cannot distinguish "no used nodes passed" from "used nodes intentionally empty"; `SCMCommonPlacementPolicy` adds a sentinel to handle that nuance. Implementations must keep placement validation and repair recommendations consistent.

Test signals: Tests should cover node filtering, excluded/used/favored inputs, insufficient capacity, rack/topology validation, and repair selection under replicated and EC layouts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/PlacementPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/PlacementPolicyValidateProxy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/PlacementPolicyValidateProxy.java

Purpose: `PlacementPolicyValidateProxy` routes container placement validation to either the default placement policy or the EC placement policy based on the container's replication type.

Important APIs and types: The constructor accepts two `PlacementPolicy` instances. `validateContainerPlacement(List<DatanodeDetails>, ContainerInfo)` examines `ContainerInfo.getReplicationType()` and passes `getReplicationConfig().getRequiredNodes()` to the chosen policy.

Control flow: The method switches on replication type. EC containers use `ecPlacementPolicy`; all other types use `defaultPlacementPolicy`.

State and persistence behavior: The proxy stores only policy references and persists no state.

Dependencies and integration points: It sits between replication/container health callers and policy-specific placement validators, allowing EC placement rules to differ from replicated-container rules without spreading switch logic across callers.

Risks: Null policies are not checked, so construction must supply both. Any new replication type defaults to the non-EC policy unless the switch is expanded. The proxy only handles validation, not datanode selection or repair recommendations.

Test signals: Unit tests should verify EC routing, default routing for RATIS/STAND_ALONE or future non-EC types, and required-node propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/PlacementPolicyValidateProxy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/SCMCommonPlacementPolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/SCMCommonPlacementPolicy.java

Purpose: `SCMCommonPlacementPolicy` is the shared base class for SCM placement policies. It enforces common invariants for healthy writable nodes, free space, peer removal, topology-aware validation, and replica repair choices while leaving actual node selection to subclasses.

Important APIs and types: Public and protected APIs include `chooseDatanodes`, `chooseDatanodesInternal`, `filterNodesWithSpace`, static `hasEnoughSpace`, `getResultSet`, abstract `chooseNode`, `validateContainerPlacement`, `isValidNode`, `replicasToCopyToFixMisreplication`, and `replicasToRemoveToFixOverreplication`. It uses `NodeManager`, `DatanodeInfo`, `NodeStatus`, `NetworkTopology`, `ContainerReplica`, `ContainerPlacementStatusDefault`, and `SCMException`.

Control flow: `chooseDatanodes` normalizes deserialized datanode objects through `NodeManager`, removes excluded and used nodes from healthy in-service nodes, checks cardinality, then filters by metadata and data space. `getResultSet` repeatedly calls subclass `chooseNode`, removes selected nodes and optionally their peers, and enforces the requested result count. Validation computes required racks, handles empty or non-rack-aware topology with simple valid/invalid single-replica statuses, groups replicas by placement group, adjusts max replicas per rack for overreplication, and returns a placement status.

State and persistence behavior: The class keeps references to `NodeManager`, configuration, a non-secure random, and cached valid/invalid placement objects. It persists nothing but reads live node topology, peer lists, storage reports, and node statuses.

Dependencies and integration points: Subclasses provide policy-specific `chooseNode` and may override rack-count methods. Replication Manager uses validation and repair recommendations. `ScmUtils.shouldRemovePeers` controls whether existing pipeline peers are removed from candidate lists.

Risks: `hasEnoughSpace` requires `DatanodeDetails` to be a `DatanodeInfo`; callers that bypass normalization can fail preconditions. Topology can be transiently empty, so the code explicitly guards divide-by-zero. Repair algorithms assume placement groups can be retrieved; unexpected null groups can affect grouping. Peer removal depends on configuration and pipeline limits, influencing allocation distribution.

Test signals: Strong tests need to cover healthy-node shortages, space shortages, protobuf-only datanode normalization, rack-count validation, empty topology, overreplication adjustments, peer removal, and replica copy/remove selection by placement group and replica index.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/SCMCommonPlacementPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ScmUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ScmUtils.java

Purpose: `ScmUtils` is a static utility class for SCM bind-address resolution, placement-policy peer-removal configuration, container report queues, and certificate-signing checks during root CA rotation.

Important APIs and types: Key methods include `getScmBlockProtocolServerAddress`, `getScmBlockProtocolServerAddressKey`, `getClientProtocolServerAddress`, `getClientProtocolServerAddressKey`, `getScmDataNodeBindAddress`, `getScmDataNodeBindAddressKey`, `shouldRemovePeers`, `initContainerReportQueue`, `getContainerReportConfPrefix`, and `checkIfCertSignRequestAllowed`.

Control flow: Address helpers derive service/node-specific config keys with `ConfUtils.addKeySuffixes`, prefer host bind keys, optionally parse deprecated combined address keys for ports, log deprecation warnings, and build `InetSocketAddress` values. `shouldRemovePeers` checks pipeline limit and same-peer disallow config. Queue initialization creates one `ContainerReportQueue` per configured event thread. Certificate checks throw `SCMException` when rotation or post-rotation states prohibit the requested operation.

State and persistence behavior: The class is stateless and reads only configuration and rotation-manager state.

Dependencies and integration points: It integrates with SCM protocol servers, datanode heartbeat container report handling, placement policy peer filtering, HA config suffixes, and security certificate workflows.

Risks: Deprecated address keys can still override ports, so warnings are important for operators. Queue sizing directly affects container report backpressure. Certificate rotation checks must be applied consistently by callers or forbidden operations may proceed during sensitive rotation windows.

Test signals: Tests should verify address precedence for suffixed and unsuffixed keys, warning paths for deprecated address configs, peer-removal boolean combinations, container report queue counts and sizes, and both CA rotation exception codes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ScmUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/BlockManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/BlockManager.java

Purpose: `BlockManager` is the SCM-facing interface for block allocation, logical deletion, lifecycle management, and access to the block deletion subsystem.

Important APIs and types: It defines `allocateBlock(long, ReplicationConfig, String, ExcludeList)`, `deleteBlocks(List<BlockGroup>)`, `getDeletedBlockLog`, `start`, `stop`, `getSCMBlockDeletingService`, and inherits `close`. It returns `AllocatedBlock` and can throw `IOException` or `TimeoutException`.

Control flow: Implementations allocate blocks transparently inside containers according to replication config and exclusions. Logical deletion writes block groups to `DeletedBlockLog` atomically so blocks become pending deletion and invisible to SCM namespace consumers.

State and persistence behavior: The interface has no state. Its contract requires implementations to persist deletion transactions before considering delete requests accepted.

Dependencies and integration points: It is called by SCM block protocol handlers and integrates with container allocation, replication config handling, `ExcludeList`, and the asynchronous SCM block deleting service.

Risks: Delete semantics are atomic at the request level by contract; partial persistence would break OM/SCM consistency. Allocation can time out or fail under safe mode, capacity pressure, or pipeline/container unavailability in implementations.

Test signals: Interface-level tests should target implementations, verifying allocation validation, safe-mode rejection, deletion transaction persistence, and service start/stop idempotence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/BlockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/BlockManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/BlockManagerImpl.java

Purpose: `BlockManagerImpl` is the concrete SCM block manager. It allocates block IDs inside writable containers, creates the deleted-block log and deleting service, registers metrics and JMX, and groups block deletions by container.

Important APIs and types: It implements `BlockManager` and `BlockmanagerMXBean`. Key fields are `StorageContainerManager`, `PipelineManager`, `WritableContainerFactory`, `SequenceIdGenerator`, `DeletedBlockLogImpl`, `SCMBlockDeletingService`, and `ScmBlockDeletingServiceMetrics`. Important methods are `allocateBlock`, private `newBlock`, `deleteBlocks`, `start`, `stop`, `close`, and accessors.

Control flow: Construction pulls managers from SCM, reads container size, registers an MBean, creates metrics, builds `DeletedBlockLogImpl`, and creates `SCMBlockDeletingService`. `allocateBlock` rejects safe mode and invalid block sizes, asks the writable-container factory for a container, and delegates to `newBlock`, which gets the container pipeline, allocates a local ID, creates `ContainerBlockID`, increments pipeline metrics, and returns `AllocatedBlock`. `deleteBlocks` rejects safe mode, groups `DeletedBlock` entries by container ID, and persists deletion transactions in the deleted-block log.

State and persistence behavior: Runtime state includes manager references, metrics, MBean name, and the deletion service. Persistent behavior is delegated to `DeletedBlockLogImpl`, which writes transactions to SCM DB. Sequence IDs provide durable unique local block IDs and delete transaction IDs.

Dependencies and integration points: It is tightly integrated with SCM HA metadata, pipeline manager, writable container selection, block deleting service, metrics, and JMX. Delete requests from OM ultimately enter this path before physical deletion commands are sent to datanodes.

Risks: `newBlock` returns null if the pipeline is missing, so callers must handle null allocation. `stop` calls service shutdown and `close`, while `close` also shuts down the service; repeated close paths should remain harmless. Safe-mode checks are critical to avoid mutation during SCM initialization.

Test signals: Tests should cover safe-mode exceptions, invalid size bounds, successful container-backed allocation with sequence IDs and pipeline metrics, missing pipeline behavior, grouping deletes by container, and cleanup of metrics/MBeans/services.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/BlockManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/BlockmanagerMXBean.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/BlockmanagerMXBean.java

Purpose: `BlockmanagerMXBean` is the marker JMX management interface for `BlockManagerImpl`.

Important APIs and types: The interface currently declares no attributes or operations. `BlockManagerImpl` implements it and registers itself with Hadoop `MBeans` under `BlockManager`.

Control flow: The interface participates in MBean registration by identifying the management surface. Since it is empty, registration exposes no explicit custom methods from this interface.

State and persistence behavior: There is no state and no persistence.

Dependencies and integration points: It integrates with JMX/Hadoop MBeans and can be expanded if block manager metrics or controls need MBean attributes in the future.

Risks: An empty MBean may have limited operational value. Adding methods later changes the management API and should be done deliberately with compatibility in mind.

Test signals: Current signals are limited to successful registration/unregistration in `BlockManagerImpl` lifecycle tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/BlockmanagerMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/DatanodeDeletedBlockTransactions.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/DatanodeDeletedBlockTransactions.java

Purpose: This package-private wrapper accumulates deleted-block transactions selected for each datanode during one SCM block-deletion scan.

Important APIs and types: It stores `Map<DatanodeID, List<DeletedBlocksTransaction>>` and an aggregate `blocksDeleted` count. Methods include `addTransactionToDN`, `getDatanodeTransactionMap`, `getBlocksDeleted`, `getTransactionIDList`, `getNumberOfBlocksForDatanode`, and `isEmpty`.

Control flow: `DeletedBlockLogImpl.getTransactions` calls `addTransactionToDN` for each replica datanode that should receive a transaction. `SCMBlockDeletingService` later iterates the map and emits one `DeleteBlocksCommand` per datanode.

State and persistence behavior: This class is in-memory only and scoped to a scan iteration. `blocksDeleted` counts replica work, not unique logical blocks, because the same transaction may be sent to several datanodes.

Dependencies and integration points: It bridges persisted deleted-block log scanning and command creation. It is used for per-datanode throttling through `getNumberOfBlocksForDatanode` and for logging transaction ID lists.

Risks: Counting blocks per replica can be confused with unique block counts. The class is not synchronized and should remain single-thread confined during scan processing.

Test signals: Tests should verify accumulation by datanode, block-count totals, empty behavior, and transaction ID string conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/DatanodeDeletedBlockTransactions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/DeletedBlockLog.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/DeletedBlockLog.java

Purpose: `DeletedBlockLog` defines the persisted SCM log for blocks pending physical deletion on datanodes.

Important APIs and types: The interface exposes `getTransactions`, `incrementCount`, `recordTransactionCreated`, `onDatanodeDead`, `onSent`, `addTransactions`, `getNumOfValidTransactions`, `reinitialize`, `getTransactionToDNsCommitMapSize`, and `getTransactionSummary`. It uses `DeletedBlocksTransaction`, `DeletedBlock`, `DatanodeDeletedBlockTransactions`, `DatanodeDetails`, `DatanodeID`, `SCMCommand`, and SCM metadata `Table`s.

Control flow: Producers call `addTransactions` to atomically persist container-to-block deletion work. The background service calls `getTransactions` to scan and select work for healthy datanodes, then `recordTransactionCreated` and `incrementCount` after command creation. Heartbeat paths call `onSent` and command-status event paths commit or retry through the implementation.

State and persistence behavior: Implementations must persist deletion transactions and support reinitialization from SCM DB tables after leadership or metadata reload. Summary data can expose aggregate pending-deletion counts.

Dependencies and integration points: It is the central contract between `BlockManagerImpl`, `SCMBlockDeletingService`, datanode command tracking, and SCM HA metadata.

Risks: Duplicate command suppression, retry counting, and transaction removal must be consistent across leadership changes and datanode failures. Atomic add semantics are critical to avoid losing pending deletes.

Test signals: Tests should cover add/scan/remove, reinitialize, datanode death cleanup, command sent/executed/failed flows, summary counters, and transaction map size throttling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/DeletedBlockLog.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/DeletedBlockLogImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/DeletedBlockLogImpl.java

Purpose: `DeletedBlockLogImpl` implements the deleted-block log using SCM metadata tables and coordinates transaction creation, scan selection, duplicate suppression, command ACK handling, and summary accounting.

Important APIs and types: It implements `DeletedBlockLog` and `EventHandler<DeleteBlockStatus>`. Key collaborators are `DeletedBlockLogStateManager`, `SCMDeletedBlockTransactionStatusManager`, `ContainerManager`, `SCMContext`, `SequenceIdGenerator`, and `ScmBlockDeletingServiceMetrics`. Core methods are `addTransactions`, `getTransactions`, `constructNewTransaction`, `onMessage`, `recordTransactionCreated`, `onSent`, `onDatanodeDead`, `reinitialize`, `onBecomeLeader`, and `onFlush`.

Control flow: `addTransactions` converts each container's deleted blocks into a `DeletedBlocksTransaction`, batches by roughly 90 percent of the Ratis log appender queue byte limit, and persists through the status manager. `getTransactions` locks, clears timed-out command records, scans from `lastProcessedTransactionId`, wraps at table end, skips open or unhealthy/under-replicated containers, removes transactions for missing/deleted containers, avoids duplicate sends per datanode, and returns per-datanode work under a block limit. `onMessage` only commits as leader; executed command statuses commit transaction ACKs, failed statuses update failure metrics, and all statuses update command records.

State and persistence behavior: Persistent state lives in the deleted-block transaction table and stateful-service config table. In-memory state includes `lastProcessedTransactionId`, a command timeout, per-datanode distribution factor, and a lock guarding scans and ACK processing. Transaction records include block-size fields when the storage-space-distribution layout feature is finalized.

Dependencies and integration points: It links block-manager delete requests to SCM HA tables, replication health checks, datanode command events, command-status reports, metrics, and layout-feature-aware accounting.

Risks: Scan fairness depends on correct cursor wrap behavior. Containers not healthy or not represented in the included datanode set are skipped, delaying deletion but preserving safety. Missing/deleted containers cause transaction removal. The command timeout and duplicate-suppression maps must be cleared appropriately on leadership changes. Size summary accuracy depends on `txSizeMap` being populated before removals.

Test signals: Important tests should cover batching by byte size, scan wraparound, open/unhealthy/deleted/missing container branches, duplicate command suppression, ACK success/failure, non-leader event skipping, timeout cleanup, and layout-feature summary updates.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/DeletedBlockLogImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/DeletedBlockLogStateManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/DeletedBlockLogStateManager.java

Purpose: `DeletedBlockLogStateManager` defines the HA-replicated state-management interface for deleted-block transactions in SCM DB.

Important APIs and types: It extends `SCMHandler`, returns Ratis `RequestType.BLOCK`, and marks `addTransactionsToDB`, `removeTransactionsFromDB`, and deprecated retry-count methods with `@Replicate`. It exposes `getReadOnlyIterator`, `onFlush`, and `reinitialize`.

Control flow: The replicated add/remove methods are invoked through SCM HA proxy machinery so mutations are applied through the state machine. Default overloads pass null summaries, while newer overloads persist `DeletedBlocksTransactionSummary` alongside transaction changes.

State and persistence behavior: Implementations write to the deleted-block transaction table and optionally the stateful config table. `onFlush` allows implementations to clear transient state after Ratis transaction-buffer flush.

Dependencies and integration points: It connects `DeletedBlockLogImpl` and `SCMDeletedBlockTransactionStatusManager` to SCM Ratis replication and metadata tables. The `@Replicate` annotation relies on the module's annotation processor configuration.

Risks: Deprecated retry-count methods remain as replicated no-ops for compatibility; callers should not rely on persisted retry counts. Any mutation not going through replicated methods could break HA consistency.

Test signals: Tests should verify proxy invocation, add/remove persistence, summary persistence, iterator read-only behavior, flush cleanup, and reinitialization after leadership or DB reload.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/DeletedBlockLogStateManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/DeletedBlockLogStateManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/DeletedBlockLogStateManagerImpl.java

Purpose: `DeletedBlockLogStateManagerImpl` persists deleted-block transactions and summary data into SCM metadata tables through the HA transaction buffer, while hiding transactions that are queued for deletion but not yet flushed.

Important APIs and types: Fields include `Table<Long, DeletedBlocksTransaction> deletedTable`, `Table<String, ByteString> statefulConfigTable`, `ContainerManager`, `SCMHADBTransactionBuffer`, and `deletingTxIDs`. It implements `getReadOnlyIterator`, `addTransactionsToDB`, `removeTransactionsFromDB`, `onFlush`, `reinitialize`, and a builder that wraps the implementation with `DeletedBlockLogStateManagerInvoker`.

Control flow: The custom read-only iterator advances over the deleted table while skipping IDs in `deletingTxIDs`. Adds write transactions to the buffer, update the latest delete transaction ID per container in `ContainerManager`, and optionally write a summary under `SERVICE_NAME`. Removes mark IDs as deleting and enqueue table removals plus optional summary updates. `onFlush` clears `deletingTxIDs`; `reinitialize` swaps table references after asserting no pending deleting IDs.

State and persistence behavior: Persistent transaction and summary mutations are staged in `SCMHADBTransactionBuffer`, then flushed through SCM HA. `deletingTxIDs` is transient state preventing unflushed removals from being selected again during scans.

Dependencies and integration points: It integrates with SCM Ratis proxying, metadata tables, transaction buffer, and container delete transaction ID tracking.

Risks: If `onFlush` is missed, `deletingTxIDs` can hide transactions indefinitely. If reinitialization occurs with pending IDs, the precondition catches a dangerous state. The iterator does not support `seekToLast` or remove, so callers must treat it as read-only.

Test signals: Tests should cover iterator skipping, add buffering, remove buffering, summary writes, `ContainerManager.updateDeleteTransactionId`, flush clearing, and builder proxy behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/DeletedBlockLogStateManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/SCMBlockDeletingService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/SCMBlockDeletingService.java

Purpose: `SCMBlockDeletingService` is the background SCM service that scans pending deleted-block transactions and enqueues `DeleteBlocksCommand`s to datanodes.

Important APIs and types: It extends `BackgroundService` and implements `SCMService`. Important methods are `getTasks`, inner `DeletedBlockTransactionScanner.call`, `setBlockDeleteTXNum`, `getBlockDeleteTXNum`, `notifyStatusChanged`, `shouldRun`, `getDatanodesWithinCommandLimit`, `stop`, and `getServiceName`. It uses `DeletedBlockLog`, `NodeManager`, `EventPublisher`, `SCMContext`, `SCMServiceManager`, `ScmConfig`, and metrics.

Control flow: Construction configures the background interval, timeout, safe-mode exit delay, datanode command queue limit, transaction-commit-map limit, registers the config for reconfiguration, and registers the service. The scanner exits unless SCM is leader-ready, out of safe mode, and past the delay. It selects healthy in-service datanodes under command limits, skips if the transaction commit map is too large, fetches transactions from the log, creates one `DeleteBlocksCommand` per datanode, records command creation, fires `SCMEvents.DATANODE_COMMAND`, updates metrics, and increments retry counts for processed transaction IDs.

State and persistence behavior: The service stores runtime status, safe-mode exit time, limits, and references. It does not persist directly; transaction state remains in `DeletedBlockLog` and status managers.

Dependencies and integration points: It integrates with SCM service lifecycle, leader/safe-mode state, datanode command queues, event publishing, datanode heartbeats, dynamic config, and deletion metrics.

Risks: Overly strict command limits can starve deletion; overly loose limits can overload datanodes. `transactionToDNsCommitMapLimit` protects memory growth but can pause deletion. Leadership changes are handled by catching `NotLeaderException` and `shouldRun`, but races around command creation are still important.

Test signals: Tests should verify service gating by safe mode/leader/delay, datanode filtering by queue counts, per-datanode command generation, metrics increments, retry-count increments, transaction-map threshold skipping, and dynamic block deletion limit validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/SCMBlockDeletingService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/SCMDeletedBlockTransactionStatusManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/SCMDeletedBlockTransactionStatusManager.java

Purpose: `SCMDeletedBlockTransactionStatusManager` manages in-memory status for deleted-block transactions and delete-block SCM commands, suppressing duplicate sends, tracking ACK progress across datanodes, removing fully committed transactions, and maintaining persisted pending-deletion summary counters.

Important APIs and types: It owns `transactionToDNsCommitMap`, `transactionToRetryCountMap`, `txSizeMap`, `DeletedBlockLogStateManager`, `ContainerManager`, metrics, and inner `SCMDeleteBlocksCommandStatusManager`. Public or visible methods include `incrementRetryCount`, `recordTransactionCreated`, `onSent`, `onBecomeLeader`, `cleanAllTimeoutSCMCommand`, `isDuplication`, `addTransactions`, `removeTransactions`, `commitTransactions`, `commitSCMCommandStatus`, `getSummary`, `getTransactionSummary`, `reinitialize`, and `setDisableDataDistributionForTest`.

Control flow: Command records start as `TO_BE_SENT`, transition to `SENT` when SCM observes dispatch, and are removed when datanodes report `EXECUTED` or `FAILED`, or when they time out. `recordTransactionCreated` records the command and initializes commit-map entries. `isDuplication` checks both already committed and in-processing states. `commitTransactions` ignores failed ACK items, adds successful datanodes to the commit set, and removes a transaction only after all current container replica datanodes have committed and the required node count is satisfied. Add/remove operations persist through `DeletedBlockLogStateManager`, with summary updates when the storage-space-distribution feature is finalized.

State and persistence behavior: Command status, retry counts, commit maps, and transaction size maps are in memory and cleared on leadership changes. Aggregate summary counters are loaded from and written to the stateful config table under `DeletedBlockLogStateManagerImpl.SERVICE_NAME`. Transaction rows are added and removed through the replicated state manager.

Dependencies and integration points: It is called by `DeletedBlockLogImpl` during scans, command creation, ACK processing, datanode death, leadership changes, and reinitialization. It uses container replica state to decide when deletion is complete.

Risks: In-memory maps can grow if datanodes stop responding; timeout cleanup and service-level map limits mitigate that. Asynchronous retry-count increments are eventually consistent and diagnostic only. Summary counters can drift if `txSizeMap` lacks entries for removed transactions; the code warns on initialization failure but continues. Replica-set changes during deletion affect the all-datanodes-committed condition.

Test signals: Tests should cover command status transitions, duplicate detection, timeout removal, datanode death cleanup, leadership reset, failed and successful ACK handling, transaction removal only after all replicas commit, summary add/remove persistence, reinitialize loading, and storage-space-distribution disabled test mode.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/SCMDeletedBlockTransactionStatusManager.java -->
