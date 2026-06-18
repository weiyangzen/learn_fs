# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/server/TestServerConstructor.java

Purpose: Parameterized validation of `Server` constructor argument checks.

Important APIs/types/functions: `constructorFailParams`, `initTestServerConstructor`, and parameterized `constructorFail`.

Control flow: each row supplies invalid combinations of name, home/config/log/temp directories, and configuration. The test stores them in instance fields and asserts `new Server(...)` throws `IllegalArgumentException`.

State and persistence: no filesystem creation; only parameter fields.

Dependencies/integration: JUnit 5 parameterized tests and Hadoop `Configuration`.

Risks and test signals: compact signal that constructor validation rejects null/empty/non-absolute or incomplete values. It does not include positive constructor cases, which are covered in `TestServer`.
