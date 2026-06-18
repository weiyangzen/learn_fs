# sources/cloud-native/containerd/internal/cri/server/container_status_windows.go

## Purpose
This Windows-specific status helper currently returns an empty CRI container user.

## Important APIs, Types, and Functions
`toCRIContainerUser` has the same signature as other platform implementations and returns `&runtime.ContainerUser{}`.

## Control Flow, State, and Persistence
No containerd spec lookup or mutation occurs. Windows user details are not surfaced through this CRI field by this implementation.

## Dependencies and Integration Points
It integrates with generic `toCRIContainerStatus` on Windows builds and depends only on CRI runtime types.

## Risks and Test Signals
Risk is limited observability for Windows run-as user in CRI status. There are no direct tests in this subset; Windows create tests cover username selection in the OCI spec.
