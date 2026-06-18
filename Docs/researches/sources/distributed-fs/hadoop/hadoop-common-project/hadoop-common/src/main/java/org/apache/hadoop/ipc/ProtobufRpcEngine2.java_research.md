# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufRpcEngine2.java

## Purpose
`ProtobufRpcEngine2` is the primary shaded-protobuf Hadoop RPC engine. It creates protobuf client proxies, registers the protobuf RPC request deserializer, builds RPC servers, dispatches server calls to shaded or legacy protobuf services, and supports asynchronous/deferred responses.

## Important APIs, Types, and Functions
`registerProtocolEngine` binds `RPC_PROTOCOL_BUFFER` to `RpcProtobufRequest` and `ProtoBufRpcInvoker`. `Invoker` implements client proxy invocation and return decoding. `Server` extends `RPC.Server`, registers protocol implementations, exposes `registerForDeferredResponse2`, and owns `CURRENT_CALLBACK`/`CURRENT_CALL_INFO`. `ProtoBufRpcInvoker` validates protocol/version, finds method descriptors, decodes requests, invokes `BlockingService`, and wraps responses with `RpcWritable`.

## Control Flow
Client proxy calls require `(RpcController, Message)` arguments, build `RequestHeaderProto`, call `Client.call`, and either set a thread-local `AsyncGet` or decode the response immediately. Server calls decode the request header, select the declaring protocol and client version, reject unknown protocols or versions, then dispatch to shaded `BlockingService` or `ProtobufRpcEngine.Server.processCall` for unshaded legacy services. Deferred responses mark the current server call and return null until callback completion.

## State and Persistence Behavior
State is runtime only: static client cache, return prototype caches, connection ids, auth fallback flags, alignment context, and thread-local async/deferred call data. No persistent data is written.

## Dependencies and Integration Points
It integrates with `RPC`, `Client`, `RpcWritable`, `ProtocolMetaInfoPB`, shaded protobuf, legacy engine compatibility, tracing, SASL/security setup via higher `RPC` methods, and server metrics. Tests include `TestProtoBufRpc`, `TestProtoBufRpcServerHandoff`, `TestProtoBufRPCCompatibility`, and `TestRPC`.

## Risks and Test Signals
High-risk areas are protocol-version lookup, legacy/shaded service branching, thread-local cleanup, method-name uniqueness, async response decoding, and deferred metrics timing. Tests should cover unknown method/protocol, version mismatch, shaded and unshaded services, async mode, deferred success/error, and client cache clearing.
