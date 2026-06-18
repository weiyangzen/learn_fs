# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestModTime.java

## Purpose
This test validates HDFS file and directory modification-time semantics for create, rename, delete, close, and NameNode edit-log replay.

## Important APIs, Types, And Functions
`testModTime` creates files/directories, captures `FileStatus.getModificationTime`, performs rename and delete operations, and checks which inode mtimes change. `testModTimePersistsAfterRestart` verifies the file mtime updated by close persists after NameNode restart. Helpers `cleanupFile` and `printDatanodeReport` handle cleanup and diagnostics.

## Control Flow
The first test starts a six-DataNode cluster, creates `testdir1/test1.dat`, records file and directory mtimes, creates another file under the directory, creates a second directory, renames the first file into the second directory, and deletes it. Assertions confirm a file's mtime is preserved by rename, source and destination directories change on rename, unrelated directories do not change on delete, and the deletion target directory does change. The restart test creates an open file, sleeps, closes it, restarts the NameNode, and compares mtimes before and after restart.

## State And Persistence
State under test is HDFS inode modification time and edit-log replay of OP_CLOSE-related mtime updates. `testModTimePersistsAfterRestart` is the persistence-sensitive regression path: the later close time must be reflected after NameNode restart rather than reverting to create/open time.

## Dependencies And Integration Points
The file uses `MiniDFSCluster`, `DFSClient`, `FileSystem`, `FileStatus`, `DFSTestUtil`, `ThreadUtil.sleepAtLeastIgnoreInterrupts`, and datanode reports for diagnostics.

## Risks
Mtime assertions compare coarse wall-clock values; very fast operations or filesystem clock behavior can make equality/inequality checks sensitive. The test prints diagnostics to standard output and relies on real sleeping to force an observable mtime increase. Rename semantics must distinguish file inode mtime from parent directory mtime.

## Test Signals
Signals include nonzero file mtimes, unchanged file mtime after rename, changed parent directory mtimes on namespace updates, unchanged unrelated directory mtime after deletion elsewhere, increased mtime after close, and exact preservation of close mtime after NameNode restart.
