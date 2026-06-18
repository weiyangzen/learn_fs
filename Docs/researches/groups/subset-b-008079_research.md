# subset-b-008079 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestBlockOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestBlockOutputStream.java

## Purpose
`TestBlockOutputStream` is the baseline integration test for RATIS `RatisBlockOutputStream` buffering, flushing, commit watching, metrics, and data durability. It uses a `MiniOzoneCluster` with five datanodes, tiny client-side buffer sizes, checksum disabled, HBase enhancement flags enabled, and RATIS/client timeouts tuned low enough to exercise synchronous and asynchronous flush paths without long hangs.

## Important APIs, types, and functions
The class exposes reusable package-private helpers used by later failure tests: `createCluster()`, `createCluster(int)`, `newClientConfig(...)`, `newClient(...)`, `createKey(...)`, and `getKeyName()`. The constants `CHUNK_SIZE`, `FLUSH_SIZE`, `MAX_FLUSH_SIZE`, `BLOCK_SIZE`, `VOLUME`, and `BUCKET` define the miniature block geometry. Tests inspect `OzoneOutputStream`, `KeyOutputStream`, `RatisBlockOutputStream`, `BufferPool`, and `XceiverClientMetrics`; metrics are checked for `WriteChunk`, `PutBlock`, pending operation counts, and total operation counts.

## Control flow
`createCluster` builds the cluster, waits for a factor-three pipeline, and creates a volume/bucket. Each parameterized test runs for all combinations of `streamBufferFlushDelay` and put-block piggybacking. The test body writes a specific byte count, unwraps the stream stack, checks buffer count and stream-entry count, optionally calls `flush()`, closes the key, checks post-close cleanup, and finally reads back the key through `TestHelper.validateData`.

The tested write-size regimes are: less than a chunk, exactly flush size, more than one chunk but below flush size, more than flush size, exactly max flush size, and more than max flush size. These regimes intentionally trigger different transitions: data sitting only in memory, flush-size automatic write chunking, explicit flush, full-buffer `watchForCommit`, and close-time final `PutBlock`.

## State and persistence behavior
The test asserts internal stream state directly: `writtenDataLength`, `totalDataFlushedLength`, `totalAckDataLength`, `commitIndex2flushedDataMap`, `BufferPool` size, and `computeBufferData()`. It verifies that close drains stream entries, clears commit-index tracking, and leaves no buffered data. Persistence is validated by rereading keys from the object store, while OM and datanode persistence details are exercised indirectly through actual RATIS writes.

## Dependencies and integration points
This file integrates Ozone client RPC, SCM pipeline allocation, RATIS block streaming, datanode container operations, and metrics. It depends on `ClientConfigForTesting` to force small chunks and flush windows, `OzoneClientFactory.getRpcClient` for client variants, and `TestHelper.createKey`/`validateData` for object-store interactions.

## Risks and test signals
Several tests are annotated `@Flaky("HDDS-11564")`, reflecting timing sensitivity around asynchronous operation completion. Assertions sometimes allow pending counts to be less than or equal to expected values because write and put-block operations can complete before the assertion. The strongest signals are metric deltas, stream cleanup after close, exact ack/flushed lengths, and successful readback for every flush-delay/piggybacking combination.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestBlockOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestBlockOutputStreamWithFailures.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestBlockOutputStreamWithFailures.java

## Purpose
`TestBlockOutputStreamWithFailures` extends the baseline stream checks into failure handling. It verifies that `KeyOutputStream` and `RatisBlockOutputStream` recover from container closure, dead datanodes, single-node RATIS failures, and preallocated block failures while preserving committed data and cleaning up retry state.

## Important APIs, types, and functions
The file imports constants and helpers from `TestBlockOutputStream`, so it uses the same chunk/flush/block geometry and client configuration matrix. It directly inspects `KeyOutputStream`, `RatisBlockOutputStream`, `XceiverClientRatis`, `Pipeline`, and `commitInfoMap`. Failure classification uses `HddsClientUtils.checkForException` and accepts `ContainerNotOpenException`, `RaftRetryFailureException`, or `GroupMismatchException` depending on race timing. `stopAndRemove(DatanodeDetails)` removes a datanode service from the cluster list and stops it.

