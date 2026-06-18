# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Progressable.java

## Purpose
`Progressable` is Hadoop's stable public callback interface for code that must report liveness or progress to the framework during long-running operations.

## Important APIs, Types, And Functions
The interface declares one method, `progress()`. Implementations decide how to propagate that signal.

## Control Flow
There is no built-in control flow. Callers invoke `progress()` opportunistically from loops or blocking operations. Framework implementations can reset timeout counters, update task status, or drive monitoring.

## State And Persistence
The interface owns no state and no persistence. State is entirely implementation-specific.

## Dependencies And Integration Points
It depends only on Hadoop annotations. It appears in utility algorithms such as `QuickSort.sort(..., Progressable)` and in Hadoop IO/MapReduce paths where repeated progress signals prevent false task timeouts.

## Risks
The contract does not specify idempotency, blocking behavior, or exception handling. Callers should assume implementations may be nontrivial and avoid invoking it while holding locks that could deadlock with framework callbacks.

## Test Signals
Tests generally use counting implementations to assert that long-running utilities call `progress()` and that exceptions or slow callbacks are handled according to the caller's own contract.
