# sources/cloud-native/moby/daemon/server/router/volume/volume.go

## Purpose
`volume.go` defines the volume router and registers volume API endpoints.

## Important APIs, Types, And Functions
`volumeRouter` stores local and cluster backends plus routes. `NewRouter`, `Routes`, and `initRoutes` implement setup.

## Control Flow
Routes include list, inspect, create, prune, update, and delete. Prune requires API 1.25+, update requires API 1.42+.

## State And Persistence
Only backend references and route metadata are stored.

## Dependencies And Integration Points
Uses the shared router package and version wrappers.

## Risks
The wildcard `{name:.*}` can capture names with slashes but also requires careful route ordering for future additions.

## Test Signals
`volume_routes_test.go` exercises the handlers registered here.
