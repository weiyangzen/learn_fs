<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_update_resources.go -->
# sources/cloud-native/cri-o/server/container_update_resources.go

## Purpose

This file implements CRI `UpdateContainerResources`, translating CRI Linux resource updates to OCI runtime resources and updating CRI-O's stored resource view.

## Important APIs, Types, and Functions

`UpdateContainerResources(ctx, req)` validates container state, allows NRI mutation of requested resources, validates memory updates, calls runtime update, updates internal stored resources, and sends NRI post-update. `toOCIResources` converts CRI CPU, memory, and cgroup v2 unified fields to `rspec.LinuxResources`. `reapplySharedCPUs` merges OpenShift shared CPUs into requested cpusets.

## Control Flow

The RPC resolves a container and requires it to be running or created. If Linux resources are present, it reapplies shared CPUs from `OPENSHIFT_SHARED_CPUS`, calls NRI update, defaults to the original resources if NRI returns nil, validates the new memory limit, converts resources to OCI, calls runtime `UpdateContainer`, updates CRI-O's resource store, and runs NRI post-update. If no Linux section is present, it returns success without mutation.

## State and Persistence Behavior

Runtime cgroup resources are updated through the runtime. CRI-O updates the in-memory/stored Linux resources associated with the container via `UpdateContainerLinuxResources`. The request object can be mutated in place by `reapplySharedCPUs`.

## Dependencies and Integration Points

It depends on CRI Linux resource types, OpenContainers runtime spec resources, cgroup v2 detection, cgroup memory swap support, NRI update hooks, runtime update API, and Kubernetes cpuset parsing.

## Risks and Edge Cases

`strings.Split(env, "=")` assumes env strings contain `=`, which is normally true but could panic for malformed spec env entries. Shared CPU merge mutates `req.Linux.CpusetCpus`. Memory validation is platform-specific and can be skipped when stats are unavailable. Swap is set equal to memory limit only when memory swap cgroup support exists.

## Test Signals

Tests cover success with nil Linux resources, CPU field conversion, cgroup v2 unified fields, invalid state, invalid IDs, and NRI-enabled success. They do not cover shared CPU merge or memory validation failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_update_resources.go -->
