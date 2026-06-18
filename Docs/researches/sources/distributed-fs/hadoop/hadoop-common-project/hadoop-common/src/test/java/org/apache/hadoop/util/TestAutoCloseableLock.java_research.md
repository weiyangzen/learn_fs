<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestAutoCloseableLock.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestAutoCloseableLock.java

## Purpose

`TestAutoCloseableLock.java` tests a lock wrapper designed for try-with-resources usage.

## Important APIs, Types, and Functions

Tests exercise `AutoCloseableLock.acquire`, `close`, `isLocked`, and `tryLock`, plus a worker thread helper that checks lock visibility from another thread.

## Control Flow

One test manually acquires and closes the lock. Multi-thread tests hold the lock in one thread, start a second thread that confirms it cannot acquire with `tryLock`, then release. The try-with-resources test ensures automatic close releases the lock after the block.

## State and Persistence Behavior

State is the in-memory lock hold state. No persistence exists.

## Dependencies and Integration Points

It integrates with `AutoCloseableLock`, Java threading, and JUnit 5 assertions.

## Risks and Edge Cases

The tests assume deterministic lock ownership/visibility across threads and do not deeply cover reentrancy or close-without-acquire behavior.

## Test Signals

Signals are `isLocked` transitions, identity of returned lock object, failed `tryLock` while held, and unlocked state after close/resource exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestAutoCloseableLock.java -->
