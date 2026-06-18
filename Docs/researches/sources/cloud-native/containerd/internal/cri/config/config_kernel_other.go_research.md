# sources/cloud-native/containerd/internal/cri/config/config_kernel_other.go

## Purpose

`config_kernel_other.go` provides non-Linux no-op validation for unprivileged port and ICMP settings.

## Important APIs, Types, and Functions

- `ValidateEnableUnprivileged` returns nil on non-Linux builds.

## Control Flow

The function ignores its context and runtime config and succeeds.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It is selected by `!linux` build tag and keeps `ValidateRuntimeConfig` platform-neutral.

## Risks and Edge Cases

Non-Linux platforms do not enforce Linux kernel prerequisites. Any platform-specific equivalent validation would need a separate implementation.

## Test Signals

Compile success on non-Linux platforms is the primary signal.
