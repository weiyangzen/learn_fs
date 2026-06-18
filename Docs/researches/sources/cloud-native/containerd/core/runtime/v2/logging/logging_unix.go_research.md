# sources/cloud-native/containerd/core/runtime/v2/logging/logging_unix.go

## Purpose
Implements `logging.Run` for Unix platforms. It exposes inherited file descriptors and environment variables to a custom logging function and coordinates readiness through a wait pipe.

## APIs, Flow, State, Dependencies, Risks, And Tests
`Run(fn LoggerFunc)` builds a context, reads `CONTAINER_ID` and `CONTAINER_NAMESPACE`, wraps file descriptors 3 and 4 as stdout/stderr readers, and fd 5 as the wait pipe. It installs `SIGTERM` handling, runs the logger function in a goroutine, and exits with status 1 if the function returns an error or 0 on success. The `ready` closure writes one byte to the wait pipe then closes it.

State consists of inherited file descriptors and signal/context lifetime. No disk persistence occurs. Dependencies include `os`, `os/signal`, Unix signals, and the common logging contract.

Integration is with shim-launched logging binaries that receive container IO as fds. Risks include missing or invalid fds, logger goroutine blocking, repeated `ready` calls, and startup deadlock if `ready` is never called. Test signals should simulate fds/pipes, verify wait-byte behavior, and confirm signal cancellation and exit code paths.
