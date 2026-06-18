# sources/cloud-native/moby/daemon/server/router/network/network.go

## Purpose
`network.go` defines the network router and registers Docker network API routes.

## Important APIs, Types, And Functions
`networkRouter` stores local and cluster backends plus route metadata. `NewRouter`, `Routes`, and `initRoutes` implement the common router pattern.

## Control Flow
Routes include list, inspect, create, connect, disconnect, prune, and delete. Prune is gated to API 1.25+.

## State And Persistence
The router stores only backend references. Network persistence is handled by backends.

## Dependencies And Integration Points
Integrates network route handlers with the shared router constructors and version wrappers.

## Risks
Path patterns use `{id:.+}` and `{id:.*}` to capture IDs/names that may include special characters while preserving empty-match behavior for some endpoints.

## Test Signals
No direct tests in this file; network API route tests exercise registrations.
