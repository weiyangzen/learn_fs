# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/driver/impl/StateStoreMySQLImpl.java

Purpose: SQL-backed `StateStoreDriver` that stores selected federation record types in MySQL tables, one table per record class with `recordKey` and serialized `recordValue` columns.

Important APIs/types/functions: configuration prefix `state-store-mysql.*`; valid tables are `MembershipState`, `RouterState`, `MountTable`, and `DisabledNameservice`. Key methods are `initDriver`, `initRecordStorage`, `get`, `putAll`, `remove`, `removeAll`, helpers `insertRecord`, `updateRecord`, `recordExists`, `removeRecord`, and inner `MySQLStateStoreHikariDataSourceConnectionFactory`.

Control flow: initialization creates a Hikari-backed `SQLConnectionFactory`. Record storage checks metadata for the expected table and creates it if absent. `get` selects all rows from a validated table and deserializes `recordValue`. `putAll` processes each record independently: validate table, escape primary key, serialize, check existence, then insert or update according to `allowUpdate`/`errorIfExists`. Removes fetch existing records, filter through `Query`, and delete matching keys; `removeAll` truncates the table.

State/persistence behavior: state is durable in MySQL, with serialized values capped by the table schema's `VARCHAR(2047)`. Keys are escaped by `StateStoreSerializableImpl`. Metrics track successful and failed operations, and updates set record modification time before serialization.

Dependencies/integration: depends on HikariCP, JDBC, Hadoop `DFSUtil.getPassword`, federation SQL connection factory used by router token code, and state-store serializer configuration.

Risks: SQL table names are string-formatted but restricted to a hard-coded allowlist; the `recordValue` size limit can reject or truncate larger serialized records depending on database behavior; put operations are not batched or transactional across records; existence-check then insert/update is race-prone; metadata table lookup may be case-sensitive by MySQL settings.

Test signals: tests should cover table creation, credential loading, Hikari property passthrough, duplicate insert/update semantics, failed key reporting, oversized serialized records, concurrent puts to the same key, remove filtering, and driver readiness after shutdown.
