# sources/cloud-native/containerd/integration/container_stop_signal_test.go

## Purpose

This Linux-focused test validates CRI custom stop signal support and default stop signal reporting. It ensures configured stop signals are persisted in container status and are actually used when stopping a container.

## Important APIs, Types, And Functions

- `TestContainerStopSignals` table-tests SIGUSR1, SIGUSR2, SIGHUP, SIGINT, and SIGTERM.
- `TestDefaultContainerStopSignal` checks that containers without custom configuration report `SIGTERM`.
- `writeStopSignalScript` creates a trap script mounted into the container.
- `WithStopSignal`, `WithVolumeMount`, and `WithLogPath` build the test container config.

## Control Flow

The custom-signal test skips Windows, creates a sandbox with host networking and a temporary log directory, writes a shell script that traps a named signal, mounts it, starts the container, checks `ContainerStatus.StopSignal`, stops the container, and verifies exit code zero plus a log line saying the signal was received. The default test starts a sleeping container without `StopSignal`, checks status reports `SIGTERM`, stops it, and checks it exits.

## State And Persistence Behavior

The configured stop signal is stored in container CRI metadata/status. The proof of signal delivery is persisted only in the temporary CRI log file.

## Dependencies And Integration Points

It depends on CRI `StopContainer`, container status stop signal fields, BusyBox shell trap behavior, volume mounts, and CRI log formatting through `checkContainerLog`.

## Risks And Edge Cases

Shell trap names must match BusyBox `sh` behavior. The test assumes the child sleep process is cleaned up by the trap. SELinux or mount restrictions could prevent the generated script from being executable, although it is written with mode `0644` and invoked as `sh /path`.

## Test Signals

Passing confirms both API-level stop-signal reporting and runtime signal delivery behavior.
