# subset-b-008074 research

Grouped research for Apache Ozone integration-test files. Each section is bounded with the exact source path markers required by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/RootedOzoneContract.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/RootedOzoneContract.java

## Purpose

`RootedOzoneContract` is a Hadoop filesystem contract adapter for Ozone's rooted `ofs://` URI form. It specializes the shared `AbstractOzoneContract` test support so Hadoop FS contract tests can exercise a filesystem rooted at the Ozone service rather than at a single volume/bucket authority.

## Important APIs, Types, And Functions

The important type is `RootedOzoneContract`, a concrete subclass of `AbstractOzoneContract`. Its only local behavior is `getRootURI()`, which returns `OzoneConsts.OZONE_OFS_URI_SCHEME + "://" + OzoneConsts.OZONE_URI_DELIMITER`. The constructor accepts a Hadoop `Configuration` and `MiniOzoneCluster`, then delegates to the abstract superclass.

## Control Flow

Construction stores cluster/configuration behavior in the parent. During contract setup, the superclass asks for the root URI, and this class supplies `ofs:///`, allowing tests to resolve paths below the Ozone service root.

## State And Persistence Behavior

This class owns no mutable state beyond inherited test-cluster references. Persistence is entirely in the MiniOzoneCluster and Ozone Manager metadata touched by contract tests.

## Dependencies And Integration Points

It depends on Hadoop `Path`, `MiniOzoneCluster`, `OzoneConsts`, and the sibling `AbstractOzoneContract`. It integrates with `TestRootedOzoneContract`, which instantiates it from an Ozone configuration.

## Risks And Test Signals

The risk is URI-shape drift: rooted OFS behavior depends on the exact scheme and delimiter. Contract failures around path qualification, root listing, volume/bucket traversal, or authority parsing signal regressions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/RootedOzoneContract.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/TestOzoneContractFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/TestOzoneContractFSO.java

## Purpose

`TestOzoneContractFSO` runs the shared Ozone filesystem contract suite against buckets created with the `FILE_SYSTEM_OPTIMIZED` layout. It verifies that the Hadoop `o3fs` contract still holds when Ozone uses directory-aware FSO metadata internally.

## Important APIs, Types, And Functions

The class extends `AbstractOzoneContractTest`. It overrides `createOzoneConfig()` to call the superclass, then sets `OZONE_DEFAULT_BUCKET_LAYOUT` to `FILE_SYSTEM_OPTIMIZED.name()`. It overrides `createContract(Configuration)` and returns a new `OzoneContract`.

## Control Flow

The abstract test harness creates an `OzoneConfiguration`, applies the FSO bucket-layout override, starts or accesses the MiniOzoneCluster, and runs inherited Hadoop FS contract tests through the returned `OzoneContract`.

## State And Persistence Behavior

The file itself is stateless. The meaningful state is bucket layout selection in configuration and the OM metadata entries created by contract operations. FSO layout persists directory and file entries differently from legacy buckets, so the contract validates both path semantics and metadata backend compatibility.

## Dependencies And Integration Points

It depends on `OMConfigKeys.OZONE_DEFAULT_BUCKET_LAYOUT`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `OzoneConfiguration`, and `OzoneContract`. It is paired with the legacy and rooted contract tests to cover layout variants.

## Risks And Test Signals

Risks include contract gaps masked by shared setup and behavior differences between FSO directories and Hadoop path expectations. Failures in rename, delete, mkdirs, list status, or file creation under this class are strong signals of FSO-specific filesystem regressions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/TestOzoneContractFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/TestOzoneContractLegacy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/TestOzoneContractLegacy.java

## Purpose

`TestOzoneContractLegacy` runs the same shared filesystem contract suite with the bucket layout forced to `LEGACY`. It protects compatibility for Ozone deployments and clients that still use the original key-layout semantics.

## Important APIs, Types, And Functions

The class extends `AbstractOzoneContractTest`. Its `createOzoneConfig()` override sets `OZONE_DEFAULT_BUCKET_LAYOUT` to `LEGACY.name()`. Its `createContract(Configuration)` override returns an `OzoneContract`, which supplies the `o3fs` contract implementation.

## Control Flow

The inherited test harness requests the configuration, receives the legacy layout override, creates the Ozone FS contract, and executes the inherited Hadoop contract tests against a MiniOzoneCluster-backed filesystem.

## State And Persistence Behavior

The only local state is configuration. Persistent behavior lives in the OM bucket layout and key metadata created during the test run. Legacy buckets store path-like keys without the FSO directory table behavior, so this file validates the older persistence shape.

## Dependencies And Integration Points

Dependencies include `OMConfigKeys`, `BucketLayout.LEGACY`, `OzoneConfiguration`, and `OzoneContract`. It complements `TestOzoneContractFSO` by keeping both metadata layouts under the same contract expectations.

## Risks And Test Signals

The main risk is accidental preference for FSO semantics in shared filesystem code. Contract failures in directory markers, parent handling, rename/delete, or path qualification under the legacy configuration indicate compatibility regressions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/TestOzoneContractLegacy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/TestRootedOzoneContract.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/TestRootedOzoneContract.java

## Purpose

`TestRootedOzoneContract` runs the common Ozone filesystem contract tests through the rooted OFS contract rather than the bucket-scoped Ozone contract. Its goal is to validate service-root path handling for Hadoop filesystem clients.

## Important APIs, Types, And Functions

