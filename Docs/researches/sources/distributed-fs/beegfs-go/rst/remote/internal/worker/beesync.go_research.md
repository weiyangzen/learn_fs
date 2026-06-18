# sources/distributed-fs/beegfs-go/rst/remote/internal/worker/beesync.go

## Purpose
This file implements the concrete BeeSync worker-node client used by BeeRemote to configure sync nodes, submit work requests, update work state, and monitor readiness.

## Important APIs, Types, and Functions
`BeeSyncNode` embeds `baseNode` and stores a gRPC connection and `flex.WorkerNodeClient`. `newBeeSyncNode` wires the node as its own `grpcClientHandler`. `connect` creates the gRPC connection, resolves unspecified BeeRemote bind addresses for callback reachability, checks worker capabilities, sends `UpdateConfig`, and sends `BulkUpdateWork`. `heartbeat`, `disconnect`, `SubmitWork`, `UpdateWork`, and `reportError` implement the rest of the worker interface.

## Control Flow
`connect` optionally reads a TLS CA file, opens a client connection via `beegrpc`, discovers a concrete Remote address if the configured host is unspecified, verifies required features via `registry.GetComponentRegistry`, applies node config, and replays bulk work updates. `SubmitWork` and `UpdateWork` require the node to be `ONLINE`, retry `FailedPrecondition` responses for configured attempts, notify the base handler once via `rpcErr`, and return protobuf work results. `SubmitWork` panics on `AlreadyExists` because duplicate work on a node is considered an invariant violation.

## State and Persistence Behavior
The BeeSync node itself does not persist data; it manages connection/client state and reports transitions to `baseNode`. Configuration and outstanding work are replayed to the sync node on reconnect. RPC wait-group accounting lets the base node drain or cancel in-flight unary calls during disconnect.

## Dependencies and Integration Points
The code depends on `common/beegfs/beegrpc` for TLS/proxy-aware client connections, `common/registry` for capability checks, gRPC status codes, protobuf `flex.WorkerNode`, and `baseNode` lifecycle management. It is instantiated by `worker.NewWorkerNodesFromConfig` and used by `workermgr.Pool`.

## Risks and Edge Cases
The `alreadyNotified` flag is never set after sending `rpcErr`, so repeated retry iterations may attempt duplicate nonblocking notifications. `SubmitWork` panic on `AlreadyExists` can crash BeeRemote instead of isolating a bad node. `connect` treats feature incompatibility as retryable, which may cause repeated reconnect attempts for static version mismatches. Address autodetection mutates a cloned config only after a heartbeat succeeds; failures here can prevent node startup when Remote listens on an unspecified address.

## Test Signals
`beesync_connect_test.go` verifies feature negotiation failures and unimplemented capability handling. There is no direct test for successful config replay, TLS hints, SubmitWork retry behavior, panic-on-duplicate behavior, or address autodetection.
