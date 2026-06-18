# sources/control-plane/longhorn-engine/app/cmd/ls_replica.go

## Purpose
Implements the `ls-replica`/`ls` CLI command to print controller-known replicas with their modes and disk chains.

## Important APIs, Types, and Functions
- `LsReplicaCmd()` defines the command.
- `lsReplica()` obtains controller replica list and prints `ADDRESS`, `MODE`, and `CHAIN` columns.
- `getChain(address, volumeName)` opens a replica client and returns `Replica.Chain`.

## Control Flow
`lsReplica` creates a controller client, gets `ReplicaList`, and iterates each replica. Replicas in `types.ERR` are printed without chain lookup. For others, it uses a replica client without instance-name validation to fetch the disk chain and emits a tabwriter table.

## State and Persistence Behavior
Read-only. It observes controller replica membership and replica disk-chain metadata. No mutations occur.

## Dependencies and Integration Points
Uses `getControllerClient`, `pkg/replica/client`, `pkg/types`, and stdout tabwriter output. `snapshot.go` reuses `getChain` to derive snapshot lists from replica chains.

## Risks and Edge Cases
Chain lookup failures are silently represented as an empty chain, which avoids breaking `ls` but can hide replica RPC issues. The function intentionally omits replica instance-name validation because caller does not know it.

## Test Signals
Indirectly tested by snapshot list paths and CLI integration tests that inspect chains. There is no dedicated `ls-replica` test in the listed subset.
