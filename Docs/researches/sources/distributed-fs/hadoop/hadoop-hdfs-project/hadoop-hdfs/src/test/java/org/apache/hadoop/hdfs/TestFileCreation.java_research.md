# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileCreation.java

## Purpose

`TestFileCreation.java` is the central HDFS file-creation regression suite. The complete 1,439-line file was read. It spans server defaults, client default caching, file and directory creation rules, overwrite, delete-on-exit, failure cleanup, lease persistence, non-recursive creation, simulated storage, concurrent writes, close semantics, non-canonical paths, file ID checks, and block cleanup after overwrite.

## Important APIs, Types, and Functions

Key APIs are `FileSystem.create`, `createNonRecursive`, `DistributedFileSystem`, `DFSClient`, `HdfsDataOutputStream`, `FsServerDefaults`, `MiniDFSCluster`, `SimulatedFSDataset`, `LeaseManager`, `NameNodeAdapter`, `BlockManager`, `LocatedBlocks`, `NamenodeProtocols.create/complete`, and metrics assertions. Public helpers `createFile`, `create`, `writeFile`, `testFileCreationNonRecursive`, and `createNonRecursive` are reused by neighboring tests.

## Control Flow

Server-default tests configure NameNode defaults, use Mockito to alter `FSNamesystem.getServerDefaults`, and verify client cache staleness or expiry. `checkFileCreation` validates root existence, directory overwrite rejection, file creation, quota/content length accounting, hostname and local interface settings, and simulated-storage usage. Failure tests kill DataNodes or create with insufficient replication, then confirm bad allocations are removed. Lease tests keep files open across renames and two NameNode restarts, then rewrite DFSOutputStream `src` fields to continue writing renamed files. Other tests cover DFSClient death, non-recursive parent errors, concurrent files, sync-on-close, hard lease expiry, filesystem close with open files, close timeout after DataNode loss, direct RPC rejection of non-canonical paths versus `Path` normalization, complete file ID mismatch, and overwrite block deletion through restart and checkpoint.

## State and Persistence Behavior

The file heavily exercises persistent namespace state: leases in fsimage, edit replay after restart, block maps, marked-delete queues, quotas, file status lengths, storage usage, and checkpointed overwrite results.

## Dependencies and Integration Points

It integrates NameNode RPCs, DFSClient output streams, block manager internals, DataNode datasets, metrics, permissions-disabled overwrite behavior, UGI, reflection against `DFSOutputStream.src`, and test utilities across HDFS.

## Risks and Edge Cases

Risks include lease loss after restart or rename, stale server defaults, corrupted edits from non-canonical RPC paths, blocks left in block maps after overwrite, close hangs under replication minimum, and accidental parent creation in non-recursive mode.

## Test Signals

Signals include exact defaults, metrics counters, file lengths, content summaries, simulated dataset usage, expected exception types/messages, located block counts, safe block cleanup assertions, byte equality after restart/checkpoint, and timeout-limited close behavior.
