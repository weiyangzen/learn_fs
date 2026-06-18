# sources/cloud-native/moby/daemon/server/router/session/session_routes.go

## Purpose
`session_routes.go` implements POST `/session`.

## Important APIs, Types, And Functions
`startSession` calls `sr.backend.HandleHTTPRequest` and wraps any error as `errdefs.InvalidParameter`.

## Control Flow
The handler performs no parsing itself; all protocol handling is delegated. Backend errors are reclassified as invalid parameters for the HTTP API.

## State And Persistence
State is owned by the backend session implementation.

## Dependencies And Integration Points
Depends on `errdefs` for API error classification and the session backend.

## Risks
Blanket invalid-parameter wrapping can hide backend error specificity. If the backend writes before returning an error, normal error response writing may not be useful.

## Test Signals
No direct unit tests.