The class extends `AbstractOzoneContractTest` and overrides `createContract(Configuration)` to return `new RootedOzoneContract(conf, getCluster())`.

## Control Flow

The inherited fixture starts or retrieves the MiniOzoneCluster, passes it to the rooted contract, and then executes the shared Hadoop FS contract tests with paths resolved from the OFS root URI.

## State And Persistence Behavior

No local state is added. Contract operations create and mutate Ozone volumes, buckets, and keys beneath the rooted namespace, and assertions validate that the root-level URI layer maps those operations correctly.

## Dependencies And Integration Points

The file depends on `AbstractFSContract`, Hadoop `Configuration`, `AbstractOzoneContractTest`, and `RootedOzoneContract`. It is the test-side integration point for `RootedOzoneContract`.

## Risks And Test Signals

Rooted OFS has broader namespace behavior than bucket-scoped `o3fs`; failures can reveal authority parsing, root listing, path qualification, or volume/bucket boundary issues. The test also depends on the shared abstract suite being broad enough to cover root-specific edge cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/TestRootedOzoneContract.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/package-info.java

## Purpose

This package descriptor declares package-level documentation for `org.apache.hadoop.fs.ozone` integration tests. It gives Javadoc a package anchor for Ozone Hadoop filesystem tests under `hadoop-ozone/integration-test`.

## Important APIs, Types, And Functions

There are no classes, methods, fields, or executable APIs. The only language construct is `package org.apache.hadoop.fs.ozone;` following the ASF license header and package comment.

## Control Flow

There is no runtime control flow. The file is compiled only as package metadata.

## State And Persistence Behavior

The file is stateless and does not affect Ozone persistence. Any effect is documentation-time only.

## Dependencies And Integration Points

It integrates with Java/Javadoc package documentation and with the compiler's package-info handling. It does not import or reference runtime Ozone classes.

## Risks And Test Signals

Risk is limited to stale package documentation or accidental package-name mismatch. Compilation of the test source tree is the main signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/TestRemoteEx.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/TestRemoteEx.java

## Purpose

`TestRemoteEx` verifies that HDDS/SCM exception types survive Hadoop IPC `RemoteException` wrapping and unwrapping. It protects client-side error typing for exceptions returned across RPC boundaries.

## Important APIs, Types, And Functions

The class defines a local `SomeException extends SCMException` with a `ResultCodes.FAILED_TO_CHANGE_CONTAINER_STATE` code. `testSCMException()` uses Reflections to find every `SCMException` subtype under the package and passes each to `runUnwrappingRemoteException`. The helper builds a `RemoteException` from the exception class name and message, unwraps it through `unwrapRemoteException(clazz)`, and asserts the concrete class and message.

## Control Flow

The test discovers subclasses, then for each class executes a synthetic remote-wrap/unwrap round trip. There is no cluster startup.

## State And Persistence Behavior

No persistent state is touched. State is limited to reflection metadata and transient exception objects.

## Dependencies And Integration Points

It depends on `SCMException`, Hadoop's relocated `org.apache.hadoop.ipc_.RemoteException`, and `org.reflections.Reflections`. It integrates with the RPC exception contract expected by HDDS clients.

## Risks And Test Signals

New `SCMException` subclasses that lack suitable constructors or cannot be instantiated by Hadoop's unwrapping logic will fail here. This test is sensitive to package scanning and to exception class renames.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/TestRemoteEx.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestAllocateContainer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestAllocateContainer.java

## Purpose

`TestAllocateContainer` exercises SCM's client-side container allocation API in a non-HA MiniOzoneCluster. It checks basic allocation, invalid replication input, and both RATIS and EC replication configurations.

## Important APIs, Types, And Functions

The abstract class implements `NonHATests.TestCase`, using `cluster()` from the injected non-HA fixture. `init()` creates a `StorageContainerLocationProtocolClientSideTranslatorPB`; `cleanup()` closes it. Tests call `allocateContainer`, `getContainer`, and `getContainerWithPipeline` using `RatisReplicationConfig`, `ECReplicationConfig`, and null replication.

## Control Flow

Setup creates the RPC translator from the cluster configuration. Each allocation test calls SCM, receives a container ID and pipeline, then validates that lookup by ID returns consistent metadata. The null replication test asserts that SCM rejects invalid input.

## State And Persistence Behavior

Allocations persist container metadata in SCM's container state manager and may create or select pipelines. The test does not write data blocks; it validates the control-plane state created by allocation.

## Dependencies And Integration Points

Dependencies include `StorageContainerLocationProtocolClientSideTranslatorPB`, replication config classes, `ContainerWithPipeline`, and `NonHATests`. It integrates with SCM's client protocol server and container manager.

## Risks And Test Signals

Failures indicate allocation API regressions, replication config validation gaps, EC/RATIS pipeline selection issues, or lookup inconsistency between allocation and container retrieval.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestAllocateContainer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestCloseContainer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestCloseContainer.java

## Purpose

`TestCloseContainer` verifies close-container behavior across SCM, datanodes, restart, replica reporting, and checksum generation. It uses a three-datanode MiniOzoneCluster and real client writes to exercise control-plane and datanode state transitions.

## Important APIs, Types, And Functions

Setup tunes heartbeat/report intervals, starts `MiniOzoneCluster`, creates an `OzoneClient`, volume, and bucket. Tests use `OzoneTestUtils.closeContainers`, `StorageContainerManager`, `ContainerInfo`, `ContainerReplica`, `OzoneContainer`, and `ContainerMerkleTreeTestUtils`. Helpers include `getContainerReplicas` and `checkContainerCloseInDatanode`.

