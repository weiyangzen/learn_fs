# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestDirHelper.java

Purpose: JUnit 5 extension that creates and exposes isolated local test directories for methods annotated with `@TestDir`.

Important APIs/types/functions: constants `TEST_DIR_PROP` and `TEST_DIR_ROOT`, static `delete`, `getTestDir`, `resetTestCaseDir`, `beforeEach`, and `afterEach`.

Control flow: static initialization loads properties, validates `test.dir` is absolute and at least four characters, appends `test-dir`, deletes/recreates the root, and stores the resolved property. Before each annotated test it creates a unique directory named from the method and an atomic counter, deletes any prior content, creates the directory, and stores it in an inheritable thread-local. After each test it clears the thread-local.

State and persistence: deletes and creates directories under the configured test root; maintains static counter and thread-local directory reference.

Dependencies/integration: JUnit extension callbacks, Java reflection, and `SysPropsForTestsLoader`.

Risks and test signals: critical infrastructure with destructive delete behavior guarded by minimum path length. It exits the JVM on invalid root configuration and can remove preexisting content under `test.dir/test-dir`.
