<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/tags/IntegrationTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/tags/IntegrationTest.java

## Purpose

`IntegrationTest.java` marks JUnit 5 tests that require a configured external service, commonly remote cloud stores.

## Important APIs, Types, and Functions

The annotation targets methods and types, is retained at runtime, is inherited, and applies `@Tag("integration")`.

## Control Flow

There is no executable logic. JUnit and build tooling consume the runtime annotation during test discovery.

## State and Persistence Behavior

No mutable state exists. Runtime annotation metadata is retained in compiled classes.

## Dependencies and Integration Points

It depends on Java annotation APIs and JUnit Jupiter `Tag`, integrating with Maven/Surefire/Failsafe or custom runner tag filters.

## Risks and Edge Cases

Incorrectly tagging unit tests as integration can reduce normal coverage; failing to tag external-service tests can make CI unstable or require unavailable credentials.

## Test Signals

The main signal is successful include/exclude behavior for the `integration` tag in the test runner.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/tags/IntegrationTest.java -->
