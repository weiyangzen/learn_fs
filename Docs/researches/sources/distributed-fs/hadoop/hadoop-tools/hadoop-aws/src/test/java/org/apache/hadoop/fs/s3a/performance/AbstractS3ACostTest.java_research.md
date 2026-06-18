# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/AbstractS3ACostTest.java

## Purpose
`AbstractS3ACostTest` is a shared base class for S3A integration tests that assert operation-cost metrics. It wraps `AbstractS3ATestBase` with metric-diff validation, common file/dir creation helpers, and status probe helpers.

## Important APIs, Types, and Functions
- Extends `AbstractS3ATestBase`.
- `createConfiguration()` disables filesystem caching and removes create-performance overrides while preserving access point ARN bucket config.
- `setup()` initializes an `OperationCostValidator`, records whether bulk delete is enabled, selects the delete marker statistic, and sets the audit span source.
- `setupCostValidator()` registers all counter and duration `Statistic` values as tracked metrics.
- Helpers include `buildFile()`, `dir()`, `file()`, `create()`, `execRename()`, `directoriesInPath()`, `resetStatistics()`, `verifyMetrics()`, `verifyMetricsIntercepting()`, `interceptOperation()`, `verify()`, `verifyInnerGetFileStatus()`, `interceptGetFileStatusFNFE()`, `isDir()`, `isFile()`, `with()`, and `assertEmptyDirStatus()`.

## Control Flow
Subclasses call inherited helpers around S3A operations. Each helper starts or relies on an audit span, executes a closure, and asks `OperationCostValidator` to compare metric diffs with expected probes. File helpers create or close objects through standard FS APIs, while status helpers call S3A internals to assert HEAD/LIST costs. Setup chooses the correct delete statistic depending on multi-delete configuration.

## State and Persistence Behavior
State includes the `OperationCostValidator`, `isBulkDelete`, and `deleteMarkerStatistic`. Helpers create S3 files/directories when used by subclasses. Metric baselines are reset with `resetStatistics()`.

## Dependencies and Integration Points
The class integrates S3A statistics, operation cost models, audit spans, file status internals, Hadoop contract utilities, and S3A test utilities such as `innerGetFileStatus()` and `isBulkDeleteEnabled()`.

## Risks and Edge Cases
Because it tracks every counter/duration statistic, new metrics or changed cost profiles can break many subclasses. It removes create-performance overrides to keep costs deterministic, but subclasses can still alter configuration. Access point ARN preservation avoids breaking access-point test buckets.

## Test Signals
Passing subclasses using this base signal not just functional correctness but stable S3A request/metric cost envelopes for filesystem operations.
