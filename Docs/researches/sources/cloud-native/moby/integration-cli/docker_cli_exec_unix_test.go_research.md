# sources/cloud-native/moby/integration-cli/docker_cli_exec_unix_test.go

Purpose: Unix-specific TTY and pty coverage for `docker exec`, including stdin close behavior and TERM environment behavior.

Important APIs/types/functions: `TestExecInteractiveStdinClose`, `TestExecTTY`, `TestExecWithTERM`, and `TestExecWithNoTERM`. The file uses `github.com/creack/pty` to execute CLI commands under a pseudo-terminal.

Control flow: tests start Linux busybox containers, run `docker exec` under pty, write commands through the pty, wait with explicit timeouts, and read buffered output. TERM tests execute shell checks that pass or fail based on whether `$TERM` is populated with `-t`.

State and persistence: only temporary running containers and exec sessions are created. No durable state is expected beyond normal test cleanup.

Dependencies and integration points: non-Windows build tag, Linux daemon, local daemon for TTY tests, pty support, busybox shell, and Docker CLI `exec -i`, `exec -it`, and `exec -t`.

Risks: pty reads can include NUL bytes or terminal echo, so output is trimmed where needed. Tests are time-sensitive and can fail if exec startup or pty flushing is slow. TERM behavior depends on CLI/daemon TTY negotiation.

Test signals: failures indicate regressions in pty-backed exec completion, TTY stdin/exit handling, or incorrect TERM injection for TTY vs non-TTY exec sessions.
