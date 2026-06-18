# subset-b-008081 Research

Grouped research for Apache Ozone integration tests covering stream reads, container report handling, replication, EC recovery, datanode command handlers, container metrics, and OzoneContainer service behavior. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestStreamRead.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestStreamRead.java

Purpose: This integration test validates `StreamBlockInputStream` behavior against the older non-stream block read path and direct block-file reads. It writes a 128 MB key into a one-datanode MiniOzoneCluster, then checks that stream reads return the same bytes and MD5 digest as the local container block file across several checksum and buffer sizes.

Important APIs and types: The test configures `OzoneClientConfig.setStreamReadBlock`, `ClientConfigForTesting`, `MiniOzoneCluster`, `TestBucket`, `OzoneBucket.createStreamKey`, `KeyInputStream.isStreamBlockInputStream`, `ClientProtocol.getKeyInfo`, `OmKeyInfo`, `OmKeyLocationInfo`, `BlockID`, `ContainerData`, and `ContainerLayoutVersion.FILE_PER_BLOCK.getChunkFile`. `SizeInBytes`, `CheckedBiConsumer`, `MessageDigest`, and `CodecBuffer` support sizing, repeated operations, and digest verification.

Control flow: `newCluster` builds a quiet one-node cluster with fixed block, chunk, flush, max buffer, and checksum settings. Each test method calls `runTestReadKey` with a different bytes-per-checksum value. The runner starts the cluster, creates stream and non-stream clients from cloned configs, writes a dummy key to warm up the client path, then repeatedly creates the target key with different application write buffer sizes. For every key, it discovers the single OM location, resolves the backing block file from the datanode container set, computes an expected MD5 from the file, shuffles stream-read, non-stream-read, and file-read operations, and verifies full-length reads.

State and persistence behavior: The durable state under test is the key's file-per-block chunk file on the datanode volume and the OM key-location metadata that maps the key to one block/container. The test asserts the block file exists and has `BLOCK_SIZE`, then reads the same persistent bytes through three independent surfaces. No SCM replication behavior is expected because the cluster has one datanode and replication factor one.

Dependencies and integration points: It covers the client RPC read stack, OM key lookup, datanode container storage layout, checksum configuration, and client stream buffering. It also establishes a performance-style signal via throughput prints, although correctness comes from byte counts and MD5 equality.

Risks: The key size and repeated reads make the test relatively expensive. It assumes one location, one block, file-per-block layout, and `BLOCK_SIZE == KEY_SIZE`, so future layout or multipart allocation changes would need test updates. The random write buffer is reused until the key is filled, which is fine for equality checks but not broad content diversity.

Test signals: Strong signals are `KeyInputStream.isStreamBlockInputStream` true/false for the two client configs, exact key-size byte counts, block-file existence and size, and MD5 equality between streamed reads, non-stream reads, and file reads for checksum sizes 512 bytes, 16 KB, and 256 KB.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestStreamRead.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/TestContainerReplication.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/TestContainerReplication.java

Purpose: This class tests Ozone container replication and EC replica remapping in real MiniOzoneCluster deployments. It verifies under-replication recovery for RATIS containers under multiple placement policies, imported-container state after datanode restart, and EC read recovery when replica indexes move between datanodes while a stream is already open.

Important APIs and types: The suite uses `MiniOzoneCluster`, `OzoneClient`, `ObjectStore`, `TestDataUtil.createKey`, `OmKeyArgs`, `OmKeyInfo`, `OmKeyLocationInfo`, `RatisReplicationConfig`, `ECReplicationConfig`, `SCMContainerPlacement*` policies, `SCMContainerPlacementMetrics`, `ReplicationManagerConfiguration`, `ContainerProtocolCalls.readChunk`, `OzoneContainer`, and `ContainerProtos.ContainerType.KeyValueContainer`. The shared helpers `waitForContainerClose`, `waitForReplicaCount`, and `isContainerClosed` come from `TestHelper`.

Control flow: The parameterized RATIS test builds a five-datanode cluster with short stale/dead intervals and a selected placement policy. It writes a small replicated key, records placement metrics, closes the container, shuts down one pipeline node, waits for replicas to fall to two, then waits for replication manager to restore three replicas and checks placement metrics advanced. `testImportedContainerIsClosed` forces replication to import a container onto a restarted fourth node and asserts the imported copy is closed. The EC test writes an RS-3-2 key, maps replica indexes to datanodes, reads the first stripe, stops replication manager, deletes replica indexes 1 and 3 from selected nodes, restarts replication manager to reconstruct missing indexes, then verifies the original open input stream handles moved replicas and reports expected failed read-chunk retries.

State and persistence behavior: The tests mutate container placement in SCM, container replica records, and on-disk datanode container directories. `deleteContainer` directly invokes the datanode key-value container handler with force, removes local container state, and triggers heartbeat so SCM sees the new replica set. EC state is especially important: the OM key location pipeline still maps replica indexes, while SCM replication changes which datanode hosts an index.

Dependencies and integration points: Coverage spans OM key metadata, SCM placement policies and metrics, ReplicationManager, datanode heartbeat/report propagation, container import, EC reconstruction, and client read fallback. Mockito static mocking wraps `ContainerProtocolCalls.readChunk` to count replica-index read failures while preserving real behavior.

