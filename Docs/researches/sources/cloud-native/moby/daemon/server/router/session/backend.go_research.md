# sources/cloud-native/moby/daemon/server/router/session/backend.go

## Purpose
`backend.go` defines the session router's backend contract.

## Important APIs, Types, And Functions
`Backend` exposes `HandleHTTPRequest(ctx context.Context, w http.ResponseWriter, r *http.Request) error`.

## Control Flow
The session route delegates the entire request/response handling to the backend, which owns upgrade/session protocol details.

## State And Persistence
The interface itself has no state. Backend implementations manage build/session connection state.

## Dependencies And Integration Points
Depends on standard HTTP and context packages. Used by the deprecated `/session` router.

## Risks
Because the backend writes directly to the response, normal router error behavior may be limited after output starts.

## Test Signals
Session/build integration tests validate backend behavior.
