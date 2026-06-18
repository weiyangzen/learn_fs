# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/HFSTestCase.java

Purpose: Base class for tests needing the HTTPFS/HDFS test harness.

Important APIs/types/functions: class `HFSTestCase` extends `HTestCase` and registers `TestHdfsHelper` as a JUnit 5 extension through `@RegisterExtension`.

Control flow: no methods beyond extension registration. Subclasses inherit directory, Jetty, exception, and HDFS helpers.

State and persistence: `TestHdfsHelper` manages MiniDFS state when tests use `@TestHdfs`; this class itself holds an extension instance.

Dependencies/integration: JUnit 5 extension model, `HTestCase`, and `TestHdfsHelper`.

Risks and test signals: foundational test infrastructure. Its behavior is mostly covered indirectly by subclasses and directly by `TestHFSTestCase`.
