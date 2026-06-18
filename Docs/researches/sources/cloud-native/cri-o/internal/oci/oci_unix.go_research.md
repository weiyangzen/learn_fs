# sources/cloud-native/cri-o/internal/oci/oci_unix.go

## Purpose
Unix non-Windows helper code for TTY exec handling and process killing.

## Important APIs and Control Flow
`ptyStarter` adapts `pty.Start` to `ExecStarter`. `Kill` sends SIGKILL and ignores ESRCH. `setSize` applies terminal window size with `TIOCSWINSZ`. `ttyCmd` starts an exec command in a PTY through `Container.StartExecCmd`, tracks/deletes the exec PID, closes stdout and PTY, handles resize events, copies stdin/stdout concurrently, and waits for process exit.

## Integration, Risks, and Tests
Used by `runtimeOCI.ExecContainer` when TTY is requested. Risks include goroutine copy races, stdout close expectations, and terminal resize errors being logged only. Stop/exec PID tests indirectly cover the `ExecStarter` tracking pattern; TTY IO itself is not deeply tested here.