Risks: The tests are timing-sensitive and one EC case is marked flaky. They rely on specific replica-index assignments and a fixed 3-2-1k EC layout. Static mocking of a low-level read path is powerful but can obscure unrelated failures if call signatures change.

Test signals: Expected signals include restored replica counts, one extra datanode request and success in placement metrics, imported replica closed state, zero read failures before replica movement, failure counts for indexes 1 and 3 after movement, and byte-for-byte EC read equality with the original data.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/TestContainerReplication.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/TestContainerReportHandling.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/TestContainerReportHandling.java

Purpose: This parameterized integration test verifies SCM handling of full container reports for non-empty replicas whose SCM container is already in `DELETING` or `DELETED`. It protects the rule that such replicas should be deleted when block commit sequence IDs are eligible for RATIS, while EC ignores the bcsid comparison.

Important APIs and types: The test uses `MiniOzoneCluster`, `OzoneClient`, `ReplicationConfig`, `TestHelper.ReplicationInput`, `TestDataUtil.createKey`, `OmKeyArgs`, `OmKeyInfo`, `ContainerID`, `ContainerManager`, `HddsProtos.LifeCycleState`, `HddsProtos.LifeCycleEvent`, `waitForContainerClose`, `waitForContainerStateInSCM`, and `GenericTestUtils.waitFor`.

Control flow: `delStatesAndReplication` creates four cases from `DELETING` and `DELETED` crossed with RATIS and EC replication inputs. The test creates a cluster sized for the selected replication type, writes a small key, looks up the key's first location, waits for the local and SCM container state to become closed, and then drives SCM state transitions manually through `ContainerManager.updateContainerState`. For the `DELETED` case it applies `DELETE` followed by `CLEANUP`. It restarts every datanode in the key pipeline to force full container reports, then waits until SCM's replica set for the container becomes empty.

State and persistence behavior: SCM's in-memory and persisted container state transitions from closed to deleting or deleted, while datanodes retain closed non-empty replicas until restart sends a report. The observable final state is that `ContainerManager.getContainerReplicas(containerID)` is empty. The test also records and deletes the cluster base directory in `finally`, ensuring local MiniOzone storage is cleaned even after failures.

Dependencies and integration points: It exercises OM key lookup, SCM lifecycle management, datanode restart and full report generation, SCM report processing, and delete-replica command scheduling. It depends on `TestHelper.ReplicationInput` for correct datanode counts and replication configs.

Risks: The test waits up to 180 seconds for replica cleanup and assumes datanode restarts reliably trigger full reports. It directly mutates SCM state with `ContainerManager`, which is intentional but bypasses higher-level deletion flows. The core assertion is SCM-side replica disappearance, not explicit datanode directory deletion.

Test signals: The key signals are non-empty initial replica sets, exact SCM lifecycle state after `DELETE` and optional `CLEANUP`, datanode restart for each pipeline node, and eventual empty SCM replica tracking for both RATIS and EC cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/TestContainerReportHandling.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/TestContainerReportHandlingWithHA.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/TestContainerReportHandlingWithHA.java

Purpose: This is the SCM HA counterpart to `TestContainerReportHandling`. It verifies that leader-driven deletion handling for `DELETING` or `DELETED` containers works when the cluster has multiple StorageContainerManagers and the closed state must be visible on every SCM before deletion is driven.

Important APIs and types: It uses `MiniOzoneHAClusterImpl`, `MiniOzoneCluster.newHABuilder`, `StorageContainerManager`, `ContainerManager`, `ContainerID`, `ReplicationConfig`, `TestHelper.ReplicationInput`, `waitForContainerClose`, `waitForContainerStateInSCM`, `HddsProtos.LifeCycleState`, `HddsProtos.LifeCycleEvent`, and the same OM lookup types used by the non-HA test.

Control flow: The parameter source crosses desired final deletion state with RATIS and EC replication. The test creates a three-SCM HA cluster with one OM and enough datanodes for the selected replication. After writing and closing a key container, it calls `waitForContainerStateInAllSCMs` to ensure every SCM has the closed container state. It then updates the leader's `ContainerManager` through `DELETE` and optional `CLEANUP`, restarts all datanodes that host the key, and waits until the leader's replica set for the container is empty.

State and persistence behavior: The test stresses replicated SCM metadata and leader state. Container lifecycle state is expected to be present on all SCMs before the delete transition. Replica tracking is then validated on the leader after reports from restarted datanodes. Like the non-HA version, it cleans the cluster base directory manually in `finally`.

Dependencies and integration points: This covers HA builder configuration, SCM leader access via `cluster.getScmLeader()`, OM key metadata, datanode full container reports, and HA propagation of container lifecycle state. The helper method iterates `cluster.getStorageContainerManagersList()` to avoid asserting delete behavior before followers have observed closure.

Risks: The test does not explicitly fail over the SCM leader, so it covers HA state propagation but not leader change during deletion. It assumes the current leader remains valid while commands are scheduled. Timing is similar to the non-HA test and can be affected by report intervals and HA transaction flush latency.

