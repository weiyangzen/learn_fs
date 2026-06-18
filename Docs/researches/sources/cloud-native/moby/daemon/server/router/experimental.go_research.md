# sources/cloud-native/moby/daemon/server/router/experimental.go

## Purpose
`experimental.go` wraps routes so they can be disabled unless the daemon is running with experimental features enabled.

## Important APIs, Types, And Functions
`ExperimentalRoute` extends `Route` with `Enable` and `Disable`. `experimentalRoute` stores the wrapped local route and the currently active handler. `Experimental` builds a disabled wrapper. `notImplementedError` marks disabled access as not implemented.

## Control Flow
When disabled, `Handler` returns `experimentalHandler`, which returns `notImplementedError`. `Enable` swaps the handler to the original route handler; `Disable` restores the disabled handler. Method and path always pass through to the wrapped route.

## State And Persistence
The wrapper stores mutable in-memory handler state. No persistent daemon state is written.

## Dependencies And Integration Points
It integrates with the shared router interfaces and daemon feature toggling code that can discover `ExperimentalRoute` values and call `Enable` or `Disable`.

## Risks
Because enablement mutates handler pointers, route setup must happen before concurrent request serving or use external synchronization. Error classification relies on the `NotImplemented` marker method.

## Test Signals
No direct tests; behavior is validated by routes that are registered as experimental and by HTTP error classification.
