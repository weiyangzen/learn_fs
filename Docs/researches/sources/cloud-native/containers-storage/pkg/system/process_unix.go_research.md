# sources/cloud-native/containers-storage/pkg/system/process_unix.go

Purpose: Unix process liveness and forced termination helpers.

Important APIs/types/functions: `IsProcessAlive(pid int) bool` and `KillProcess(pid int)`.

Control flow: liveness calls `unix.Kill(pid, 0)` and treats nil and `EPERM` as alive. Killing sends `SIGKILL` and ignores the result.

State/persistence: affects live process state when `KillProcess` succeeds; no stored metadata.

Dependencies/integration: selected for Linux, FreeBSD, Solaris, and Darwin; used by cleanup or process-management paths that need coarse liveness checks.

Risks: PID reuse can make liveness checks stale immediately. Ignoring kill errors hides permission, non-existent PID, and race failures.

Test signals: tests should cover current process liveness, missing PID false results, and permission behavior where feasible.
