# sources/cloud-native/moby/daemon/server/middleware/experimental.go

## Purpose
Adds the `Docker-Experimental` response header to every wrapped API request.

## Important APIs, Types, And Functions
`ExperimentalMiddleware` stores the header value. `NewExperimentalMiddleware` converts a boolean into `"true"` or `"false"`. `WrapHandler` sets the header before calling the next handler.

## Control Flow
The wrapper sets `Docker-Experimental` on the response and delegates to the wrapped API function.

## State And Persistence
No daemon state changes. The middleware writes response headers.

## Dependencies And Integration Points
Installed in the API server middleware chain to advertise daemon experimental mode to clients.

## Risks And Edge Cases
The header is set before downstream handlers, so later middleware/handlers could overwrite it. It reflects the value captured at middleware construction.

## Test Signals
No direct listed tests; API header integration tests should verify the header.
