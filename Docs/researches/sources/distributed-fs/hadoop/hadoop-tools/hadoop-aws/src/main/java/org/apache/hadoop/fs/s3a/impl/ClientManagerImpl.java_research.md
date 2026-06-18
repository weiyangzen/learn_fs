<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ClientManagerImpl.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ClientManagerImpl.java

## Purpose

`ClientManagerImpl` is the default lazy lifecycle manager for sync, async, unencrypted, and transfer-manager AWS clients used by S3A.

## Important APIs, Types, and Functions

It stores configured client factories, creation parameters, a duration tracker, and `LazyAutoCloseableReference` wrappers. Public methods implement all `ClientManager` getters, `getUri()`, `serviceStop()`, and `toString()`.

## Control Flow

Constructor wires lazy references to callable factory methods. Getters are synchronized, check the service is not closed, and create clients on first use while tracking creation duration. Transfer manager creation forces async client creation. `serviceStop()` closes all created resources asynchronously and waits for all close futures.

## State and Persistence Behavior

State is in-memory client references and service state. Lazy references close only if created. No client metadata is persisted.

## Dependencies and Integration Points

It depends on `S3ClientFactory`, AWS sync/async clients, `S3TransferManager`, Hadoop `AbstractService`, IO statistics duration tracking, and lazy-close utilities.

## Risks and Edge Cases

Null unencrypted factory is allowed until the unencrypted client is requested. Close failures are awaited together. Synchronization serializes lazy creation and protects closed-state checks.

## Test Signals

Test lazy creation order, transfer-manager dependency on async client, close of only created resources, closed-service rejection, checked and unchecked getter failure paths, duration tracking, and CSE unencrypted factory behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ClientManagerImpl.java -->
