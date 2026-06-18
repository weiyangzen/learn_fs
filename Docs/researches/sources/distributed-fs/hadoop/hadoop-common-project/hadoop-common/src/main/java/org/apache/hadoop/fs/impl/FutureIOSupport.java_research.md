# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FutureIOSupport.java

## Purpose
Deprecated compatibility facade over org.apache.hadoop.util.functional.FutureIO.

## Important APIs, Types, and Functions
awaitFuture overloads, raiseInnerCause overloads, propagateOptions overloads, eval().

## Control Flow
Every method delegates to FutureIO, preserving older linkage while centralizing actual future handling in FutureIO.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Used by external or older filesystem implementations that imported this class.

## Risks and Test Signals
Risks are compatibility/linkage regressions and exception conversion mismatches. Tests should compare behavior with FutureIO for IO, runtime, interrupted, timeout, and completion failures.
