# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/driver/impl/StateStoreZooKeeperImpl.java

Purpose: ZooKeeper-backed `StateStoreDriver` for federation state records. It stores each record type under a parent znode and each primary key as a child znode containing serialized record data.

Important APIs/types/functions: uses `ZKCuratorManager`, Curator framework state, ACLs, and optional thread-pool concurrency. Driver methods include `initDriver`, `initRecordStorage`, `get`, `putAll`, `remove(List<Query<T>>)` plus single-query overload, `removeAll`, `writeNode`, and `createRecord`.

Control flow: initialization reads the parent znode, async thread count, and ZooKeeper address, starts Curator, and loads ACLs. Per-record storage creates the class znode recursively. Reads list children and fetch records serially or concurrently; corrupt empty/unparseable znodes are deleted. Writes create each child znode if needed, reject existing nodes when updates are disallowed and `error` is true, then set data. Removes read current records, map each query to matching records, delete unique znodes, and report per-query counts.

State/persistence behavior: durable state is ZooKeeper znode data under `baseZNode/<recordName>/<escapedPrimaryKey>`. `createRecord` copies ZooKeeper ctime/mtime into record dates. Metrics track read/write/remove/failure durations.

Dependencies/integration: integrates Router federation with Hadoop's `ZKCuratorManager`, `RBFConfigKeys` ZooKeeper settings, state-store serializer, `StateStoreUtils.filterMultiple`, and `StateStoreOperationResult` failure-key reporting.

Risks: `remove(clazz, query)` calls `.get(query)` on the returned map and may unbox null when no records match; create-then-set is not an atomic compare-and-set update; corrupt data deletion is automatic and irreversible; async reads call `future.get()` twice for non-null results; connection/session behavior is delegated to Curator configuration.

Test signals: tests should cover sync and async modes, ACL path creation, corrupt znode cleanup, duplicate insert semantics, per-query remove counts including no-match queries, stat-derived dates, shutdown, and metrics on ZooKeeper failures.
