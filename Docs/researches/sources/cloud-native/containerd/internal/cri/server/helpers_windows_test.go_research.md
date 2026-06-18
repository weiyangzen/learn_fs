
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers_windows_test.go -->
# sources/cloud-native/containerd/internal/cri/server/helpers_windows_test.go

## Purpose

This Windows-only test file validates the Windows branch of `hostNetwork`, where host networking is determined by HostProcess pod configuration.

## Important APIs, Types, and Functions

The file defines `TestWindowsHostNetwork`, which calls the shared `hostNetwork` helper with `runtime.PodSandboxConfig` values containing `WindowsSandboxSecurityContext.HostProcess`.

## Control Flow

The table-driven test checks three cases: explicit `HostProcess: false`, explicit `HostProcess: true`, and an empty Windows security context. It compares the helper result to the expected boolean for each case.

## State and Persistence Behavior

There is no persistent or mutable state. The test builds CRI config structs in memory.

## Dependencies and Integration Points

The test depends on CRI runtime API types and the shared `hostNetwork` helper. It protects sandbox networking decisions for Windows HostProcess pods.

## Risks and Edge Cases

The test does not cover nil `PodSandboxConfig`, nil `Windows` config, or nil security context beyond the empty security context object. It does not exercise actual CNI or HostProcess runtime behavior.

## Test Signals

Passing tests show that Windows HostProcess pods are treated as host-network pods and that false or absent HostProcess settings do not request host networking.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers_windows_test.go -->
