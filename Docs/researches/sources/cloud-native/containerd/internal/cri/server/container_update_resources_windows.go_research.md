
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_update_resources_windows.go -->
# sources/cloud-native/containerd/internal/cri/server/container_update_resources_windows.go

## Purpose

This Windows-specific file maps CRI Windows resource updates into OCI Windows resource fields for the shared `UpdateContainerResources` handler.

## Important APIs, Types, and Functions

`updateOCIResource` deep-copies an OCI spec, ensures `spec.Windows` exists, and applies `opts.WithWindowsResources`. `getResources` returns `spec.Windows.Resources` for runtime task update.

## Control Flow

The mapper clones the supplied spec with `util.DeepCopy`, initializes the Windows subsection when missing, and calls the CRI opts helper to apply CRI Windows resource values. Errors are wrapped with Windows resource context. The shared handler persists and applies the returned spec.

## State and Persistence Behavior

This file only constructs an in-memory cloned spec. Containerd metadata updates, task resource updates, and CRI status synchronization are owned by `container_update_resources.go`.

## Dependencies and Integration Points

It depends on OCI runtime spec, CRI runtime API, CRI config, CRI opts, and CRI util. It integrates with `copyResourcesToStatus`, which knows how to project Windows CPU shares/count/maximum, memory limit, and CPU affinity back into CRI status.

## Risks and Edge Cases

Windows resource support differs from Linux and is delegated to `opts.WithWindowsResources`. Missing or unsupported resource fields may silently preserve previous values depending on the opts helper. The shared top-level NRI call currently passes Linux resources, so Windows-specific NRI resource mutation is not represented here.

## Test Signals

Direct tests should mirror the Linux mapper tests for CPU shares/count/maximum, memory limit, affinity, nil `Windows` spec initialization, empty-field preservation, and task update using `spec.Windows.Resources`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_update_resources_windows.go -->
