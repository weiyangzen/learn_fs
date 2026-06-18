
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_update_resources_other.go -->
# sources/cloud-native/containerd/internal/cri/server/container_update_resources_other.go

## Purpose

This non-Linux, non-Windows build file provides a stub `UpdateContainerResources` implementation for unsupported platforms. It preserves CRI API availability while making no platform resource changes.

## Important APIs, Types, and Functions

The only exported behavior is `(*criService).UpdateContainerResources`. It uses `containerStore.Get` and `container.Status.Update` but does not inspect CRI resource fields or update an OCI spec.

## Control Flow

The handler resolves the requested container ID. If not found, it returns a wrapped error. It then runs a container status update transaction that returns the status unchanged and returns an empty `UpdateContainerResourcesResponse`.

## State and Persistence Behavior

No resource state is changed. The status transaction may still serialize with other store operations, but it returns the same status. No containerd metadata, runtime task, NRI hook, or filesystem state is touched.

## Dependencies and Integration Points

The file depends only on context, fmt, CRI runtime API types, and `containerstore`. It is selected by the `!windows && !linux` build constraint and keeps the CRI server package compiling on other platforms.

## Risks and Edge Cases

Callers receive success even though resource updates are effectively ignored. That is a compatibility choice but can be surprising if kubelet or tests expect an unimplemented error. Because it has no NRI integration, plugins cannot observe unsupported-platform resource updates.

## Test Signals

Useful tests would assert that unsupported builds return success for existing containers, error for missing containers, and leave status/resources/spec unchanged.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_update_resources_other.go -->
