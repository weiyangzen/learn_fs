# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/servlet/TestServerWebApp.java

Purpose: Unit tests for `ServerWebApp` system-property directory resolution, lifecycle, failed init handling, and HTTP authority resolution.

Important APIs/types/functions: tests `getHomeDirNotDef`, `getHomeDir`, `lifecycle`, `failedInit`, and `testResolveAuthority`; `ServerWebApp.getHomeDir`, `getDir`, `contextInitialized`, `contextDestroyed`, and `resolveAuthority`.

Control flow: static directory helpers are checked against required and defaulted system properties. Lifecycle creates an anonymous `ServerWebApp`, sets home/config/log/temp properties, initializes/destroys it, and checks server status transitions. Failed init sets an invalid services property and expects runtime failure. Authority resolution reads configured hostname and port into an `InetSocketAddress`.

State and persistence: mutates JVM system properties and uses temporary directories from `@TestDir`; no cleanup of these properties is visible in the file.

Dependencies/integration: server lifecycle, servlet context listener flow, JUnit, and custom test directory helper.

Risks and test signals: catches global-property contract regressions. Property mutation can leak across tests if names collide, but test-specific prefixes reduce the risk.
