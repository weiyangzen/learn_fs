<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_update_resources_test.go -->
# sources/cloud-native/cri-o/server/container_update_resources_test.go

## Purpose

This suite tests CRI resource update behavior and resource conversion.

## Important APIs, Types, and Functions

It calls `sut.UpdateContainerResources`, sets `testContainer` spec/state, inspects updated `specs.LinuxResources`, and covers NRI-enabled setup.

## Control Flow

Tests verify success with no Linux resources, CPU period/quota/shares and cpuset updates, unified cgroup v2 map updates when running on cgroup v2, error on invalid container state, error on invalid/empty IDs, and success when NRI is enabled.

## State and Persistence Behavior

The tests mutate the in-memory container spec and state. They inspect the container spec after update to confirm stored resource changes.

## Dependencies and Integration Points

They depend on CRI resource types, runtime-spec resources, internal cgroup detection, mock runtime setup, NRI config, and shared harness helpers.

## Risks and Edge Cases

The suite does not test memory limit validation, runtime update errors, shared CPU environment merge, NRI returning modified resources, or post-update NRI failures.

## Test Signals

The strongest signal is that successful resource updates are reflected in the container's stored OCI resources, not only sent to the runtime.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_update_resources_test.go -->
