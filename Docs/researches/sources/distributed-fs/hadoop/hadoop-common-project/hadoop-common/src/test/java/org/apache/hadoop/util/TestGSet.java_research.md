<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestGSet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestGSet.java

## Purpose

`TestGSet.java` stress-tests Hadoop `GSet` implementations, especially `LightWeightGSet` and `LightWeightResizableGSet`, for map/set semantics, iteration behavior, and capacity computation.

## Important APIs, Types, and Functions

It uses `GSet`, `LightWeightGSet`, `LightWeightResizableGSet`, `LightWeightGSet.LinkedElement`, nested `GSetTestCase`, `IntData`, and `IntElement`, plus capacity helpers `computeCapacity`, `getPercent`, and `isPowerOfTwo`.

## Control Flow

Exception tests verify null keys/elements, remove behavior, iterator remove rules, and concurrent modification detection. Main tests generate randomized integer elements, insert, lookup, replace, remove, iterate, clear, and compare against an internal oracle collection. Capacity tests validate invalid percentages/memory and ensure computed capacities are powers of two near the requested memory percentage.

## State and Persistence Behavior

State is in-memory random data, GSet buckets, linked elements, and oracle collections. There is no persistence.

## Dependencies and Integration Points

It integrates with Hadoop's memory-efficient hash set used by storage subsystems, `HadoopIllegalArgumentException`, Java iterators, and JUnit 5.

## Risks and Edge Cases

Risks include linked-element pointer corruption, iterator invalidation, replacement semantics, null handling, resizing behavior, and capacity overflow/rounding against JVM max memory.

## Test Signals

Signals include oracle equality after randomized operations, size checks, expected exceptions, concurrent modification detection, iterator remove semantics, and capacity power-of-two/percentage bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestGSet.java -->
