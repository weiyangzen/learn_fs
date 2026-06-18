# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/ExceptionHandler.java

## Purpose

`ExceptionHandler` converts exceptions thrown by the Netty WebHDFS handlers into JSON HTTP responses compatible with WebHDFS clients.

## Important APIs, Control Flow, and State

`exceptionCaught(Throwable)` normalizes non-`Exception` throwables, traces debug details, converts Jersey `ParamException` into an `IllegalArgumentException`, unwraps `ContainerException`, selected `SecurityException` causes, and Hadoop `RemoteException`, maps exception classes to HTTP statuses, serializes the exception via `JsonUtil.toJsonString`, and returns a `DefaultFullHttpResponse` with JSON content type and length.

`toCause` has special handling for `SecurityException` caused by invalid delegation tokens whose cause is `StandbyException`, returning the standby exception so HA standby errors are not masked. There is no retained state or persistence.

## Dependencies, Integration, Risks, and Tests

Dependencies include Netty response buffers, Jersey exceptions, Hadoop `RemoteException`, `StandbyException`, `AuthorizationException`, token `InvalidToken`, and `JsonUtil`. It integrates with `WebHdfsHandler.exceptionCaught` and `HdfsWriter.exceptionCaught`.

Risks include mapping all `IOException` to `FORBIDDEN`, exposing exception messages in JSON, losing cause details during normalization, and status choices diverging from WebHDFS servlet behavior. Tests should cover parameter errors, file-not-found, authorization/security errors, remote exception unwrap, invalid-token standby conversion, unsupported operations, and unknown exception 500 responses.
