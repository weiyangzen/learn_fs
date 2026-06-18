# sources/cloud-native/moby/daemon/server/router/container/container.go

## Purpose
Registers all container-related API routes.

## Important APIs, Types, And Functions
`containerRouter` stores the backend and route slice. `NewRouter`, `Routes`, and `initRoutes` create the router and route table.

## Control Flow
`initRoutes` registers HEAD, GET, POST, PUT, and DELETE routes for container archive, list, inspect, logs, stats, attach, exec, create, kill, pause/unpause, restart/start/stop/wait/resize, rename, update, prune, commit, and remove. The prune route has a minimum API version of 1.25.

## State And Persistence
Router state is an in-memory backend reference and route slice.

## Dependencies And Integration Points
Integrates the container HTTP API with route handlers in `container_routes.go` and the daemon backend interface.

## Risks And Edge Cases
Many routes use greedy `{name:.*}` matching to support names with slashes. Route ordering matters because overlapping patterns could otherwise shadow each other.

## Test Signals
API route registration and handler tests validate route methods, paths, and version guards.
