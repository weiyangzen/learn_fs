# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufRpcEngineCallback2.java

## Purpose
`ProtobufRpcEngineCallback2` is the shaded-protobuf deferred response callback for `ProtobufRpcEngine2` server implementations.

## Important APIs, Types, and Functions
It declares `setResponse(org.apache.hadoop.thirdparty.protobuf.Message message)` and `error(Throwable t)`.

## Control Flow
Server code obtains an implementation from `ProtobufRpcEngine2.Server.registerForDeferredResponse2`, returns control to the RPC engine, and later completes the call through the callback.

## State and Persistence Behavior
No state is declared here. Runtime implementation state captures the active `Call`, `RPC.Server`, and method name.

## Dependencies and Integration Points
It depends on Hadoop's shaded protobuf package and integrates with `ProtobufRpcEngine2.Server` deferred handling and metrics.

## Risks and Test Signals
Risks include failure to call exactly one completion method and thread-local callback leakage. Tests should cover deferred success/error, metrics update, and callback use from another thread.
