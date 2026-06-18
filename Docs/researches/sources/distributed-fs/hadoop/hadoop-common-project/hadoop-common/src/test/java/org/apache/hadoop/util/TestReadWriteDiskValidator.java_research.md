# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestReadWriteDiskValidator.java

Purpose: tests `ReadWriteDiskValidator` and its metrics by exercising successful read/write checks and failure accounting.

Important APIs and types: `DiskValidatorFactory.getInstance`, `ReadWriteDiskValidator.checkStatus`, `ReadWriteDiskValidatorMetrics`, `DefaultMetricsSystem`, `MetricsCollectorImpl`, `MetricsRecords`, `DiskChecker.DiskErrorException`, and `Shell.getSetPermissionCommand`.

Control flow: the success test runs 100 checks against the test build directory, verifies read/write quantile estimator counts, fetches the metrics source, and asserts failure metrics are zero and latency metrics exist. The failure test creates a temp directory, chmods it to `000`, expects `DiskErrorException` twice, collects metrics after each failure, and verifies failure count increments and last-failure timestamp increases.

State and persistence: uses filesystem test directories and metrics-system singleton state. Permissions are mutated to simulate disk access failure.

Dependencies and integration points: validates Hadoop disk-health probing and metrics publication used by datanode/local storage health checks.

Risks: platform permissions can behave differently, metrics source names are path-derived, and global metrics state may retain prior registrations. Test signals are metric values, metric existence checks, and failure message assertions.
