# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/WrappedIOException.java

## Purpose
Deprecated UncheckedIOException subclass for wrapping IOException in APIs that cannot throw checked exceptions.

## Important APIs, Types, and Functions
Constructor requires IOException cause.

## Control Flow
No flow beyond Preconditions.checkNotNull(cause) and superclass initialization.

## State and Persistence Behavior
No state beyond wrapped cause.

## Dependencies and Integration Points
Retained for compatibility; replaced generally by standard UncheckedIOException usage.

## Risks and Test Signals
Tests should verify null rejection and cause preservation for compatibility.
