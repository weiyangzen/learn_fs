<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shutdown/shutdown.go -->
# sources/cloud-native/containerd/pkg/shutdown/shutdown.go

## Purpose
Context-like shutdown service with asynchronous callbacks and error propagation.

## Important APIs, Types, And Functions
Service interface, ErrShutdown, WithShutdown, shutdownService.Shutdown, Done, Err, and RegisterCallback are exported or central.

## Control Flow
WithShutdown returns a context backed by shutdownService. Shutdown marks one-time state, runs callbacks concurrently under a 30-second timeout via errgroup, stores first error or ErrShutdown, and closes doneC.

## State And Persistence
Keeps callback list, shutdown flag, terminal error, and done channel in memory under a mutex. No persistence.

## Dependencies And Integration Points
Used by shim server plugins to coordinate graceful shutdown and plugin callbacks.

## Risks And Edge Cases
Parent context cancellation does not cancel the shutdown context by design. RegisterCallback after Shutdown appends but will not run in the current implementation. Err returns nil until callbacks finish.

## Test Signals
No direct tests in subset; shim run path relies on Done/Err semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shutdown/shutdown.go -->
