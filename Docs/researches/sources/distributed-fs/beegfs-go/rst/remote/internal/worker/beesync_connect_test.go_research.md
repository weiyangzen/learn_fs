# sources/distributed-fs/beegfs-go/rst/remote/internal/worker/beesync_connect_test.go

## Purpose
This file tests BeeSync worker-node connection capability negotiation against lightweight in-process gRPC worker servers.

## Important APIs, Types, and Functions
`testWorkerNodeServer` implements `GetCapabilities` with a configurable feature map. `unimplementedCapabilitiesServer` leaves capabilities unimplemented. `startWorkerNodeServer` creates a local gRPC server on `127.0.0.1:0`. `newTestBeeSyncNode` builds a TLS-disabled BeeSync node for the test address. `connectInputs` creates minimal config and bulk-update inputs. The two tests assert required-feature and unimplemented-capability failures.

## Control Flow
Each test starts a temporary gRPC server, constructs a BeeSync node, calls `node.connect`, and inspects the retry flag and error chain. The required-feature test provides one supported feature but asks for an extra feature. The unimplemented test checks behavior when the server does not support the capability RPC.

## State and Persistence Behavior
The tests use no persisted state. They allocate a gRPC listener and close it in cleanup; the BeeSync node closes its client connection with `disconnect`.

## Dependencies and Integration Points
The tests integrate the worker client with actual gRPC server plumbing and `common/registry` capability helpers. They validate the connection-time contract consumed by `baseNode.connectLoop`.

## Risks and Edge Cases
The tests focus on negative capability cases. They do not test successful `UpdateConfig`/`BulkUpdateWork`, heartbeat address discovery, TLS configuration, retry backoff, or runtime SubmitWork/UpdateWork behavior.

## Test Signals
Passing tests confirm that incompatible or capability-less sync nodes surface registry errors and are treated as retryable connection failures.
