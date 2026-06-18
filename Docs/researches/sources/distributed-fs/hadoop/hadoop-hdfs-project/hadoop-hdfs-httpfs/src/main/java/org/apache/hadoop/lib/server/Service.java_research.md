<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/Service.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/Service.java

## Purpose
`Service` defines the managed component contract for the HttpFS service container.

## Important APIs, Types, And Functions
Methods include `init(Server)`, `postInit()`, `destroy()`, `getServiceDependencies()`, `getInterface()`, and `serverStatusChange(Server.Status, Server.Status)`. `getInterface()` is the key used by `Server.get(Class)` and de-duplication.

## Control Flow
`Server` loads configured service classes, validates each implementation against `getInterface`, checks declared dependencies against initialized services, calls `init`, later calls `postInit`, notifies status changes, and finally calls `destroy` in reverse order.

## State And Persistence
The interface itself has no state. Implementations hold service state.

## Dependencies And Integration Points
It depends on `Server` and `ServiceException`. Concrete implementations in this subset include filesystem access, instrumentation, scheduler, and groups.

## Risks
Implementations must return stable interface classes. Dependency arrays are checked only against already initialized services, making configured order significant. Exceptions in status notification can tear down the whole server.

## Test Signals
Container tests should use fake services to verify lifecycle order, dependency ordering, interface validation, and status-change failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/Service.java -->
