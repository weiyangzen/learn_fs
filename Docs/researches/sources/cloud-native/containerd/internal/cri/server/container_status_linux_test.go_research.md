# sources/cloud-native/containerd/internal/cri/server/container_status_linux_test.go

## Purpose
This Linux-only test file validates `toCRIContainerUser`.

## Important APIs, Types, and Functions
`TestToCRIContainerUser` uses `fakeSpecOnlyContainer` from `container_status_test.go` and container store wrappers to check user extraction paths.

## Control Flow, State, and Persistence
The table covers nil embedded container, spec retrieval error, no `Process`, no additional groups, and additional groups. All data is in-memory OCI spec data.

## Dependencies and Integration Points
It depends on containerd container interface fakes, runtime-spec `Process.User`, CRI `ContainerUser`, and Linux build tags. It protects the status response user field.

## Risks and Test Signals
Signals are exact expected errors and exact UID/GID/supplemental group conversion. The test does not cover how `toCRIContainerStatus` logs and suppresses these errors, only the helper itself.
