# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ZeroCopyUnavailableException.java

## Purpose
IOException used when zero-copy read support cannot be provided.

## Important APIs, Types, and Functions
Constructors accept message, message plus exception, or exception only.

## Control Flow
No internal flow; thrown by zero-copy/ByteBuffer read paths when prerequisites are missing.

## State and Persistence Behavior
No state beyond IOException cause/message.

## Dependencies and Integration Points
Related to FSDataInputStream enhanced ByteBuffer/zero-copy APIs.

## Risks and Test Signals
Tests should verify callers degrade or surface this exception consistently when zero-copy is disabled or unsupported.
