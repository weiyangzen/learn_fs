# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/server/TestServer.java

Purpose: Comprehensive unit suite for the HTTPFS library `Server` container: constructors, directory validation, config loading precedence, lifecycle states, service loading, dependency validation, replacement/addition, and cleanup ordering.

Important APIs/types/functions: `createServer`, `getAbsolutePath`, `LifeCycleService`, `TestService`, `TestServiceExceptionOnStatusChange`, abstract `MyService`, service variants `MyService1` through `MyService7`, and tests for `constructorsGetters`, init failure cases, `lifeCycle`, `changeStatus`, config loading, illegal states, invalid services, missing dependencies, and `services`.

Control flow: tests construct `Server` with explicit or derived home/config/log/temp dirs, validate missing/non-directory paths map to expected `ServerException` codes, and verify default/site/system-property config precedence. Service tests load configured service class lists, record lifecycle ordering in static `ORDER` or `LIFECYCLE`, assert post-init and destroy ordering, force init/destroy/status-change failures, override services using `server.services.ext`, replace/add services using `setService`, and check dependency handling.

State and persistence: creates temporary directories and config/log4j/site XML files under `@TestDir`. Static lists record lifecycle order and are cleared before scenarios. Server state transitions through `UNDEF`, `BOOTING`, `NORMAL`/`ADMIN`, `SHUTTING_DOWN`, and `SHUTDOWN`.

Dependencies/integration: JUnit 5, custom `@TestDir` and `@TestException`, Hadoop `Configuration`, `StringUtils`, and `XException`/`ServiceException` error contracts.

Risks and test signals: central regression signal for service container correctness. Static lifecycle lists and multi-scenario test method are somewhat coupled, but the suite captures many edge cases: invalid classes, no default constructor, wrong interface, missing dependency, init rollback, destroy tolerance, and runtime service mutation.
