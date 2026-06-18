# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/MockS3AFileSystem.java

## Purpose

Test double for `S3AFileSystem` that relays most filesystem calls to an injected mocked `S3AFileSystem`, while stubbing S3A internals enough for committer and write-operation unit tests. It provides predictable URI/bucket identity, request construction, logging hooks, empty listing behavior, and no-op statistics.

## Important APIs, Types, and Functions

The class extends `S3AFileSystem` and exposes constants `BUCKET`, `FS_URI`, logging levels, and `REQUEST_FACTORY`. It overrides initialization, URI/path qualification, `getWriteOperationHelper()`, `createWriteOperationHelper()`, committer statistics, counters/gauges, `deleteObjectAtPath()`, and `createStoreContext()`. Delegated methods include `exists`, `open`, `create`, `append`, `rename`, `delete`, `listStatus`, `mkdirs`, and `getFileStatus`.

## Control Flow

Construction records the delegate filesystem and a pair of staging committer client outcomes, sets the URI, bucket, encryption secrets, and root. `initialize()` stores the configuration and creates a `WriteOperationHelper` with empty statistics, a noop auditor, and minimal callbacks. Public filesystem operations call `event()` for optional name/stack logging, then forward to the delegate. Methods that would create fake parents, update counters, or close resources are deliberately inert.

## State, Dependencies, and Integration Points

State includes the delegate mock, outcome pair, log level, configuration, write helper, and synthetic root path. It integrates with `RequestFactoryImpl`, `WriteOperationHelper`, `EmptyS3AStatisticsContext`, audit test support, committer tests, and `StoreContextBuilder`.

## Risks and Test Signals

Because it subclasses a complex filesystem and selectively overrides internals, it can drift when S3A initialization contracts change. The no-op statistics and empty `listFiles()` are intentional but can hide behavior if used outside narrow unit tests. Its value is high for verifying call paths and request construction without live S3 side effects.
