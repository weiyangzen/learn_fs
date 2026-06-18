## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataNodeFaultInjector.java

Purpose: provides a test-only singleton hook surface for injecting failures, delays, and observations into DataNode, data-transfer, block-report, directory-scanner, and erasure-coding paths. Production behavior is intentionally no-op.

Important APIs and functions: `get()` returns the global injector and `set(DataNodeFaultInjector)` replaces it for tests. Hook methods include data-transfer write/flush and ack hooks (`writeBlockAfterFlush`, `stopSendingPacketDownstream`, `delaySendingAckToUpstream`, `delayAckLastPacket`, `delayWriteToDisk`, `delayWriteToOsCache`), heartbeat/report hooks (`dropHeartbeatPacket`, `startOfferService`, `endOfferService`, `blockUtilSendFullBlockReport`, `noRegistration`), pipeline/failure hooks (`failMirrorConnection`, `failPipeline`, `throwTooManyOpenFiles`), erasure-coding reconstruction hooks (`stripedBlockReconstruction`, `stripedBlockWriterInit`, `stripedBlockChecksumReconstruction`, `delayBlockReader`, `badDecoding`), and scanner/dataset timing hooks (`delayDeleteReplica`, `delayDiffRecord`, `delayGetMetaDataInputStream`, `waitUntilStorageRemoved`).

Control flow: callers in `BlockReceiver`, `DataXceiver`, `BPServiceActor`, `BPOfferService`, `BlockSender`, EC reconstructors/readers/writers, `DirectoryScanner`, and dataset classes synchronously invoke `DataNodeFaultInjector.get()` at selected fault boundaries. Unless a test has replaced the singleton, the method returns normally, returns `false`, or does nothing. Tests subclass or override methods to throw checked exceptions, sleep, mutate buffers, drop packets, or record timing.

State and persistence: the only state is the static process-wide `instance`; there is no persistence. Because the singleton is mutable and global, tests must restore it to the default injector to avoid cross-test contamination.

Dependencies and integration points: depends on DataNode-adjacent types such as `ReplicaInPipeline`, `DirectoryScanner`, and `ByteBuffer`. It is annotated `@VisibleForTesting` and `@InterfaceAudience.Private`, signaling that production code may call it but external users should not depend on it.

Risks: global mutable fault state can make parallel tests flaky if not reset. Hook placement affects production hot paths, so adding blocking or allocation-heavy default behavior would be dangerous. Hook methods that throw checked exceptions must match caller expectations; changing a no-op hook to throw in production would alter core write/read/report semantics.

Test signals: this file is itself test infrastructure. Useful tests are the downstream tests that install custom injectors to simulate packet drops, slow acks, short-circuit response errors, EC decode corruption, stale directory-scanner diffs, too many open files, or missing DataNode registration.
