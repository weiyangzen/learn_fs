# sources/control-plane/longhorn-engine/app/cmd/rm_replica.go

## Purpose
Implements `rm-replica`/`rm`, deleting a replica from the controller by address.

## Important APIs, Types, and Functions
- `RmReplicaCmd()` defines the CLI command.
- `rmReplica()` validates an address arg and calls `ControllerClient.ReplicaDelete`.

## Control Flow
The command requires at least one positional argument and ignores any extras. It opens a controller client with global flags, defers close logging, and delegates deletion.

## State and Persistence Behavior
Mutates controller in-memory replica membership and may trigger controller-side cleanup or frontend behavior. It does not directly remove replica disk files.

## Dependencies and Integration Points
Depends on `getControllerClient` and controller client RPC. Related test scenarios directly use gRPC `replica_delete`; CLI command behavior is analogous.

## Risks and Edge Cases
No validation of address scheme beyond server-side handling. Repeated deletes are handled by controller semantics; this wrapper does not special-case idempotency.

## Test Signals
`integration/core/test_controller.py` covers delete behavior through the gRPC client. `test_cli.py` includes removing ERR replicas before snapshot cleanup through controller client, not necessarily this CLI wrapper.
