<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSShellTouch.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSShellTouch.java

## Purpose
`TestDFSShellTouch` validates the HDFS implementation of the newer `-touch` shell command, especially explicit timestamp parsing and selective access/modification time updates for files and directories.

## Important APIs, Types, and Functions
- Shared `MiniDFSCluster`, `DistributedFileSystem`, and `FsShell` are initialized once for the class.
- `TouchCommands.Touch().getDateFormat()` is reused to format and parse timestamps in the same syntax accepted by the shell command.
- `shellRun` invokes `shell.run(args)`, logs the command, and returns the exit code.
- `FileStatus#getAccessTime` and `getModificationTime` are the verification surface.

## Control Flow
`testTouch` creates a file, then applies `-touch -t`, `-touch -a -t`, `-touch -m -t`, combined `-a -m`, missing timestamp failure, and `-c -t` behavior. Between selective updates, it stores the previous `FileStatus` and sleeps briefly so unchanged and changed fields can be distinguished.

`testTouchDirs` creates a directory and a child file, then repeats full, modification-only, and access-only updates against the directory itself. It verifies that directory timestamps are updated through the shell and cleans up both paths.

## State and Persistence Behavior
The tests persist timestamp metadata on HDFS files/directories, not contents. They create fixed relative paths (`newFile1`, `dir2/newFile2`, `dir2`) in the shell working directory and delete them at the end of each test. Timestamp precision depends on the date format used by the touch command and on the NameNode storing times exactly enough for equality comparisons.

## Dependencies and Integration Points
The file integrates `FsShell`, `org.apache.hadoop.fs.shell.TouchCommands`, HDFS `setTimes` behavior, timestamp parsing/formatting, and `FileStatus` metadata reads. It also uses AssertJ for fluent checks and `StringUtils.join` for logging.

## Risks
The tests depend on `Thread.sleep(500)` and millisecond timestamp equality after format/parse truncation. Fixed relative paths can collide in parallel runs. `-c` coverage is slightly indirect because it is invoked on an existing file even though the assertion message says non-existent file.

## Test Signals
Signals include exact exit-code checks and exact timestamp equality for both fields, plus unchanged-field assertions for `-a` and `-m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSShellTouch.java -->
