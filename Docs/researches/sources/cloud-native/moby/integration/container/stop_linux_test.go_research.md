# sources/cloud-native/moby/integration/container/stop_linux_test.go

Purpose: Linux-specific stop cancellation behavior test plus log polling helper.

Important APIs and flow: `TestStopContainerWithTimeoutCancel` runs a container trapping TERM and looping, starts `ContainerStop` with a cancellable context and timeout, waits until logs contain `received TERM`, cancels the client context, expects the request to return a canceled error while the container remains running, then waits for daemon-side stop timeout to stop it. `logsContains` reads `ContainerLogs`, demultiplexes stdout with `stdcopy.StdCopy`, and polls for the marker string.

State and dependencies: Uses signal traps, container logs, goroutines, context cancellation, and daemon stop timers. It is time-sensitive but local to one container.

Risks and signals: It guards the contract that canceling the HTTP request does not cancel the daemon's already-started stop operation. Failures can leave containers killed too early or never stopped after client disconnect.