## Control flow
The class starts a 25-datanode cluster to leave enough replacement capacity. `testContainerClose` runs several private scenarios against each client configuration: close-container during watch-for-commit, factor-one RATIS close handling, writes larger than max flush size, and exception during close. Separate parameterized tests cover one datanode failure, two datanode failure, single-node pipeline failure, and failure with preallocated blocks.

Most scenarios first write `MAX_FLUSH_SIZE + CHUNK_SIZE`, force a flush, capture the `RatisBlockOutputStream`, then inject a failure by closing the container through `TestHelper.waitForContainerClose` or stopping datanodes. The next write/flush forces the stream to discard failed chunks or blocks, allocate a new block, and retry the data. Final assertions validate stream-entry count transitions, retry count reset, exception type, buffer drain, and complete readback of either one copy or two concatenated copies of the data.

## State and persistence behavior
The tests focus on state handoff after failure. They confirm `retryCount` resets to zero after exception handling, `commitIndex2flushedDataMap` is drained, buffered data is zero after close, location/stream entries are discarded where appropriate, and `commitInfoMap` remains stable when no datanode actually fails. Persistence is validated by reading object data after recovery, including cases where the same data is intentionally written before and after failure.

## Dependencies and integration points
Integration spans client retry logic, SCM block allocation, RATIS commit tracking, container close handling, datanode lifecycle methods, and the MiniOzoneCluster service list. Factor-one and factor-three paths are both covered. Preallocation uses `createKey(..., 3 * BLOCK_SIZE, ReplicationFactor.ONE)` to ensure unused entries exist before the failure.

## Risks and test signals
The class is marked `@Flaky("HDDS-11849")`; accepted exception classes show that SCM pipeline destruction, container closure, and RATIS retry exhaustion are timing dependent. The important regression signals are no data loss after reallocation, no leaked buffered bytes or stream entries, proper exception unwrapping, and retry-count reset. Cluster mutation through `stopAndRemove` is powerful but risky because it changes MiniOzoneCluster internals directly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestBlockOutputStreamWithFailures.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestClientRetryContainerStateMachineFailures.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestClientRetryContainerStateMachineFailures.java

## Purpose
This integration test verifies that client writes can retry successfully when the container state machine encounters leader or follower write failures caused by simulated full datanode volumes. It targets RATIS factor-three writes and checks retry behavior for first-chunk, next-chunk, small, and multi-megabyte writes.

## Important APIs, types, and functions
The fixture creates a three-datanode `MiniOzoneCluster`, configures a single pipeline, disables stream buffer flush delay, shortens RATIS watch timeouts, and sets snapshot threshold to one. It uses `OzoneOutputStream`, `ObjectStore`, `ReplicationConfig.fromTypeAndFactor`, `StorageVolume.incrementUsedSpace/decrementUsedSpace`, `XceiverServerRatis`, and `RaftServer` APIs. `checkDnPipelineIfLeader(OzoneContainer, AtomicBoolean)` scans RATIS groups and marks whether a datanode is leader for a three-peer group. `generateData(int)` fills deterministic data.

## Control flow
Every test creates or primes a RATIS/THREE key to ensure a pipeline exists, identifies leader or follower datanode volumes, records each volume's available space, and increments used space to exhaust that volume. Writes are then attempted through normal object-store APIs. The leader tests either run ten concurrent small key writes, one 5 MB key write, or a second chunk write after the first chunk has flushed. Follower tests exhaust one non-leader volume either before a 1 KB write or before writing the second chunk.

All tests restore volume usage in `finally`, so the cluster should remain usable. Failures inside asynchronous writer tasks call `fail`, and a `GenericTestUtils.waitFor` loop waits until all concurrent tasks decrement an `AtomicLong` counter.

## State and persistence behavior
The persistent state under manipulation is datanode volume accounting. By artificially consuming all available bytes, the tests induce container write failures without deleting files or stopping processes. State restoration is explicit and uses the recorded `(StorageVolume, availableBytes)` pairs. Success is mostly defined by the absence of `IOException` from create/write/flush under retry; this validates that client-side retry can allocate or continue correctly after state-machine write failure.

## Dependencies and integration points
The file integrates Ozone client writes, SCM pipeline limits, container volume usage, datanode `OzoneContainer`, RATIS server leadership, and client retry. It depends on heartbeat and close-container timing configuration to keep the test focused on write retry rather than node death.

