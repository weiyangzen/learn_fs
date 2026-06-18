<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_unix.go -->
# sources/cloud-native/containerd/pkg/shim/shim_unix.go

## Purpose
Unix signal, listener, reaping, logging, and pipe readiness helpers for shim server.

## Important APIs, Types, And Functions
setupSignals, setupDumpStacks, serveListener, reap, handleExitSignals, openLog, and awaitPipeReady implement Unix behavior.

## Control Flow
Signals are registered for TERM/INT/PIPE and optionally CHLD. serveListener uses inherited fd 3 or an explicit Unix socket path. reap consumes SIGCHLD and calls reaper.Reap. openLog opens the log FIFO on stderr fd.

## State And Persistence
Registers process signal handlers and opens listeners/FIFOs; no durable state by itself.

## Dependencies And Integration Points
Integrates pkg/sys/reaper, containerd/fifo, x/sys/unix, and shared shim server logic.

## Risks And Edge Cases
Unix socket path limit is enforced only for explicit paths. Signal channels are shared with exit handling, so short actions intentionally ignore exit signals in reap.

## Test Signals
Socket behavior covered by util_unix_test and abstract socket tests; reaping covered by reaper package.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_unix.go -->
