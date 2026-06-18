# Research Report: subset-b-007457

This grouped report covers Hadoop HDFS Router-Based Federation state-store tests, record tests, contract fixtures, static-analysis suppressions, and JDiff API baselines. Each file section is delimited for the reconciliation lane and preserves the original source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/TestStateStoreMembershipState.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/TestStateStoreMembershipState.java

Purpose: `TestStateStoreMembershipState` is a JUnit 5 integration-style test for `MembershipStore`, the Router-Based Federation state-store facade that receives NameNode heartbeat records and exposes active and expired membership views. It extends `TestStateStoreBase`, uses the configured `StateStoreService`, and shortens membership expiration and deletion windows to two seconds through `RBFConfigKeys.FEDERATION_STORE_MEMBERSHIP_EXPIRATION_MS` and `FEDERATION_STORE_MEMBERSHIP_EXPIRATION_DELETION_MS` so expiry behavior can be tested quickly.

Important APIs and helpers: the test exercises `NamenodeHeartbeatRequest/Response`, `GetNamenodeRegistrationsRequest/Response`, `GetNamespaceInfoRequest/Response`, and `UpdateNamenodeRegistrationRequest`. Local helpers build `MembershipState` records with router, nameservice, namenode, cluster, block pool, RPC/service/lifeline/web endpoints, service state, and safemode state; `namenodeHeartbeat()` submits a registration; `getNamenodeRegistration()` and `getExpiredNamenodeRegistration()` query cached active and expired views using partial `MembershipState` keys. Shared fixture utilities include `clearRecords`, `synchronizeRecords`, `createMockRegistrationForNamenode`, and `verifyException`.

Control flow and state behavior: each test clears all `MembershipState` rows before running. The core happy path writes heartbeat records into the driver, explicitly reloads the `MembershipStore` cache with `getStateStore().loadCache(MembershipStore.class, true)`, and then checks quorum-selected results. The quorum tests intentionally insert multiple records for the same `(nameserviceId,namenodeId)` from different routers and validate that majority state wins, that equal `dateModified` values still produce an active representative when active has majority, that expired records are ignored for active quorum, and that all-expired groups are excluded from the active cache. When there is no majority, the newest record is selected, even if it reports standby.

Persistence and cache semantics: the file distinguishes persisted driver contents from store caches. Heartbeats update persistent records; cache refresh computes representative active membership and expired membership lists. `testRegistrationExpiredAndDeletion()` verifies a live record moves from active cache to expired view after the expiration interval, can be revived by a fresh heartbeat, and is removed from expired records after the deletion interval. `testRegistrationExpiredRaceCondition()` uses a Mockito spy and `GenericTestUtils.DelayAnswer` around `overrideExpiredRecords()` to create a cache-refresh race: an expired record is loaded, a fresh active heartbeat is written before refresh completes, and the stale refresh must not overwrite the active state in the driver.

Dependencies and integration points: the test depends on Hadoop RBF resolver types (`FederationNamenodeServiceState`, `FederationNamespaceInfo`), router config keys, the state-store protocol request/response layer, `Time`, JUnit assertions, Mockito, and `GenericTestUtils.waitFor`. It integrates with the global `StateStoreService` test fixture rather than mocking the driver, except for the delayed spy used to test a concurrency edge.

Risks and test signals: these tests are sensitive to wall-clock sleeps and short expiration windows; slow CI could make timeout-based assertions noisy. They strongly signal the intended membership contract: writer-side operations fail when the driver is unavailable, cached read/override paths can still be invoked in disconnected scenarios, namespace info excludes unavailable NameNodes with empty cluster/block-pool IDs, and stale expired-cache work must not corrupt newer persistent heartbeats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/TestStateStoreMembershipState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/TestStateStoreMountTable.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/TestStateStoreMountTable.java

Purpose: `TestStateStoreMountTable` validates the `MountTableStore` API used by RBF routers to persist and query federated mount-table entries. It extends `TestStateStoreBase`, builds a two-nameservice fixture from `FederationTestUtils.NAMESERVICES`, and clears all `MountTable` records before each test.

Important APIs and helpers: it exercises `AddMountTableEntryRequest/Response`, `UpdateMountTableEntryRequest/Response`, `RemoveMountTableEntryRequest`, `GetMountTableEntriesRequest/Response`, and `QueryResult<MountTable>`. Helper `getMountTableEntry()` queries one source path and returns the first sorted result; helper `getMountTableEntries()` requires a non-null root path and returns records plus the state-store response timestamp.

