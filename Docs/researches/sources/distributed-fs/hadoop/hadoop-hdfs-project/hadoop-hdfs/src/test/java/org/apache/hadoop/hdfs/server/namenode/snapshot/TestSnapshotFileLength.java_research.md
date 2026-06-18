# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotFileLength.java

## Purpose
`TestSnapshotFileLength` verifies that a file read through a snapshot path is capped at the file length captured when the snapshot was taken, even if the live file is later appended or opened for append. It also verifies that shell-level `-cat` observes the same snapshot length boundary.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `DistributedFileSystem`, `DFSTestUtil`, `AppendTestUtil`, `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, `FileChecksum`, `FsShell`, and `ToolRunner`. Snapshot paths are built with `SnapshotTestHelper.getSnapshotPath`. Configuration sets `DFS_NAMENODE_MIN_BLOCK_SIZE_KEY` and `DFS_BYTES_PER_CHECKSUM_KEY` to the test block size so checksum and read-length expectations are deterministic.

## Control Flow
`testSnapshotfileLength` creates a file, appends enough data to make an original length, snapshots the parent, records the snapshot checksum, opens the live file for append, validates that live checksums fail while the file is under construction, writes and flushes additional bytes, then confirms the snapshot still reads only the original length and retains the original checksum. After closing the append stream, the live file checksum diverges while the snapshot checksum remains unchanged. `testSnapshotFileLengthWithCatCommand` repeats the length check through `FsShell -cat`, redirecting stdout/stderr into a byte buffer and asserting the emitted byte count equals the snapshot length.

## State and Persistence Behavior
The tests are about snapshot inode state rather than NameNode restarts. They confirm that snapshot file metadata stores length and checksum-relevant block state independently from subsequent live-file appends and under-construction block state.

## Dependencies and Integration Points
Coverage crosses client read paths, checksum retrieval, append/hflush behavior, snapshot namespace resolution, `FsShell` command execution, and NameNode block/checksum behavior for files under construction.

## Risks and Edge Cases
Important risks include clients reading beyond snapshot length, snapshot checksums accidentally tracking the live file, checksum calls on under-construction files succeeding when they should fail, and command-line tools bypassing snapshot length checks. The test relies on byte counts captured from process-global `System.out` and `System.err`, so the finally block restoring streams is important.

## Test Signals
Assertions cover live versus snapshot `FileStatus` lengths, positioned reads, whole-file buffer reads, checksum equality/inequality before and after append close, expected under-construction checksum failure text, and shell output byte count.
