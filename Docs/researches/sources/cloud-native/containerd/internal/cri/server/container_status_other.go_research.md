# sources/cloud-native/containerd/internal/cri/server/container_status_other.go

## Purpose
This non-Linux/non-Windows helper returns an empty CRI container user for platforms without a platform-specific user mapping implementation.

## Important APIs, Types, and Functions
`toCRIContainerUser` accepts context and container metadata but returns `&runtime.ContainerUser{}` and nil error.

## Control Flow, State, and Persistence
There is no side effect or spec lookup. The function is a build-tagged compatibility implementation.

## Dependencies and Integration Points
It integrates with `toCRIContainerStatus`, ensuring status construction can compile and return a user field on other platforms.

## Risks and Test Signals
The risk is loss of user reporting on platforms where it could become meaningful. There are no direct tests in this subset; behavior is intentionally minimal.
