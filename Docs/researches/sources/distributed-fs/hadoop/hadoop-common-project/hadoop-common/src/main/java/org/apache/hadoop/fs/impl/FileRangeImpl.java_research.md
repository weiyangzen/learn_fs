# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FileRangeImpl.java

## Purpose
Default mutable implementation of FileRange with offset, length, associated future, and optional caller reference.

## Important APIs, Types, and Functions
Constructor, getOffset(), getLength(), setOffset(), setLength(), setData(), getData(), getReference(), toString().

## Control Flow
No validation in setters/constructor; validation is expected in VectoredReadUtils or callers. setData stores a CompletableFuture<ByteBuffer> returned to clients.

## State and Persistence Behavior
Stores mutable range metadata and future. No persistence.

## Dependencies and Integration Points
Used by FileRange factory paths and CombinedFileRange.

## Risks and Test Signals
Risks are invalid offset/length being set and future replacement races. Tests should cover factory validation and reference preservation.
