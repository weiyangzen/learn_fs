# sources/cloud-native/moby/integration-cli/docker_api_logs_test.go

Purpose: exercises the Engine API `/containers/{id}/logs` behavior through both raw HTTP requests and the Go client. The file focuses on stdout/stderr option validation, follow behavior, timestamped output, not-found handling, and `until` filtering.

Important APIs, types, and functions: `TestLogsAPIWithStdout`, `TestLogsAPINoStdoutNorStderr`, `TestLogsAPIFollowEmptyOutput`, `TestLogsAPIContainerNotFound`, `TestLogsAPIUntilFutureFollow`, `TestLogsAPIUntil`, and `TestLogsAPIUntilDefaultValue`. It uses `client.ContainerLogsOptions`, `client.ContainerLogs`, `request.Get`, `stdcopy.StdCopy`, `daemonTime`, and integration helpers from `cli` and `testutil`.

Control flow: tests create BusyBox containers with deterministic log-producing commands, wait for container state where needed, then stream or decode log responses. `TestLogsAPIWithStdout` reads the first followed line on a goroutine and bounds it with a 30-second timeout. The `until` tests first collect timestamped logs, derive a cutoff from daemon time or an observed log timestamp, and assert later messages are excluded while `"0"` preserves default behavior.

State and persistence behavior: no repository persistence is changed. Runtime state is Docker daemon container state plus container log buffers. Follow tests deliberately hold HTTP response bodies/readers open and close them in goroutines; `UntilFutureFollow` synchronizes through `chLog` and `stop`.

Dependencies and integration points: depends on the integration daemon, BusyBox image, Docker CLI helpers, raw test HTTP request helpers, Moby client API types, `stdcopy` multiplex decoding, and `containerd/errdefs` for invalid-argument matching. Linux-only gating is used for daemon-time-sensitive follow/until behavior.

Risks and edge cases: timing-heavy tests can be sensitive to slow daemons, log driver delays, or clock skew between test process and daemon. `TestLogsAPIUntil` assumes at least three split log lines and timestamp format stability. The follow-empty-output regression checks response immediacy but does not inspect response status before closing the body.

Test signals: validates successful followed stdout streaming with timestamps, invalid requests with neither stdout nor stderr, immediate follow response for quiet containers, 404 for missing containers, bounded log streaming until future daemon time, exclusion of later logs by timestamp cutoff, and preservation of all logs when `Until` is the default `"0"`.
