# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/CombinedFileRange.java

## Purpose
FileRangeImpl subclass representing one physical read covering multiple logical FileRange requests for vectored IO.

## Important APIs, Types, and Functions
Constructor, getUnderlying(), merge(), getDataSize(), toString().

## Control Flow
Constructor sets offset/length from rounded start/end and appends the original. merge checks gap against minSeek and total size against maxSize, updates length, and appends underlying range if compatible.

## State and Persistence Behavior
Maintains mutable length, underlying list, and dataSize for optimization accounting. No persistence.

## Dependencies and Integration Points
Created by VectoredReadUtils.mergeSortedRanges and consumed by filesystem vector read implementations.

## Risks and Test Signals
Risks include int length overflow, exposing mutable underlying list, and merge threshold off-by-one. Tests should cover adjacent, overlapping, far apart, maxSize, and dataSize calculations.
