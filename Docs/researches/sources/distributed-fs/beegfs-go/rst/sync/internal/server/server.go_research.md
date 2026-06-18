# sources/distributed-fs/beegfs-go/rst/sync/internal/server/server.go

## Purpose
This file implements BeeSync's worker-node gRPC server, which BeeRemote calls to configure the node, submit work, cancel/update work, check heartbeat readiness, and inspect capabilities.

## Important APIs, Types, and Functions
`Config` defines address and TLS settings. `WorkerNodeServer` embeds the unimplemented Flex worker server and stores logger, wait group, gRPC server, work manager, capability registry, and start time. `New`, `ListenAndServe`, `Stop`, `UpdateConfig`, `BulkUpdateWork`, `SubmitWork`, `UpdateWork`, `Heartbeat`, and `GetCapabilities` implement lifecycle and RPC behavior.

## Control Flow
`New` creates a TLS-enabled or plaintext gRPC server and registers the Flex worker service. `ListenAndServe` starts a TCP listener and serves in a goroutine. `UpdateConfig` forwards RST and BeeRemote config to the work manager and returns success/failure in-band. `BulkUpdateWork` currently accepts only `UNCHANGED`. `SubmitWork` and `UpdateWork` call work-manager methods. `Heartbeat` reports manager readiness.

## State and Persistence Behavior
The server persists no state directly. It tracks active RPC handlers with a wait group. Durable work state lives in `workmgr.Manager`. Capabilities include start timestamp and build info from the registry.

## Dependencies and Integration Points
It integrates `sync/internal/workmgr`, `common/registry`, gRPC/TLS, protobuf `flex`, and zap logging. BeeRemote's `BeeSyncNode.connect`, `SubmitWork`, `UpdateWork`, and heartbeat calls target this server.

## Risks and Edge Cases
`BulkUpdateWork` does not yet support cancellation or replay updates for outstanding work, limiting offline recovery behavior. TLS is disabled if cert/key are missing or explicitly disabled, with only a warning. Some RPC methods do not increment/decrement the server wait group, unlike the remote server, so `Stop` may not fully wait for every handler path.

## Test Signals
No direct tests cover this server. BeeSync connection tests use minimal worker servers instead of this implementation, and work-manager tests call the manager directly.
