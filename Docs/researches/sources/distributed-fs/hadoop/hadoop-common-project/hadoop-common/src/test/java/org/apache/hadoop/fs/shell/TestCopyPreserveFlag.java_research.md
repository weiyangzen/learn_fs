# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCopyPreserveFlag.java

## Purpose
Tests the `-p` preserve flag across FsShell copy commands: `put`, `copyFromLocal`, `get`, and `cp`, including combinations with queue size and thread options.

## Important APIs, Types, and Functions
The test uses `CopyCommands.Put`, `CopyCommands.CopyFromLocal`, `CopyCommands.Get`, and `CopyCommands.Cp`. It configures `LocalFileSystem`, fixed source modification/access times, and a non-default `FsPermission`. Helpers `assertAttributesPreserved` and `assertAttributesChanged` inspect `FileStatus` permission and timestamps.

## Control Flow
Each test setup creates a local working root, source directory/file, target directory, writes sample data, sets file and directory permissions, and sets timestamps. `run` executes a command with the local configuration and expects exit code 0. Tests run commands with and without `-p`, with `-q 100`, with `-t 10`, and for directory `cp`. Special-character path coverage uses a source directory containing a space. Preserve-enabled cases assert target modification time, access time, and permissions equal the source fixtures; non-preserve cases assert they differ.

## State and Persistence
State is local filesystem metadata under a temporary root. It is deleted after each test. The preserved state includes times and permissions, which are the behavior under test.

## Dependencies and Integration Points
This is cross-command coverage for `CommandWithDestination` copy attribute propagation. It also verifies queue-size options on `Put` and `Get` remain compatible with preservation.

## Risks and Edge Cases
Local filesystem timestamp precision and default permissions can affect "changed" assertions, but fixed times are intentionally far from current time. The tests cover attributes but not ownership/group preservation. Directory preserve behavior is checked for `cp`.

## Test Signals
Passing tests signal that `-p` consistently preserves time and permission metadata while default copy paths create fresh metadata, even with thread and queue options.
