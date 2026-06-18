<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/tools/GetGroupsTestBase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/tools/GetGroupsTestBase.java

## Purpose

`GetGroupsTestBase.java` is an abstract reusable test base for Hadoop `getgroups`-style command-line tools.

## Important APIs, Types, and Functions

It owns `Configuration conf`, synthetic `UserGroupInformation` users, abstract `getTool(PrintStream)`, `setUpUsers`, tests for no user, existing users, nonexistent users, mixed user lists, helper `getExpectedOutput`, and `runTool`.

## Control Flow

Setup registers the current user plus two test users with known groups. Each test invokes `ToolRunner.run(getTool(out), args)`, captures output in a `ByteArrayOutputStream`, and compares exact lines of `user : group...` output.

## State and Persistence Behavior

State is in-memory UGI test-user registry and captured output streams. No files are written.

## Dependencies and Integration Points

The base integrates with `UserGroupInformation`, Hadoop `Tool`/`ToolRunner`, subclass implementations of group lookup tools, and JUnit 5.

## Risks and Edge Cases

Exact output formatting depends on line separators and UGI group ordering. UGI test-user state is process-global, so tests must avoid name collisions.

## Test Signals

Signals include current-user fallback, multi-user ordering, empty group output for remote nonexistent users, and interleaved existing/nonexistent user behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/tools/GetGroupsTestBase.java -->
