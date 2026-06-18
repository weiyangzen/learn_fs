# sources/cloud-native/containerd/integration/container_update_resources_test.go

## Purpose

This Linux test file validates CRI `UpdateContainerResources` behavior for memory and swap limits before and after container start, and verifies that container status reflects updated resources. It cross-checks CRI state, OCI specs, and live cgroup state.

## Important APIs, Types, And Functions

- `checkMemoryLimit`, `checkMemorySwapLimit`, and `checkMemoryLimitInContainerStatus` assert expected spec/status fields.
- `getCgroupSwapLimitForTask` and `getCgroupMemoryLimitForTask` read cgroup v1/v2 stats for a running container task.
- `isSwapLikelyEnabled` gates swap tests based on `/proc/swaps` and cgroup support.
- `TestUpdateContainerResources_MemorySwap`, `TestUpdateContainerResources_MemoryLimit`, and `TestUpdateContainerResources_StatusUpdated` cover swap, memory, and status propagation.

## Control Flow

The swap test skips when swap/accounting is unavailable, creates a container with memory and swap limits, verifies OCI spec fields, starts the task, validates cgroup limits, updates swap, then rechecks spec and cgroup state. The memory-limit test performs a similar sequence around memory limits and default swap mirroring when the swap controller is available. The status test checks `ContainerStatus.Resources.Linux.MemoryLimitInBytes` before start, after update while created, and after update while running.

## State And Persistence Behavior

Resource updates mutate container metadata/OCI spec stored by containerd and live cgroup controller state for running tasks. Status reads reflect persisted CRI container resource fields.

## Dependencies And Integration Points

The file integrates CRI resource APIs, containerd client task/spec access, cgroups v1/v2 libraries, `criopts.SwapControllerAvailable`, and Linux kernel swap accounting.

## Risks And Edge Cases

Swap behavior varies heavily by kernel, cgroup mode, and host configuration. cgroup v2 reports swap as swap limit plus memory usage limit, so assertions encode that API detail. Host controllers with unlimited or disabled limits can cause skips or unexpected values.

## Test Signals

Passing confirms resource updates are written to OCI metadata, applied to live cgroups, and exposed through CRI status.