Control flow and state behavior: `testSynchronizeMountTable()` bulk synchronizes mock entries, reloads the mount-store cache, and confirms default destination preservation. `testAddMountTableEntry()` proves the empty store gains one visible entry after an add and cache reload. `testRemoveMountTableEntry()` bulk inserts, removes by `srcPath`, reloads, and checks the count decreases. `testUpdateMountTableEntry()` inserts an entry, verifies the original nameservice, replaces the same source path with a new destination map, and verifies the update is visible.

Persistence and cache semantics: write APIs operate against the state-store driver, while reads are cache-backed and require `mountStore.loadCache(true)` in the tests before assertions. The tests show mount-table records are keyed by source path and that updating a source path replaces destination metadata without adding an extra row.

Dependencies and integration points: the test uses `FederationStateStoreTestUtils.createMockMountTable()` and `synchronizeRecords()` for fixture construction, state-store protocol classes for API coverage, and `verifyException()` for disconnected-driver checks. It integrates with `StateStoreService` and the configured test driver through the base class.

Risks and test signals: disconnected-driver behavior expects add, update, remove, and even cached get after explicit cache load to throw `StateStoreUnavailableException`. The assertions are mostly count and default-destination checks; they do not deeply validate ordering beyond the helper comment that shortest mount string sorts first.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/TestStateStoreMountTable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/TestStateStoreRouterState.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/TestStateStoreRouterState.java

Purpose: `TestStateStoreRouterState` tests `RouterStore`, the state-store facade that records router heartbeats, exposes individual router registrations, and lists all router states. It reduces router expiration and deletion windows to two seconds via `RBFConfigKeys.FEDERATION_STORE_ROUTER_EXPIRATION_MS` and `FEDERATION_STORE_ROUTER_EXPIRATION_DELETION_MS`.

Important APIs and helpers: it uses `RouterHeartbeatRequest`, `GetRouterRegistrationRequest`, `GetRouterRegistrationsRequest`, `RouterState`, and `RouterServiceState`. The test verifies heartbeat-populated metadata, including router address, service status, build version, and `FederationUtil.getCompileInfo()`.

Control flow and state behavior: each test clears `RouterState` records. `testUpdateRouterStatus()` submits a `RUNNING` heartbeat and immediately reads the same router by address. `testRouterStateExpiredAndDeletion()` writes a running heartbeat, waits until subsequent reads report `EXPIRED`, sends another heartbeat to revive the record, waits for it to expire again, and then waits until deletion produces a record with null status. `testGetAllRouterStates()` writes two router heartbeats, reloads the cache, sorts returned records, and verifies both addresses and statuses.

Persistence and cache semantics: router heartbeats persist state-store records with last-modified timestamps that drive expiry. Reads use the router store and cache refresh where needed. The expiry test demonstrates a three-phase lifecycle: running, expired, and deleted/null-status after deletion grace.

Dependencies and integration points: the class depends on state-store protocol classes, router status/config types, `GenericTestUtils.waitFor`, and Hadoop time utilities. It uses the same state-store base fixture as the membership and mount-table tests, so it is a cross-driver behavior test when run with different state-store configurations.

Risks and test signals: the test is timing-sensitive because it polls for two-second expiry/deletion windows with three-second timeouts. It signals that heartbeat refresh must restore an expired router to running, and that disconnected-driver behavior must raise `StateStoreUnavailableException` for single get, list get, and heartbeat writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/TestStateStoreRouterState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/driver/TestStateStoreDriverBase.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/driver/TestStateStoreDriverBase.java

Purpose: `TestStateStoreDriverBase` is the reusable conformance suite for state-store driver implementations. Concrete driver tests call its methods to verify basic CRUD behavior, duplicate/update rules, fetch miss behavior, metrics accounting, and cache-load metrics across `MembershipState`, `MountTable`, `RouterState`, and `DisabledNameservice` records.

Important APIs and helpers: the class owns static `StateStoreService` and `Configuration` fixtures, initializes them through `FederationStateStoreTestUtils.newStateStore(conf)`, and exposes `getStateStoreDriver()` and `getStateStoreService()`. It generates fake records for supported record classes, including nested `StateStoreVersion` for `RouterState`. Reflection helpers locate getters/setters, inspect serializable fields, convert primary-key strings to typed values, and validate committed records while ignoring generated fields such as `dateCreated`, `dateModified`, and `proto`.

