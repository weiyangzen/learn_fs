# sources/cloud-native/moby/integration-cli/docker_cli_attach_unix_test.go

Purpose: adds Unix-only pseudo-terminal coverage for CLI attach lifecycle: attach exits cleanly when a container stops, a container can be reattached after using the detach key sequence, and detach leaves the container running.

Important APIs, types, and functions: `TestAttachClosedOnContainerStop`, `TestAttachAfterDetach`, and `TestAttachDetach`. It uses `github.com/creack/pty.Open`, `exec.Command`, pty stdin/stdout/stderr wiring, detach byte sequence `16` then `17` (`Ctrl-p`, `Ctrl-q`), `cli.DockerCmd`, `cli.WaitRun`, `inspectField`, and `bufio.Reader`.

Control flow: the stop test opens a pty, starts `docker attach`, stops the container from a goroutine, waits for `docker wait`, and asserts the attach command exits without error. The after-detach test starts `docker run -ti`, sends the detach sequence through the pty, waits for the original run command to exit, opens a new pty, attaches again, sends a newline, and checks for a shell prompt. The long-ID detach test attaches to a `cat` container, verifies echoed input, sends the detach sequence, waits for attach to exit, and verifies the container is still running.

State and persistence behavior: state is Unix pty file descriptors, subprocess lifecycle, and container runtime state. No repository or daemon configuration is persisted. Tests explicitly close ptys and kill attach processes where needed.

Dependencies and integration points: build-tagged `!windows` and depends on local daemon behavior for pty attach. It extends the `DockerCLIAttachSuite` defined in `docker_cli_attach_test.go` and uses the same `attachWait` timeout constant.

Risks and edge cases: pty timing is fragile, with short sleeps around detach sequence writes and prompt reads. `TestAttachClosedOnContainerStop` requires a local daemon because remote attach/pty behavior can differ. Prompt assertion depends on BusyBox shell prompt text. Deferred process kill in reattach cleanup may race with normal attach exit but is bounded.

Test signals: confirms attach returns on container stop without surfacing an error, detach sequence exits the client while leaving the container alive, reattach after detach reaches an interactive shell, and detach works with a long container ID in TTY mode.
