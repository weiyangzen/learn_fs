# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingProxy.java

## Purpose
`GrpcMessagingProxy` stores optional address remapping for messaging servers, allowing a logical server address to bind through a different proxy address.

## Important APIs, Types, and Functions
It exposes `addProxy(InetSocketAddress, InetSocketAddress)`, `hasProxyFor(InetSocketAddress)`, and `getProxyFor(InetSocketAddress)`.

## Control Flow, State, and Persistence
The class stores a mutable `HashMap` from source address to proxy address. `addProxy()` mutates the map and returns `this` for chaining. There is no persistence or synchronization.

## Dependencies and Integration Points
It depends only on `InetSocketAddress` and collection classes. `GrpcMessagingServer.listen()` consults it before choosing the bind address.

## Risks and Test Signals
Risks include lack of thread safety, exact `InetSocketAddress` equality requirements, and stale proxy mappings. Signals are server binding to proxy addresses and non-proxied addresses binding directly.
