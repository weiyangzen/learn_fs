<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestClientProtocolForPipelineRecovery.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestClientProtocolForPipelineRecovery.java

Purpose: Large slow-test suite covering DFS client and NameNode protocol behavior during write pipeline recovery, lease validation, DataNode restarts/upgrades, delayed packets/acks, transferBlock replacement, close-stage failures, and slow-node eviction.

Important APIs, types, and functions: `NamenodeProtocols.updateBlockForPipeline`, `DFSOutputStream`, `DataStreamer`, `PipelineAck`, `BlockConstructionStage`, `DFSAdmin -shutdownDatanode/-evictWriters`, `DataNodeFaultInjector`, `DFSClientFaultInjector`, `DataNodeTestUtils`, `DatanodeProtocolClientSideTranslatorPB.registerDatanode`, `ReplicaInPipeline`, `GenericTestUtils.waitFor`, and `SubjectInheritingThread`.

Control flow: `testGetNewStamp` rejects finalized, nonexistent, non-lease-holder, and null-lease-holder update attempts, then accepts the real lease holder for an RBW block. Other tests inject packet failure, dropped heartbeat packets, delayed upstream acks, restart OOB messages, writer eviction, restart timeout failure, rolling upgrade restarts with generation-stamp recovery, remote upgrade while a background writer keeps flushing, zero-byte partial-block recovery, transferBlock with end-of-chunk extra bytes, dead DataNode re-registration followed by repeated `updatePipeline`, adding a DataNode/failing nodes during `PIPELINE_CLOSE`, and marking a slow downstream node bad after threshold slow acks.

State and persistence behavior: Tests manipulate active write pipeline state: generation stamps, streamer node arrays, pipeline recovery counters, DataNode liveness, replica bytes acked/on disk, bad-node/slow-node tracking, and client lease ownership. State is mostly runtime and cluster-local; the key persistence-like signal is that closed files remain readable after recovery scenarios.

Dependencies and integration points: Integrates the DFS client write path, NameNode lease/block protocols, DataNode data-transfer pipeline, admin commands, fault injectors, rolling upgrade shutdown/restart handling, block reports, and block reader verification.

Risks: Marked `@Tag("slow")` because many cases depend on sleeps, socket timeouts, background writers, and asynchronous shutdown threads. It reaches into internal streamers and fault injectors, so refactors in write pipeline internals can require careful test updates. Several tests assert absence of corruption by reading after complex failure injection rather than inspecting every intermediate state.

Test signals: Success means expected protocol calls fail or succeed with correct lease/block states, generation stamps advance on recovery, pipeline recovery counters remain correct for upgrade waits, failed/slow nodes are replaced as intended, close and repeated close remain safe where expected, and files remain readable after injected pipeline failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestClientProtocolForPipelineRecovery.java -->
