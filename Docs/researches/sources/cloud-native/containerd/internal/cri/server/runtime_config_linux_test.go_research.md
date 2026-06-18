# sources/cloud-native/containerd/internal/cri/server/runtime_config_linux_test.go

## Purpose

This Linux test file validates CRI runtime config cgroup driver selection.

## Important APIs, Types, and Functions

`newFakeRuntimeConfig` builds fake runtimes with optional runc v2 and `SystemdCgroup`. `TestRuntimeConfig` asserts the response for no runtimes, non-runc runtimes, sorted fallback, and default runtime priority.

## Control Flow

Each test mutates a test CRI service config, calls `RuntimeConfig`, and compares `resp.Linux.CgroupDriver` to expected values, using host systemd detection only for fallback cases.

## State and Persistence Behavior

Only in-memory test configuration is changed.

## Dependencies and Integration Points

It exercises `RuntimeConfig`, `getCgroupDriver`, runtime option generation, and systemd auto-detection.

## Risks and Test Signals

The test protects kubelet-visible cgroup driver reporting. It does not cover malformed runtime options beyond the helper's normal generation behavior.
