<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/opts/opts_linux.go -->
# sources/cloud-native/containerd/core/runtime/opts/opts_linux.go

## Purpose
Provides a Linux namespace deletion option that cleans cgroup resources by namespace.

## Important APIs, Types, And Functions
- `WithNamespaceCgroupDeletion(ctx, i *namespaces.DeleteInfo) error` removes the cgroup path derived from the namespace delete info.

## Control Flow
The function calls `cgroups.Remove(filepath.Join("/", constants.CgroupNamespace, i.Name))` and returns any error.

## State And Persistence
Mutates host cgroup state by deleting the namespace cgroup. No in-process state is stored.

## Dependencies And Integration Points
Builds on `core/cgroups`, runtime constants, and namespace delete hooks. Intended for Linux cleanup when namespaces are deleted.

## Risks And Edge Cases
This is Linux-only and operates on cgroup paths. Incorrect namespace names or cgroup layout changes can cause failed cleanup or unintended path targeting if upstream helpers do not sanitize as expected.

## Test Signals
No direct listed tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/opts/opts_linux.go -->
