# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDeadNodeDetection.java

Purpose: tests DFSClient dead-node detection, shared detector lifecycle, background probe queues, dead-node recovery, suspect-node handling, and cleanup when streams or clients close.

Important APIs and types: `DeadNodeDetector`, `DFSClient`, `DFSInputStream`, `ClientContext`, `MiniDFSCluster`, `BlockMissingException`, `SubjectInheritingThread`, `DeadNodeDetector.UniqueQueue`, and dead-node detection config keys.

Control flow: setup enables dead-node detection with short probe intervals/timeouts. Tests create replicated small files, stop datanodes, trigger reads that throw `BlockMissingException`, then wait until detected-dead-node counts reach expected values. Multi-stream tests confirm shared client context. Recovery restarts one DN and expects count reduction. Probe tests spy suspect/dead queues. Suspect-node test disables probe thread, restarts a DN, then starts scheduler and expects queues to drain. Lifecycle tests open two DFS instances to the same URI and verify detector sharing, shutdown, and recreation.

State and persistence: creates and deletes test files, stops/restarts datanodes, mutates static test flags for detector threads, tracks detector queues and client dead-node maps, and closes streams/filesystems to trigger cleanup.

Dependencies and integration: integrates DFSInputStream failure handling, ClientContext sharing, background detector scheduler, datanode probe connection attempts, and MiniDFSCluster node lifecycle.

Risks: background-thread timing and static test flags can cause flakiness if cleanup fails; repeated `clearAndGetDetectedDeadNodes` both observes and mutates detector state; tests depend on same-context DFSClient reuse.

Test signals: exact dead-node map sizes, detected-dead-node counts, expected datanode UUIDs, Mockito queue offer/poll counts, suspect queue drain after scheduler start, detector alive/shutdown/null state after filesystem close, and cleanup to zero dead nodes after file deletion/stream close.