## Risks and test signals
The concurrent test uses `CompletableFuture.runAsync` without collecting futures, so assertion failures inside workers rely on JUnit `fail` being thrown in asynchronous threads and the counter reaching zero. The use of direct volume-space mutation is effective but must always be balanced in `finally`. Strong signals are successful flush completion under leader/follower volume-full conditions and bounded wait completion for the parallel writers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestClientRetryContainerStateMachineFailures.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestClientRetryTimeout.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestClientRetryTimeout.java

## Purpose
`TestClientRetryTimeout` is a timing-focused integration test. It verifies that write and watch operations fail or recover within acceptable bounds when pipelines, followers, leaders, or all datanodes are unavailable. The class documents expected timeout budgets for newer retry configuration and guards against regressions to multi-minute or multi-ten-minute hangs.

## Important APIs, types, and functions
The setup creates a seven-datanode `MiniOzoneCluster` with small chunk/flush/block sizes, stream buffer flush delay disabled, fast leader election, high stale-node interval, and expanded pipeline limits. Tests unwrap `OzoneOutputStream` into `KeyOutputStream`, `RatisBlockOutputStream`, `XceiverClientRatis`, and `Pipeline`. Datanode role checks use `RatisTestHelper.isRatisFollower` and `isRatisLeader`. Helper methods are `getKeyName()`, `createKey(...)`, and `generateData(int)`.

## Control flow
The ordered tests progressively damage the cluster. `testWriteToDeadPipelineFailsFast` establishes a pipeline, shuts down all nodes in that pipeline, writes more data, measures write/flush/close time, and restarts the nodes. `testWatchForCommitWithDeadFollowersFailsFast` shuts down one follower so majority write can succeed but all-committed watch can fail or fall back. `testWriteWithLeaderFailureFailsFast` kills the current leader mid-stream. `testEndToEndWriteWithAllDatanodesDownFailsFast` shuts down every datanode, attempts another write, and measures total Ozone-level retry time.

Each test catches `IOException` as an expected outcome and treats successful recovery as acceptable if it completes within the same budget. Durations are measured with `System.nanoTime()` and asserted with AssertJ against `MAX_SINGLE_CYCLE_DURATION`, `MAX_WATCH_DURATION`, or `MAX_TOTAL_WRITE_DURATION`.

## State and persistence behavior
The test manipulates process liveness rather than on-disk data. Initial writes establish block streams and pipelines; subsequent writes test retry state after shutdowns. Datanodes are restarted between ordered tests, and the cluster waits for readiness after restarts.

## Dependencies and integration points
This file integrates client retry policy, RATIS leader/follower behavior, pipeline allocation, datanode lifecycle control, and MiniOzoneCluster readiness. The comments explicitly connect expected durations to RPC write timeout, watch timeout, exponential backoff, and Ozone max retries.

## Risks and test signals
These tests are inherently long-running: acceptable bounds are 2, 4, and 10 minutes. They are also sensitive to hardware and CI load. The important signal is not exact exception type, but elapsed time remaining below the documented thresholds. Ordered execution matters because cluster state is reused and repaired across tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestClientRetryTimeout.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestCloseContainerHandlingByClient.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestCloseContainerHandlingByClient.java

## Purpose
This abstract `NonHATests.TestCase` verifies that the Ozone client handles close-container exceptions during normal RATIS key writes. It focuses on data length, block-location metadata, and readback after a container is closed between writes or before stream close.

## Important APIs, types, and functions
The class depends on an externally supplied `cluster()` from the non-HA test harness. It uses `MiniOzoneCluster`, `ObjectStore`, `OzoneOutputStream`, `KeyOutputStream`, `OzoneInputStream`, `OmKeyArgs`, `OmKeyInfo`, `OmKeyLocationInfo`, `RatisReplicationConfig`, and `StandaloneReplicationConfig`. Helper methods wrap `TestHelper.waitForContainerClose`, `TestHelper.createKey`, and `TestHelper.validateData`.

## Control flow
`init()` reads configured chunk and block sizes, creates a client, volume, and bucket, and seeds a random string for deterministic data. Tests write one or more chunks/blocks, force the current container closed with `waitForContainerClose(key)`, then continue writing or close the stream. After close, they query OM key metadata via `lookupKey` and validate data by reading the key.

The scenarios cover flush-and-close after a mid-stream close, close consistency when no extra data is written, several multi-block preallocation and partial-buffer cases, a RATIS factor-three path, and a larger two-write case. Multi-block tests inspect key location counts and each `OmKeyLocationInfo` length to verify that remaining buffered data is copied into newly allocated blocks when the original container closes.

