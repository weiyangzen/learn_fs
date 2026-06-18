# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterProxyServiceHandler.java

## Purpose
`MetaMasterProxyServiceHandler` is the gRPC service adapter for Alluxio proxy heartbeats. It lets proxy processes report liveness and metadata to the meta master.

## Important APIs and Types
- Extends `MetaMasterProxyServiceGrpc.MetaMasterProxyServiceImplBase`.
- Holds `MetaMaster mMetaMaster`.
- `proxyHeartbeat(ProxyHeartbeatPRequest, StreamObserver<ProxyHeartbeatPResponse>)` forwards the whole proxy heartbeat request.

## Control Flow
The single RPC uses `RpcUtils.call`; it delegates the complete `ProxyHeartbeatPRequest` to `mMetaMaster.proxyHeartbeat` and returns an empty response built with `ProxyHeartbeatPResponse.newBuilder().build()`.

## State and Persistence
The handler has no local state. Proxy liveness and metadata are represented in meta-master state, commonly through `ProxyInfo` records.

## Dependencies and Integration Points
The class integrates gRPC proxy service definitions with `MetaMaster`. It is part of cluster monitoring and web/UI status paths that need proxy liveness.

## Risks and Edge Cases
- The handler does no request normalization; malformed or incomplete request fields rely on deeper validation.
- Annotated `NotThreadSafe`; concurrent correctness depends on `MetaMaster.proxyHeartbeat`.

## Test Signals
Test that the complete request is passed through, successful calls return an empty response, and failures are converted by `RpcUtils`.
