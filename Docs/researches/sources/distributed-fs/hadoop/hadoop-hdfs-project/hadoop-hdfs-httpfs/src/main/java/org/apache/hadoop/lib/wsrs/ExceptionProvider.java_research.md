# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/ExceptionProvider.java

## Purpose
`ExceptionProvider` is a JAX-RS exception mapper that converts uncaught throwables into HTTP error responses for HttpFS REST endpoints.

## Important APIs, Types, and Functions
It implements `ExceptionMapper<Throwable>`. `toResponse(Throwable)` returns a BAD_REQUEST response by default. `createResponse(Response.Status, Throwable)` delegates to `HttpExceptionUtils.createJerseyExceptionResponse`. `getOneLineMessage` truncates messages at the first platform line separator. `log` emits debug-level exception details.

## Control Flow
Jersey calls `toResponse` when endpoint dispatch throws. The default implementation maps every throwable to HTTP 400, relying on subclasses or other mappers for more specific status mapping if present.

## State and Persistence
No mutable request state is stored. Logging is the only side effect.

## Dependencies and Integration Points
The web descriptors include `org.apache.hadoop.lib.wsrs` in Jersey provider package scanning, making this mapper available to HttpFS resources. It depends on Hadoop `HttpExceptionUtils` to produce the JSON/HTTP response shape expected by Hadoop clients.

## Risks
The broad `Throwable` mapping can hide server-side faults as client BAD_REQUEST unless a more specific mapper intercepts them. `getOneLineMessage` is unused in this class, suggesting either legacy behavior or subclass hooks. Debug-only logging may make production diagnosis dependent on client-visible JSON.

## Test Signals
`BaseTestHttpFSWith` has negative paths for invalid create overwrite, invalid working directory, xattr names, and snapshot diff parameters; these exercise exception conversion through client-visible failures.
