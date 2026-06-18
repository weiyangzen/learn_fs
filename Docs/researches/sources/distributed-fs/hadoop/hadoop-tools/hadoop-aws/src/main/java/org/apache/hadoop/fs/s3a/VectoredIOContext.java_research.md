# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/VectoredIOContext.java

## Purpose
`VectoredIOContext` holds configuration for S3A vectored read behavior: range merge thresholds and maximum active range reads.

## Important APIs, Types, and Functions
APIs are `setMinSeekForVectoredReads()`, `getMinSeekForVectorReads()`, `setMaxReadSizeForVectoredReads()`, `getMaxReadSizeForVectorReads()`, `setVectoredActiveRangeReads()`, `getVectoredActiveRangeReads()`, `build()`, and `toString()`.

## Control Flow and State
Setters validate the instance is still mutable and values are non-negative, then return `this`. `build()` marks the object immutable. Later setter calls fail through `checkMutable()`.

## State and Persistence Behavior
State is in-memory configuration. It becomes immutable after `build()` but is not deeply copied by this class. Zero values can intentionally disable range merging or extra active reads.

## Dependencies and Integration Points
Dependency is Hadoop `Preconditions.checkState`. `S3AReadOpContext` carries this object into `S3AInputStream#readVectored(...)` behavior.

## Risks and Test Signals
Risks include forgetting to call `build()`, sharing a mutable instance across streams, invalid zero/threshold interpretation, and naming inconsistency between `Vector` and `Vectored` getter/setter names. Tests should cover non-negative validation, immutability after build, toString content, and read-vector range-combination behavior using the configured thresholds.