Control flow: `testInsert()` removes all records of a class, validates an empty read, writes one record, verifies field equality and timestamps, then bulk inserts ten more. `testPut()` inserts ten records with `putAll(..., allowUpdate=false, errorIfExists=true)`, asserts duplicate failures report failed primary keys, attempts a same-primary-key update while updates are disallowed, and finally allows an update and checks the original set changed when the record type has non-primary fields. `testRemove()` removes one record directly, removes two by `Query<T>`, and then removes all. `testFetchErrors()` verifies empty fetches and nonmatching queries return empty/null rather than false positives.

State and persistence behavior: the base class tests state-store driver persistence in terms of `BaseRecord` primary keys and typed query matching. It expects drivers to stamp creation and modification times on commit and to avoid updating modification time for expired records. `removeAll()` explicitly clears the main RBF record families used by tests.

Metrics behavior: `testMetrics()` checks `StateStoreMetrics` counters for write, read, failure, and remove operations over single, multiple, and query-based driver calls. `testCacheLoadMetrics()` and `getMountTableCacheLoadSamples()` assert the `CacheMountTableLoad` mutable rate exists and receives samples after refreshes.

Dependencies and integration points: concrete tests for file, filesystem, MySQL, and ZooKeeper drivers use this base. It depends on `StateStoreDriver`, `StateStoreOperationResult`, `Query`, `QueryResult`, `StateStoreMetrics`, Hadoop federation record classes, and JUnit lifecycle hooks. Because it uses reflection over record getters and setters, changes to record accessor naming or primary-key field types can affect many driver tests at once.

Risks and test signals: random record generation can expose serialization/key bugs across driver implementations but may make failures harder to reproduce without logged values. The duplicate-key checks are strong signals for `putAll` contract semantics: failed duplicate inserts must return failed record keys, not silently update. Metrics assertions make it risky to add extra hidden driver operations inside public driver methods without updating expected counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/driver/TestStateStoreDriverBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/driver/TestStateStoreFile.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/driver/TestStateStoreFile.java

Purpose: `TestStateStoreFile` applies the driver conformance suite to `StateStoreFileImpl`, the local file-backed state-store implementation. It parameterizes every test over `FEDERATION_STORE_FILE_ASYNC_THREADS` values of `20` and `0` to cover asynchronous and synchronous file-writing modes.

Important APIs and helpers: `setupCluster()` obtains a file-driver state-store configuration with `FederationStateStoreTestUtils.getStateStoreConfiguration(StateStoreFileImpl.class)`, sets the async-thread count, and initializes the base `StateStoreService`. `initTestStateStoreFile()` captures the parameter, calls setup, and clears all persisted test records.

Control flow and persistence behavior: each parameterized test initializes a fresh file-backed state store, delegates to a base conformance method (`testInsert`, `testPut`, `testRemove`, `testFetchErrors`, or `testMetrics`), and tears down the state-store service after the test. `testCacheLoadMetrics()` seeds `CacheMountTableLoad` with `-1`, captures the current sample count, refreshes caches once, and expects one additional nonnegative cache-load sample.

Dependencies and integration points: the class depends on JUnit 5 parameterized tests and method sources, `StateStoreFileImpl`, and the shared driver base. It is the main bridge between generic driver semantics and the local filesystem implementation.

Risks and test signals: running the same contract with zero async threads and twenty async threads signals that the file driver must preserve identical CRUD, duplicate-key, metrics, and cache-load semantics regardless of execution mode. Any async timing behavior that changes visible write completion or metric accounting is likely to fail here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/driver/TestStateStoreFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/driver/TestStateStoreFileBase.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/driver/TestStateStoreFileBase.java

Purpose: `TestStateStoreFileBase` is a focused unit test for `StateStoreFileBaseImpl.isOldTempRecord()`, the helper that identifies stale temporary record files in file-backed state-store implementations.

Important APIs and control flow: `testTempOld()` checks that ordinary file names and nested paths are not treated as old temporary records, constructs a `.tmp` filename using the current `Time.now()` timestamp and expects it to be fresh, then constructs another `.tmp` filename one minute in the past and expects it to be old.

State and persistence behavior: the test does not touch the state-store driver directly. It protects cleanup logic used by file-backed persistence so that only timestamped temp records older than the cleanup threshold are eligible for removal.

Dependencies and integration points: it depends on `StateStoreFileBaseImpl.isOldTempRecord`, `Time`, `TimeUnit`, and JUnit assertions. It is an integration signal for any future changes to temp-file naming conventions.

Risks and test signals: the test encodes a one-minute-old threshold expectation without explicitly naming the production constant. It signals that cleanup must avoid deleting arbitrary files and fresh temp records, while detecting stale temp artifacts generated by interrupted writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/driver/TestStateStoreFileBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/driver/TestStateStoreFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/driver/TestStateStoreFileSystem.java

