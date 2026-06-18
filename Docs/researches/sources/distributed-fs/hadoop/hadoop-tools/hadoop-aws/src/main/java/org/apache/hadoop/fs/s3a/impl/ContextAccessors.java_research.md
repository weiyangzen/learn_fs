<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ContextAccessors.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ContextAccessors.java

## Purpose

`ContextAccessors` defines S3A filesystem-level services exposed to `StoreContext` without giving store operations a direct filesystem reference.

## Important APIs, Types, and Functions

It declares path/key conversion, temp-file creation, bucket-location lookup, path qualification, active audit span lookup, and request factory access.

## Control Flow

Implementations must translate exceptions and provide the filesystem's authoritative behavior. Operation classes call these methods through `StoreContext` to avoid coupling to `S3AFileSystem`.

## State and Persistence Behavior

The interface has no state. Implementations may rely on filesystem state such as URI, working directory, region cache, and thread-local audit spans.

## Dependencies and Integration Points

It integrates with `Path`, Java `File`, S3A request factories, audit spans, retry annotations, and bucket-region discovery.

## Risks and Edge Cases

The active audit span is thread-local and must be captured before asynchronous handoff. Bucket location may fail with access denied. Path/key conversion must preserve root handling as empty key.

## Test Signals

Use mock implementations to test store operations. Cover root key conversion, relative path qualification, temp-file failures, access-denied bucket location, request factory retrieval, and audit-span capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ContextAccessors.java -->
