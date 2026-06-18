# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufRpcEngineCallback.java

## Purpose
This deprecated callback interface lets legacy unshaded protobuf RPC server implementations complete a response asynchronously after registering for a deferred response.

## Important APIs, Types, and Functions
`setResponse(com.google.protobuf.Message message)` supplies the eventual protobuf response. `error(Throwable t)` completes the deferred RPC with an error.

## Control Flow
Server code calls `ProtobufRpcEngine.Server.registerForDeferredResponse`, returns from the service method, and later invokes one callback method. The engine marks the call as deferred and updates response/error plus metrics when callback fires.

## State and Persistence Behavior
The interface carries no state. Implementations capture the current RPC server call and method name in runtime memory.

## Dependencies and Integration Points
It depends on unshaded protobuf and is superseded by `ProtobufRpcEngineCallback2`. It integrates with `ProtobufRpcEngine.Server`.

## Risks and Test Signals
Risks are callback invocation after request context is gone, double completion, and legacy protobuf classpath issues. Handoff/deferred-response tests should include success and error callbacks.