## Control Flow

`testReplicasAreReportedForClosedContainerAfterRestart` writes data, closes a container, restarts SCM, and waits for replica state to be reported after heartbeat/container reports resume. `testCloseClosedContainer` asserts idempotent handling when closing an already closed container. `testContainerChecksumForClosedContainer` writes keys, closes containers, waits for datanodes to close them, and checks checksum files for closed containers.

## State And Persistence Behavior

The test mutates OM key state, SCM container lifecycle state, datanode container state, replica reports, and checksum files on datanode storage. Restart verifies persistence of SCM metadata and subsequent reconciliation from datanode reports.

## Dependencies And Integration Points

It integrates Ozone client writes, SCM container manager, replication manager, datanode state machines, container checksums, and MiniOzoneCluster lifecycle.

## Risks And Test Signals

Race sensitivity is high because close and report processing are asynchronous. Failures signal lifecycle idempotency bugs, lost replica reports after restart, checksum-generation regressions, or stale container state on datanodes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestCloseContainer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestCommitInRatis.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestCommitInRatis.java

## Purpose

`TestCommitInRatis` validates retry handling for Ozone output-stream flush/commit behavior when Ratis watch levels are `MAJORITY_COMMITTED` or `ALL_COMMITTED`. It focuses on correct propagation and recovery from retry failures in the write pipeline.

## Important APIs, Types, And Functions

The class configures chunk, flush, max-flush, and block sizes, starts a MiniOzoneCluster, and uses Ozone client APIs to create volumes, buckets, and keys. The parameterized test uses `RaftProtos.ReplicationLevel` values and exercises write/flush paths through Ratis.

## Control Flow

`startCluster` applies test configuration and creates the cluster/client. The parameterized test writes key data using a configured watch type, triggers flush/commit behavior, validates the expected retry path, and shuts the cluster down in cleanup logic.

## State And Persistence Behavior

The test persists key data through OM metadata, SCM block allocation, datanode chunks, and Ratis log commits. The observed state is whether committed data survives and whether exceptions align with the requested Ratis commit level.

## Dependencies And Integration Points

It depends on MiniOzoneCluster, Ozone client streams, Ratis replication-level APIs, and SCM/datanode write pipelines.

## Risks And Test Signals

As a Ratis timing test, it can be sensitive to commit latency. Failures indicate watch-level mismatch, retry error handling regressions, or data visibility bugs around flush/commit boundaries.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestCommitInRatis.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestContainerOperations.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestContainerOperations.java

## Purpose

`TestContainerOperations` covers SCM container CLI/client operations in a non-HA cluster: create/list/get pipeline, idempotent state transitions, datanode usage compatibility, healthy-node counts, operational states, and RATIS/EC create paths.

## Important APIs, Types, And Functions

The abstract class implements `NonHATests.TestCase`. Setup creates `ContainerOperationClient` and `ScmClient`. Tests use `ContainerWithPipeline`, `DatanodeUsageInfo`, `NodeStatus`, `RatisReplicationConfig`, `ECReplicationConfig`, and SCM container lifecycle APIs.

## Control Flow

The test fixture obtains SCM clients, then individual tests allocate/create containers, list with a limit, fetch pipeline details, inspect datanode usage, query node counts, and change node operational states such as `IN_SERVICE`, `DECOMMISSIONING`, and `IN_MAINTENANCE`. Replication-specific create helpers validate returned pipelines.

## State And Persistence Behavior

Container creation persists container records in SCM metadata and may create pipelines. Node operational-state changes update SCM node manager state. Usage info reflects datanode reports and compatibility fields.

## Dependencies And Integration Points

It integrates SCM client protocol, container manager, node manager, datanode usage reporting, and replication config handling. It is a bridge between CLI/client surface and SCM internal state.

## Risks And Test Signals

Failures reveal API/CLI contract drift, bad container-list limits, pipeline lookup inconsistency, broken node usage compatibility, or operational-state accounting regressions. Asynchronous reports can make usage-related assertions timing-sensitive.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestContainerOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestContainerReportWithKeys.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestContainerReportWithKeys.java

## Purpose

`TestContainerReportWithKeys` verifies that after key writes, SCM receives container reports and tracks container replica/key-related metadata consistently enough to locate the written containers and replicas.

## Important APIs, Types, And Functions

The abstract non-HA test uses `OzoneClient`, `ObjectStore`, `OzoneOutputStream`, `StorageContainerManager`, `OmKeyArgs`, `OmKeyLocationInfo`, `ContainerInfo`, and `ContainerReplica`. It writes random data through the object-store API and inspects SCM container state.

## Control Flow

Setup captures the cluster client and SCM. The test creates volume/bucket/key data, closes the output stream, resolves key location information through OM helpers, and checks the corresponding SCM container and replica information after reports arrive.

## State And Persistence Behavior

The test writes durable key data to datanodes and persists OM key metadata. SCM state is updated asynchronously by datanode container reports carrying container/replica information.

## Dependencies And Integration Points

It links Ozone object-store writes, OM key-location metadata, SCM container manager, replica tracking, and datanode container reports.

## Risks And Test Signals

The major risk is report timing. Failures indicate missing container reports after writes, stale SCM replica maps, or divergence between OM key locations and SCM container metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestContainerReportWithKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestContainerSmallFile.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestContainerSmallFile.java

## Purpose

