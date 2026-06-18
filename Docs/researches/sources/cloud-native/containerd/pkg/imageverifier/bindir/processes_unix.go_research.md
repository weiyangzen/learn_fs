# sources/cloud-native/containerd/pkg/imageverifier/bindir/processes_unix.go

Purpose: Unix process-management shim for verifier binaries. It starts each verifier in a separate process group so context cancellation kills both the verifier and any subprocesses it created.

Important APIs/types/functions: `process` wraps `*exec.Cmd`; `startProcess(ctx, cmd)` sets `cmd.SysProcAttr = &unix.SysProcAttr{Setpgid: true}`, installs `cmd.Cancel` to send `SIGKILL` to `-cmd.Process.Pid`, starts the command, and returns the wrapper; `(*process).cleanup` is a no-op on Unix.

Control flow: before `cmd.Start`, the command is configured to become process-group leader. When `exec.CommandContext` observes context cancellation, Go calls `cmd.Cancel`, which targets the whole process group rather than only the immediate child.

State/persistence: no persistent state. Runtime state is only the OS process group and the process handle owned by `exec.Cmd`.

Dependencies/integration: used by `bindir.runVerifier` after pipes and context deadlines are configured. Depends on `golang.org/x/sys/unix` for `SysProcAttr` and `Kill`.

Risks: process-group kill assumes `cmd.Process` is initialized when `Cancel` runs. A verifier that changes process groups can escape cleanup. Sending `SIGKILL` prevents graceful teardown but is intentional for bounded verifier timeouts.

Test signals: exercised by `slow_child_process.go` through `bindir_test.go`, which verifies verifier timeouts do not leave a long-running child process alive.
