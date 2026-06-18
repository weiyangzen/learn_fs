# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DeadNodeDetector.java

`DeadNodeDetector` is a client-side daemon that proactively probes DataNodes considered suspect or dead by `DFSInputStream` instances sharing a DFS client context. It keeps a shared in-memory `deadNodes` map keyed by DataNode UUID and a `suspectAndDeadNodes` map from streams to node sets, letting streams avoid bad replicas while allowing recovered nodes to be removed.

Important APIs are `addNodeToDetect()`, `isDeadNode()`, `clearAndGetDetectedDeadNodes()`, stream-specific `removeNodeFromDeadNodeDetector()`, `shutdown()`, testing hooks for disabling schedulers, and queue accessors. Internal types include `UniqueQueue<T>`, `Probe`, `ProbeScheduler`, `ProbeType`, and the daemon state enum.

Construction copies configuration, creates queues and thread pools, reads HDFS client detection intervals/timeouts, and starts separate suspect/dead scheduler threads. `work()` cycles `INIT -> CHECK_DEAD -> IDLE`, periodically enqueueing known dead nodes. Scheduler threads drain de-duplicated queues, avoid duplicate probes through `probeInProg`, and submit `Probe` tasks. A probe calls `ClientDatanodeProtocol.getDatanodeInfo()` with a timeout; successful dead probes remove nodes, successful suspect probes clear per-stream local dead state, and failed suspect probes promote nodes to `deadNodes`.

State is process-local only: maps, queues, pools, and threads. Dependencies include `DFSInputStream`, `DatanodeInfo`, `DFSUtilClient.createClientDatanodeProtocolProxy()`, HDFS client config keys, `SubjectInheritingThread`, and `Daemon.DaemonFactory`.

Risks center on concurrency and lifecycle: weakly consistent iteration while removing stream entries, stuck RPCs that may outlive `Future.cancel(true)`, executor shutdown without `shutdownNow()`, and reliance on stable DataNode UUIDs. Test signals include duplicate queue suppression, suspect-to-dead promotion, dead removal after successful probe, stream pruning, scheduler-disabled deterministic tests, timeout behavior, and shutdown/join behavior.
