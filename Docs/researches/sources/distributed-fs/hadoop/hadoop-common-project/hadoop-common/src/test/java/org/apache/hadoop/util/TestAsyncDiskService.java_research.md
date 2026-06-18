<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestAsyncDiskService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestAsyncDiskService.java

## Purpose

`TestAsyncDiskService.java` validates per-volume task execution and shutdown behavior for `AsyncDiskService`.

## Important APIs, Types, and Functions

The class defines volatile `count`, nested `ExampleTask`, and `testAsyncDiskService`. It uses `AsyncDiskService.execute`, `shutdown`, and `awaitTermination`.

## Control Flow

The test creates a service with two volumes, submits 100 tasks alternating between volumes, verifies submission to an unknown volume throws, shuts down, waits up to five seconds, and asserts all tasks incremented the counter.

## State and Persistence Behavior

State is in-memory only: executor queues and a synchronized counter. No disk IO is performed despite the service name.

## Dependencies and Integration Points

It integrates with Hadoop's asynchronous disk executor abstraction, JUnit 5, and SLF4J.

## Risks and Edge Cases

Thread scheduling can make shutdown timing flaky on very slow hosts. The volatile counter is incremented under synchronization to avoid lost updates.

## Test Signals

Signals include successful execution count, unknown-volume `RuntimeException`, and timely executor termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestAsyncDiskService.java -->
