# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataMetricsTest.java

## Purpose
This PowerMock/JUnit test class validates metrics emitted by the legacy metadata sync path in `DefaultFileSystemMaster`, `InodeSyncStream`, `UfsStatusCache`, the instrumented metadata sync executors, and per-mount UFS operation counters. It extends `FileSystemMasterSyncMetadataTestBase`, which provides a real `DefaultFileSystemMaster` backed by a local `FlakyLocalUnderFileSystem` and static mocking of `UnderFileSystem.Factory`.

## Important APIs, Types, and Functions
- `metadataSyncMetrics()` constructs `InodeSyncStream` instances directly and asserts `DefaultFileSystemMaster.Metrics` counters for stream count, success, failure, skipped streams, changed/no-change paths, and per-path failures.
- `metadataPrefetchMetrics()` exercises `UfsStatusCache.prefetchChildren`, `fetchChildrenIfAbsent`, `remove`, and sync-time prefetch behavior through `InodeSyncStream`.
- `ufsStatusCacheSizeMetrics()` validates cache size counters for single statuses and children lists.
- `instrumentedThreadPool()` stresses `MetricKey.MASTER_METADATA_SYNC_EXECUTOR` and `MASTER_METADATA_SYNC_PREFETCH_EXECUTOR` meters under concurrent repeated syncs.
- `mountPointOpsCount()` reads a mount-specific counter from `MountTable.getUfsSyncMetric`.
- The test uses `AuthenticatedClientUser`, `UserState`, `MetricsSystem`, Dropwizard `Counter`/`Meter`, `LockingScheme`, `DescendantType`, and `FileSystemMasterCommonPOptions`.

## Control Flow
Setup delegates to the base fixture, then sets an authenticated user. The tests create local UFS directory/file hierarchies, run sync streams against `/` or individual paths, mutate UFS state, and compare metric deltas after each operation. Error coverage is driven by `FlakyLocalUnderFileSystem` flags that make `getStatus` or `listStatus` throw `IOException`, `RuntimeException`, or sleep.

`metadataPrefetchMetrics` first validates explicit cache prefetches, then invokes a full `InodeSyncStream` with prefetch enabled and checks aggregate prefetch counts. The concurrent tests use fixed thread pools; each worker repeatedly syncs a per-thread directory and checks monotonic executor meters before final exact total assertions.

## State and Persistence Behavior
The source file is test-only and does not persist production state directly. It observes state transitions in the inode tree, UFS status cache contents, and global `MetricsSystem` counters/meters. The base fixture uses a UFS journal, but this class focuses on in-memory metric side effects rather than replay.

## Dependencies and Integration Points
It integrates `DefaultFileSystemMaster` with `InodeSyncStream`, `UfsStatusCache`, `MountTable`, `InodeTree`, the absent-path cache, executor-service instrumentation, and the local UFS adapter. Static UFS factory mocking means the master under test always receives the base fixture's flaky UFS.

## Risks
- Several assertions depend on exact counter deltas and can fail when sync internals add or remove UFS calls.
- Global metrics state must be reset correctly; leakage from previous tests would invalidate exact counts.
- Concurrency tests assume executor meters increase promptly and monotonically, making them sensitive to instrumentation or scheduling changes.
- The `mIsSlow` retry check asserts only that retries are positive, so it detects retry presence but not retry policy quality.

## Test Signals
Strong regression signals include `SyncStatus.OK`, `NOT_NEEDED`, and `FAILED`; exact `INODE_SYNC_STREAM_*` counters; exact prefetch success/failure/cancel/path counts; cache size counters after add/replace/remove; executor submitted/completed totals; and per-mount UFS operation count totals.
