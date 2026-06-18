# sources/cloud-native/moby/daemon/server/router/debug/debug.go

## Purpose
`debug.go` registers daemon debug endpoints for expvar and pprof under the standard router abstraction.

## Important APIs, Types, And Functions
`NewRouter` constructs `debugRouter`, `initRoutes` registers `/debug/vars`, `/debug/pprof/`, specific pprof handlers, and `/debug/pprof/{name}`. `frameworkAdaptHandler` and `frameworkAdaptHandlerFunc` adapt standard `http.Handler` values into `httputils.APIFunc`.

## Control Flow
Route registration is static. Each adapted handler ignores router variables, invokes the standard library handler, and returns nil so server middleware/error conversion does not interfere.

## State And Persistence
No state is persisted. The endpoints expose process-global expvar and pprof state from the daemon process.

## Dependencies And Integration Points
Depends on `expvar`, `net/http/pprof`, `httputils`, and the router package. The server registers this router like any other API router.

## Risks
Debug endpoints expose sensitive runtime/process information and should only be registered in daemon configurations that intend to expose them. Handler adaptation bypasses structured error responses.

## Test Signals
No local tests; behavior is covered by route registration and standard library pprof functionality.
