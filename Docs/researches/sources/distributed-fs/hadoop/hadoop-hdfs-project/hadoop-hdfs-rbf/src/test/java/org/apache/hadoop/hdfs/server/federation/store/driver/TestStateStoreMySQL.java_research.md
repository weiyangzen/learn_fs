# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/driver/TestStateStoreMySQL.java

Purpose: `TestStateStoreMySQL` runs the generic state-store driver conformance tests against `StateStoreMySQLImpl`. Although the implementation under test is the MySQL driver, the test uses an in-memory Apache Derby database through JDBC to provide an SQL backend during unit tests.

Important APIs and setup: `initDatabase()` opens `jdbc:derby:memory:StateStore;create=true`, creates schema `TESTUSER`, builds a `StateStoreMySQLImpl` configuration, sets connection URL, username, password, and JDBC driver class `org.apache.derby.jdbc.EmbeddedDriver`, and initializes the shared state-store service. `startup()` clears existing records before each test; `cleanupDatabase()` drops the in-memory Derby database and treats the expected Derby drop exception as success.

Control flow and persistence behavior: the test delegates insert, update/duplicate semantics, delete, fetch-error, and metrics validation to `TestStateStoreDriverBase`. Because the backend is SQL, these tests cover schema/table persistence behavior through the MySQL driver code path while avoiding an external MySQL service.

Dependencies and integration points: the file depends on JDBC (`Connection`, `DriverManager`, `Statement`), Hadoop test utilities for state-store configuration, `StateStoreMySQLImpl`, and JUnit lifecycle annotations. It is the SQL-driver integration point for the same `BaseRecord` families used by other driver tests.

Risks and test signals: Derby compatibility is not identical to MySQL, so this test is strongest for generic SQL driver semantics and weaker for MySQL-specific dialect or deployment issues. It signals that the SQL driver must honor primary-key duplicate behavior, typed serialization, timestamp stamping, remove semantics, and metric accounting.
