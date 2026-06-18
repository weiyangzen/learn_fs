# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcInvocationHandler.java

## Purpose
`RpcInvocationHandler` is the common dynamic-proxy handler contract for Hadoop RPC proxies.

## Important APIs, Types, and Functions
It extends `InvocationHandler` and `Closeable`, and requires `getConnectionId()` to expose the associated `Client.ConnectionId`.

## Control Flow
Dynamic proxies created by RPC engines route method calls through implementations. Utility code uses `Proxy.getInvocationHandler` and this interface for connection reuse and shutdown.

## State and Persistence Behavior
The interface has no state. Implementations store client, connection id, caches, and close state in memory.

## Dependencies and Integration Points
Implemented by protobuf engine invokers and `ProxyCombiner.CombinedProxyInvocationHandler`; consumed by `RPC.getConnectionIdForProxy`, `RPC.stopProxy`, and `RpcClientUtil`.

## Risks and Test Signals
Risks include proxy handlers not being closeable or returning wrong connection ids. Tests should verify proxy stop and metadata proxy connection reuse.