## State and persistence behavior
The state under test includes preallocated stream entries, OM key size, key location versions, block lengths, and persisted object bytes. Container closure forces the client to discard or bypass failing block streams and allocate new blocks, while OM should reflect only successfully committed data. The tests assert both metadata size and full byte equality.

## Dependencies and integration points
This file integrates client-side block stream recovery, SCM container closure, OM key lookup, RATIS replication config, and the non-HA test harness. It is abstract because concrete subclasses provide the cluster topology.

## Risks and test signals
The class uses replication config values in `OmKeyArgs` that are not always the same as the create-key type in every test, so the main signal is OM lookup and key data rather than replication assertion. The strongest regression indicators are incorrect `dataSize`, wrong number of location infos, missing reallocated block data, or readback mismatch after a container close.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestCloseContainerHandlingByClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerReplicationEndToEnd.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerReplicationEndToEnd.java

## Purpose
`TestContainerReplicationEndToEnd` simulates a complete closed-container replication path. It verifies that after one original replica node is lost, Replication Manager copies a closed container to a new datanode and the key remains readable from the replicated container after the original pipeline nodes are shut down.

## Important APIs, types, and functions
The fixture uses `MiniOzoneCluster` with four datanodes, starts Replication Manager, and tunes heartbeat, container report, stale/dead node, pipeline destroy, follower slowness, and no-leader timeouts. The test uses `XceiverClientManager`/`XceiverClientSpi` to send a raw `CloseContainer` command, `ContainerID`, `PipelineID`, `Pipeline`, `ContainerOperation` protos, `OmKeyLocationInfo`, and `GenericTestUtils.waitFor`.

## Control flow
The test creates a RATIS/THREE key, writes and flushes `"ratis"`, captures its single key location, resolves the container and pipeline from SCM, and closes the key. If SCM has not already moved the container to `CLOSING` or `CLOSED`, the test finalizes it. It then sends an explicit close-container command to the first pipeline node and waits for SCM to report `CLOSED`.

After shutting down the old replica node, it selects a datanode not in the original pipeline and waits until that datanode's container set contains the container. It checks the new replica has a positive block commit sequence ID. Finally it shuts down the other original pipeline nodes and validates the key data, forcing reads to use the newly replicated container.

## State and persistence behavior
The test observes SCM container lifecycle state, datanode container sets, replica placement, and block commit sequence IDs. Persistence is proven by reading the key after original replicas are unavailable. State movement depends on container reports and Replication Manager intervals.

## Dependencies and integration points
This is an end-to-end path across Ozone client writes, OM key metadata, SCM container and pipeline managers, datanode close-container handling, Replication Manager, and client reads. It uses raw container protocol commands rather than only public object-store APIs.

## Risks and test signals
The test uses sleeps based on `containerReportInterval`, so timing can be sensitive. The decisive signals are SCM state `CLOSED`, the new datanode acquiring the container, positive BCSID on the replicated container, and successful read after all original pipeline nodes are stopped.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerReplicationEndToEnd.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerStateMachine.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerStateMachine.java

## Purpose
This test class validates two single-datanode container state-machine behaviors: corrupting a container directory during a write marks the container unhealthy, and RATIS snapshot retention stays bounded when the snapshot threshold is low.

## Important APIs, types, and functions
The setup enables block tokens and OM test security, uses test certificate and secret-key clients, sets snapshot threshold to one, disables stream buffer flush delay, and creates a one-datanode RATIS pipeline. It uses `ContainerStateMachine`, `SimpleStateMachineStorage`, `StatemachineImplTestUtil`, `RatisServerConfiguration`, `FileUtil.fullyDelete`, `OzoneManager.startSecretManager`, and `TestHelper.getStateMachine`.

## Control flow
`testContainerStateMachineFailures` creates a RATIS/ONE key, writes and flushes data to create a container, writes again, captures the single `OmKeyLocationInfo`, deletes the corresponding container directory, and lets try-with-resources close the stream. After close it asserts the datanode's container state is `UNHEALTHY`.

`testRatisSnapshotRetention` starts by asserting no latest snapshot. It writes ten keys, each with a flush and second write, then inspects the snapshot directory and verifies the number of retained snapshots is within one of configured retention. It writes ten more keys and asserts the count remains bounded.

