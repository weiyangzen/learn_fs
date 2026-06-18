# sources/cloud-native/moby/daemon/server/router/session/session.go

## Purpose
`session.go` defines the deprecated `/session` router for BuildKit/session style HTTP requests.

## Important APIs, Types, And Functions
`sessionRouter` stores a backend and routes. `NewRouter`, `Routes`, and `initRoutes` implement route setup for POST `/session`.

## Control Flow
Construction stores the backend and registers a single route handled by `startSession`.

## State And Persistence
Only route metadata and the backend pointer are stored.

## Dependencies And Integration Points
Uses the shared router package. Comments note deprecation because the engine now supports HTTP/2 and h2c directly.

## Risks
Deprecated endpoint behavior must remain stable until removal for old clients.

## Test Signals
Integration tests for legacy session clients are the primary signal.