Purpose: `TestStateStoreFileSystem` applies the shared driver conformance suite to `StateStoreFileSystemImpl`, the FileSystem-backed state-store implementation, using a real `MiniDFSCluster` as the backing filesystem.

Important APIs and helpers: `setupCluster()` builds a `Configuration` for `StateStoreFileSystemImpl`, sets `StateStoreFileSystemImpl.FEDERATION_STORE_FS_PATH` to `/hdfs-federation/`, sets `FEDERATION_STORE_FS_ASYNC_THREADS` to the parameter value, starts a one-datanode `MiniDFSCluster`, waits for it to become available, and initializes the base state store. Tests are parameterized over async-thread values `20` and `0`.

Control flow and persistence behavior: the normal insert, update, delete, fetch-error, and metrics tests delegate to `TestStateStoreDriverBase` after removing all existing records. `testInsertWithErrorDuringWrite()` wraps the driver with a Mockito spy, intercepts `getWriter()`, returns a spy `BufferedWriter`, forces `write(String)` to throw `IOException`, and then verifies through the base helper that no `MembershipState` record was inserted after the failed write. `testCacheLoadMetrics()` expects two refreshes to add two cache-load samples.

Dependencies and integration points: this test integrates HDFS `MiniDFSCluster`, `StateStoreFileBaseImpl`, `StateStoreFileSystemImpl`, Mockito stubbing, and the shared RBF driver base. It exercises real filesystem semantics such as directory creation, writer failure, and cleanup through the state-store driver abstraction.

Risks and test signals: the MiniDFSCluster dependency makes the test heavier than the local file test. It strongly signals atomicity expectations for file-backed writes: if serialization or write fails, no partial logical record should be visible. The parameterization requires synchronous and asynchronous filesystem modes to behave identically from the driver API perspective.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/driver/TestStateStoreFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/driver/TestStateStoreMySQL.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/driver/TestStateStoreMySQL.java

Purpose: `TestStateStoreMySQL` runs the generic state-store driver conformance tests against `StateStoreMySQLImpl`. Although the implementation under test is the MySQL driver, the test uses an in-memory Apache Derby database through JDBC to provide an SQL backend during unit tests.

Important APIs and setup: `initDatabase()` opens `jdbc:derby:memory:StateStore;create=true`, creates schema `TESTUSER`, builds a `StateStoreMySQLImpl` configuration, sets connection URL, username, password, and JDBC driver class `org.apache.derby.jdbc.EmbeddedDriver`, and initializes the shared state-store service. `startup()` clears existing records before each test; `cleanupDatabase()` drops the in-memory Derby database and treats the expected Derby drop exception as success.

Control flow and persistence behavior: the test delegates insert, update/duplicate semantics, delete, fetch-error, and metrics validation to `TestStateStoreDriverBase`. Because the backend is SQL, these tests cover schema/table persistence behavior through the MySQL driver code path while avoiding an external MySQL service.

Dependencies and integration points: the file depends on JDBC (`Connection`, `DriverManager`, `Statement`), Hadoop test utilities for state-store configuration, `StateStoreMySQLImpl`, and JUnit lifecycle annotations. It is the SQL-driver integration point for the same `BaseRecord` families used by other driver tests.

Risks and test signals: Derby compatibility is not identical to MySQL, so this test is strongest for generic SQL driver semantics and weaker for MySQL-specific dialect or deployment issues. It signals that the SQL driver must honor primary-key duplicate behavior, typed serialization, timestamp stamping, remove semantics, and metric accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/driver/TestStateStoreMySQL.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/driver/TestStateStoreZK.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/driver/TestStateStoreZK.java

Purpose: `TestStateStoreZK` validates `StateStoreZooKeeperImpl` against the shared state-store driver contract and adds ZooKeeper-specific tests for null znode cleanup and asynchronous operation performance.

Important APIs and setup: `setupCluster()` starts a Curator `TestingServer`, creates a `CuratorFramework` client with `RetryNTimes`, configures `RBFConfigKeys.FEDERATION_STORE_ZK_ADDRESS`, disables frequent connection auto-repair by setting `FEDERATION_STORE_CONNECTION_TEST_MS` to one hour, sets `FEDERATION_STORE_ZK_ASYNC_MAX_THREADS` to ten, captures the configured parent znode, and initializes the base state store. Each test removes all records and sets concurrent mode off before starting.

