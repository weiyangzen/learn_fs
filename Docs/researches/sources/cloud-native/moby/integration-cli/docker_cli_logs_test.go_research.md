# sources/cloud-native/moby/integration-cli/docker_cli_logs_test.go

Purpose: tests `docker logs` output correctness, pagination boundaries, stdout/stderr routing, timestamps, tail/since/follow behavior, details fields, missing containers, and daemon goroutine cleanup.

Important APIs and functions: `DockerCLILogsSuite`, `testLogsContainerPagination`, `ConsumeWithSpeed`, `exec.Command`, `io.Pipe`, local daemon creation via `daemon.New`, `waitForStableGoroutineCount`, `waitForGoroutines`, and `icmd`.

Control flow: pagination tests generate exact byte counts around page-size boundaries. Timestamp tests parse RFC3339Nano with fixed padding. Tail and since tests create known log streams and filter them. Follow tests start `docker logs -f`, wait or kill the client, and assert clean process exit. Goroutine tests use a separate daemon and compare daemon goroutine counts before and after killed follow clients with and without output.

State and persistence: creates containers whose log files persist after exit, exercises log-driver detail metadata from labels/env, and starts temporary daemons with disabled iptables for leak checks.

Dependencies and integration points: busybox shell output, json-file logging behavior, `containerd/log` timestamp format, process pipes, daemon API goroutine metrics, and Linux/local daemon constraints for leak tests.

Risks: timing-sensitive follow and since tests can be flaky; goroutine counts require stabilization; slow-consumer behavior depends on pipe buffering; Windows tty/stderr behavior differs and is gated.

Test signals: logs return exact byte counts, stream separation is correct, `--tail`, `--since`, `--timestamps`, `--details`, and `--follow` behave correctly, and killed log followers do not leak daemon goroutines.
