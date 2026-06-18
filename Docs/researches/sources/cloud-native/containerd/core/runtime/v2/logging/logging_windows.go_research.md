# sources/cloud-native/containerd/core/runtime/v2/logging/logging_windows.go

## Purpose
Implements `logging.Run` for Windows logging binaries using named pipe paths supplied in environment variables.

## APIs, Flow, State, Dependencies, Risks, And Tests
`Run` delegates to `runInternal`, prints any returned error to stderr, and exits nonzero. `runInternal` requires `CONTAINER_STDOUT` and `CONTAINER_STDERR`, dials them with go-winio, dials `CONTAINER_WAIT`, builds `Config`, watches interrupt/SIGTERM, and invokes the logger function. `ready` writes a byte to the wait pipe then closes it.

State is the named pipe connections and signal-driven context. There is no disk persistence. Dependencies include `github.com/Microsoft/go-winio`, `net`, `os/signal`, and Windows syscall signals.

Integration mirrors Unix logging but the shim passes pipe names instead of inherited fds. Risks include missing env vars, pipe dial timeouts/failures, leaked connections if logger exits before readiness, and named-pipe behavior differences in multi-container shims. Test signals are unit tests for missing env var errors, fake pipe readiness, signal cancellation, and error propagation from `LoggerFunc`.