`TestContainerSmallFile` exercises low-level container protocol calls for small writes and reads. It validates allocate/write/read behavior, invalid block/container errors, BCS ID handling, and echo RPC behavior through a real non-HA cluster.

## Important APIs, Types, And Functions

Setup creates `StorageContainerLocationProtocolClientSideTranslatorPB` and `XceiverClientManager`. Tests call SCM allocation and `ContainerProtocolCalls` for write/read/chunk and echo paths. Important types include `BlockID`, `ContainerWithPipeline`, `ContainerProtos`, `ByteString`, and `StorageContainerException`.

## Control Flow

Each test allocates or references a container, obtains an xceiver client for the pipeline, then performs protocol calls. Invalid-read tests intentionally use wrong block or container IDs and assert the expected exception/result. The BCS test writes and reads with block commit sequence IDs.

## State And Persistence Behavior

Successful tests create containers and block/chunk data on datanodes. BCS IDs are persisted in block/container metadata and affect read validation. Invalid tests should not mutate valid container state.

## Dependencies And Integration Points

The file integrates SCM allocation, xceiver client pooling, datanode container protocol, protobuf command responses, and Ozone container test helpers.

## Risks And Test Signals

Failures can indicate wire-protocol regressions, bad error mapping, BCS ID handling bugs, or client-manager lifecycle leaks. Low-level protocol tests are sensitive to pipeline readiness and datanode state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestContainerSmallFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestDatanodeSCMNodesReconfiguration.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestDatanodeSCMNodesReconfiguration.java

## Purpose

`TestDatanodeSCMNodesReconfiguration` validates dynamic datanode reconfiguration of SCM peer lists in HA clusters. It covers SCM migration/decommission and adding/removing an SCM node while datanodes are running.

## Important APIs, Types, And Functions

The class uses `MiniOzoneHAClusterImpl`, `HddsDatanodeService`, `StorageContainerManager`, `ConfUtils`, SCM node keys, reconfiguration handlers, datanode connection managers, queue metrics, and `DecommissionScmResponseProto`. Helpers include `decommissionSCM` and `assertIsPropertyReconfigurable`.

## Control Flow

Setup starts a three-SCM HA cluster with datanodes. `testSCMMigration` decommissions SCM peers and validates that datanode SCM connections, queue metrics, and endpoint state machines converge to the reduced peer set. `testAddAndRemoveOneSCM` bootstraps an additional SCM, pushes new SCM address properties into datanode configs, triggers reconfiguration, waits for registration, then removes the SCM and waits for stale/dead accounting.

## State And Persistence Behavior

The test mutates SCM HA membership, datanode runtime configuration, connection-manager state, queue metrics, and node-health records. SCM decommission also changes Ratis peer configuration and active SCM membership.

## Dependencies And Integration Points

It integrates SCM HA bootstrap/decommission, datanode reconfiguration, SCM datanode protocol connections, heartbeat queues, and node manager health state.

## Risks And Test Signals

The test is asynchronous and timeout-sensitive. Failures point to non-reconfigurable keys, leaked SCM connections, incorrect queue/executor sizing, failed datanode registration to new SCMs, or stale peer membership after decommission.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestDatanodeSCMNodesReconfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestFailoverWithSCMHA.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestFailoverWithSCMHA.java

## Purpose

`TestFailoverWithSCMHA` verifies client-visible behavior during SCM HA leader failover. It also checks that container balancer configuration persists across SCMs and that admin commands show retry guidance when SCM is unavailable.

## Important APIs, Types, And Functions

The test builds a MiniOzone HA cluster with one OM and three SCMs. It uses Ozone client key operations, SCM leader discovery, SCM shutdown/restart, container balancer configuration, and Ozone admin command execution. Constants define SCM/OM service IDs and SCM admin command families.

## Control Flow

Setup starts the HA cluster. `testFailover` performs writes, shuts down the active SCM, waits for a new leader, and verifies client operations continue. `testContainerBalancerPersistsConfigurationInAllSCMs` updates balancer config and verifies replication to all SCMs. `testRetryMessageShownWhenScmUnavailable` runs admin commands while SCMs are unavailable and checks user-facing retry output.

## State And Persistence Behavior

The tests persist OM keys, SCM HA Ratis state, balancer configuration, and leader/follower state. Failover validates that SCM metadata and service discovery survive leader replacement.

## Dependencies And Integration Points

It integrates MiniOzone HA, Ozone clients, SCM Ratis leader election, container balancer configuration storage, and admin CLI command handling.

## Risks And Test Signals

Failures indicate HA failover gaps, stale SCM client routing, missing replicated configuration, or poor unavailable-service messaging. Timing around leader election is the main flakiness vector.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestFailoverWithSCMHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestGetCommittedBlockLengthAndPutKey.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestGetCommittedBlockLengthAndPutKey.java

## Purpose

`TestGetCommittedBlockLengthAndPutKey` validates SCM/datanode block commit metadata and key finalization responses. It checks committed block length lookup, invalid-block handling, and put-key response semantics in a non-HA cluster.

## Important APIs, Types, And Functions

The abstract test uses `OzoneClient`, `StorageContainerLocationProtocolClientSideTranslatorPB`, `XceiverClientManager`, `ContainerProtocolCalls`, `BlockID`, `ContainerWithPipeline`, `OmKeyArgs`, and key-location helpers. Tests are `tesGetCommittedBlockLength`, `testGetCommittedBlockLengthForInvalidBlock`, and `tesPutKeyResposne`.

