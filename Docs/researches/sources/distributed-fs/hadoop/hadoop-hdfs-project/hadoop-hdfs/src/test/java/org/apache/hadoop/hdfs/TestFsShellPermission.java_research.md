# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFsShellPermission.java

## Purpose
Tests privilege and permission behavior of `FsShell -rm -r` and `-rm -r -f` against HDFS directories and files owned by different users.

## APIs and Control Flow
`FileEntry` describes test paths, directory flags, owners, groups, and permissions. `createFiles` materializes those entries, sets permission and owner, and `deldir` cleans test roots. `execCmd` captures `FsShell.run` output and return code. `TestDeleteHelper.execute` builds a fixture under `/testroot`, runs the shell command under a chosen `UserGroupInformation`, then verifies whether the target was deleted. Helper factories create empty-directory, non-empty-directory, and single-file cases with varying target permissions and user identities. `testDelete` creates a `MiniDFSCluster`, builds the helper list, and executes each scenario.

## State, Dependencies, Integration
State is HDFS ownership, group, permissions, and delete side effects. It depends on `FsShell`, `FileSystemTestHelper`, `UserGroupInformation`, `FsPermission`, and Apache `StringUtils`. It integrates CLI behavior with Namenode permission enforcement.

## Risks and Test Signals
The signal is binary existence after command execution for each permission matrix entry. Risks include captured `System.out` global mutation, command parsing by whitespace, and permission semantics that depend on parent directory permissions more than child readability.
