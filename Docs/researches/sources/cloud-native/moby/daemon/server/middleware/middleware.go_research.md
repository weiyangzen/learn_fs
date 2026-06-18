# sources/cloud-native/moby/daemon/server/middleware/middleware.go

## Purpose
Defines the common API middleware interface used by the daemon server.

## Important APIs, Types, And Functions
`Middleware` requires `WrapHandler(func(ctx, w, r, vars) error) func(ctx, w, r, vars) error`.

## Control Flow
Interface definition only.

## State And Persistence
No state.

## Dependencies And Integration Points
Implemented by experimental and version middlewares and consumed by server route setup.

## Risks And Edge Cases
All middleware must preserve the API handler signature and error propagation behavior.

## Test Signals
Compile-time checks through middleware implementations and server setup.
