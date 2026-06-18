# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/SysPropsForTestsLoader.java

Purpose: Static test-property loader for HTTPFS tests.

Important APIs/types/functions: constant `TEST_PROPERTIES_PROP`, static initializer, and no-op `init` used to trigger class loading.

Control flow: on class load it resolves the requested `test.properties` file name, searches upward from the current path for the file, loads properties if found, and sets only missing JVM system properties. If the user explicitly set `test.properties` but the file is absent, it prints an error and exits with `System.exit(-1)`. Otherwise it logs that no file exists.

State and persistence: mutates JVM system properties and reads a local properties file. No write operations.

Dependencies/integration: Java `Properties`, file traversal, and helper classes that call `init` in static blocks.

Risks and test signals: centralizes test configuration but has process-global side effects and can terminate the JVM during class loading. Search logic is somewhat complex and path-dependent.
