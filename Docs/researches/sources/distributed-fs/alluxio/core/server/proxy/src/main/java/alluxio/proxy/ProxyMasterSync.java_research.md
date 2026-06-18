# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/ProxyMasterSync.java

## Purpose
`ProxyMasterSync` is a heartbeat executor that lets a proxy periodically register liveness and version information with the primary master. This supports administrative visibility into live proxy instances.

## Important APIs, Types, and Functions
The class implements `HeartbeatExecutor`. Its main methods are the constructor, `heartbeat(long timeLimitMs)`, and `close`. It owns the proxy `Address` and a `RetryHandlingMetaMasterProxyClient`.

## Control Flow, State, and Persistence
Construction creates the retrying master client with proxy address and start time, then logs the start timestamp. Each heartbeat calls `mMasterClient.proxyHeartbeat`. If an `IOException` occurs, it logs the failure and disconnects the client so a later heartbeat can reconnect. `close` is currently a no-op. State is process-local client connection state.

## Dependencies and Integration Points
It integrates the proxy process heartbeat thread with the meta master proxy gRPC service through `RetryHandlingMetaMasterProxyClient` and Alluxio `HeartbeatExecutor`.

## Risks
`close` does not close the underlying client explicitly. Repeated heartbeat failures are logged but do not stop the proxy, which is intentional for availability but can hide registration problems. The class is not thread-safe and is intended for one heartbeat thread.

## Test Signals
Useful tests should mock the client and verify successful heartbeat, disconnect on `IOException`, and tolerance of repeated failures without throwing from the heartbeat thread.