## Control Flow

Setup opens client/SCM translator resources. Tests write or allocate blocks, query committed lengths through container protocol paths, assert invalid-block exceptions, and inspect put-key responses after key creation.

## State And Persistence Behavior

Committed block length is persisted in datanode block metadata and exposed through protocol calls. OM key metadata and SCM block/container state are mutated by writes and put-key operations.

## Dependencies And Integration Points

It connects Ozone client writes, SCM allocation, datanode block metadata, container protocol calls, and OM key commit flow.

## Risks And Test Signals

Failures signal mismatches between written chunk lengths and committed block metadata, bad invalid-block error mapping, or regressions in key finalization responses. The typo in method names is harmless but makes name-based test filtering less intuitive.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestGetCommittedBlockLengthAndPutKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestRatisPipelineLeader.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestRatisPipelineLeader.java

## Purpose

`TestRatisPipelineLeader` verifies that SCM pipeline metadata reflects Ratis leader identity and updates after leadership changes. It protects client routing assumptions that depend on pipeline leader information.

## Important APIs, Types, And Functions

The class starts a MiniOzoneCluster, obtains RATIS pipelines, and uses `Pipeline`, `PipelineManager`, and datanode/Ratis leader inspection. Tests are `testLeaderIdUsedOnFirstCall`, `testLeaderIdAfterLeaderChange`, and helper `verifyLeaderInfo`.

## Control Flow

Setup starts the cluster. The first test validates that initial pipeline retrieval includes leader ID. The second forces or waits for a leader change, retrieves pipeline metadata again, and verifies SCM reports the new leader. The helper compares SCM pipeline leader metadata with the Ratis group state.

## State And Persistence Behavior

Pipeline state is maintained in SCM and backed by Ratis leader election inside datanode pipelines. The test observes volatile leader state rather than durable key data.

## Dependencies And Integration Points

It integrates SCM pipeline manager, MiniOzoneCluster datanodes, Ratis consensus state, and pipeline metadata returned to clients.

## Risks And Test Signals

Failures indicate stale pipeline leader caching, missing leader detection on first lookup, or inability to refresh metadata after Ratis leadership changes. Timing around leader election is the main risk.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestRatisPipelineLeader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMDatanodeProtocolServer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMDatanodeProtocolServer.java

## Purpose

`TestSCMDatanodeProtocolServer` is a focused unit/integration test for command metadata returned by SCM's datanode protocol server. It verifies commands carry SCM term and deadline information.

## Important APIs, Types, And Functions

The single test `ensureTermAndDeadlineOnCommands` uses `SCMDatanodeProtocolServer`, SCM command builders, and command protobuf fields to ensure generated commands contain the expected term/deadline values.

## Control Flow

The test constructs or invokes command generation, then asserts the command metadata fields are populated. It does not need a full MiniOzoneCluster.

## State And Persistence Behavior

No durable state is changed. The validated state is transient command metadata used by datanodes to evaluate command freshness and leadership context.

## Dependencies And Integration Points

It integrates with SCM datanode protocol command construction and the datanode command-consumption contract.

## Risks And Test Signals

Missing term/deadline values can cause datanodes to execute stale commands or reject valid ones after leadership changes. Test failure is a direct signal that command metadata initialization changed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMDatanodeProtocolServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMDbCheckpointServlet.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMDbCheckpointServlet.java

## Purpose

`TestSCMDbCheckpointServlet` tests SCM DB checkpoint download servlet behavior for supported HTTP methods, excluded file handling, and invalid POST content type. It protects the HTTP checkpoint endpoint used for snapshot/checkpoint transfer.

## Important APIs, Types, And Functions

The class uses `SCMDbCheckpointServlet`, `DBCheckpoint`, servlet request/response mocks, `@ParameterizedTest` with `getHttpMethods`, and helper methods `setupHttpMethod`, `setupPostMethod`, `setupGetMethod`, and `doEndpoint`. It writes response output to a temporary file through a custom `ServletOutputStream`.

## Control Flow

Setup starts a MiniOzoneCluster and captures the SCM checkpoint servlet dependencies. Parameterized tests configure GET or POST request mocks, invoke the endpoint, and inspect the generated archive/output while excluding selected files. The invalid POST test asserts rejection of an unsupported content type.

## State And Persistence Behavior

The servlet snapshots SCM metadata into checkpoint files and streams archive bytes to HTTP responses. The test reads temporary output archives but does not intentionally mutate SCM logical state.

## Dependencies And Integration Points

It integrates SCM metadata store checkpointing, HTTP servlet request/response handling, archive generation, and checkpoint exclusion lists.

## Risks And Test Signals

Failures indicate broken DB checkpoint streaming, incorrect method/content-type handling, resource leaks in output streams, or archive content drift. The endpoint is operationally sensitive because followers and admins depend on checkpoint downloads.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMDbCheckpointServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMInstallSnapshot.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMInstallSnapshot.java

## Purpose

`TestSCMInstallSnapshot` validates local SCM checkpoint download and installation behavior outside the full HA follower-catch-up path. It ensures SCM can create a DB checkpoint and install it through snapshot utilities.

## Important APIs, Types, And Functions

The class uses `MiniOzoneCluster`, `StorageContainerManager`, `DBCheckpoint`, SCM metadata store APIs, and temporary directories. Tests are `testDownloadSnapshot`, `downloadSnapshot`, and `testInstallCheckPoint`.

## Control Flow

