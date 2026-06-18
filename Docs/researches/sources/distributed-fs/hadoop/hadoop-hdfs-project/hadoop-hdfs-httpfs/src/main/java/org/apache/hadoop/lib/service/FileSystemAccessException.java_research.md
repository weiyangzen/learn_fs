<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/FileSystemAccessException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/FileSystemAccessException.java

## Purpose
`FileSystemAccessException` is the coded checked exception for filesystem access service failures.

## Important APIs, Types, And Functions
The `ERROR` enum defines `H01` through `H11`: missing service property, Kerberos init failure, executor error, invalid service-created config, NameNode validation failure, missing `fs.defaultFS`, unhealthy namenode, generic message, invalid auth mode, missing Hadoop config directory, and Hadoop config load failure. Constructor delegates to `XException`.

## Control Flow
`FileSystemAccessService` throws this exception from initialization, validation, and execution paths. `HttpFSExceptionProvider` unwraps it to map the cause when possible.

## State And Persistence
Each instance stores the error code/message/cause through `XException`; no persistent state.

## Dependencies And Integration Points
It depends on `XException` and is part of the `FileSystemAccess` service contract and HttpFS exception mapping.

## Risks
Some errors wrap causes, but mapper unwrapping can hide the service-specific code from HTTP responses. The H04 template has a typo but its semantics are important: callers must use service-created configurations.

## Test Signals
Tests should cover each major error path in `FileSystemAccessService`, especially invalid config marker, missing default FS, whitelist rejection, and executor exception wrapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/FileSystemAccessException.java -->