Test signals: Strong signals include closed state observed on all SCMs, exact leader state after `DELETE` and optional `CLEANUP`, datanode restarts for all replica hosts, and eventual empty leader-side replica records for both RATIS and EC replication inputs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/TestContainerReportHandlingWithHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/TestECContainerRecovery.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/TestECContainerRecovery.java

Purpose: This integration suite validates EC container reconstruction, over-replication cleanup, and recovery timeout behavior. It runs a long-lived ten-datanode MiniOzoneCluster configured for small EC chunks and short heartbeat/report intervals, then manipulates datanode availability and replication manager scheduling around EC containers.

Important APIs and types: Key types include `ECReplicationConfig`, `DefaultReplicationConfig`, `ECKeyOutputStream`, `Pipeline`, `ContainerInfo`, `ContainerID`, `ContainerReplica`, `ReplicationManager`, `StorageContainerManager`, `ReconstructECContainersCommandHandler`, `ECReconstructionCoordinator`, `DatanodeConfiguration`, `OzoneClientConfig`, and `GenericTestUtils` reflection helpers. Configuration touches checksum, block size, heartbeat, container report, recovering-container timeout, and replication-manager intervals.

Control flow: `init` builds shared cluster state, disables checksums, sets EC-friendly client buffers, creates a volume, and initializes deterministic input chunks. `testContainerRecoveryOverReplicationProcessing` writes an EC key, finds the SCM container tied to the EC pipeline, shuts down one datanode to close the pipeline and container, stops replication manager to observe under-replication at four replicas, restarts it to reconstruct five, stops it again, restarts the original datanode to create six replicas, then restarts replication manager and waits for replica state repair and count back to five. `testECContainerRecoveryWithTimedOutRecovery` lowers each datanode container-set recovering timeout, mocks each reconstruction coordinator, waits until the target reconstructed container becomes unhealthy, then verifies the timed-out recovering container is removed.

State and persistence behavior: The tests directly observe SCM replica counts, SCM lifecycle state compared with datanode replica state, datanode container-set entries, and recovering-container timeout state. The timeout test temporarily changes `ContainerSet.setRecoveringTimeout` on every datanode and restores the original timeout values after validation.

Dependencies and integration points: Coverage includes client EC write allocation, SCM container manager, replication manager under/over-replication processors, datanode shutdown/restart semantics, command handler reconstruction, and datanode scrub logic for recovering containers.

Risks: Shared static cluster state improves speed but makes tests sensitive to prior failure cleanup. Reflection and coordinator mocking are coupled to private field names. Replica-count waits use long timeouts because they depend on asynchronous replication manager and heartbeat loops.

Test signals: Expected signals are SCM container state matching closed replica state, counts of four, five, six, and five replicas at the appropriate stages, no mismatched replica states before over-replication cleanup completes, reconstruction coordinator invocation after an unhealthy recovering state, and eventual removal of the timed-out recovering container from the reconstructed datanode.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/TestECContainerRecovery.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/TestHelper.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/TestHelper.java

Purpose: `TestHelper` is a shared utility class for Ozone container integration tests. It centralizes key creation, data validation, container and pipeline close waits, datanode container lookup, replica counting, SCM state waits, and replication input definitions used by RATIS and EC tests.

Important APIs and types: The helper wraps `ObjectStore`, `OzoneOutputStream`, `OzoneDataStreamOutput`, `KeyOutputStream`, `KeyDataStreamOutput`, `BlockOutputStreamEntry`, `BlockDataStreamOutputEntry`, `MiniOzoneCluster`, `MiniOzoneHAClusterImpl`, `StorageContainerManager`, `ContainerManager`, `ContainerInfo`, `ContainerReplica`, `Pipeline`, `XceiverServerRatis`, `StateMachine`, and `GenericTestUtils.waitFor`. The nested `ReplicationInput` enum maps RATIS to three datanodes and `RatisReplicationConfig.getInstance(THREE)`, and EC to five datanodes and `new ECReplicationConfig(3, 2)`.

Control flow: Container presence and closed checks scan cluster datanode services for a matching `DatanodeDetails` and inspect `ContainerSet`. Key helpers create RATIS or EC keys and stream keys through Ozone client APIs. `waitForContainerClose` overloads extract container IDs from output-stream entries, locate pipelines through SCM, wait for containers to appear and be open on all pipeline nodes, fire `SCMEvents.CLOSE_CONTAINER`, then wait until each datanode reports closed container data. Pipeline-close helpers ask SCM's pipeline manager to close pipelines, then poll each datanode's Ratis server until the Raft group is gone. Replica-count waits poll SCM container replica records.

State and persistence behavior: The helper reads live datanode `ContainerSet` state, SCM container metadata, pipeline manager state, and Ratis server group state. `validateData` performs durable data verification by reading a key and comparing file hashes. The helper does not persist state itself, but it drives state transitions through SCM event queue and pipeline manager APIs.

Dependencies and integration points: It is a cross-cutting fixture for client I/O, OM key block streams, SCM container/pipeline managers, datanode state machines, Ratis write channels, HA SCM leader selection, and Ozone metrics/logging through assertions.

