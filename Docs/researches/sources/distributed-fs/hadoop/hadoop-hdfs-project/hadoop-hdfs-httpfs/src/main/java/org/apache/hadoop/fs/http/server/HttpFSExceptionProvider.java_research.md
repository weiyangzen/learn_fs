<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSExceptionProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSExceptionProvider.java

## Purpose
`HttpFSExceptionProvider` is the Jersey exception mapper for HttpFS REST requests. It translates server and filesystem exceptions into HTTP responses and writes audit/server logs with request metadata from MDC.

## Important APIs, Types, And Functions
The class extends `org.apache.hadoop.lib.wsrs.ExceptionProvider` and is annotated with `@Provider`. `toResponse(Throwable)` unwraps `FileSystemAccessException` and Jersey `ContainerException`, then maps `SecurityException` to `401`, `FileNotFoundException` to `404`, `IOException` to `500`, `UnsupportedOperationException` and `IllegalArgumentException` to `400`, and unknown failures to `500`. `log(Response.Status, Throwable)` writes audit and server warnings using `method` and `path` MDC values. `logErrorFully` emits debug-level stack details for selected server-side failures.

## Control Flow
Jersey calls `toResponse` when an endpoint throws. The mapper normalizes wrapper exceptions before choosing a status, calls the inherited `createResponse`, and relies on the inherited provider to invoke logging behavior.

## State And Persistence
There is no persistent state. Side effects are HTTP response construction and log emission.

## Dependencies And Integration Points
It depends on Jersey, the shared `ExceptionProvider`, `FileSystemAccessException`, SLF4J, and MDC values set by HttpFS request filters/endpoints. It is central to how `HttpFSServer` executor failures surface to clients.

## Risks
`SecurityException` maps to unauthorized rather than forbidden, which is externally visible. `FileSystemAccessException` and `ContainerException` unwrapping assumes a meaningful cause; null causes could lead to less specific mapping. Full stack traces for IO/bad-request classes are only debug-level.

## Test Signals
Tests should assert status mappings, wrapper unwrapping, error body format inherited from `ExceptionProvider`, and audit log fields when MDC values are present or absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSExceptionProvider.java -->
