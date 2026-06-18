# sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_other.go

## Purpose

This non-Linux, non-Windows helper file supplies portable no-op/simple implementations for helpers required by the common pod sandbox controller.

## Important APIs, Types, and Functions

`ensureRemoveAll` delegates directly to `os.RemoveAll`. `modifyProcessLabel` returns nil and does not alter the OCI spec.

## Control Flow

Both functions are single-step implementations without Linux mount retry, SELinux, or KVM label logic.

## State and Persistence Behavior

Only `ensureRemoveAll` changes filesystem state by removing the requested path. No mount or label state is managed.

## Dependencies and Integration Points

The file integrates with shared controller cleanup code under the `!windows && !linux` build tag.

## Risks and Test Signals

The simplified remove path will not handle busy mounts or Linux-style namespace artifacts. Compile and platform smoke tests are the meaningful signals.