Risks: Helpers assume key output streams are `KeyOutputStream` or `KeyDataStreamOutput` implementations and write channels are `XceiverServerRatis` for pipeline close validation. Some waits have fixed timeouts that can be tight on slow environments. Direct firing of close events bypasses higher-level operational flows by design.

Test signals: Reusable signals include boolean container presence/closed status, exact replica count in SCM, matching read/write hashes, pipeline Raft group disappearance, SCM lifecycle state equality, and non-empty extracted container ID lists from client streams.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/TestHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestBlockDeletion.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestBlockDeletion.java

Purpose: This integration suite validates the end-to-end deleted-block pipeline from OM key deletion through SCM deleted-block log, datanode delete-block command handling, local container DB cleanup, SCM transaction commitment, container statistics updates, and final empty-container deletion. It covers RATIS and EC key layouts plus several edge cases around restart and invalid replica statistics.

Important APIs and types: The test uses `MiniOzoneCluster`, `OzoneManagerProtocol.deleteKey`, `SCMBlockDeletingService`, `DeletedBlockLogImpl`, `ScmBlockDeletingServiceMetrics`, `ReplicationManager`, `ContainerManager`, `ContainerStateManager`, `ContainerReplica`, `ContainerSet`, `KeyValueContainerData`, `BlockUtils.getDB`, `DBHandle`, `Table<String, BlockData>`, `OzoneTestUtils`, `OmKeyLocationInfoGroup`, and `GenericTestUtils`. Configuration reduces block deletion, heartbeat, report, command status, and expired replica op intervals.

Control flow: `init` creates a three-datanode cluster with fast deletion intervals and disabled frequent replication-manager processing. `testBlockDeletion` writes a key, looks up block locations, waits until block table entries exist on datanodes, verifies no delete transactions, deletes the key, confirms open containers do not delete blocks, closes all containers, waits until block and deleting-block keys disappear from every datanode DB, checks delete transaction IDs match SCM, waits for deleted-block transactions to be removed from SCM DB, restarts a datanode, and checks metrics consistency. Other tests verify container used bytes and key counts fall to zero after deletion, container `isEmpty` survives datanode restart, invalid key-count replicas do not block container deletion, and parallel delete command processing drains multiple deleted blocks.

State and persistence behavior: The suite is heavily persistence-oriented. It inspects datanode RocksDB block data tables, SCM deleted-block transaction table, SCM container table state, datanode `KeyValueContainerData.deleteTransactionId`, SCM `ContainerInfo.deleteTransactionId`, replica `isEmpty`, pending deletion block counts, and persisted `DELETED` container lifecycle state after explicit SCM DB flushes.

Dependencies and integration points: It covers OM delete metadata, SCM block manager, SCM HA transaction buffer, datanode command dispatcher, block deleting service, key-value container DB schema, replication manager empty-container deletion, metrics counters, event queue processing, and log output from deletion handlers.

Risks: Several waits depend on asynchronous deletion, report, and command-status loops; one parameterized test is marked flaky. It assumes all involved containers are key-value containers and accesses datanode 0 for some container state checks. Some assertions use sleeps before waits, making runtime sensitive to environment speed.

Test signals: Strong signals include block table entry presence before deletion, block and deleting-block key absence after deletion, non-zero and matching delete transaction IDs only for containers with deleted blocks, deleted-block transaction table cleanup, metric created/completed/sent/success/failure relationships, zero used bytes/key counts, zero pending deletion blocks, persisted `DELETED` lifecycle state, and valid retry-count log patterns.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestBlockDeletion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestCloseContainerByPipeline.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestCloseContainerByPipeline.java

Purpose: This class tests datanode close-container command handling for containers associated with SCM pipelines. It validates handler invocation, standalone one-node closure, RATIS three-node closure, DB separation across pipeline members, and the quasi-closed to closed transition path.

Important APIs and types: It uses `MiniOzoneCluster`, `OzoneClient`, `ObjectStore`, `OzoneOutputStream`, `OmKeyArgs`, `OmKeyLocationInfo`, `ContainerInfo`, `Pipeline`, `CloseContainerCommand`, `SCMCommand`, `CommandHandler`, `NodeManager.addDatanodeCommand`, `KeyValueContainerData`, `BlockUtils.getDB`, `DBHandle`, and datanode `ContainerData` state predicates.

Control flow: The class starts one shared ten-datanode cluster with low owner-container count and expanded pipeline limits, creates a volume and bucket, then each test writes a key to create an open container. `testIfCloseContainerCommandHandlerIsInvoked` finds the target datanode and close handler, queues a `CloseContainerCommand`, waits for the container to close, and asserts invocation count increased. The standalone test closes a one-replica RATIS container and verifies later pipeline closure does not reopen or alter closed state. The RATIS test sends close commands to each of three pipeline datanodes, captures each local container DB handle, asserts distinct DB stores, and waits for every replica to close. The quasi-close test closes the pipeline first, waits for quasi-closed state, then sends a forced close command.

State and persistence behavior: The observable state is local datanode `ContainerData` transitioning from open to closed or quasi-closed, plus container metadata DB handles for each RATIS replica. SCM state is used to locate pipelines and provide the leader term on queued commands, but assertions focus on datanode container state.

