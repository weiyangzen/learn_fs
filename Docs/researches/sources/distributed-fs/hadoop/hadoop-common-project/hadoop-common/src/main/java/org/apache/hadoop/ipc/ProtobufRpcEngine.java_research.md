# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufRpcEngine.java

## Purpose
`ProtobufRpcEngine` is the deprecated RPC engine for unshaded protobuf 2.5 clients. It remains for compatibility while server dispatch is implemented by `ProtobufRpcEngine2` and can handle legacy unshaded service implementations.

## Important APIs, Types, and Functions
`getProxy` overloads create dynamic proxies backed by `Invoker`. `Invoker.invoke` validates protobuf RPC arguments, builds `RpcProtobufRequest`, calls `Client.call`, supports asynchronous mode through `ASYNC_RETURN_MESSAGE`, and decodes return messages by cached default instances. The nested `Server` extends `ProtobufRpcEngine2.Server` and provides legacy callback registration and `processCall` for unshaded `BlockingService`.

## Control Flow
Client calls enter the dynamic proxy, wrap method/header plus payload, trace/log the call, and decode the returned `RpcWritable.Buffer`. Server compatibility dispatch looks up the protobuf method descriptor, decodes the request payload, invokes `callBlockingMethod`, handles deferred callback registration, and maps `ServiceException` causes back to server exceptions.

## State and Persistence Behavior
State includes the static `ClientCache`, per-invoker return prototype cache, connection id, fallback/auth flags, and thread-local async/deferred callback state. It persists nothing.

## Dependencies and Integration Points
It uses legacy `com.google.protobuf`, Hadoop `Client`, `RpcWritable`, `RPC.Server`, tracing, and `ProtobufRpcEngine2` registration. Tests in protobuf RPC compatibility and handoff suites exercise both old and new paths.

## Risks and Test Signals
Risks include classpath dependence on unshaded protobuf, thread-local callback leakage, incorrect async return handling, and compatibility drift with `ProtobufRpcEngine2`. Tests should cover old client/new server interoperability, deferred responses, error unwrapping, async mode, and client cache cleanup.
