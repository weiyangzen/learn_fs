# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileAppend3.java

## Purpose

`TestFileAppend3.java` implements append scenarios from HADOOP-2658 and related partial-checksum regressions. The complete 629-line file was read. It validates append at block boundaries, non-boundaries, simultaneous append exclusion, corrupted replicas, rename while appending, partial CRC chunk append, small append races, and mixed `NEW_BLOCK`/normal append sequences.

## Important APIs, Types, and Functions

Important APIs include `DistributedFileSystem.append`, `CreateFlag.NEW_BLOCK`, `LocatedBlocks`, `LocatedBlock`, `ExtendedBlock`, `DataNodeTestUtils.getFSDataset`, `InterDatanodeProtocol`, Mockito `spy/when`, `DFSClientAdapter`, and `SubjectInheritingThread`. Static fixture setup creates one 5-DataNode cluster with `BLOCK_SIZE=64 KiB`, replication 3, and 512 bytes per checksum.

## Control Flow

The TC tests use a shared cluster. TC1 appends half a block after exactly one full block. TC2 appends after a 1.5-block file and, for `NEW_BLOCK`, asserts separate block sizes. TC5 opens one append stream and verifies other clients cannot append until it closes. TC7 truncates one replica's data to zero before appending and verifies remaining replicas preserve readability. TC11 appends, hflushes, renames the file before close, then checks DataNode stored block sizes match NameNode located block sizes. TC12 and `testAppendToPartialChunk` focus on appending to partial checksum chunks over multiple hflushes. `testSmallAppendRace` delays `DFSClient.getFileInfo` with Mockito and runs concurrent small append attempts to expose stale file status bugs.

## State and Persistence Behavior

State includes open leases, renamed under-construction files, corrupted materialized replicas, block sizes on DataNodes, static cluster/filesystem state, and file content across repeated appends.

## Dependencies and Integration Points

The suite links DFSClient append paths, inter-DataNode recovery logging, DataNode datasets, Mockito-injected client delays, and append helper content generation.

## Risks and Edge Cases

Risks include stale file status across checksum chunk boundaries, not rejecting simultaneous appenders, mismatched DataNode and NameNode block lengths after rename, and partial checksum chunk corruption when `NEW_BLOCK` leaves a middle block incomplete.

## Test Signals

Signals are `AppendTestUtil.check` byte verification, expected IO failures for concurrent append, exact located block counts and sizes, matching DataNode stored block byte counts, and no checksum failures during repeated small append races.
