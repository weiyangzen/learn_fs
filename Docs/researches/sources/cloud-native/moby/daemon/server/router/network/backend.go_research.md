# sources/cloud-native/moby/daemon/server/router/network/backend.go

## Purpose
`backend.go` defines local and swarm-cluster network backend contracts used by the network router.

## Important APIs, Types, And Functions
`Backend` covers local network list/inspect summaries, create, connect, disconnect, delete, and prune. `ClusterBackend` covers swarm network list/summaries, single get, lookup by name, create, and remove.

## Control Flow
Route handlers call both interfaces to merge local and swarm networks, resolve ambiguous names/IDs, and route create/delete operations to local or cluster implementations.

## State And Persistence
Implementations persist network definitions, endpoints, and pruning effects. The interface file holds no state.

## Dependencies And Integration Points
Depends on API network types, daemon filters, internal daemon network filters, server backend list config, and network backend connect/disconnect request types.

## Risks
The split backend contract makes ambiguity handling a router responsibility. Local and swarm data can race or duplicate by name/ID.

## Test Signals
Compilation plus network API tests validate that local and cluster implementations satisfy the contract.
