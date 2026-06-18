# sources/cloud-native/moby/daemon/server/router/system/backend.go

## Purpose
`backend.go` defines system, cluster, build, and status-provider contracts used by the system router.

## Important APIs, Types, And Functions
`Backend` exposes `SystemInfo`, `SystemVersion`, `SystemDiskUsage`, event subscribe/unsubscribe, and registry auth. `ClusterBackend` exposes swarm info. `BuildBackend` exposes build-cache disk usage. `StatusProvider` exposes a swarm status string.

## Control Flow
System routes call these interfaces to build `/info`, `/version`, `/system/df`, `/events`, `/_ping`, and `/auth` responses.

## State And Persistence
Implementations read daemon/system state, subscribe to events, and authenticate to registries. The interface file stores no state.

## Dependencies And Integration Points
Depends on API events/registry/swarm/system types, daemon filters, and backend/buildbackend option structs.

## Risks
The router composes data from multiple backends concurrently; missing or nil implementations must be handled by routes.

## Test Signals
System route integration tests and compile-time backend satisfaction validate this contract.
