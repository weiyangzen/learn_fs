# sources/cloud-native/moby/daemon/server/router/local.go

## Purpose
`local.go` implements the concrete route type and constructors used by all daemon HTTP routers.

## Important APIs, Types, And Functions
`RouteWrapper` decorates routes. `localRoute` implements `Route` with method/path/handler. Constructors include `NewRoute`, method-specific helpers (`NewGetRoute`, `NewPostRoute`, `NewPutRoute`, `NewDeleteRoute`, `NewOptionsRoute`, `NewHeadRoute`), and `WithMinimumAPIVersion`. `versionError` marks invalid parameters.

## Control Flow
Constructors create a `localRoute`, then apply wrappers in order. `WithMinimumAPIVersion` returns a route whose handler checks `httputils.VersionFromContext(ctx)` and rejects versions lower than the minimum before invoking the original handler.

## State And Persistence
Routes are immutable values except where wrappers provide mutable implementations such as experimental routes. No persistent state is written.

## Dependencies And Integration Points
Used by every router in the daemon server. Integrates version comparison helpers, `httputils.APIFunc`, and HTTP method constants.

## Risks
Minimum-version failures intentionally return invalid-parameter style errors rather than 404 to avoid conflicting with endpoint business semantics. Wrapper order matters when combining experimental/version wrappers.

## Test Signals
Route behavior is indirectly covered by server route registration and API-version integration tests.
