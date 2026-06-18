# sources/cloud-native/containerd/internal/cri/server/podsandbox/helpers_windows.go

## Purpose

This Windows helper file provides Windows-compatible implementations for shared pod sandbox cleanup and SELinux/KVM label hooks.

## Important APIs, Types, and Functions

`ensureRemoveAll` wraps `os.RemoveAll`. `modifyProcessLabel` returns nil because SELinux process label conversion is not applicable to Windows.

## Control Flow

Both functions are direct no-op/simple implementations without retries, mount unmounts, or label mutation.

## State and Persistence Behavior

Only filesystem deletion is performed. There is no namespace, mount, SELinux, or snapshot remap behavior in this file.

## Dependencies and Integration Points

It satisfies shared helper symbols for Windows builds of the pod sandbox controller.

## Risks and Test Signals

Windows cleanup behavior depends on `os.RemoveAll` semantics and open-handle behavior. Windows sandbox spec tests provide platform coverage for the broader controller path.
