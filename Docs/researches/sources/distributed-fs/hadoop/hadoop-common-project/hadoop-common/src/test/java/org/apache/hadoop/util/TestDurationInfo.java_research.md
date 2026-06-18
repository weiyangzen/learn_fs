<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestDurationInfo.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestDurationInfo.java

## Purpose

`TestDurationInfo.java` tests timed logging/measurement helper `DurationInfo`.

## Important APIs, Types, and Functions

Tests construct `DurationInfo` with logger/message variants, call `value`, `finished`, `close`, and `toString`, and assert null message handling.

## Control Flow

The suite creates an info object, sleeps, finishes/closes it, and verifies elapsed duration is positive. It also checks formatted messages for log-on-start true/false and double-close idempotence.

## State and Persistence Behavior

State is in-memory start/end timestamps and closed/finished status. Output may go through SLF4J logger but no file is directly written.

## Dependencies and Integration Points

It integrates with `DurationInfo`, SLF4J, and JUnit 5.

## Risks and Edge Cases

Timing assertions use real sleep and can be slow. The exact `toString` value assumes zero elapsed immediately after creation.

## Test Signals

Signals include positive duration after sleep, stable formatted message, idempotent close, and `NullPointerException` for null message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestDurationInfo.java -->
