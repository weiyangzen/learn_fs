# sources/cloud-native/moby/daemon/server/router/checkpoint/checkpoint.go

## Purpose
Registers experimental checkpoint API routes.

## Important APIs, Types, And Functions
`checkpointRouter` stores a `Backend` and route slice. `NewRouter`, `Routes`, and `initRoutes` construct and expose the route table.

## Control Flow
`NewRouter` creates the router and initializes routes. `initRoutes` registers GET and POST `/containers/{name:.*}/checkpoints` plus DELETE `/containers/{name}/checkpoints/{checkpoint}`, all marked experimental.

## State And Persistence
Router state is an in-memory backend pointer and route list.

## Dependencies And Integration Points
Integrates with daemon server router abstractions and checkpoint route handlers in `checkpoint_routes.go`.

## Risks And Edge Cases
The GET/POST route allows greedy container names, while DELETE uses a non-greedy `{name}` pattern, which may affect names containing slashes.

## Test Signals
Route registration is usually covered by API router integration tests.
