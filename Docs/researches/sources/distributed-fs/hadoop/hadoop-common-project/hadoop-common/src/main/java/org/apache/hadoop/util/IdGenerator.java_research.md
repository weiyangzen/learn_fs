# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IdGenerator.java

## Purpose

`IdGenerator` is a minimal interface for objects that allocate monotonically or otherwise uniquely generated IDs.

## Important APIs, Types, And Functions

It declares `long nextValue()`. Implementations provide the allocation policy; the interface does not specify persistence, monotonicity after restart, or concurrency guarantees.

## Control Flow, State, And Persistence

There is no state in the interface. Consumers should treat ID behavior as implementation-defined unless a concrete implementation documents stronger guarantees.

## Dependencies And Integration Points

It has no external dependencies. It provides a common seam for Hadoop subsystems that need pluggable ID allocation.

## Risks And Test Signals

The missing semantic contract can lead to assumptions about uniqueness or ordering that a given implementation may not satisfy. Concrete implementation tests should cover concurrency, overflow, restart behavior, and collision guarantees.
