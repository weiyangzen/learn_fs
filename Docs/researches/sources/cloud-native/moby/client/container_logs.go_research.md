<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_logs.go -->
# sources/cloud-native/moby/client/container_logs.go

Purpose: retrieves container logs as a stream with stdout/stderr, time range, follow, tail, timestamps, and details options.

Important APIs/types/functions: `ContainerLogsOptions`, `ContainerLogsResult` interface, `Client.ContainerLogs`, and private `containerLogsResult`.

Control flow: validates container id, maps booleans to `1` query values, parses `Since` and `Until` through the internal timestamp helper, suppresses `tail` for empty or `all`, GETs `/containers/{id}/logs`, and returns a context-cancel-aware read closer. The caller owns closing the stream.

State and integration behavior: read-only daemon stream; no local persistence. Stream format depends on container TTY state and may be raw or stdcopy-multiplexed.

Dependencies: `client/internal/timestamp`, shared `get`, `newCancelReadCloser`, and `io.ReadCloser`.

Risks and test signals: risks include invalid timestamp error wrapping, stream leaks, incorrect default tail handling, and caller demultiplexing assumptions. `container_logs_test.go` and example tests cover errors, invalid ids, timestamp parsing, query cases, stream reading, and close behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_logs.go -->
