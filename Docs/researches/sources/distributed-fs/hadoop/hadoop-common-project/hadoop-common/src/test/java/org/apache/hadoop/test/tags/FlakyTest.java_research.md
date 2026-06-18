<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/tags/FlakyTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/tags/FlakyTest.java

## Purpose

`FlakyTest.java` defines a JUnit 5 tag annotation for tests that are flaky due to external factors and may be filtered out of CI runs.

## Important APIs, Types, and Functions

The annotation targets methods and types, is retained at runtime, is inherited, carries `@Tag("flaky")`, and requires a `String value()` reason.

## Control Flow

There is no runtime code beyond annotation metadata consumed by JUnit discovery and tag filtering.

## State and Persistence Behavior

No state is owned. Metadata persists in compiled class files at runtime retention.

## Dependencies and Integration Points

It integrates with JUnit Jupiter tagging and build/test runner filters that include or exclude `flaky`.

## Risks and Edge Cases

Misuse can hide real race bugs. The required `value` helps document rationale but can be vague if not reviewed.

## Test Signals

Annotation retention, inherited behavior, and runner filtering by `flaky` are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/tags/FlakyTest.java -->
