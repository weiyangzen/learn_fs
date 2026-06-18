# sources/cloud-native/containerd/internal/cri/config/config_kernel_linux_test.go

## Purpose

`config_kernel_linux_test.go` unit-tests Linux unprivileged ICMP/port kernel validation.

## Important APIs, Types, and Functions

- `TestValidateEnableUnprivileged` patches `kernelGreaterEqualThan` and runs table-driven cases.

## Control Flow

The test saves the original function, restores it with cleanup, then verifies validation passes when settings are disabled, fails with the expected message on kernels below 4.11, and passes on kernels at/above the minimum.

## State and Persistence Behavior

It mutates a package-level function variable during each subtest and restores it after the test.

## Dependencies and Integration Points

It depends on Linux build, containerd kernel version type, and testify assertions. It validates behavior called by `ValidateRuntimeConfig`.

## Risks and Edge Cases

Subtests share a patched package variable; they are not parallelized, which avoids data races. The test does not cover kernel probe errors.

## Test Signals

Failure indicates broken kernel gating for CRI unprivileged port/ICMP defaults.
