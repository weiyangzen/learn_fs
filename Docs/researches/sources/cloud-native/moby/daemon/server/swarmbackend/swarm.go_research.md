# sources/cloud-native/moby/daemon/server/swarmbackend/swarm.go

## Purpose
`swarm.go` defines option structs shared between HTTP swarm routers and daemon/swarm backend implementations.

## Important APIs, Types, And Functions
Types include `ConfigListOptions`, `NodeListOptions`, `TaskListOptions`, `UpdateFlags`, `ServiceUpdateOptions`, `ServiceListOptions`, and `SecretListOptions`.

## Control Flow
Routers fill these structs from filters/query parameters and pass them to backend methods.

## State And Persistence
No state is stored. The structs carry request options for backend operations that may mutate swarm state.

## Dependencies And Integration Points
Depends on API swarm registry-auth source type and daemon filters. Used by swarm router handlers and backend interfaces.

## Risks
Adding fields affects both routers and backend implementations. `ServiceUpdateOptions` must preserve registry-auth and rollback semantics.

## Test Signals
Compilation plus swarm route tests validate option wiring.
