# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/sftp/TestSFTPFileSystem.java

## Purpose
Integration-tests Hadoop `SFTPFileSystem` against an embedded Apache MINA SSHD SFTP server backed by the local filesystem. It validates basic file operations, metadata mapping, connection pooling, and close behavior.

## Important APIs, Types, and Functions
The test configures `SshServer`, `UserAuthPasswordFactory`, a password authenticator accepting `user/password`, `SimpleGeneratorHostKeyProvider`, and `SftpSubsystemFactory`. Hadoop APIs include `FileSystem.get`, `LocalFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, and `Path`. Helper `touch` creates files through either local or SFTP filesystem. Assertions inspect `((SFTPFileSystem) sftpFs).getConnectionPool().getLiveConnCount()`.

## Control Flow
`@BeforeAll` skips Windows, starts SSHD on an OS-assigned port, configures `fs.sftp.impl`, sets the SFTP port, disables FS cache, creates a clean local test directory, and stores local filesystem handles. Each test obtains a fresh `sftpFs`; `@AfterEach` closes it. Tests create/delete files, verify existence from both local and SFTP views, read bytes, compare status paths and lengths, assert failure for deleting non-empty directories and invalid renames, compare access/modify times truncated to seconds, create directories, and verify filesystem close drains the connection pool and is reentrant.

## State and Persistence
Persistent test state is a temporary local directory under `GenericTestUtils.getTestDir()`. The embedded SFTP server exposes that filesystem to SFTP operations. Tests clean up files they create and `@AfterAll` deletes the whole test directory and stops SSHD.

## Dependencies and Integration Points
This file bridges Hadoop filesystem abstraction with Apache SSHD/SFTP. It depends on platform assumptions, test directory helpers, SFTP connection pool internals, and local filesystem timestamp semantics.

## Risks and Edge Cases
The test is skipped on Windows. Timestamp assertions account for SFTP second-level precision by truncating milliseconds. Network/server startup and local host behavior can make tests more integration-sensitive than pure unit tests. Connection count expectations assume one live connection per active filesystem operation series.

## Test Signals
Passing tests signal that SFTP create/open/delete/rename/list-status metadata operations work against a real SFTP protocol endpoint and that `SFTPFileSystem.close()` reliably closes pooled connections.