Control flow and ZooKeeper behavior: `generateFakeZNode()` maps a record class to the expected state-store znode path under the base znode and a fake primary key. `testGetNullRecord()` manually creates persistent znodes with null data for each record family, calls `driver.get(recordClass)`, and asserts the driver deletes those invalid znodes; it repeats the check in concurrent mode. CRUD and fetch-error tests run once in synchronous mode and once after `setEnableConcurrent(true)`.

Performance and persistence behavior: `testAsyncPerformance()` creates 1000 `MountTable` records, measures synchronous `putAll`, measures synchronous removal of five entries, clears the rest, then enables concurrent mode and asserts async `putAll` and async `removeMultiple` are faster than the synchronous equivalents. `testCacheLoadMetrics()` expects three explicit cache refreshes to add three mount-table cache-load samples.

Dependencies and integration points: the class integrates Curator test server/client, ZooKeeper `CreateMode`, `StateStoreUtils.getRecordName`, ZooKeeper driver configuration, RBF record classes, and the shared driver base. It is the concrete contract test for both sequential and concurrent ZooKeeper driver paths.

Risks and test signals: wall-clock performance comparisons can be environment-sensitive, especially under loaded CI. The null-record cleanup test is a strong compatibility signal: the driver must tolerate and remove malformed znodes rather than returning null data as records or failing future reads. The repeated synchronous/concurrent contract checks signal that concurrency is an internal optimization, not an API behavior change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/driver/TestStateStoreZK.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/records/MockStateStoreDriver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/records/MockStateStoreDriver.java

Purpose: `MockStateStoreDriver` is an in-memory test implementation of `StateStoreBaseImpl` that can deliberately throw `IOException` on driver operations. It is used to test state-store and resolver resilience without external persistence.

Important APIs and data structures: it tracks readiness with `initialized`, exposes `setGiveErrors(boolean)` to enable induced failures, and stores records in a static `VALUE_MAP` keyed first by `StateStoreUtils.getRecordName(recordClass)` and then by `BaseRecord.getPrimaryKey()`. Implemented operations include `initDriver()`, `initRecordStorage()`, `isDriverReady()`, `close()`, `get(Class<T>)`, `putAll(List<T>, allowUpdate, errorIfExists)`, `clearAll()`, `removeAll(Class<T>)`, and query-based `remove(Class<T>, Query<T>)`.

Control flow and persistence behavior: every read/write/remove operation calls `checkErrors()` first. `get()` returns a snapshot list of values for the requested record family and a current timestamp. `putAll()` creates the record-family map if needed, overwrites only when the old record is absent or `allowUpdate` is true, and throws an `IOException` on duplicate records when `errorIfExists` is true. `remove()` iterates through values and removes records whose query matches.

Dependencies and integration points: the driver relies on `StateStoreBaseImpl` for base driver behavior and `StateStoreOperationResult` for bulk write results. It is integrated by `TestRouterState.testStateStoreResilience()` through `RBFConfigKeys.FEDERATION_STORE_DRIVER_CLASS`, where induced read errors validate that cache refresh failure does not discard the previous resolver cache.

Risks and test signals: because `VALUE_MAP` is static, tests must call `clearAll()` or `close()` to avoid cross-test contamination. The implementation returns a successful `StateStoreOperationResult` after successful `putAll`, but duplicate-with-error throws rather than returning failed keys, so it is a simple failure injector rather than a full conformance implementation. It signals cache-failure behavior more than production persistence fidelity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/records/MockStateStoreDriver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/records/TestMembershipState.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/records/TestMembershipState.java

Purpose: `TestMembershipState` validates the `MembershipState` record model and its nested `MembershipStats` serialization. It ensures NameNode membership metadata and storage/health statistics survive getters, setters, and state-store serializer round trips.

Important fields and APIs: the fixture includes router, nameservice, namenode, cluster ID, block pool ID, RPC/service/lifeline/web addresses, web scheme, safemode flag, service state, created/modified timestamps, and many stats counters: blocks, files, active/dead/stale/decommissioning datanodes, maintenance datanodes, missing blocks, total and available space, corrupt files, scheduled replication blocks, missing replication-factor-one blocks, and highest-priority low-redundancy replicated and EC blocks.

Control flow and state behavior: `createRecord()` constructs a `MembershipState` through `newInstance()`, manually sets dates, creates a `MembershipStats` instance, populates every tested stat, and attaches it to the record. `validateRecord()` asserts all scalar membership fields and all nested stat fields. `testGetterSetter()` validates the constructed object directly; `testSerialization()` serializes to a string through `StateStoreSerializer.getSerializer()` and deserializes back to `MembershipState` before validation.

