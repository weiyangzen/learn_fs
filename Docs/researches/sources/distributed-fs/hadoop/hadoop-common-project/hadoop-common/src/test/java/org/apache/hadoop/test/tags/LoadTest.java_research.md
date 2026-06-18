<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/tags/LoadTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/tags/LoadTest.java

## Purpose

`LoadTest.java` marks JUnit 5 tests that generate load or perform load-oriented validation.

## Important APIs, Types, and Functions

The annotation targets methods and types, is retained at runtime, is inherited, and applies `@Tag("load")`.

## Control Flow

There is no executable flow. Test runners use the tag metadata to select or skip load tests.

## State and Persistence Behavior

The file owns no state; annotation metadata persists in class files.

## Dependencies and Integration Points

It integrates with JUnit Jupiter tag filtering and Hadoop test profiles that separate heavy load tests from regular unit tests.

## Risks and Edge Cases

Load tests may be expensive or timing-sensitive; wrong tagging can either hide coverage or overload routine CI jobs.

## Test Signals

Runner filtering by `load` and annotation inheritance on classes are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/tags/LoadTest.java -->
