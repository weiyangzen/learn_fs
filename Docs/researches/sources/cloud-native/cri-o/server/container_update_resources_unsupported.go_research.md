<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_update_resources_unsupported.go -->
# sources/cloud-native/cri-o/server/container_update_resources_unsupported.go

## Purpose

This non-Linux file provides basic memory update validation for platforms without Linux cgroups.

## Important APIs, Types, and Functions

`validateMemoryUpdate(ctx, c, newMemoryLimit)` rejects negative memory limits and otherwise returns success.

## Control Flow

There is a single branch: negative values error, zero or positive values pass. Context and container parameters are unused except for signature compatibility.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It satisfies the platform-specific validation hook used by `UpdateContainerResources` on non-Linux builds.

## Risks and Edge Cases

Because there are no cgroups, it cannot validate current usage or enforce cgroup semantics. Runtime update support may still fail later.

## Test Signals

No direct tests are present; build-tag compilation and generic update tests are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_update_resources_unsupported.go -->
