# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestAdminHelper.java

## Purpose
`TestAdminHelper` is a focused unit test for `AdminHelper.prettifyException`. It verifies how admin CLI helper code formats exceptions with and without explicit messages.

## Important APIs, Types, And Functions
The only production API under test is `AdminHelper.prettifyException(Throwable)`. The tests use JUnit 5 `@Test`, `assertTrue`, and `assertEquals`.

## Control Flow
`prettifyExceptionWithNpe` passes a plain `NullPointerException` and asserts the formatted string starts with the exception type plus the test method stack frame, proving message-less exceptions include useful location context. `prettifyException` passes an `IllegalArgumentException` with a cause and asserts only `IllegalArgumentException: Something is wrong` is emitted, proving the top-level message is preferred over nested-cause noise.

## State And Persistence Behavior
There is no persistent state. All behavior is pure string formatting of freshly constructed exceptions.

## Dependencies And Integration Points
This test supports HDFS admin tools that print user-facing exception summaries. It indirectly constrains CLI stderr/stdout quality because many admin commands call helper formatting when surfacing failures.

## Risks And Edge Cases
The NPE assertion includes a package and method prefix, so stack-frame naming changes or wrapper methods can break it. The cause-bearing exception test protects against overly verbose or misleading nested exception output.

## Test Signals
Signals are exact or prefix string matches. There is no MiniDFSCluster dependency, making this a fast unit-level guard for CLI error formatting.
