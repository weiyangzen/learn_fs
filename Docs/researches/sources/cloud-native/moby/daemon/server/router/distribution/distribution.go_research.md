# sources/cloud-native/moby/daemon/server/router/distribution/distribution.go

## Purpose
`distribution.go` defines the distribution router object and registers the image-distribution inspection endpoint.

## Important APIs, Types, And Functions
`distributionRouter` stores `backend` and `routes`. `NewRouter`, `Routes`, and `initRoutes` implement the common router pattern.

## Control Flow
`initRoutes` installs `GET /distribution/{name:.*}/json` with minimum API version 1.30. The route is later registered both versioned and unversioned by the server.

## State And Persistence
No persistent state is managed; the router stores route metadata and a backend reference.

## Dependencies And Integration Points
Integrates the distribution route handler with the shared `router` package and `WithMinimumAPIVersion`.

## Risks
The `{name:.*}` matcher intentionally captures slashes for registry/image names. Changing it would break image references.

## Test Signals
No direct tests; route availability is covered by API integration behavior.
