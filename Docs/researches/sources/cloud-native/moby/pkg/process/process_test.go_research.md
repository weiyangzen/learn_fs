# sources/cloud-native/moby/pkg/process/process_test.go

Purpose: tests for process liveness behavior.

APIs and flow: `TestAlive` checks invalid PIDs, the current process PID, and a completed child process. The exited-process case is skipped on Windows.

State and dependencies: spawns a short-lived `echo` command and observes its `ProcessState.Pid`; no persistent state.

Integration points: exercises the platform `alive` implementation through the public `Alive` wrapper.

Risks and signals: the invalid-PID cases document the process-group safety boundary. There is no explicit `Kill` or `Zombie` coverage in this file.
