# sources/control-plane/longhorn-engine/app/cmd/update_replica.go

## Purpose
Implements `update-replica`/`update` for changing a controller replica mode.

## Important APIs, Types, and Functions
- `UpdateReplicaCmd()` defines the CLI and `--mode` flag.
- `updateReplica()` validates address and mode, then calls `ControllerClient.ReplicaUpdate`.

## Control Flow
The helper requires a replica address and only accepts `types.WO`, `types.RW`, or `types.ERR`. It opens a controller client and delegates update, returning updated `ControllerReplicaInfo`.

## State and Persistence Behavior
Mutates controller replica mode state. This can affect IO routing, rebuild eligibility, and failure semantics; direct persistence is controlled by controller internals.

## Dependencies and Integration Points
Depends on `pkg/types` mode constants and `getControllerClient`. It mirrors gRPC operations tested in controller integration tests.

## Risks and Edge Cases
Usage text says RO/RW/ERR, but validation accepts WO/RW/ERR. This mismatch can confuse callers and is a documentation/API risk.

## Test Signals
`integration/core/test_controller.py::test_replica_change` covers mode update through gRPC. No direct CLI test for `update-replica` appears here.
