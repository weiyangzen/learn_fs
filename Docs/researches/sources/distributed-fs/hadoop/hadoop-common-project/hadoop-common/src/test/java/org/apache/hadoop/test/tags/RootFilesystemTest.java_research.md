<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/tags/RootFilesystemTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/tags/RootFilesystemTest.java

## Purpose

`RootFilesystemTest.java` marks tests that operate against or require the root filesystem.

## Important APIs, Types, and Functions

It is a runtime, inherited annotation for methods and types with `@Tag("root")`.

## Control Flow

There is no code flow beyond JUnit tag discovery.

## State and Persistence Behavior

No runtime state is owned; annotation metadata is retained.

## Dependencies and Integration Points

It depends on Java annotation metadata and JUnit Jupiter tagging. Build jobs can use the `root` tag to isolate tests that require special filesystem assumptions or privileges.

## Risks and Edge Cases

Root filesystem tests can be destructive or environment-dependent if not isolated. Incorrect tagging can cause tests to fail on CI nodes with restricted permissions.

## Test Signals

Runner filtering for the `root` tag and class-level inheritance are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/tags/RootFilesystemTest.java -->
