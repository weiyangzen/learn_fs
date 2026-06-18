# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestPipelineCloseRecoveryByteArrayLeak.java

Purpose: regression test for HDFS-17916, ensuring pipeline-close recovery returns the final DFSPacket byte buffer to `ByteArrayManager`.

Important APIs/types/functions: `MiniDFSCluster`, `DFSClientFaultInjector.failPacket`, `DFSTestUtil.createFile`, `ByteArrayManager.Impl`, `ManagerMap.countAllocated`, `GenericTestUtils.waitFor`.

Control flow: the test enables the write `ByteArrayManager`, sets allocation tracking threshold to zero, lowers locate-following-block retries, and installs a fault injector that reports every last-in-block ack as failed. It starts a three-datanode cluster, writes a 1 MiB replicated file to force streamer recovery in `PIPELINE_CLOSE`, extracts the client's `ByteArrayManager`, and waits until all tracked buffers are released.

State and persistence behavior: creates a temporary MiniDFSCluster and a file `/pipelineCloseRecoveryLeak.dat`. Global `DFSClientFaultInjector` state is saved and restored in `finally`; the cluster is always shut down.

Dependencies and integration points: integrates DFSClient streamer fault injection, datanode pipeline recovery, client context byte-array pooling, and cluster write path behavior.

Risks: timing-sensitive due to asynchronous streamer release; `waitFor` allows 5 seconds. Because it modifies a global fault injector, failure to restore would affect later tests, but cleanup is explicit.

Test signals: `ByteArrayManager` is the bounded implementation and `ManagerMap.countAllocated()` reaches zero after close.