Setup starts a cluster. `testDownloadSnapshot` obtains a checkpoint and checks it is valid. `testInstallCheckPoint` downloads a checkpoint, installs it into a target location, and validates the installed checkpoint contents/state.

## State And Persistence Behavior

The test snapshots SCM RocksDB metadata and materializes checkpoint files on disk. Installation copies or restores checkpoint contents but does not represent normal client data mutation.

## Dependencies And Integration Points

It integrates SCM metadata store checkpoint creation, DB checkpoint lifecycle, local filesystem temp paths, and snapshot installation helper code used by HA catch-up.

## Risks And Test Signals

Failures reveal checkpoint corruption, missing files, bad cleanup/lifecycle handling, or restore-path incompatibility. Disk-path handling is the main edge case.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMInstallSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMInstallSnapshotWithHA.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMInstallSnapshotWithHA.java

## Purpose

`TestSCMInstallSnapshotWithHA` verifies SCM Ratis snapshot installation in a three-SCM HA cluster, including normal follower catch-up and rejection of old or corrupted checkpoints. The class is marked flaky for HDDS-5631.

## Important APIs, Types, And Functions

Setup configures SCM HA snapshot threshold and raft-log purge gap, starts a MiniOzone HA cluster with two active SCMs and one inactive SCM. Tests use `StorageContainerManager`, `SCMHAManagerImpl`, `SCMStateMachine`, `SCMMetadataStore`, `SCMDBDefinition`, `ContainerInfo`, `GenericTestUtils`, and a `DummyExitManager`. Helper `writeToIncreaseLogIndex` allocates containers until a target log index is reached.

## Control Flow

`testInstallSnapshot` advances the leader log, starts the inactive SCM, and waits for snapshot installation to bring it up to date. Failure tests attempt installing an old checkpoint or a corrupted checkpoint and assert errors/logging/exit behavior rather than successful catch-up.

## State And Persistence Behavior

The tests mutate SCM Ratis logs, snapshots, metadata tables, and container allocation records. Follower state is rebuilt from snapshots, and corrupted/old checkpoint paths validate persistence safeguards.

## Dependencies And Integration Points

It integrates SCM HA Ratis, snapshot purge/install logic, metadata store checkpointing, container allocation, and process-exit handling.

## Risks And Test Signals

Failures indicate follower catch-up gaps, snapshot-index validation bugs, checkpoint corruption handling regressions, or unsafe process-exit behavior. Timing and log-purge thresholds are sensitive.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMInstallSnapshotWithHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMMXBean.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMMXBean.java

## Purpose

`TestSCMMXBean` validates SCM JMX/MXBean exposure for SCM status and container state counts in a non-HA cluster. It ensures monitoring data matches SCM internal state.

## Important APIs, Types, And Functions

The abstract class implements `NonHATests.TestCase`. It queries platform `MBeanServer` object names, `StorageContainerManager`, SCM container manager, and JMX `TabularData`. Tests are `testSCMMXBean` and `testSCMContainerStateCount`; helper `verifyEquals` compares tabular rows to expected maps.

## Control Flow

Setup stores SCM from the cluster. Tests retrieve JMX attributes, compare SCM ID/cluster ID/service state fields, then compare container state counts from the MXBean against container manager values.

## State And Persistence Behavior

No new persistent state is the target. Container counts reflect SCM's in-memory and persisted container metadata. JMX exposes monitoring snapshots.

## Dependencies And Integration Points

It integrates SCM server state, Java Management Extensions, container manager state-count aggregation, and non-HA test fixtures.

## Risks And Test Signals

Failures indicate monitoring drift, broken MXBean registration/object names, or inconsistent container count aggregation. These are operational observability regressions rather than client data-path failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMNodeManagerMXBean.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMNodeManagerMXBean.java

## Purpose

`TestSCMNodeManagerMXBean` verifies JMX exposure from SCM's node manager, including disk usage and node-count information. It protects monitoring consistency for datanode health and capacity views.

## Important APIs, Types, And Functions

The abstract non-HA class uses `StorageContainerManager`, platform `MBeanServer`, JMX `TabularData`/`CompositeData`, and node manager methods `getNodeInfo()` and `getNodeCount()`. Helpers convert node-count objects into maps and compare tabular data to expected maps.

## Control Flow

Setup captures SCM. `testDiskUsage` reads the node-manager MXBean disk-usage attribute and compares it to SCM node manager data. `testNodeCount` reads node-count JMX data and compares it with internal counts grouped by state/status.

## State And Persistence Behavior

The test observes node manager state populated from datanode registration and reports. It does not mutate persistent metadata.

## Dependencies And Integration Points

It integrates SCM node manager, datanode reporting, Java JMX, and non-HA test scaffolding.

## Risks And Test Signals

Failures show MXBean schema drift, key/name mismatches in tabular data, or divergence between internal and exposed node metrics. Report timing can affect disk-usage visibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMNodeManagerMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMSnapshot.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMSnapshot.java

## Purpose

`TestSCMSnapshot` tests SCM HA snapshot creation and restart recovery. It ensures SCM transaction indexes advance after replicated metadata mutations and survive SCM restart.

## Important APIs, Types, And Functions

Setup configures pipeline creation interval and `OZONE_SCM_HA_RATIS_SNAPSHOT_THRESHOLD`, then starts a MiniOzoneCluster with three datanodes. The test uses `StorageContainerManager`, `ContainerManager`, `PipelineManager`, `RatisReplicationConfig`, `ContainerInfo`, and transaction info from the SCM HA DB transaction buffer.

