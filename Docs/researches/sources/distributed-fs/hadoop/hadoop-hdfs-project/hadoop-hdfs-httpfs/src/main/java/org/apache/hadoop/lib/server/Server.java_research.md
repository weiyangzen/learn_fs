<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/Server.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/Server.java

## Purpose
`Server` is the generic runtime container used by HttpFS' `ServerWebApp`. It provides directory validation, configuration loading/overlay, log4j setup, service class loading and de-duplication, dependency-checked lifecycle management, status transitions, and service lookup.

## Important APIs, Types, And Functions
`Status` defines `UNDEF`, `BOOTING`, `HALTED`, `ADMIN`, `NORMAL`, `SHUTTING_DOWN`, and `SHUTDOWN`, with settable/operational flags. Constructors accept home/config/log/temp dirs and optional config. Key methods are `init`, `setStatus`, `ensureOperational`, `initLog`, `initConfig`, `loadServices`, `initServices`, `checkServiceDependencies`, `destroyServices`, `destroy`, `get`, and `setService`. Config constants are `services`, `services.ext`, and `startup.status`.

## Control Flow
`init()` moves from `UNDEF` to `BOOTING`, validates directories, loads build metadata, initializes logging, loads default/site/system-property config, loads service classes from base and extension lists, removes duplicate service interfaces with last implementation winning, initializes services in order, post-initializes all, then sets startup status from config. `destroy()` reverses service order and shuts log4j. `setStatus` notifies services and destroys the server on notification failure.

## State And Persistence
The server stores current status, directory paths, configuration, logger, and a `LinkedHashMap<Class, Service>` keyed by service interface. It reads config/log/build files but does not write state.

## Dependencies And Integration Points
It integrates with Hadoop `Configuration`, `ConfigurationUtils`, log4j, SLF4J, `ConfigRedactor`, service implementations, and classpath resources named after the server.

## Risks
`destroy()` calls `ensureOperational`, so destruction from non-operational states can throw. Service class instantiation uses deprecated no-arg `newInstance`. Missing build metadata resource causes a runtime exception. `getPrefixedName` rejects empty names via `Check.notEmpty`, while callers must pass non-empty suffixes. Programmatic `setService` initializes but does not post-init the replacement.

## Test Signals
Tests should cover config overlay/default injection, redacted system-property override logging, service de-duplication, dependency failure, reverse destroy order, status notifications and failure shutdown, and programmatic service replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/Server.java -->
