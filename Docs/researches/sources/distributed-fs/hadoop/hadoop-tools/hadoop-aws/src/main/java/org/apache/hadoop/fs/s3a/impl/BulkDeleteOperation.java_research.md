<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BulkDeleteOperation.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BulkDeleteOperation.java

## Purpose

`BulkDeleteOperation` adapts Hadoop `BulkDelete` to S3A by validating paths under a base path, converting them to S3 object identifiers, and returning per-path delete failures.

## Important APIs, Types, and Functions

The class implements `pageSize()`, `basePath()`, `bulkDelete(Collection<Path>)`, and `close()`. Its nested `BulkDeleteOperationCallbacks` performs the actual S3 delete and returns key/error pairs.

## Control Flow

`bulkDelete()` requires the path collection to be non-null and no larger than the configured page size. Each path must be absolute and under `basePath`; it is converted with `StoreContext.pathToKey()`. Callback key failures are mapped back to qualified Hadoop paths with `keyToPath()`.

## State and Persistence Behavior

State is immutable after construction: callbacks, base path, and page size plus inherited context/span. No data is persisted and `close()` is empty.

## Dependencies and Integration Points

It depends on `BulkDeleteUtils.validatePathIsUnderParent`, AWS `ObjectIdentifier`, S3A `StoreContext`, retry annotations, and callback implementations backed by `S3AStore`.

## Risks and Edge Cases

Validation is strict: relative paths, paths outside the base, and oversized batches fail before S3 calls. Empty batches are delegated as an empty object list, with callback behavior expected to be safe.

## Test Signals

Cover base-path rejection, page-size enforcement, absolute-path validation, key/path round trips, callback error mapping, empty input, and captured audit span propagation through the callback implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BulkDeleteOperation.java -->