## Control Flow

The test records initial transaction info, allocates containers through container manager and pipeline manager, verifies transaction index advancement, restarts SCM, then asserts the post-restart transaction index is at least the snapshot index and that allocated containers/pipelines remain accessible.

## State And Persistence Behavior

Container and pipeline records are persisted through SCM HA/Ratis state and snapshots. Restart validates recovery from on-disk DB and Ratis snapshot data.

## Dependencies And Integration Points

It integrates SCM HA transaction buffering, Ratis snapshot thresholding, container allocation, pipeline management, and MiniOzoneCluster restart.

## Risks And Test Signals

Failures indicate snapshot threshold misbehavior, lost transaction indexes, or missing container/pipeline metadata after restart. Because snapshots are threshold-driven, allocation count and timing matter.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSecretKeySnapshot.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSecretKeySnapshot.java

## Purpose

`TestSecretKeySnapshot` verifies that SCM symmetric secret keys are transferred to a lagging HA follower through snapshot installation and continue to synchronize after the follower rejoins.

## Important APIs, Types, And Functions

The test creates a secure MiniKdc-backed Ozone HA cluster with block tokens enabled, short secret-key rotation durations, snapshot threshold/purge settings, and one inactive SCM. It uses `SecretKeyManager`, `ManagedSecretKey`, `SCMStateMachine`, `StorageContainerManager`, and helper `writeToIncreaseLogIndex`.

## Control Flow

Setup configures Kerberos principals/keytabs, starts two active SCMs plus an inactive SCM, and waits for readiness. The test waits until the leader has rotated keys, advances the Ratis log via container allocations, starts the inactive follower, waits for its state machine to apply the snapshot, then compares follower keys with leader keys and verifies later rotations replicate normally.

## State And Persistence Behavior

The central persistent state is SCM's secret-key table, Ratis log, snapshot checkpoint, and container allocation records used to advance log index. Follower state is restored from snapshot while it missed live rotations.

## Dependencies And Integration Points

It integrates MiniKdc security setup, block-token secret key management, SCM HA snapshot install, Ratis state-machine indexes, and container manager mutations.

## Risks And Test Signals

Failures indicate missing secret-key table data in snapshots, follower pause/catch-up problems, or post-snapshot replication breakage. Time-based key rotation and security setup are flakiness risks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSecretKeySnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSecretKeysApi.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSecretKeysApi.java

## Purpose

`TestSecretKeysApi` validates the secure SCM secret-key RPC API. It covers successful key retrieval and rotation, lookup by key ID, failover consistency, authorization denial, and behavior when Hadoop security authorization is disabled.

## Important APIs, Types, And Functions

The final class sets up MiniKdc, Kerberos principals/keytabs, secure Ozone configuration, and a MiniOzone HA cluster. It uses `SecretKeyProtocol`, `ManagedSecretKey`, `getSecretKeyClientForDatanode`, `StorageContainerManager`, `RemoteException`, and `AuthorizationException`. Helpers include `setSecureConfig`, `startCluster`, `getSecretKeyProtocol`, and `enableBlockToken`.

## Control Flow

Setup starts KDC and creates credentials. `testSecretKeyApiSuccess` enables block tokens, shortens rotation windows, waits for multiple active keys, checks current/all/by-ID calls, then verifies unauthorized users are rejected. `testSecretKeyApi` checks default single-key behavior. `testSecretKeyAfterSCMFailover` shuts down the active SCM and compares keys after failover. `testSecretKeyWithoutAuthorization` confirms access when authorization is disabled.

## State And Persistence Behavior

Secret keys are persisted in SCM metadata and replicated through HA. Kerberos keytabs and MiniKdc state are temporary test artifacts. Failover validates key-list persistence across leaders.

## Dependencies And Integration Points

It integrates Hadoop security, MiniKdc, SCM secret-key protocol, block-token configuration, SCM HA, and client RPC authorization.

## Risks And Test Signals

Failures indicate security misconfiguration, unauthorized protocol access, key rotation bugs, HA replication gaps, or stale secret-key clients after failover. The happy-case test is marked flaky for HDDS-8900.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSecretKeysApi.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestStorageContainerManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestStorageContainerManager.java

## Purpose

`TestStorageContainerManager` is a broad integration test for core SCM behavior: initialization, authorization, block deletion, datanode registration after reinitialization, topology-aware heartbeat processing, close-container command recovery, container-report queue behavior, and SCM info reporting.

## Important APIs, Types, And Functions

The class uses `MiniOzoneCluster`, `StorageContainerManager`, `SCMClientProtocolServer`, `SCMStorageConfig`, `DeletedBlockLog`, `SCMBlockDeletingService`, `NodeManager`, `ReplicationManager`, `EventQueue`, `FixedThreadPoolWithAffinityExecutor`, `ContainerReportHandler`, `IncrementalContainerReportHandler`, datanode stores, and Ratis group validation. Helpers configure topology/block deletion, create delete transactions, inspect datanode DB tables, validate Ratis storage, and locate container servers.

## Control Flow

The main `test` starts a cluster, runs block-deletion, RPC-permission, and heartbeat-topology checks, then stops/reinitializes SCM and verifies old datanodes react to mismatched cluster IDs. Separate tests cover deletion throttling, SCM initialization/failure/info, close-container commands after SCM restart, dropped full container-report events, long queue/execution metrics, and non-dropping incremental report queues.

