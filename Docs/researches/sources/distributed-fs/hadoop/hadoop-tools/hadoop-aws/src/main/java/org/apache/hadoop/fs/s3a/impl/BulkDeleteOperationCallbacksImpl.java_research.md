<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BulkDeleteOperationCallbacksImpl.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BulkDeleteOperationCallbacksImpl.java

## Purpose

`BulkDeleteOperationCallbacksImpl` is the concrete S3A store-backed callback for `BulkDeleteOperation`.

## Important APIs, Types, and Functions

It implements `bulkDelete(List<ObjectIdentifier>)` and has a private `deleteSingleObject(String)` helper. Constructor state includes the store, log path, page size, and audit span.

## Control Flow

The callback activates the audit span, checks the batch size, returns immediately for zero keys, and uses single-object delete for one key. Multi-key deletes build a bulk delete request via the store request factory and call `store.deleteObjects()` through `Invoker.once`; returned S3 errors are converted to key/string pairs. Single-object access-denied failures are returned as per-key errors rather than thrown.

## State and Persistence Behavior

The class is stateless apart from constructor fields. It does not persist delete state; S3 object deletion is the external side effect.

## Dependencies and Integration Points

It integrates with `S3AStore`, request factories, AWS `DeleteObjectsResponse`, `S3Error`, `ObjectIdentifier`, audit spans, and Hadoop retry translation.

## Risks and Edge Cases

Single-object and multi-object error semantics differ: access denied on a single delete is returned as an item failure, while other IO failures propagate. Page-size checks duplicate the public operation's check and protect direct callback use.

## Test Signals

Tests should cover zero, one, and many keys; access-denied single delete; returned multi-delete errors; page overflow; span activation; and request factory invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BulkDeleteOperationCallbacksImpl.java -->
