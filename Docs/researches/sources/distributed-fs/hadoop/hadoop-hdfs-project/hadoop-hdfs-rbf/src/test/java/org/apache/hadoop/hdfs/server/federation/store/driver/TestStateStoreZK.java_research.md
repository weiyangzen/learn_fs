# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/driver/TestStateStoreZK.java

Purpose: `TestStateStoreZK` validates `StateStoreZooKeeperImpl` against the shared state-store driver contract and adds ZooKeeper-specific tests for null znode cleanup and asynchronous operation performance.

Important APIs and setup: `setupCluster()` starts a Curator `TestingServer`, creates a `CuratorFramework` client with `RetryNTimes`, configures `RBFConfigKeys.FEDERATION_STORE_ZK_ADDRESS`, disables frequent connection auto-repair by setting `FEDERATION_STORE_CONNECTION_TEST_MS` to one hour, sets `FEDERATION_STORE_ZK_ASYNC_MAX_THREADS` to ten, captures the configured parent znode, and initializes the base state store. Each test removes all records and sets concurrent mode off before starting.

Control flow and ZooKeeper behavior: `generateFakeZNode()` maps a record class to the expected state-store znode path under the base znode and a fake primary key. `testGetNullRecord()` manually creates persistent znodes with null data for each record family, calls `driver.get(recordClass)`, and asserts the driver deletes those invalid znodes; it repeats the check in concurrent mode. CRUD and fetch-error tests run once in synchronous mode and once after `setEnableConcurrent(true)`.

Performance and persistence behavior: `testAsyncPerformance()` creates 1000 `MountTable` records, measures synchronous `putAll`, measures synchronous removal of five entries, clears the rest, then enables concurrent mode and asserts async `putAll` and async `removeMultiple` are faster than the synchronous equivalents. `testCacheLoadMetrics()` expects three explicit cache refreshes to add three mount-table cache-load samples.

Dependencies and integration points: the class integrates Curator test server/client, ZooKeeper `CreateMode`, `StateStoreUtils.getRecordName`, ZooKeeper driver configuration, RBF record classes, and the shared driver base. It is the concrete contract test for both sequential and concurrent ZooKeeper driver paths.

Risks and test signals: wall-clock performance comparisons can be environment-sensitive, especially under loaded CI. The null-record cleanup test is a strong compatibility signal: the driver must tolerate and remove malformed znodes rather than returning null data as records or failing future reads. The repeated synchronous/concurrent contract checks signal that concurrency is an internal optimization, not an API behavior change.
