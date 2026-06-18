# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/AlignmentContext.java

## Purpose

`AlignmentContext` is an IPC extension point for carrying state identifiers between Hadoop RPC clients and servers. It lets implementations reject or coordinate calls when client and server state are too far apart.

## Important APIs, control flow, and state

The interface defines server-to-client response state methods (`updateResponseState`, `receiveResponseState`), client-to-server request state methods (`updateRequestState`, `receiveRequestState`), `getLastSeenStateId()`, and `isCoordinatedCall(protocolName, method)`. Implementations own all state; this interface only specifies where request and response protobuf headers are updated or inspected.

## Dependencies and integration points

It uses `RpcRequestHeaderProto` and `RpcResponseHeaderProto`. `Client` attaches an alignment context to each call, passes it to `ProtoUtil.makeRpcRequestHeader()`, and updates it when a successful response arrives. `Server` and protobuf RPC engines expose builders and server construction paths that accept an alignment context.

## Risks and test signals

Incorrect implementation can cause stale reads, unnecessary rejections, or inconsistent client state. `receiveRequestState()` can throw `IOException`, so server request admission paths must handle alignment failures. Test signals should cover header field propagation, threshold-based rejection, successful response state updates, and coordinated versus uncoordinated methods.
