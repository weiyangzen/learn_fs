# sources/cloud-native/containerd/internal/cri/server/container_start_other.go

## Purpose
This non-Linux start helper provides a no-op `updateContainerIOOwner` implementation for platforms where Linux user namespace fifo ownership does not apply.

## Important APIs, Types, and Functions
`updateContainerIOOwner` accepts the same context, containerd container, and CRI container config as the Linux version and returns nil task options and nil error.

## Control Flow, State, and Persistence
No state is read or mutated. The helper exists for build compatibility and platform separation.

## Dependencies and Integration Points
It depends only on containerd task option and CRI config types. It integrates with `StartContainer`, which appends the returned options before creating a task.

## Risks and Test Signals
The risk is platform-specific IO ownership requirements emerging without implementation here. There are no direct tests; compilation and start path integration provide the main signal.
