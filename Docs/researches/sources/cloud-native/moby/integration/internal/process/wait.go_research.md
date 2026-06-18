# sources/cloud-native/moby/integration/internal/process/wait.go

Purpose: polling predicate for waiting until an OS process is no longer alive.

Important APIs and helpers: `NotAlive(pid int)` returns a gotest poll check that uses `system.IsProcessAlive`.

Control flow: each poll call checks the PID. If alive, it continues; if not alive, it succeeds.

State and persistence: reads host process state only. It does not signal or reap processes.

Dependencies and integration: depends on Moby internal system process helper and gotest poll.

Risks: PID reuse can theoretically produce false continues if another process reuses the PID before the check. The helper assumes `IsProcessAlive` captures platform-specific process existence correctly.

Test signals: helper-only; supports live-restore tests waiting for container processes to exit while the daemon is stopped.
