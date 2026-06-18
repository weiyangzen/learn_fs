<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/ServiceException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/ServiceException.java

## Purpose
`ServiceException` is a thin subclass of `ServerException` used by `Service` implementations to report initialization and lifecycle failures.

## Important APIs, Types, And Functions
It exposes a single public constructor accepting any `XException.ERROR` plus parameters and delegates to `ServerException`.

## Control Flow
Concrete services throw it from `init` or `postInit`. `Server.initServices` catches `ServerException`, destroys already initialized services, and propagates failure.

## State And Persistence
No additional state beyond `ServerException` and `XException`.

## Dependencies And Integration Points
It depends on `ServerException` and `XException.ERROR`; service implementations often pass domain-specific error enums such as `FileSystemAccessException.ERROR`.

## Risks
Because it accepts any error enum, callers must choose meaningful codes. It does not add service identity automatically; callers should include context in parameters.

## Test Signals
Formatting and cause propagation are inherited; service initialization tests should confirm thrown `ServiceException` triggers container cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/ServiceException.java -->