## State and persistence behavior
The first test mutates on-disk container contents and observes in-memory container state. The second test observes RATIS snapshot files under `SimpleStateMachineStorage` and asserts cleanup/retention behavior after repeated state-machine transactions. Both tests use real persisted state in MiniOzoneCluster storage directories.

## Dependencies and integration points
Integration includes secure client setup, OM secret manager, datanode container set, RATIS state machine storage, and Ozone client writes. The static `getSnapshotPath` helper is also used by nearby state-machine tests.

## Risks and test signals
Because snapshot creation and deletion can be asynchronous, the retention check allows an off-by-one difference. The unhealthy-container test depends on close-time failure detection after deleting a directory. Strong signals are exact `UNHEALTHY` state and bounded snapshot file count before and after additional writes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerStateMachine.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerStateMachineFailureOnRead.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerStateMachineFailureOnRead.java

## Purpose
`TestContainerStateMachineFailureOnRead` verifies that a read-state-machine failure causes SCM to close the affected RATIS pipeline. The injected failure is deletion of the leader's container directory while a follower is temporarily stopped and then restarted.

## Important APIs, types, and functions
The test configures short report intervals, long stale/pipeline destroy timeouts, one datanode pipeline limit, RATIS request/watch timeouts, and suppresses noisy `GrpcLogAppender` logs. It uses `RatisReplicationConfig`, `RatisTestHelper`, `XceiverClientRatis`, `TestOzoneContainer.createContainerForTesting`, `KeyOutputStream`, `OmKeyLocationInfo`, `PipelineManager`, and `PipelineNotFoundException`.

## Control flow
The test locates the single factor-three RATIS pipeline, finds a follower, and shuts it down. Before creating the Ozone key, it verifies the pipeline is still usable by creating a test container through a raw `XceiverClientRatis`. It then writes and flushes a RATIS/THREE key and captures the container location. After finding the current leader, it deletes that leader's container directory, restarts the stopped follower, waits for cluster readiness and an additional fixed delay, and then checks the original pipeline state.

If the pipeline still exists in SCM, it must be `CLOSED`; if it was already removed, `PipelineNotFoundException` is treated as acceptable.

## State and persistence behavior
The persistent fault is a deleted leader container directory. The expected state transition is pipeline closure or removal after the restarted follower catches up and the state machine hits read failure. The key's container location ties the on-disk deletion to the active pipeline.

## Dependencies and integration points
This test spans SCM pipeline management, RATIS role detection, low-level xceiver client container creation, Ozone key writes, datanode restart, and container state-machine read paths. It intentionally separates pipeline health from later read-state failure.

## Risks and test signals
The test uses `Thread.sleep(10000)` after restart, so it may be timing-sensitive on slow environments. It prints stack traces inside role-detection lambdas instead of failing immediately. The primary signal is that the damaged pipeline is no longer open: it is either `CLOSED` or absent.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerStateMachineFailureOnRead.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerStateMachineFailures.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerStateMachineFailures.java

## Purpose
This large integration test suite covers container state-machine failure handling for missing RATIS pipelines, datanode ID changes, corrupt containers, unhealthy metadata persistence, failed apply transactions, idempotent close/write behavior on closed containers, and client retry after follower failures.

## Important APIs, types, and functions
The shared fixture starts a ten-datanode cluster with fast reports/heartbeats, short stale/dead intervals, close-container wait duration, pipeline scrub/destroy timeouts, RATIS client/server timeouts, snapshot threshold one, and stream buffer flush delay disabled. It uses `ContainerStateMachine`, `XceiverServerRatis`, `XceiverClientManager`, `HddsDispatcher`, `ContainerDataYaml`, `KeyValueContainerData`, `CloseContainerCommand`, `RatisHelper`, `SimpleStateMachineStorage`, `FileInfo`, `ContainerTestHelper`, and `LambdaTestUtils`.

## Control flow
`testContainerStateMachineCloseOnMissingPipeline` removes RATIS groups with `notifyGroupRemove`, queues SCM close commands, and waits for containers to become `QUASI_CLOSED`. `testContainerStateMachineRestartWithDNChangePipeline` deletes a datanode's data volumes and datanode ID file, restarts it, and waits until a retry write allocates a new location. The ordered final `testContainerStateMachineFailures` deletes a container directory, expects `UNHEALTHY`, changes the RATIS storage dir before restart, and verifies the unhealthy container is not loaded into the regular set.