## State And Persistence Behavior

This file exercises SCM storage directories, Ratis group directories, SCM DB metadata, OM key locations, deleted-block transaction logs, datanode block/delete transaction tables, node heartbeat timestamps, container lifecycle state, event queues, and command queues. Several tests deliberately restart, delete, or reinitialize SCM storage to validate persistence safeguards.

## Dependencies And Integration Points

It integrates SCM client protocol, security authorization, OM/key creation helpers, datanode heartbeat and report dispatch, block deletion service, topology mapping, replication manager, event framework, and datanode RocksDB schemas.

## Risks And Test Signals

Risks include broad test coupling, sleeps around asynchronous reports, and internal-state mocking. Failures are high-signal for SCM lifecycle, metadata persistence, delete-block processing, heartbeat/report backpressure, or admin authorization regressions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestStorageContainerManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestStorageContainerManagerHA.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestStorageContainerManagerHA.java

## Purpose

`TestStorageContainerManagerHA` validates SCM HA bootstrap behavior and leadership metrics in clusters with multiple OMs and SCMs. It covers primordial SCM startup, adding SCMs, and metrics that expose leadership state.

## Important APIs, Types, And Functions

The class uses MiniOzone HA builder APIs, `StorageContainerManager`, SCM bootstrap/deactivation utilities, and metrics assertions. Tests are `testPrimordialSCM`, `testBootStrapSCM`, and `testSCMLeadershipMetric`; setup initializes HA cluster parameters and teardown shuts the cluster down.

## Control Flow

Initialization builds a HA topology. The primordial test validates initial SCM HA state. The bootstrap test brings additional SCMs into the service and checks cluster readiness. The metrics test reads leadership metrics and confirms leader/follower reporting aligns with actual SCM roles.

## State And Persistence Behavior

The tests mutate SCM HA membership, SCM storage initialization, Ratis peer state, and metrics values. Bootstrap persists SCM identity and service membership.

## Dependencies And Integration Points

It integrates MiniOzone HA orchestration, SCM bootstrap flow, Ratis leadership, and metrics registration.

## Risks And Test Signals

Failures indicate bootstrap regressions, incorrect primordial SCM assumptions, role-reporting drift, or HA metrics not matching Ratis leadership. Cluster startup and leader election timing are key risks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestStorageContainerManagerHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestStorageContainerManagerHAWithAllRunning.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestStorageContainerManagerHAWithAllRunning.java

## Purpose

`TestStorageContainerManagerHAWithAllRunning` validates that a fully running SCM HA ensemble stays synchronized while serving client writes. It checks all SCM roles, applied indexes, and HA metrics after data-plane activity.

## Important APIs, Types, And Functions

The abstract class implements `HATests.TestCase`, using the provided HA cluster. It relies on Ozone object-store put-key helpers, `StorageContainerManager`, SCM Ratis role/state access, and metric validation helpers. Key helpers are `doPutKey`, `getLastAppliedIndex`, `areAllScmInSync`, `assertRatisRoles`, and `checkSCMHAMetricsForAllSCMs`.

## Control Flow

`testAllSCMAreRunning` verifies all SCMs are active, writes a key through OM/client paths, waits until followers catch up to the leader's last-applied index, then validates Ratis roles and metrics across the ensemble.

## State And Persistence Behavior

The test persists a key, SCM allocation metadata, and replicated SCM Ratis log entries. It observes volatile role state and durable applied indexes on each SCM.

## Dependencies And Integration Points

It integrates HA test fixtures, Ozone client writes, OM-to-SCM allocation, SCM Ratis replication, and SCM HA metrics.

## Risks And Test Signals

Failures point to follower lag, missing replicated SCM metadata, role confusion, or incorrect HA metrics. The synchronization wait depends on Ratis progress and cluster load.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestStorageContainerManagerHAWithAllRunning.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestWatchForCommit.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestWatchForCommit.java

## Purpose

`TestWatchForCommit` validates Ozone output stream handling of Ratis watch-for-commit behavior. It covers normal key writes, retry failure, timeout, and group-mismatch cases for both majority and all-committed watch levels. The class is marked flaky for HDDS-5818.

## Important APIs, Types, And Functions

The test configures small chunk/flush/block sizes, MiniOzoneCluster, Ozone client volumes/buckets, and Ratis client settings. Parameterized tests use `RaftProtos.ReplicationLevel.MAJORITY_COMMITTED` and `ALL_COMMITTED`. Helpers include `createKey` and `validateData`.

## Control Flow

Setup starts a cluster and bucket. `testWatchForCommitWithKeyWrite` writes data and validates it can be read. Parameterized retry and timeout tests configure failure conditions around Ratis commit watching and assert expected exceptions/behavior. The group mismatch test simulates a commit watch against the wrong group and validates error handling. Cleanup shuts down client and cluster.

## State And Persistence Behavior

Successful paths persist OM key metadata, SCM block allocations, datanode chunks, and Ratis commit state. Failure paths exercise partial writes, retries, and exception handling without accepting corrupt committed data.

## Dependencies And Integration Points

It integrates Ozone output streams, SCM allocation, datanode Ratis pipelines, Ratis watch APIs, and client readback validation.

## Risks And Test Signals

Failures indicate incorrect commit-level semantics, lost data after successful writes, bad retry/timeout propagation, or unsafe handling of Ratis group mismatches. Timing and injected failure conditions make the suite sensitive.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestWatchForCommit.java -->
