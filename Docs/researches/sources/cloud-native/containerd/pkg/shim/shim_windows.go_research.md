<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_windows.go -->
# sources/cloud-native/containerd/pkg/shim/shim_windows.go

## Purpose
Windows stubs and named-pipe readiness logic for shim server support.

## Important APIs, Types, And Functions
Most server/signal/log/subreaper helpers return ErrNotImplemented; awaitPipeReady polls winio.DialPipe for up to five seconds.

## Control Flow
The start helper calls awaitPipeReady after manager.Start returns an address so the parent does not consume the bootstrap result before the named pipe is connectable.

## State And Persistence
No persistent state; only timed polling.

## Dependencies And Integration Points
Depends on go-winio, errdefs, ttrpc types, and shared shim run path.

## Risks And Edge Cases
Long-running Windows serving is not implemented in these helpers, but readiness polling must tolerate pipe-not-found and deadline/busy states without blocking containerd indefinitely.

## Test Signals
No direct tests in subset; behavior is platform integration-driven.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_windows.go -->