`testUnhealthyContainer` deletes chunks, verifies both in-memory and YAML `.container` state become `UNHEALTHY`, restarts, rereads metadata, and asserts close-container dispatch returns `CONTAINER_UNHEALTHY`. `testApplyTransactionFailure` deletes the container path before a close-container command, expects send failure, waits for the state machine to become unhealthy, verifies `takeSnapshot()` fails with `StateMachineException`, checks BCSID is unchanged, and waits for the snapshot/group directory to be removed. The idempotency tests close containers and issue duplicate or racing write-chunk commands to ensure the state machine remains healthy and snapshots advance. The retry tests delete follower chunk directories and verify data is still readable with expected OM location counts.

## State and persistence behavior
This file directly mutates storage directories, chunk paths, datanode ID files, RATIS group membership, SCM command queues, and container metadata YAML. It observes container states `QUASI_CLOSED`, `UNHEALTHY`, and `CLOSED`; snapshot file paths; block commit sequence IDs; state-machine health; key location counts; and readback bytes.

## Dependencies and integration points
The tests integrate nearly every layer involved in RATIS container writes: client stream retry, SCM node commands, datanode dispatcher, container metadata persistence, RATIS storage, state-machine snapshots, OM key lookup, and raw container protocol requests.

## Risks and test signals
This file is highly timing- and order-sensitive; one test is explicitly ordered last because changing RATIS storage location leaves pipelines dirty. There appears to be a likely typo in `testContainerStateMachineDualFailureRetry`: it writes key `ratis2` but validates `ratis1`. Important signals include state-machine health remaining true for idempotent closed-container writes, redacted failed write messages, failed snapshot after unhealthy state, YAML state persistence, and successful readback after follower chunk loss.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerStateMachineFailures.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerStateMachineFlushDelay.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerStateMachineFlushDelay.java

## Purpose
This class is a focused variant of the container state-machine corruption test with default flush-delay behavior and tiny buffer sizes. It verifies that deleting a container directory after an explicit flush still marks the container unhealthy when the stream closes.

## Important APIs, types, and functions
The setup enables block tokens and OM test secure mode, uses `CertificateClientTestImpl` and `SecretKeyTestClient`, configures fast reports/heartbeats, sets RATIS snapshot threshold one, and applies `ClientConfigForTesting` with `CHUNK_SIZE = 100`, `FLUSH_SIZE = 200`, `MAX_FLUSH_SIZE = 400`, and `BLOCK_SIZE = 800`. It uses `ContainerTestHelper.getFixedLengthString`, `KeyOutputStream`, `OmKeyLocationInfo`, and `FileUtil.fullyDelete`.

## Control flow
The single test creates a RATIS/ONE key, writes 110 bytes so the write exceeds one chunk, calls `flush()` to synchronize data under flush-delay behavior, writes a small `"ratis"` suffix, captures the single key location, deletes the container directory on the only datanode, and closes the stream through try-with-resources. It then asserts the datanode container state is `UNHEALTHY`.

## State and persistence behavior
Persistent state mutation is the container directory deletion. The test observes the in-memory container state after stream close. Small chunk sizing ensures the first write crosses a chunk boundary and exercises flush synchronization rather than only in-memory buffering.

## Dependencies and integration points
The test integrates secure MiniOzoneCluster setup, client buffer configuration, Ozone key writes, datanode container storage, and container state-machine failure detection. It is similar in spirit to `TestContainerStateMachine` but isolates flush-delay-sensitive behavior.

## Risks and test signals
The file relies on the default flush-delay setting described in comments rather than explicitly setting `setStreamBufferFlushDelay(true)`. The primary signal is exact `UNHEALTHY` state after deleting the active container path and closing the key.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerStateMachineFlushDelay.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerStateMachineStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerStateMachineStream.java

## Purpose
`TestContainerStateMachineStream` verifies the ByteBuffer streaming write path around the chunk-size boundary. It ensures data written through `OzoneDataStreamOutput` updates container `bytesUsed` for sizes one byte below and one byte above the configured chunk size.

## Important APIs, types, and functions
This abstract non-HA test uses an externally supplied `cluster()`. It creates volume/bucket state through `ObjectStore`, writes stream keys with `TestHelper.createStreamKey`, unwraps `KeyDataStreamOutput` from `OzoneDataStreamOutput.getByteBufStreamOutput()`, and resolves the target datanode with `TestHelper.getDatanodeService`. Data generation uses `ContainerTestHelper.generateData`.

