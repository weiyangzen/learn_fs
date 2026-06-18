# sources/cloud-native/moby/daemon/server/router/swarm/cluster.go

## Purpose
`cluster.go` defines the swarm router and registers swarm, service, node, task, secret, and config endpoints.

## Important APIs, Types, And Functions
`swarmRouter` stores backend and routes. `NewRouter`, `Routes`, and `initRoutes` implement setup.

## Control Flow
Route registration covers cluster lifecycle, unlock key, services and logs, nodes, tasks and logs, secrets, and configs. Secrets require API 1.25+ and configs require API 1.30+.

## State And Persistence
The router stores no durable state. Cluster state is handled by the backend.

## Dependencies And Integration Points
Uses the shared router constructors and API-version wrappers.

## Risks
The router has many endpoints with overlapping path parameters; adding new swarm paths requires care to avoid path conflicts.

## Test Signals
Swarm API integration tests verify registration and behavior.
