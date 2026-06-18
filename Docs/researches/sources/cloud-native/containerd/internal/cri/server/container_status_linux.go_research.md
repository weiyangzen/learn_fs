# sources/cloud-native/containerd/internal/cri/server/container_status_linux.go

## Purpose
This Linux-specific status helper extracts the runtime user from a container’s OCI spec and converts it into CRI `LinuxContainerUser`.

## Important APIs, Types, and Functions
`toCRIContainerUser` checks the embedded containerd container, loads `Container.Spec(ctx)`, reads `spec.Process.User`, and returns UID, GID, and supplemental groups.

## Control Flow, State, and Persistence
No state is mutated. If the container handle is nil or spec loading fails, an error is returned to the caller; `toCRIContainerStatus` logs and falls back to an empty user when this happens. If `Process` is nil, the helper returns an empty `ContainerUser`.

## Dependencies and Integration Points
It depends on containerd container spec retrieval, runtime-spec process user fields, and CRI Linux user fields. It is called during `ContainerStatus`.

## Risks and Test Signals
Risks include failure to report the actual runtime user, incorrect supplemental group type conversion, and noisy status failures. `container_status_linux_test.go` covers nil container, spec error, missing process, and additional GID conversion.