## Control flow
`setup()` reads `OZONE_SCM_CHUNK_SIZE_KEY`, creates a client, and creates a test bucket. The parameterized test runs with offsets `-1` and `+1`, deriving sizes `chunkSize - 1` and `chunkSize + 1`. For each size, it creates a RATIS stream key, writes a `ByteBuffer`, flushes, captures key location info, closes the stream, then reads the corresponding datanode container's `bytesUsed`.

## State and persistence behavior
The state under observation is datanode container accounting, not file content. The assertion allows `bytesUsed` to be greater than the test size because the container may already include previous data. The test therefore proves at least that the streaming write path accounts for the new bytes.

## Dependencies and integration points
The file covers the streaming client API, byte-buffer output implementation, RATIS stream key creation, OM key location propagation, and datanode container data accounting. It complements the normal `OzoneOutputStream` tests.

## Risks and test signals
Because it only asserts `bytesUsed >= size`, it does not prove exact accounting or readback content. Its useful signal is boundary coverage around chunk size for the streaming state-machine path and successful propagation of location info from `KeyDataStreamOutput`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerStateMachineStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestDeleteWithInAdequateDN.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestDeleteWithInAdequateDN.java

## Purpose
This integration test verifies delete behavior when a RATIS/THREE pipeline has an inadequate datanode during container close and block deletion. It ensures chunks are not deleted from closed replicas until the lagging follower rejoins and catches up.

## Important APIs, types, and functions
The fixture starts exactly three datanodes, limits pipelines, lengthens stale/dead/no-leader/pipeline-creation timeouts to prevent automatic early repair, and accelerates block deletion services. It uses `XceiverClientManager`, `XceiverClientSpi`, raw `CloseContainer` protobuf requests, `RatisTestHelper`, `ContainerStateMachine` metrics, `KeyValueHandler`, `BlockData`, `ChunkInfo`, `OzoneTestUtils.flushAndWaitForDeletedBlockLog`, and `StorageContainerException`.

## Control flow
The test creates key `ratis`, writes and flushes data, captures the single key location and container ID, locates leader and follower in the factor-three pipeline, and shuts down one follower. It writes again and closes the key, then sends a close-container command to the pipeline. After OM lookup, it fetches the block ID and reads chunk metadata from the leader's `KeyValueHandler`.

The key is deleted through the object-store bucket API and SCM deleted-block logs are flushed. The test then reads each chunk from the leader and expects success, proving deletion has not yet removed data while the follower is behind. It records read-state-machine metrics, evicts state-machine cache, restarts the follower, waits, asserts read-state-machine ops increased without failures, waits for deletion, and finally checks all datanodes throw `StorageContainerException` with `UNABLE_TO_FIND_CHUNK` when reading the old chunks.

## State and persistence behavior
The test observes chunk files, block deletion logs, state-machine read metrics, container closure, and follower catch-up. It validates a persistence invariant: closed replicas retain chunks until deletion is safe across the repaired replication group.

## Dependencies and integration points
This file integrates OM delete, SCM deleted block log flushing, datanode block deletion services, RATIS follower recovery, state-machine cache eviction, and low-level chunk manager reads.

## Risks and test signals
The test uses sleeps after follower restart and before final deletion checks, so timing is a risk. Assumptions skip the test if the initial key has more than one location or pipelines are unavailable. Strong signals are pre-catch-up chunk readability, post-catch-up deletion on all datanodes, and zero read-state-machine failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestDeleteWithInAdequateDN.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestDiscardPreallocatedBlocks.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestDiscardPreallocatedBlocks.java

## Purpose
`TestDiscardPreallocatedBlocks` verifies that when a container is closed after only part of a preallocated key has been written, the client discards the unused preallocated block in the closed container and allocates a fresh block for subsequent writes.

## Important APIs, types, and functions
This abstract non-HA test uses `TestHelper.createKey` and `waitForContainerClose`, `KeyOutputStream`, `BlockOutputStreamEntry`, `OmKeyLocationInfo`, `ContainerInfo`, `Pipeline`, and SCM container/pipeline managers. It reads block size from `OZONE_SCM_BLOCK_SIZE` and uses fixed-length test data from `ContainerTestHelper`.

