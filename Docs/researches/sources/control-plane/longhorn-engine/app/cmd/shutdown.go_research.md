# sources/control-plane/longhorn-engine/app/cmd/shutdown.go

## Purpose
Provides global signal-hook registration for graceful shutdown of controller/replica-related command processes.

## Important APIs, Types, and Functions
- Package-level `hooks []func() error`.
- `addShutdown(f)` registers a hook and lazily starts signal handling.
- `registerShutdown()` listens for `SIGINT` and `SIGTERM`, runs all hooks, and exits with status 1 if any hook fails.

## Control Flow
The first call to `addShutdown` starts a goroutine reading from a buffered signal channel. On signal, each registered hook is invoked sequentially with logging around start/failure. The process exits after hooks finish.

## State and Persistence Behavior
Maintains process-global in-memory hook list. Persistence effects depend on registered hooks, notably controller shutdown flushing/closing volume state. No locking protects `hooks`; registrations are expected during startup.

## Dependencies and Integration Points
Uses Go signal APIs, `syscall`, logrus, and function path helper. `controller.go` registers real controller shutdown; `replica.go` registers an empty hook to enable signal logging/exit.

## Risks and Edge Cases
No mutex around hook mutation and iteration. Multiple signals can trigger concurrent hook execution because the loop remains active. `os.Exit` bypasses defers outside hooks.

## Test Signals
Integration tests simulate process cleanup and SIGKILL in `test_engine_restart_after_sigkill`; graceful signal hooks are not directly asserted in this subset.
