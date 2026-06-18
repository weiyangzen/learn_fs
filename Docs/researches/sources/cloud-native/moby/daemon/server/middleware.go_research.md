# sources/cloud-native/moby/daemon/server/middleware.go

## Purpose
Applies global server middlewares around API handlers and conditionally adds debug request logging when the daemon log level is debug or lower.

## Important APIs, Types, And Functions
`(*Server).handlerWithGlobalMiddlewares(handler httputils.APIFunc) httputils.APIFunc` wraps the handler using `s.middlewares` and `middleware.DebugRequestMiddleware`.

## Control Flow
Starting from the route handler, the function iterates configured middlewares in slice order and replaces `next` with each wrapper. If logging is at debug level, it wraps the result in debug middleware. Comments note that middleware evaluation order is backwards: the first in the list is evaluated last.

## State And Persistence
No persistent state is changed. The returned function closes over the middleware chain.

## Dependencies And Integration Points
Used by the API server route setup. Depends on containerd log level, HTTP utility handler signature, and middleware package.

## Risks And Edge Cases
Middleware order is subtle and can affect headers, version validation, experimental flags, and debug logging. Debug middleware adds body peeking overhead for small JSON POST requests.

## Test Signals
Middleware-specific tests cover debug masking and version behavior; route integration tests validate combined behavior.
