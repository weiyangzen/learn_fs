# sources/cloud-native/moby/pkg/process/process.go

Purpose: platform-neutral validation layer for process liveness and force-kill helpers.

APIs and flow: `Alive(pid int)` rejects pid values below 1 to avoid process-group semantics, then dispatches to platform `alive`. `Kill(pid int)` applies the same positive-PID guard and dispatches to platform `kill`.

State and dependencies: no persistent state; only formats validation errors with stdlib `fmt`.

Integration points: platform files provide Unix, Windows, Linux-zombie, and non-Linux zombie behavior.

Risks and tests: the PID guard is important because `kill(0)`, `kill(-1)`, and negative process-group IDs can affect many processes. Tests cover invalid PID liveness and current/exited process checks.
