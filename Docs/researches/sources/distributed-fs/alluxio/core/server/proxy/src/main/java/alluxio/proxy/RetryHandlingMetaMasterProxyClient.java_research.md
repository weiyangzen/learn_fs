# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/RetryHandlingMetaMasterProxyClient.java

## Purpose
`RetryHandlingMetaMasterProxyClient` wraps the meta master proxy gRPC client with Alluxio master-client retry behavior. It sends proxy heartbeat requests containing address, start time, and build version.

## Important APIs, Types, and Functions
The class extends `AbstractMasterClient` and overrides `getRemoteServiceType`, `getServiceName`, `getServiceVersion`, and `afterConnect`. Its public operation is `proxyHeartbeat()`, which builds `ProxyHeartbeatPOptions` and calls the blocking gRPC stub through `retryRPC`.

## Control Flow, State, and Persistence
The constructor stores the proxy address and start timestamp. `afterConnect` creates a `MetaMasterProxyServiceBlockingStub` from `mChannel`. `proxyHeartbeat` builds `BuildVersion` from `RuntimeConstants.VERSION` and `REVISION_SHORT`, sets a deadline from `USER_RPC_RETRY_MAX_DURATION`, and sends `ProxyHeartbeatPRequest`. State is the gRPC channel/stub managed by the inherited master client.

## Dependencies and Integration Points
The client integrates proxy liveness with `MetaMasterProxyServiceGrpc`, Alluxio service version constants, master client context, cluster configuration, and retry logging.

## Risks
`mClient` is null until a connection is established by inherited logic, so calls must go through `retryRPC`/connect flow. The deadline uses the same maximum retry duration property as user RPCs. Incorrect address or version data affects master-side proxy registration.

## Test Signals
Useful tests should verify heartbeat request contents, service type/name/version constants, deadline application, and retry/disconnect behavior on gRPC failures.