Dependencies and integration points: It covers SCM command queuing, datanode command dispatcher, close container handler, Ratis group/pipeline closure behavior, OM key location lookup, and key-value container metadata DB access.

Risks: The class uses a shared static cluster, so failed tests can leave state for later methods. The quasi-close test is marked unhealthy. Some comments mention standalone even though current writes use RATIS with factor one, reflecting historical terminology.

Test signals: Signals include close-handler invocation count growth, closed state on target datanodes, closed state persisting after pipeline close, distinct RocksDB metadata stores for RATIS replicas, and forced close moving a quasi-closed container to closed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestCloseContainerByPipeline.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestCloseContainerHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestCloseContainerHandler.java

Purpose: This compact integration test verifies that a single datanode receiving a `CloseContainerCommand` closes an open container created by a client write. It focuses on the basic command-handler path without the broader multi-pipeline cases in `TestCloseContainerByPipeline`.

Important APIs and types: The file uses `MiniOzoneCluster`, `OzoneConfiguration`, `OzoneClientFactory`, `ObjectStore`, `OzoneOutputStream`, `OmKeyArgs`, `OmKeyLocationInfo`, `ContainerID`, `ContainerInfo`, `Pipeline`, `CloseContainerCommand`, `SCMCommand`, `NodeManager.addDatanodeCommand`, and `ContainerData.isOpen`.

Control flow: `setup` builds a one-datanode MiniOzoneCluster, sets a 1 GB container size, disables safemode pipeline creation, removes minimum RATIS volume free-space pressure, and waits for a factor-one pipeline. The test writes a small key, looks up its block location through OM, resolves the SCM container and pipeline, asserts the datanode container is not closed, queues a `CloseContainerCommand` with the SCM leader term, waits until `isContainerClosed` returns true, and asserts the final state.

State and persistence behavior: The test observes local datanode container state in `ContainerSet`. A successful command transitions the key-value container out of open state, which also implies local container metadata has been updated by the handler. The test does not inspect SCM lifecycle state or persisted DB contents.

Dependencies and integration points: Coverage is the command path from SCM node manager queue to datanode command dispatcher and close handler, with OM and SCM lookup used only to find the target container and pipeline. Configuration touches safemode and volume free-space thresholds so the single-node cluster can create the needed pipeline.

Risks: The OM lookup uses `StandaloneReplicationConfig.getInstance(ONE)` for a key created with RATIS factor one, which relies on compatible lookup behavior in this test path. The helper method treats any non-open state as closed, so it would also pass for quasi-closed states.

Test signals: The main signal is a transition from `ContainerData.isOpen() == true` to false within five seconds after the command is queued to the datanode ID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestCloseContainerHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestDeleteContainerHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestDeleteContainerHandler.java

Purpose: This integration suite validates `DeleteContainerCommandHandler` behavior for open, closed, empty, non-empty, force-deleted, and locally inconsistent key-value containers. It specifically checks the safety rules around deleting containers when RocksDB state and chunk-directory contents disagree.

Important APIs and types: The suite uses `MiniOzoneCluster`, `DeleteContainerCommand`, `CloseContainerCommand`, `NodeManager`, `ContainerMetrics`, `KeyValueContainer`, `KeyValueHandler`, `KeyValueContainerData`, `BlockUtils.getDB`, `DBHandle`, `Table<String, BlockData>`, `BatchOperation`, `OzoneTestUtils.flushAndWaitForDeletedBlockLog`, `OzoneTestUtils.waitBlockDeleted`, `ContainerData`, and `FileUtils` for chunk file manipulation.

Control flow: A shared one-datanode cluster and volume/bucket are created in `setup`. Helper `createKey` writes a small RATIS factor-one key, and `getContainerID` resolves its container through OM. Tests close containers either through `OzoneTestUtils.closeAllContainers` or explicit `CloseContainerCommand`, optionally delete keys to mark containers empty, manipulate chunk directories by touching or deleting files, clear block-related DB tables, and then queue `DeleteContainerCommand` with force true or false. They poll for deletion from the datanode `ContainerSet`, inspect logs for expected non-empty rejection messages, and assert metrics increments for failed non-empty deletes and force deletes.

State and persistence behavior: The file directly mutates and observes local persistent state: chunk files under `ContainerData.getChunksPath`, block data and last chunk info tables in RocksDB, in-memory/test block count statistics, `ContainerData.isEmpty`, and whether a container remains in the datanode container set. It also drives the normal OM/SCM delete-block pipeline so the container's empty flag becomes true after key deletion.

Dependencies and integration points: Coverage includes SCM command queuing, datanode delete command handler, key-value handler empty checks, block-deleting service, container metrics, filesystem chunk directories, RocksDB batch deletion, OM key deletion, and SCM deleted-block flushing.

Risks: The suite mutates low-level container internals for negative cases, so it is tightly coupled to key-value container storage details. It uses one static cluster and shared volume names, which can leak state if a test aborts. Some checks depend on log text and sleeps.

