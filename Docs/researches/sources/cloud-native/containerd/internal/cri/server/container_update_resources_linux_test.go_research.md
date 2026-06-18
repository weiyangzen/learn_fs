
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_update_resources_linux_test.go -->
# sources/cloud-native/containerd/internal/cri/server/container_update_resources_linux_test.go

## Purpose

This test file validates Linux OCI spec patching for CRI `UpdateContainerResources`. It focuses on CPU, memory, OOM score, cpuset, and unified cgroup resource maps.

## Important APIs, Types, and Functions

The central test is `TestUpdateOCILinuxResource`. It calls `updateOCIResource` with fake OCI specs and `runtime.UpdateContainerResourcesRequest` values, then compares the returned spec with an expected OCI spec. It uses `criopts.SwapControllerAvailable` to account for host-dependent swap controller availability.

## Control Flow

Each table case builds an input spec, a CRI request, and an expected cloned spec. The test config enables tolerance for missing hugetlb controllers. After calling `updateOCIResource`, the test asserts error presence and structural equality of the resulting spec.

## State and Persistence Behavior

All state is in-memory. The tests verify the clone output, not the shared RPC handler's metadata persistence, task update, or status transaction behavior.

## Dependencies and Integration Points

Dependencies include OCI runtime spec, protobuf pointer helpers, CRI runtime API, CRI config, and CRI opts. The expected swap field is host-aware because the underlying resource mapper only sets swap when the swap controller is available.

## Risks and Edge Cases

The test assumes host controller detection for swap, so expected output changes by environment in a controlled way. It does not assert that the input spec remains unmodified after cloning. It does not cover invalid cpuset strings, hugetlb limits, nil process, or task application.

## Test Signals

The test proves the Linux mapper updates all major resource fields, preserves unspecified fields, fills missing CPU and unified fields, and patches unified maps without dropping unrelated existing keys.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_update_resources_linux_test.go -->
