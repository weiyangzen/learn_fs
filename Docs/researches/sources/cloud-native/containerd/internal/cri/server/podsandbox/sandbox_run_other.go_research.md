# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_other.go

## Purpose

This non-Linux, non-Windows file supplies minimal sandbox spec and file hooks for other platforms.

## Important APIs, Types, and Functions

`sandboxContainerSpec` returns a generated runtime spec with default CRI annotations only. `sandboxContainerSpecOpts`, `setupSandboxFiles`, `cleanupSandboxFiles`, and `sandboxSnapshotterOpts` return empty options or nil.

## Control Flow

All functions are straight-line stubs. Spec generation ignores image config, namespace path, and runtime pod annotation inputs except for CRI default annotations.

## State and Persistence Behavior

No sandbox files, mounts, or snapshotter remap state are created by this file.

## Dependencies and Integration Points

It exists under `!windows && !linux` to satisfy the shared controller start path on other platforms.

## Risks and Test Signals

The behavior is intentionally minimal and may not create a runnable pause container on every platform. Compile and platform-specific smoke tests are the useful signals.
