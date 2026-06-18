<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/tags/ScaleTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/tags/ScaleTest.java

## Purpose

`ScaleTest.java` marks JUnit 5 tests intended to validate behavior at scale.

## Important APIs, Types, and Functions

The annotation targets methods and types, is runtime-retained, inherited, and applies `@Tag("scale")`.

## Control Flow

There is no executable logic. The tag influences JUnit test selection.

## State and Persistence Behavior

No mutable state exists; compiled annotation metadata is retained.

## Dependencies and Integration Points

It integrates with JUnit Jupiter and Hadoop build profiles that separate scale tests from ordinary unit tests.

## Risks and Edge Cases

Scale tests can require large time, data, or cluster resources. Missing tags can make default CI slow or flaky.

## Test Signals

Test runner include/exclude behavior for `scale` is the key signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/tags/ScaleTest.java -->
