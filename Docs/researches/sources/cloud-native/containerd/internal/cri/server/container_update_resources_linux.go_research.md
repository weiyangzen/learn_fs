
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_update_resources_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/container_update_resources_linux.go

## Purpose

This Linux-specific file converts CRI Linux container resource updates into OCI Linux resource fields. It supplies the platform hooks used by the shared `UpdateContainerResources` implementation.

## Important APIs, Types, and Functions

`updateOCIResource` deep-copies the supplied OCI spec, ensures `spec.Linux` exists, and applies `opts.WithResources`. `getResources` returns `spec.Linux.Resources` for `containerd.WithResources`.

## Control Flow

The function clones the old spec with `util.DeepCopy` so callers can roll back safely and so failed updates do not mutate the caller's object. It initializes `cloned.Linux` if absent, then delegates detailed field mapping to `opts.WithResources`, passing hugetlb controller compatibility settings from `criconfig.Config`. It returns the cloned patched spec or an error annotated as a Linux resource-setting failure.

## State and Persistence Behavior

This file has no direct persistence. It creates an in-memory OCI spec copy. The caller persists the result into containerd metadata and applies `spec.Linux.Resources` to a running task.

## Dependencies and Integration Points

Dependencies include OCI runtime spec, CRI runtime API, CRI config, CRI opts, and CRI util deep copy. It integrates directly with `container_update_resources.go` and with `copyResourcesToStatus`, which later translates the same OCI resource fields back to CRI status.

## Risks and Edge Cases

Deep-copy failure aborts the update. Missing `spec.Process` may matter for OOM score changes handled by `opts.WithResources`. Hugetlb controller tolerance changes behavior on hosts lacking controllers. Empty CRI fields are treated as patch semantics by the opts layer, so preserving existing values depends on that helper.

## Test Signals

`container_update_resources_linux_test.go` verifies full updates, skipped empty fields, filling missing resource groups, and patching unified cgroup v2 maps. Additional useful tests would cover hugetlb-related options and nil `Process` handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_update_resources_linux.go -->