Dependencies and integration points: this file depends on federation service-state enums and the state-store serializer abstraction. It is a record-level complement to the store-level membership tests: the store tests validate lifecycle/quorum, while this file validates that the record payload itself is complete and serializable.

Risks and test signals: the validation omits an explicit assertion for `namenodeId`, even though the fixture sets one, so a regression in that accessor would not be caught here. The test is otherwise a strong signal that new stats fields must be added to serialization and validation if they become part of the membership record contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/records/TestMembershipState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/records/TestMountTable.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/records/TestMountTable.java

Purpose: `TestMountTable` validates the `MountTable` record model used by RBF to map a source path to one or more remote namespace destinations, plus routing order, readonly state, fault-tolerance state, quotas, dates, validation, and serialization.

Important fields and APIs: the fixture uses source `/test`, two destinations (`ns0 -> /path1`, `ns1 -> /path/path2`), linked-map destination ordering, explicit created/modified dates, `DestinationOrder` values, and a `RouterQuotaUsage` object with namespace and storage-space counts/quotas. It checks `MountTable.newInstance()` overloads, `getDestinations()`, `getDefaultLocation()`, `setReadOnly()`, `setFaultTolerant()`, `setDestOrder()`, `setQuota()`, and `StateStoreSerializer`.

Control flow and state behavior: `testGetterSetter()` validates default fields, default quota reset values from `HdfsConstants.QUOTA_RESET`, default `DestinationOrder.HASH`, and explicit dates. `testSerialization()` repeats serialization checks for `RANDOM`, `HASH`, and `LOCAL` orders while preserving readonly and quota state. `testReadOnly()`, `testFaultTolerant()`, `testOrder()`, and `testQuota()` isolate each feature flag or field group.

Validation behavior: `testValidation()` asserts invalid source paths without a leading slash, destination paths without a leading slash, and empty destination namespace IDs throw exceptions containing the specific `MountTable` validation messages. A valid destination map then creates a non-null record.

Dependencies and integration points: the test integrates `RemoteLocation`, `DestinationOrder`, `RouterQuotaUsage`, `HdfsConstants`, `GenericTestUtils`, and the state-store serializer. It gives store-level tests a record contract for comparing mount-table destinations and replacement behavior.

Risks and test signals: ordered `RemoteLocation` comparison relies on linked insertion order in the fixture. The equality check in `testFaultTolerant()` signals that fault-tolerant state participates in record equality. The validation checks make source and destination path normalization strict rather than forgiving.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/records/TestMountTable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/records/TestRouterState.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/records/TestRouterState.java

Purpose: `TestRouterState` validates the `RouterState` record model, serializer round trips, and state-store cache resilience when driver refreshes fail. It bridges record-level serialization with an in-memory mock driver and `MembershipNamenodeResolver`.

Important fields and APIs: `generateRecord()` creates a `RouterState` with address, start time, `RouterServiceState.RUNNING`, version, compile info, created/modified dates, and nested `StateStoreVersion` containing a mount-table version. `validateRecord()` checks address, start time, status, compile info, version, and nested mount-table version. Serialization uses `StateStoreSerializer`.

Control flow and resilience behavior: `testGetterSetter()` and `testSerialization()` validate the record directly and after serializer round trip. `testStateStoreResilience()` creates a `StateStoreService` configured with `MockStateStoreDriver`, disables router metrics, inserts two `MembershipState` records for the same block pool with active and standby NameNodes, loads the driver, constructs a `MembershipNamenodeResolver`, refreshes caches, and verifies two NameNodes are resolved for the block pool. It then enables induced driver I/O errors, refreshes caches again, verifies the service cache update time did not advance, and confirms the resolver still returns the prior two cached NameNodes.

Dependencies and integration points: the file depends on RBF config keys, `StateStoreService`, `StateStoreDriver`, `MockStateStoreDriver`, `MembershipState`, `MembershipNamenodeResolver`, federation resolver context interfaces, and router/name-node service enums. It is the main local test proving cache refresh failure should preserve previously valid cache state.

Risks and test signals: the resilience test creates and stops a real `StateStoreService` manually and must clean up to avoid leaking state. It signals a key operational requirement: transient state-store read failures must not erase router resolver knowledge or advance cache timestamps as if refresh succeeded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/records/TestRouterState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/resources/contract/hdfs.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/resources/contract/hdfs.xml

Purpose: `hdfs.xml` is a Hadoop filesystem contract-test configuration for HDFS behavior in the RBF test resources. It declares which filesystem capabilities should be assumed by contract tests.

