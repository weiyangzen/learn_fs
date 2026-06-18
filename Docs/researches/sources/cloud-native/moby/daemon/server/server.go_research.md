# sources/cloud-native/moby/daemon/server/server.go

## Purpose
`server.go` contains the Docker API server route registration and HTTP handler wrapper logic.

## Important APIs, Types, And Functions
`Server` stores middleware. `UseMiddleware` appends middleware. `makeHTTPHandler` wraps a route with OpenTelemetry, baggage/user-agent context, global middleware, route variables, and error conversion. `CreateMux` registers versioned and unversioned routes and not-found handlers. Constants include `versionMatcher` and `statusClientClosedRequest`.

## Control Flow
For each request, `makeHTTPHandler` builds context baggage, applies global middleware, gets mux variables, calls the route handler, and converts errors to JSON or plain text for very old API versions. If the request context is canceled, it writes/logs status 499 for telemetry. `CreateMux` registers every route at `/v{version}` and bare paths, then configures not-found/method-not-allowed responses.

## State And Persistence
The server stores middleware only. No durable daemon state is changed by this file.

## Dependencies And Integration Points
Integrates gorilla/mux, route interfaces, middleware, HTTP status mapping, OpenTelemetry HTTP instrumentation, daemon version/user-agent baggage, logging, and API error response types.

## Risks
Error handling after client cancellation must avoid writing JSON to closed clients. Route registration creates both versioned/unversioned paths, so duplicate/conflicting paths matter. Old API plain-text errors are a compatibility exception.

## Test Signals
`server_test.go` verifies middleware application and version/server header propagation.
