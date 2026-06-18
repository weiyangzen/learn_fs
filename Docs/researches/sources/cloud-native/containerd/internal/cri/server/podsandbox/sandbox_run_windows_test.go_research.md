# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_windows_test.go

## Purpose

This Windows test file provides Windows sandbox spec fixtures and validates network namespace placement in the generated OCI spec.

## Important APIs, Types, and Functions

`getRunPodSandboxTestData` returns a Windows sandbox config with metadata, hostname, labels, annotations, RunAs username, credential spec, and HostProcess flag, plus image config and a spec assertion closure. `TestSandboxWindowsNetworkNamespace` checks that `spec.Windows.Network.NetworkNamespace` equals the provided namespace path.

## Control Flow

The test builds a controller fixture, generates a spec with `sandboxContainerSpec`, runs the shared spec checks, and asserts Windows network fields are present.

## State and Persistence Behavior

No containerd or filesystem state is created.

## Dependencies and Integration Points

It exercises Windows-specific spec options, CRI annotations, and the shared controller test fixture.

## Risks and Test Signals

The test catches Windows spec regressions but not real HCS runtime behavior or HostProcess networking semantics.
