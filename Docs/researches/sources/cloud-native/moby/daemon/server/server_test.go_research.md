# sources/cloud-native/moby/daemon/server/server_test.go

## Purpose
`server_test.go` verifies global middleware wrapping for route handlers.

## Important APIs, Types, And Functions
`TestMiddlewares` constructs a `Server`, installs version middleware, invokes `handlerWithGlobalMiddlewares`, and checks API version context plus `Server` response header.

## Control Flow
The test builds a GET request, recorder, and local handler that asserts middleware side effects. The wrapped handler is called directly rather than through mux registration.

## State And Persistence
No persistent state is changed.

## Dependencies And Integration Points
Depends on daemon config API version constants, `httputils.VersionFromContext`, and server middleware construction.

## Risks
It covers middleware application but not route registration, error conversion, or OpenTelemetry wrapper behavior.

## Test Signals
Confirms middleware adds API version context and Docker server version header before route handler execution.
