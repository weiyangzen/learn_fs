# sources/cloud-native/moby/daemon/server/router/debug/debug_routes.go

## Purpose
`debug_routes.go` contains the variable pprof profile route handler.

## Important APIs, Types, And Functions
`handlePprof` reads `vars["name"]`, obtains `pprof.Handler(name)`, and serves it through the current response/request.

## Control Flow
The server mux captures the `{name}` path segment and passes it to this handler. The standard pprof handler performs the actual profile lookup and response.

## State And Persistence
No state is changed; the handler reads runtime profiling state from the Go process.

## Dependencies And Integration Points
It integrates gorilla/mux route variables with `net/http/pprof`.

## Risks
Unknown profile names and handler-specific query parameters are delegated to the standard library. Access control must be handled outside this file.

## Test Signals
No direct tests.
