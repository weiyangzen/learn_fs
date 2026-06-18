# sources/cloud-native/moby/daemon/server/router/image/image.go

## Purpose
`image.go` defines the image router and registers all image HTTP API routes.

## Important APIs, Types, And Functions
`imageRouter` stores a `Backend`, `Searcher`, and route list. `NewRouter`, `Routes`, and `initRoutes` implement the common router pattern.

## Control Flow
`initRoutes` registers list, search, export, history, inspect, attestations, load, create/pull/import, push, tag, prune, and delete endpoints. Attestations require API 1.55 and prune requires API 1.25.

## State And Persistence
The router stores only backend references and route metadata. Image state changes happen in backend handlers.

## Dependencies And Integration Points
Integrates image handlers with the shared router package and API-version wrappers.

## Risks
The wildcard `{name:.*}` matcher is required for repository references with slashes. Route ordering must avoid conflicts among `/images/{name}/...`, `/images/json`, and `/images/search`.

## Test Signals
No direct tests; route behavior is covered through image API tests.