Test signals: Expected signals include rejection of non-force delete for open or non-empty containers, successful forced delete, successful non-force delete once the container is empty, failure when directory empty-check is enabled and lingering chunks remain, failure when block table remains non-empty, success when DB/chunks are cleared despite stale block count, and increments to `containerDeleteFailedNonEmpty` and `containerForceDelete`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestDeleteContainerHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestFinalizeBlock.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestFinalizeBlock.java

Purpose: This parameterized integration test verifies finalize-block semantics for both legacy and schema V3 key-value container layouts. It ensures that a finalized block rejects later write chunk and put block requests, reloads finalized-block state after datanode restart, and clears finalized-block state after container close.

Important APIs and types: The test uses `MiniOzoneCluster`, `OzoneClient`, `ObjectStore`, `OzoneOutputStream`, `OmKeyArgs`, `OmKeyLocationInfoGroup`, `ContainerInfo`, `Pipeline`, `XceiverClientManager`, `XceiverClientSpi`, `ContainerTestHelper.getWriteChunkRequest`, `getPutBlockRequest`, `getFinalizeBlockRequest`, `BlockID`, `KeyValueContainerData.getFinalizedBlockSet`, and `DatanodeConfiguration.CONTAINER_SCHEMA_V3_ENABLED`.

Control flow: `setup` creates a one-datanode cluster for the selected schema mode with short report intervals and block deletion intervals. The test writes a key, locates the first container and local block ID, acquires an xceiver client for the pipeline, verifies write chunk and put block work before finalization, sends a finalize-block request, and asserts the response local ID matches the key block. It then checks that the finalized block set contains one entry, verifies later write chunk and put block fail with "Block already finalized", restarts the datanode and checks the finalized set reloads, closes all containers, waits for the finalized set to clear, restarts again, and checks it remains empty.

State and persistence behavior: The core state is `KeyValueContainerData.finalizedBlockSet`. The test verifies it is persisted or reconstructed across datanode restart while the container is open, then removed when the container closes and remains absent across a second restart. It also validates that finalized block state gates write-path commands, not read-path behavior.

Dependencies and integration points: Coverage spans raw container protocol commands over the xceiver client, OM key metadata lookup, key-value container metadata, schema-version configuration, datanode restart/reload behavior, and SCM-driven container close.

Risks: The test uses the first SCM container and the first key location, which is valid for the single-node, single-key setup but would be fragile if setup changed. It asserts exception message text for rejected writes. `XceiverClientManager` is not explicitly closed in the test body.

Test signals: Strong signals are successful pre-finalize write/put, finalize response local ID equality, finalized set size one, rejected write chunk and put block after finalization, finalized set size one after restart, empty finalized set after close, and empty finalized set after the second restart for both schema modes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestFinalizeBlock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestRefreshVolumeUsageHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestRefreshVolumeUsageHandler.java

Purpose: This integration test verifies the datanode and SCM path for refreshing volume usage information. It checks that SCM node usage eventually reflects data written on a datanode and that an explicit refresh-volume-usage command can force updated usage reporting.

Important APIs and types: The test uses `MiniOzoneCluster`, `OzoneClient`, `ObjectStore`, `OzoneOutputStream`, `DatanodeDetails`, `ScmNodeManager.getUsageInfo`, `refreshAllHealthyDnUsageInfo`, `DUOptimized`, `HddsVolumeFactory`, `VolumeUsage.refreshNow`, and `GenericTestUtils.waitFor`.

Control flow: `setup` builds a one-datanode cluster with 1 GB containers, a 5 GB minimum datanode volume free-space setting, one-second node reports, the `HddsVolumeFactory` DU implementation, zero RATIS minimum free space, and safemode pipeline creation disabled. The test records the current SCM-used value, captures `DUOptimized` logs, writes a small key, first asserts SCM usage has not immediately changed, then waits for node reports to show a larger used value. It asks SCM node manager to refresh all healthy datanode usage info, waits again for updated usage, directly calls `refreshNow` on the datanode volume usage, and waits for the optimized DU log to mention container data usage.

State and persistence behavior: The durable state is actual key data written to the datanode volume. The observed state is SCM's cached node usage statistics and the datanode volume-usage cache. The explicit refresh path should cause SCM-visible used space to advance beyond the initial value without waiting for the default long DU refresh period.

Dependencies and integration points: Coverage includes client writes, datanode volume usage tracking, node reports, SCM node manager usage aggregation, refresh usage command scheduling, and optimized disk-usage accounting.

Risks: The test depends on filesystem usage changes being visible and on log text from `DUOptimized`. It tolerates one timeout during the pre-refresh wait because the node report might not refresh quickly, but the final assertions still depend on timing.

Test signals: Signals include initial equality of SCM used space, eventual `ScmUsed` greater than the recorded value, successful explicit refresh through `refreshAllHealthyDnUsageInfo`, and a `DUOptimized` log line containing the expected container data usage count after `refreshNow`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestRefreshVolumeUsageHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/package-info.java

Purpose: This package-info file documents the package `org.apache.hadoop.ozone.container.common.statemachine.commandhandler` as containing integration tests for command handlers. It provides package-level Javadoc rather than executable test logic.