## Control flow
The test creates a RATIS key with expected size `2 * blockSize`, causing two stream entries to be preallocated. It writes exactly one block, snapshots the original location info and stream entries, resolves the first block's container and pipeline, and asserts the pipeline has three datanodes. It then closes the current container through `waitForContainerClose`, writes another block, and verifies there are now three stream entries.

The key assertion is that the first block ID is unchanged, while the second current location's block ID differs from the originally preallocated second stream entry. This proves the unused preallocated block was discarded and replaced.

## State and persistence behavior
The test inspects client-side preallocation state and SCM-backed location information. It does not read the final key data; instead it focuses on block identity and stream-entry mutation after container closure.

## Dependencies and integration points
Integration spans the non-HA cluster fixture, Ozone client preallocation, SCM container/pipeline lookup, container close handling, and key-output stream location management.

## Risks and test signals
The test assumes factor-three RATIS pipeline size of three and that the first write consumes exactly the first preallocated block. Its strongest signal is block ID replacement for the unused second preallocation while preserving the first committed block ID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestDiscardPreallocatedBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestECKeyOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestECKeyOutputStream.java

## Purpose
`TestECKeyOutputStream` validates erasure-coded key output behavior: stream type selection, bucket default replication, overwrites between EC and RATIS, large single-write chunk striping, EC container metadata, datanode failure recovery, and unsupported hflush/hsync.

## Important APIs, types, and functions
The fixture uses a ten-datanode `MiniOzoneCluster`, `ECReplicationConfig(3,2,RS,chunkSize)`, one-megabyte chunks, small client buffer geometry, disabled checksum and flush delay, relaxed dead/stale/slowness/no-leader timeouts, allowed replication config regex, and enabled hsync flags. Key APIs include `ECKeyOutputStream`, `KeyOutputStream`, `OzoneBucket`, `BucketArgs`, `DefaultReplicationConfig`, `ContainerOperationClient`, `PipelineManager`, `ContainerID`, `Handler`, Mockito static mocking, and `GenericTestUtils.waitFor`.

## Control flow
Basic tests verify explicit EC key creation returns `ECKeyOutputStream`, creation without bucket defaults returns normal `KeyOutputStream`, and EC bucket defaults produce EC streams and readable data. Overwrite tests create a key under EC or RATIS configs and then overwrite it with the other replication type, asserting `OzoneKeyDetails.getReplicationConfig()` matches the latest write. A RATIS key can still be explicitly created in a bucket whose default is EC.

The single-write tests build buffers with optional offset and write 11, 13, 15, 20, or 21 chunks in one `write(byte[], offset, length)` call, then read back the exact selected range. The container metadata test closes existing EC pipelines, writes a fresh EC key, waits until SCM reports one key and five replicas for the container, and validates content. The datanode ID change test mocks `Handler.getDatanodeId()` to return a bogus ID once for replica index one, expects a new pipeline/location and the old container to close. The datanode-kill test shuts down the first node of the first EC pipeline mid-write, waits for flush checkpoint completion, verifies the next block group excludes the killed node, reads both copies back, and restarts the node. `testBlockedHflushAndHsync` asserts EC output rejects hflush and hsync with `NotImplementedException`.

## State and persistence behavior
The tests observe EC block-group location lists, pipeline IDs, replica indexes, SCM container key counts, replica counts, bucket default replication config, key replication config after overwrite, flush checkpoint state, and persisted readback content. They also validate recovery from pipeline/container replacement after datanode identity mismatch or node shutdown.

## Dependencies and integration points
This file integrates Ozone client EC streaming, OM bucket defaults and key metadata, SCM EC pipeline management, datanode handler identity, container operations CLI client, and read reconstruction. Mockito is used to inject a low-level datanode ID mismatch.

## Risks and test signals
`testECKeyCreatetWithDatanodeIdChange` is marked `@Unhealthy("HDDS-11821")` and has a typo in its method name. The class has a static initialization hazard: `inputSize` is initialized from `chunkSize` before `chunkSize` is assigned in `init()`, so it is initially zero unless later code relies on recalculated values elsewhere. Strong signals are exact content readback across multi-chunk EC writes, five replicas for a 3-2 EC container, new pipeline allocation after a mocked datanode ID mismatch, exclusion of a killed node from the next block group, and rejected hflush/hsync.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestECKeyOutputStream.java -->