Important properties: it enables root tests (`fs.contract.test.root-tests-enabled=true`), sets a high file random seek count (`fs.file.contract.test.random-seek-count=500`), and declares HDFS as case-sensitive. It marks support for append, atomic directory delete, atomic rename, block locality, concat, seek, strict exceptions, Unix permissions, settimes, getfilestatus, file references, content checks, `hflush`, and `hsync`. It also records that seek past EOF is rejected, rename returns false when the destination exists or source is missing, and metadata is not updated on `hsync`.

Control flow and integration behavior: this is declarative XML consumed by Hadoop contract test infrastructure, not executable Java. Test suites load these properties to decide which contract cases should run and what behavior to assert for HDFS-backed filesystems.

State and persistence behavior: the file does not create state itself, but it defines persistence and filesystem guarantees expected by tests: append/sync semantics, metadata update expectations, atomicity of rename/delete, and content verification support.

Risks and test signals: incorrect capability flags can produce false positives or false negatives in filesystem contract tests. The file signals that HDFS should be treated as a fully featured, strict filesystem for most contract operations, except metadata update on `hsync` is explicitly false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/resources/contract/hdfs.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/resources/contract/webhdfs.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/resources/contract/webhdfs.xml

Purpose: `webhdfs.xml` is the WebHDFS-specific filesystem contract-test overlay. It narrows expectations for behavior exposed through the WebHDFS protocol compared with direct HDFS.

Important properties: it sets `fs.contract.supports-strict-exceptions=false`, `fs.contract.create-visibility-delayed=true`, `fs.contract.supports-hflush=false`, `fs.contract.supports-hsync=false`, and `fs.contract.metadata_updated_on_hsync=false`.

Control flow and integration behavior: the file is loaded by contract test infrastructure for WebHDFS-backed filesystems. Its properties guide which tests are skipped or how assertions are interpreted for delayed visibility and unsupported sync operations.

State and persistence behavior: it describes externally visible persistence semantics through WebHDFS: newly created content may not be immediately visible, and hflush/hsync are not supported through this contract path.

Risks and test signals: the key signal is that WebHDFS should not be held to direct-HDFS strict exception or sync guarantees. If WebHDFS behavior changes to support hflush/hsync or immediate create visibility, this fixture would need updating to avoid stale test expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/resources/contract/webhdfs.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/resources/hdfs-site.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/resources/hdfs-site.xml

Purpose: this RBF test `hdfs-site.xml` provides a minimal HDFS site override for tests. It exists to make tiny test block sizes legal.

Important property: it sets `dfs.namenode.fs-limits.min-block-size` to `0`, disabling the normal minimum block-size guard because many tests create tiny blocks.

Control flow and integration behavior: Hadoop test clusters and filesystem tests pick this resource up as part of test configuration. It affects NameNode validation during file creation and block allocation.

State and persistence behavior: the configuration does not persist application data, but it changes NameNode policy so test files with very small blocks can be created instead of rejected.

Risks and test signals: this is test-only behavior and should not be confused with production defaults. If tests unexpectedly use production-like min block sizes, many small-block fixtures could fail at file creation time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/resources/hdfs-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/findbugsExcludeFile.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/findbugsExcludeFile.xml

Purpose: `findbugsExcludeFile.xml` is an HDFS module FindBugs/SpotBugs exclusion filter. It suppresses known or intentionally accepted static-analysis findings across generated code, protocol classes, HDFS internals, and legacy behaviors.

Important structures and rules: the root `FindBugsFilter` contains many `Match` elements targeting packages, classes, methods, fields, bug patterns, bug codes, and categories. Broad suppressions include generated record/protobuf packages, representation exposure (`EI_EXPOSE_REP`, `EI_EXPOSE_REP2`), serializer warnings (`SE_COMPARATOR_SHOULD_BE_SERIALIZABLE`, `SE_BAD_FIELD`), JSP dead stores/unwritten fields, cross-site scripting and HTTP response splitting codes, and mutable-static (`MS`) warnings under Hadoop packages.

Control flow and dependency behavior: this XML is consumed by static-analysis tooling during HDFS builds. It does not execute at runtime, but it directly controls build quality gates by deciding which analyzer findings are ignored.

State and concurrency rationale: many suppressions document intentional synchronization or lifecycle choices, such as `Client.Connection.out` closing behavior, `FSImage.lastAppliedTxId`, `FSEditLog` fields used by metrics or protected by separate locks, volatile transaction ID increment assumptions, and `DirectoryScanner.reconcile` sleeping while locked. Other suppressions explain stream ownership for datanode file wrappers and `FsDatasetImpl.getTmpInputStreams`.

