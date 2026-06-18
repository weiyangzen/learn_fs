# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_other_test.go

## Purpose

This non-Linux, non-Windows test helper supplies platform-specific default data for shared sandbox spec tests.

## Important APIs, Types, and Functions

`getRunPodSandboxTestData` returns empty `PodSandboxConfig`, empty image config, and a no-op spec check closure.

## Control Flow

There are no test cases in this file; it satisfies symbols consumed by shared tests compiled on other platforms.

## State and Persistence Behavior

No state is created or persisted.

## Dependencies and Integration Points

It integrates with `sandbox_run_test.go` under the `!windows && !linux` build tag.

## Risks and Test Signals

Because assertions are empty, shared tests provide only compile-level coverage for these platforms. Platform-specific behavior needs dedicated tests if support expands.
