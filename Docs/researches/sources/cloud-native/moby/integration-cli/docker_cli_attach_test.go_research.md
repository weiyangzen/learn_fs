# sources/cloud-native/moby/integration-cli/docker_cli_attach_test.go

Purpose: validates cross-platform Docker CLI `attach` behavior for multiple simultaneous attachments, attach failure without a usable TTY stdin, stdin disconnect semantics, and attach rejection for paused containers.

Important APIs, types, and functions: `attachWait`, `DockerCLIAttachSuite`, `TearDownTest`, `OnTimeout`, `TestAttachMultipleAndRestart`, `TestAttachTTYWithoutStdin`, `TestAttachDisconnect`, and `TestAttachPausedContainer`. It uses `exec.Command`, `StdoutPipe`, `StdinPipe`, `bufio.Reader`, `sync.WaitGroup`, `cli.DockerCmd`, `cli.WaitRun`, `inspectField`, `runSleepingContainer`, and `icmd`.

Control flow: the multiple-attach test starts a long-running echo container, launches three `docker attach` subprocesses, waits until each reads `"hello"`, kills the container, and waits for all attach commands to finish. The TTY-without-stdin test starts an interactive container and expects attach to fail with the "input device is not a TTY" message. The disconnect test attaches to `cat`, sends a line, verifies echo, closes stdin, and confirms the container remains running. The paused test pauses a container and asserts `docker attach` exits with code 1 and the expected error.

State and persistence behavior: state is transient process/container lifecycle and attached stdio streams. No files are persisted. Goroutine and process cleanup is handled with `Wait`, `Kill`, deferred pipe closes, and suite teardown.

Dependencies and integration points: integrates CLI wrappers with direct `os/exec` process handling, the configured `dockerBinary`, daemon feature gates (`DaemonIsLinux`, `IsPausable`), and test result helpers from `gotest.tools/icmd`. The suite wrapper delegates shared cleanup to `DockerSuite`.

Risks and edge cases: attach subprocesses and pipe reads are timing-sensitive and bounded by `attachWait`. Some behavior is Linux-gated due to known Windows TTY instability. The multiple-attach goroutines report errors with `c.Error` from background goroutines, which can make failure ordering less direct. `TestAttachDisconnect` kills the attach command process in cleanup even after stdin close.

Test signals: confirms multiple clients can attach and all detach/exit when the container is killed, TTY attach fails fast without a terminal stdin, closing an attached stdin does not stop a detached interactive container, and paused containers reject attach with a specific error.