Integration points and risk: the file touches broad HDFS areas: datanode storage, NameNode image/edit log, qjournal, cache replication monitor, block reader local info, startup option enum setters, JMX tooling, and async logging. The primary risk is that suppressions can hide new real bugs when class/method names remain matched but implementation intent changes. The comments are important evidence for why each warning is accepted and should be revisited when the corresponding code is refactored.

Test and build signals: this file is a build-signal artifact rather than a unit test. Any removal or tightening of entries may surface static-analysis failures; any broadening may reduce the effectiveness of the static-analysis gate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_2.10.0.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_2.10.0.xml

Purpose: `Apache_Hadoop_HDFS_2.10.0.xml` is a JDiff API baseline generated from Hadoop HDFS 2.10.0 public annotated APIs. It is used by API-difference tooling to compare HDFS public surface across releases.

Important structures: the root `api` element names `Apache Hadoop HDFS 2.10.0`, declares JDiff version `1.0.9`, references `api.xsd`, and includes a generated command-line comment showing doclet, classpath, source path, and dependency versions from the 2019 build environment. The file enumerates HDFS packages and selected public types.

API content: it includes the package documentation for `org.apache.hadoop.hdfs`, describing HDFS as a distributed `FileSystem` modeled loosely after GFS with a strict single-writer append stream model. It lists many packages such as `org.apache.hadoop.hdfs.protocol`, qjournal, datanode, namenode, tools, util, and web resources. Detailed public API entries shown include `JournalNodeMXBean.getJournalsStatus()`, the `AuditLogger` interface and its `initialize()`/`logAuditEvent()` methods, `HdfsAuditLogger` overloads, and `INodeAttributeProvider` methods for startup, shutdown, attribute lookup, and external access-control enforcer customization.

Control flow and integration behavior: this XML is not runtime code. It is an input to JDiff/reporting tasks that parse packages, classes, interfaces, methods, params, docs, visibility, abstract/static/final flags, and deprecation state to detect incompatible public API changes.

Dependencies and persistence behavior: the generated command line captures a Java 7-era build, Hadoop 2.10.0 artifacts, ZooKeeper 3.4.9, Curator 2.7.1, Guava 11.0.2, Jackson 2.7.x/1.9.x components, and other dependencies. These details document the build context for the baseline but are not API entries themselves.

Risks and test signals: hand-editing this file can corrupt API compatibility checks. The main signal is a stable public HDFS baseline for 2.10.0; changes to downstream JDiff comparisons should be interpreted as API drift from this baseline, not as executable test behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_2.10.0.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_2.10.2.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_2.10.2.xml

Purpose: `Apache_Hadoop_HDFS_2.10.2.xml` is the JDiff API baseline for Hadoop HDFS 2.10.2. It mirrors the 2.10.0 baseline structure while recording a newer generated date, release name, build paths, and dependency set.

Important structures: the root `api` element names `Apache Hadoop HDFS 2.10.2`, uses JDiff version `1.0.9`, references `api.xsd`, and contains a generated command-line comment from a 2022 build environment. The package/type/method content visible in the file is structurally the same as the 2.10.0 baseline in this subset.

API content: it preserves the `org.apache.hadoop.hdfs` package documentation about the distributed filesystem and single-writer ordered byte-stream model. It lists the same HDFS package families and includes public entries for `JournalNodeMXBean`, `AuditLogger`, `HdfsAuditLogger`, and `INodeAttributeProvider`, with method signatures, parameter types, visibility, and documentation blocks used by API comparison tooling.

Control flow and integration behavior: like the 2.10.0 file, this is a generated static API description consumed by JDiff/report tasks. It does not run in tests, but it anchors release-to-release compatibility analysis for the HDFS module.

Dependencies and version context: the command-line comment records updated build dependencies relative to 2.10.0, including newer SLF4J, HTTP components, Nimbus JOSE JWT, ZooKeeper 3.4.14, Curator 2.13.0, commons-compress, Woodstox, Netty, Jackson databind 2.9.10.7, reload4j bindings, SpotBugs annotations, and Yetus audience annotations. These are build-context differences rather than direct API entries.

Risks and test signals: the file should remain generated and source-controlled as a release baseline. The visible diff from 2.10.0 is mostly metadata and build classpath information, while the represented public API in this subset remains stable; that is the key compatibility signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_2.10.2.xml -->
