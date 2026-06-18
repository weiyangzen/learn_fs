<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/ServerException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/ServerException.java

## Purpose
`ServerException` is the coded checked exception for failures in the `Server` lifecycle and service container.

## Important APIs, Types, And Functions
The `ERROR` enum implements `XException.ERROR` with codes `S01` through `S14` for missing directories, non-directories/files, resource/config load failures, invalid service interfaces, instantiation/load errors, programmatic service replacement, dependency failures, status-change failures, service startup failures, missing system properties, and initialization failure. Constructors delegate to `XException`.

## Control Flow
`Server` throws `ServerException` from validation, configuration, service loading, dependency checks, status transitions, and service replacement. `ServiceException` subclasses it for service-specific errors.

## State And Persistence
Each exception stores an error enum, message, and optional cause through `XException`. No persistence.

## Dependencies And Integration Points
It depends on `XException` and is consumed by `Server`, `BaseService` implementations, and `HttpFSServerWebApp.init`.

## Risks
Error messages are public enough to appear in logs and startup failures; spelling mistakes in templates are compatibility noise but not behavior. Protected constructor enables subclasses to pass their own error enums.

## Test Signals
Tests should assert formatting for representative enum values and that wrapped causes are preserved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/ServerException.java -->
