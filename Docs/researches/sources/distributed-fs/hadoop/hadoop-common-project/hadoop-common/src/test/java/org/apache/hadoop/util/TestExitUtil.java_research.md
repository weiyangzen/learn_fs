<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestExitUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestExitUtil.java

## Purpose

`TestExitUtil.java` tests Hadoop's test-safe wrappers around `System.exit` and `Runtime.halt`.

## Important APIs, Types, and Functions

It uses `ExitUtil.disableSystemExit`, `disableSystemHalt`, `terminate`, `halt`, `terminateCalled`, `haltCalled`, first-exception getters/resetters, `ExitException`, `HaltException`, and `LambdaTestUtils.intercept`.

## Control Flow

Setup disables real process termination and resets state. Tests forge two exit or halt exceptions, invoke terminate/halt twice, assert the thrown object is the supplied exception, and verify only the first exception is remembered until reset.

## State and Persistence Behavior

State is static/global inside `ExitUtil`: disabled flags, first exit/halt exceptions, and called flags. Tests reset state before and after.

## Dependencies and Integration Points

It integrates with process-termination guards used by Hadoop CLI tests and extends `AbstractHadoopTestBase`.

## Risks and Edge Cases

Leaked disabled/exception state could affect unrelated tests. The first-exception retention contract matters for diagnosing the original exit cause.

## Test Signals

Signals include called flags, object identity of thrown exceptions, first-exception retention across second call, and reset clearing state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestExitUtil.java -->