Important APIs and types: There are no classes, methods, or runtime APIs beyond the package declaration. The documented package contains tests for datanode command handlers such as block deletion, close container, delete container, finalize block, refresh volume usage, and related SCM-to-datanode command flows.

Control flow: No control flow exists in this file. Its only behavior is compile-time association of Javadoc with the command-handler integration-test package.

State and persistence behavior: The file has no state and no persistence behavior. Its importance is organizational: generated docs and IDEs can associate the package with command handler integration tests.

Dependencies and integration points: It is tied to the Java package namespace used by the command handler tests in the same directory. Build tooling compiles it as normal Java source but it contributes no bytecode behavior beyond package metadata.

Risks: The Javadoc text says "handler's" rather than "handlers", a minor grammar issue. Since it has no behavior, the main risk is only package drift if files move and the package declaration no longer matches the directory.

Test signals: There are no direct test signals. Successful compilation confirms the package declaration is syntactically valid and aligned with adjacent test classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/TestCSMMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/TestCSMMetrics.java

Purpose: This test validates metrics emitted by the Ratis `ContainerStateMachine` around write, apply, commit, and read/query operations. It uses a lightweight Ratis server with a test dispatcher to check metric counters and latency gauges before and after container protocol commands.

Important APIs and types: The file uses `CSMMetrics`, `XceiverServerRatis`, `XceiverClientRatis`, `RatisTestHelper`, `MockPipeline`, `Pipeline`, `RaftGroupId`, `ContainerDispatcher`, `ContainerController`, `ContainerCommandRequestProto`, `ContainerCommandResponseProto`, `ContainerTestHelper`, and metrics helpers `getMetrics`, `assertCounter`, and `getDoubleGauge`.

Control flow: `testContainerStateMachineMetrics` delegates to `runContainerStateMachineMetrics` with gRPC Ratis initialization and server/client factories. The runner creates a mock pipeline, configures Ratis, starts one xceiver server per pipeline node, initializes the Ratis group, connects a client, asserts initial CSM counters and latency gauges are zero, sends a write-chunk request, checks write/apply/commit/bytes counters and latency gauges advanced, then sends a read-chunk request and checks query counter growth. A `finally` block closes the client and stops all servers.

State and persistence behavior: The test uses temporary Ratis storage directories under `@TempDir` and a new empty `ContainerSet` controlled by `ContainerController`. The dispatcher returns create-container-style success responses rather than real key-value persistence, so metrics state is the primary state under test. Ratis state machine metrics are keyed by `CSMMetrics.SOURCE_NAME + RaftGroupId`.

Dependencies and integration points: Coverage sits at the transport/state-machine layer: xceiver client, Ratis server, Raft group initialization, container state machine metrics source registration, and command dispatch. The custom dispatcher isolates metrics from real container storage behavior.

Risks: Because `TestContainerDispatcher` does not perform real storage operations, it validates state-machine metric accounting rather than full container command semantics. Metric names are string-sensitive and can break on metric renames.

Test signals: Strong signals are zero initial counters and gauges, one write state-machine op, one apply transaction, 1024 written and committed bytes, zero verify failures, positive write/apply latency gauges after write chunk, and one query state-machine op after read chunk.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/TestCSMMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/metrics/TestContainerMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/metrics/TestContainerMetrics.java

Purpose: This test verifies storage-container and per-volume I/O metrics for both standalone gRPC xceiver and Ratis xceiver paths. It sends create-container, write-chunk, and read-chunk commands through a real dispatcher and asserts operation counters, byte counters, percentile gauges, and volume I/O stats.

Important APIs and types: The suite uses `XceiverClientGrpc`, `XceiverClientRatis`, `XceiverServerGrpc`, `XceiverServerRatis`, `HddsDispatcher`, `ContainerMetrics`, `MutableVolumeSet`, `HddsVolume`, `VolumeChoosingPolicy`, `Handler.getHandlerForContainerType`, `ContainerChecksumTreeManager`, `StateContext`, `ContainerController`, `StorageVolumeUtil`, `DefaultMetricsSystem`, and metrics helpers `assertCounter`, `assertQuantileGauges`, and `getMetrics`.

Control flow: `setup` enables MiniCluster metrics mode, sets percentile intervals to one second, disables Ratis data stream, sets metadata dirs, and creates the volume choosing policy. Each test calls `runTestClientServer` with protocol-specific configuration, client, server, and server-init factories. The runner creates a single-node mock pipeline, creates a mutable volume set, starts the server with a dispatcher built from real key-value handlers, connects the client, writes a chunk to a test block, reads it back, and then asserts metrics. Cleanup removes registered `ContainerMetrics`, shuts down the volume set, closes the client, and stops the server.

State and persistence behavior: The test uses temporary datanode and Ratis storage dirs and sets each `HddsVolume` DB parent directory to a temp location. A real container is created implicitly by the write path, chunk bytes are written and read, and volume I/O statistics record the actual 1024-byte operations. Cleanup deletes configured datanode and Ratis storage directories.

Dependencies and integration points: It covers xceiver transports, dispatcher-to-handler routing, key-value container operations, checksum tree manager wiring, volume selection, metrics system registration, and volume I/O metric sources.

