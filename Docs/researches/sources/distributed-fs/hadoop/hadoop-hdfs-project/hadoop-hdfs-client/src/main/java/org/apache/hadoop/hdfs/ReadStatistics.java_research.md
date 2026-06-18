# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ReadStatistics.java

`ReadStatistics` tracks HDFS read counters for total, local, short-circuit, zero-copy, remote-derived bytes, block type, and erasure-coding decode time.

It exposes synchronized getters for all counters and block type, mutators `addRemoteBytes()`, `addLocalBytes()`, `addShortCircuitBytes()`, `addZeroCopyBytes()`, `addErasureCodingDecodingTime()`, package-private `setBlockType()`, and `clear()`. The copy constructor snapshots byte counters from another instance.

Counter updates are hierarchical: remote increments total only; local increments total and local; short-circuit increments total/local/short-circuit; zero-copy increments total/local/short-circuit/zero-copy. Remote bytes are computed as total minus local. `clear()` resets byte counters and EC decode time; the default block type is `CONTIGUOUS`.

State is in-memory and synchronized on the instance. It depends on `BlockType` and integrates with `DFSInputStream` and `DFSStripedInputStream` statistics exposed to HDFS clients.

Risks include the copy constructor not copying `blockType` or EC decode time, no validation against negative increments, and derived remote bytes becoming negative if counters are corrupted. Test signals include each counter path, derived remote bytes, synchronization/copy behavior, clear semantics, block type changes, EC decode accumulation, and invalid increment handling.
