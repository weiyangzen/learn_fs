# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuditLogs.java

## Purpose

`TestAuditLogs` verifies that standard HDFS and WebHDFS file operations generate correctly shaped NameNode audit log lines for allowed and denied access. It runs under both synchronous and asynchronous edit logging configurations.

## Important APIs, Types, and Functions

The class is a JUnit parameterized class over `useAsyncEdits`. It uses `MiniDFSCluster`, `DFSTestUtil`, `FileSystem`, `WebHdfsFileSystem`, `WebHdfsTestUtil`, `UserGroupInformation`, `LogCapturer`, log4j `AsyncAppender`, and regex patterns for audit format, success/failure, and WebHDFS open protocol. Helpers `verifySuccessCommandsAuditLogs` and `verifyFailedCommandsAuditLogs` scan captured audit output for matching `allowed=`, file path, and command text.

## Control Flow

`setupCluster` configures access-time precision, block reports, and async edit logging, creates a four-datanode cluster, populates test files, verifies the audit log appender is asynchronous, and creates a test UGI. Tests perform allowed HDFS open/stat, denied HDFS open, allowed WebHDFS open/stat, denied WebHDFS open, and a create using a path containing carriage-return/newline. Each scenario then scans the accumulated audit capture for required success or failure counts.

## State and Persistence Behavior

The test creates real files under `/srcdat`, changes permissions and ownership to force access outcomes, and cleans the namespace after each parameter run. Async edit logging is a NameNode configuration dimension rather than a separate persistence assertion; the tests verify audit logging remains present with the configured edit-log mode. Audit capture is static across the class and stopped after all tests.

## Dependencies and Integration Points

It integrates with `FSNamesystem.AUDIT_LOG`, log4j audit appenders, HDFS permission enforcement, WebHDFS protocol command mapping, test UGI filesystem creation, and path escaping in audit output. The expected audit line format includes `allowed`, `ugi`, `ip`, `cmd`, `src`, `dst`, and `perm`.

## Risks and Edge Cases

Because the capture is cumulative, helper counts use minimum counts for success paths and exact counts for failure paths. WebHDFS open can generate multiple audit entries, so the expected minimum differs from native HDFS. The CRLF path test checks that a malicious path does not inject raw newlines into audit output, but it only asserts matching on the `foo` prefix.

## Test Signals

Important signals are two native success audit lines for open/stat, one denied native open line, WebHDFS success lines including `cmd=open`/`cmd=getfileinfo`, one denied WebHDFS open line, `AUDIT_PATTERN` conformance, and successful create logging for a path containing `\r\n` without newline injection into the parsed audit stream.
