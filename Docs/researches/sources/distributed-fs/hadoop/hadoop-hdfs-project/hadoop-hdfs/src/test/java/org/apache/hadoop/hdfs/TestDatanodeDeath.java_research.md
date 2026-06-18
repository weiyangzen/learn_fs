# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeDeath.java

Purpose: stress tests HDFS write pipeline recovery when datanodes die or restart during active writes, both with single-file targeted failures and concurrent workloads.

Important APIs and types: `MiniDFSCluster`, `DFSOutputStream`, `FSDataOutputStream`, `FSDataInputStream`, `BlockLocation`, `SubjectInheritingThread`, `AppendTestUtil`, and HDFS heartbeat/reconstruction/client socket configs. Inner classes `Workload` and `Modify` coordinate writers and datanode restarts.

Control flow: `simpleTest` writes part of a file, obtains the write pipeline, stops a selected pipeline datanode, writes the rest, closes, and verifies full data and replication. `complexTest` starts multiple `Workload` threads creating and checking files while `Modify` waits for all workers to complete at least one file, then restarts random datanodes and resets progress stamps.

State and persistence: creates multiple HDFS files, writes deterministic random data, restarts/stops datanodes, waits for block locations and replica counts, and reads back full file contents.

Dependencies and integration: integrates DFSClient pipeline construction, packet/chunk settings, datanode restart handling, NameNode heartbeat/reconstruction timing, block-location reporting, and replica recovery.

Risks: highly timing-sensitive with sleeps, random victims/seeds, and thread coordination; long waits for replication can mask slow failures; tests use internal slowdown/chunk controls.

Test signals: file length equality, sufficient number of block locations and hosts per block, byte-for-byte data equality, and no assertion failures from workload or modifier threads.
