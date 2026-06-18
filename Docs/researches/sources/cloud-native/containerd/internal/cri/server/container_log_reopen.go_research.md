# sources/cloud-native/containerd/internal/cri/server/container_log_reopen.go

## Purpose
This file implements CRI log reopening for running containers, used after external log rotation.

## Important APIs, Types, and Functions
`(*criService).ReopenContainerLog` looks up the container, verifies it is running, calls `createContainerLoggers`, replaces the `"log"` output in container IO, and closes previous stdout/stderr writers.

## Control Flow, State, and Persistence
The method mutates the container’s IO output registry. It does not restart tasks or change container status. If the container is not running, it returns an error before touching log writers.

## Dependencies and Integration Points
It integrates CRI log rotation, container store status, `ContainerIO.AddOutput`, and log file creation logic from `container_start.go`.

## Risks and Test Signals
Risks include closing active writers incorrectly, failing to close old log files, and reopening logs for non-running containers. There are no direct tests in this subset; behavior is tied to `createContainerLoggers` and runtime IO integration.
