# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDistributedFileSystemWithECFile.java

## Purpose
Tests `DistributedFileSystem` and `FileContext` behavior for erasure-coded files, especially block-location reporting, edit-log replay of file-level EC policy choices, and filesystem read statistics. The suite starts a `MiniDFSCluster` sized to the active EC policy's data plus parity units, enables the policy, and marks `/ec` as an EC directory.

## Important APIs and Types
Key APIs include `DistributedFileSystem.enableErasureCodingPolicy`, `DFSClient.setErasureCodingPolicy`, `FileSystem.listFiles`, `FileSystem.getFileBlockLocations`, `FileContext.listLocatedStatus`, `FileContext.getFileBlockLocations`, and `FileSystem.Statistics`. It uses `ErasureCodingPolicy`, `SystemErasureCodingPolicies`, `BlockLocation`, `LocatedFileStatus`, `MiniDFSCluster`, `MiniDFSNNTopology`, and the builder-style `createFile(...).replicate()` / `.ecPolicyName(...)` APIs.

## Control Flow
`setup()` derives cell, stripe, block, and block-group sizes from `getEcPolicy()`, configures HDFS block size and load-insensitive placement, then creates an EC-enabled `/ec` tree. `createFile` writes deterministic bytes and waits for block groups. The three block-location tests cover files smaller than one cell, exactly one stripe, and larger than one block group; each validates both `DistributedFileSystem` and `FileContext` views. `testReplayEditLogsForReplicatedFile` rebuilds the cluster with HA, writes one inherited EC file, one forced replicated file, and one explicit alternate EC-policy file, then fails over to the second NameNode and verifies policy metadata. `testStatistics` reads an EC file and checks aggregate and thread-local EC byte counters.

## State, Persistence, Dependencies, Integration
Persistent state is NameNode namespace/edit-log metadata for EC policy inheritance and per-file policy overrides. The tests depend on EC policy definitions, striped block reporting, HA edit replay, and filesystem statistics accounting. Integration points include HDFS client file creation options, NameNode policy lookup, block manager reports, and `FileContext` compatibility.

## Risks and Test Signals
High-value signals are host-count and length calculations for partial EC groups, survival of replicated and alternate-policy files through HA edit replay, and EC byte-read counter correctness. Risks are timing sensitivity around block group reports and accidental coupling to default policy geometry; the random-policy subclass broadens that coverage.