Risks: The static `CONF` is mutated across protocol modes, so cleanup is important. Metric names and percentile interval suffixes are string-sensitive. The test sleeps to let quantile gauges roll to the configured interval.

Test signals: Expected metrics are `NumOps == 3`, one create container, one write chunk, one read chunk, 1024 bytes written and read, write-chunk quantile gauges for the one-second interval, and volume I/O counters showing 1024 read bytes, one read op, 1024 write bytes, and one write op.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/metrics/TestContainerMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/metrics/TestDatanodeQueueMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/metrics/TestDatanodeQueueMetrics.java

Purpose: This abstract non-HA test verifies that datanode queue metrics expose non-negative gauges for every SCM command type in both the state-context command queue and command-dispatcher queue.

Important APIs and types: It uses `DatanodeQueueMetrics`, `SCMCommandProto.Type`, metric prefixes `STATE_CONTEXT_COMMAND_QUEUE_PREFIX` and `COMMAND_DISPATCHER_QUEUE_PREFIX`, Apache Commons Text `WordUtils.capitalize`, `MetricsAsserts.getMetrics`, `MetricsAsserts.getLongGauge`, AssertJ, and the `NonHATests.TestCase` fixture interface.

Control flow: `testQueueMetrics` iterates all generated `SCMCommandProto.Type` enum values. For each type it builds a metric suffix from the capitalized enum value plus `Size`, then fetches gauges for state-context and command-dispatcher queues and asserts both are greater than or equal to zero. The test relies on the surrounding non-HA fixture to have datanode metrics registered before execution.

State and persistence behavior: No durable state is involved. The state under test is the metrics system's current gauge values for command queues. The values may be zero or positive depending on queued commands, but must not be absent or negative.

Dependencies and integration points: It connects generated SCM command protobuf types to datanode queue metric naming. This is useful coverage when adding command types, because the loop expects a gauge for every enum value in both queue surfaces.

Risks: Metric names depend on exact capitalization of enum string values, so enum naming or metric naming changes require coordinated updates. The class is abstract and depends on an external concrete non-HA test harness; run in isolation it is not a complete cluster setup.

Test signals: The signal is simple but broad: for every SCM command type, both queue-size gauges are present and non-negative under `DatanodeQueueMetrics.METRICS_SOURCE_NAME`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/metrics/TestDatanodeQueueMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestOzoneContainer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestOzoneContainer.java

Purpose: This integration test suite validates `OzoneContainer` lifecycle and raw container protocol behavior. It covers direct container startup, idempotent start/stop, operation through a datanode MiniOzoneCluster, missing-container handling, small-file get/put, closed-container read/write rules, forced delete behavior, and async xceiver client calls.

Important APIs and types: The file uses `OzoneContainer`, `ContainerTestUtils.getOzoneContainer`, `MiniOzoneCluster`, `XceiverClientGrpc`, `XceiverClientSpi`, `MockPipeline`, `Pipeline`, `ContainerTestHelper`, `ContainerProtos.ContainerCommandRequestProto`, `ContainerCommandResponseProto`, `BlockID`, `StorageVolumeUtil`, `DatanodeDetails`, `ContainerSet.getMissingContainerSet`, and `CompletableFuture`.

Control flow: Direct-start tests construct an `OzoneContainer` outside a datanode with temp metadata and data directories, initialize datanode layout, start with a random cluster ID, optionally call start/stop twice to assert idempotence, and create a container through a gRPC client. Cluster-backed tests create a one-datanode MiniOzoneCluster, obtain the first pipeline, and send raw create, write chunk, read chunk, put block, get block, update container, close container, delete container, and small-file requests. The missing-container test creates and writes a container, stops the datanode, deletes the container directory, restarts, asserts the ID is in `missingContainerSet`, verifies most commands return `CONTAINER_MISSING` or `CONTAINER_NOT_FOUND`, then creates a recovering container and verifies write/put/get succeeds. Async testing sends 1000 write-small-file requests and waits for all futures to complete.

State and persistence behavior: The suite manipulates actual metadata/data directories, datanode layout files, container directories, missing-container tracking, small-file chunk bytes, block metadata, closed container state, and deleted container state. It explicitly deletes a container directory to validate that restart detects missing persisted container data and prevents accidental recreation unless the request is for a recovering container.

Dependencies and integration points: Coverage spans gRPC xceiver client/server, OzoneContainer service lifecycle, datanode integration, container dispatcher behavior, key-value container command semantics, missing-container guardrails, storage volume setup, and async client response handling.

Risks: Several tests use the first pipeline from SCM and assume a one-datanode cluster. The missing-container test is marked flaky and depends on filesystem deletion plus datanode restart detection. Some helper names contain typos such as `testXcieverClientAsync`, but behavior is clear.

Test signals: Strong signals include successful create/write/read/put/get/update on existing containers, `CONTAINER_NOT_FOUND` for nonexistent update/get paths, exact byte equality for small-file reads, `CLOSED_CONTAINER_IO` for write and put after close while reads still succeed, `DELETE_ON_OPEN_CONTAINER` for non-force open delete, success for force delete, `CONTAINER_MISSING` for commands against a missing container, successful recovering-container recreation, and all async command futures completed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestOzoneContainer.java -->
