# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestDir.java

Purpose: Marker annotation for tests that need an isolated local test directory.

Important APIs/types/functions: annotation `@TestDir` with runtime retention and method target.

Control flow: no executable logic. `TestDirHelper` inspects this annotation before each test and prepares a method-specific directory only when present.

State and persistence: annotation metadata only.

Dependencies/integration: Java annotation model and `HTestCase`/`TestDirHelper`.

Risks and test signals: simple infrastructure contract. Missing the annotation causes `TestDirHelper.getTestDir()` to throw, which is intentionally tested elsewhere.
