# sources/cloud-native/containerd/internal/cri/config/config_kernel_linux.go

## Purpose

`config_kernel_linux.go` validates Linux kernel support for unprivileged port and ICMP configuration.

## Important APIs, Types, and Functions

- `kernelGreaterEqualThan` is a package variable pointing to `kernel.GreaterEqualThan` for test replacement.
- `ValidateEnableUnprivileged` checks kernel version `>= 4.11` when either `EnableUnprivilegedICMP` or `EnableUnprivilegedPorts` is enabled.

## Control Flow

If neither setting is enabled, validation succeeds without probing the kernel. If either is enabled, it checks the current kernel version and returns a wrapped probe error or a clear minimum-version error when too old.

## State and Persistence Behavior

No persistent state is changed. The package-level function variable is mutable only to support tests.

## Dependencies and Integration Points

It depends on containerd kernel version utilities and is called from `ValidateRuntimeConfig`.

## Risks and Edge Cases

Kernel probing failures block config validation. Tests must restore `kernelGreaterEqualThan` after monkey-patching to avoid cross-test contamination.

## Test Signals

`config_kernel_linux_test.go` covers disabled settings, too-old kernels, and supported kernels.
