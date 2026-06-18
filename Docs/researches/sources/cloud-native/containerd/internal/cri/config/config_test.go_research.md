# sources/cloud-native/containerd/internal/cri/config/config_test.go

## Purpose

`config_test.go` unit-tests CRI config validation, mutation, warning emission, host-access detection, and local image pull fallback.

## Important APIs, Types, and Functions

- `TestValidateConfig` table-drives runtime, image, and server config validation cases.
- `TestHostAccessingSandbox` verifies which sandbox security contexts count as host access.
- `TestCheckLocalImagePullConfigs` verifies transfer-service-incompatible image config settings force `UseLocalImagePull`.

## Control Flow

The main table invokes only the validation functions relevant to each case, checks errors or mutated expected structs, collects warnings, and compares deprecation warning sets. Host-access tests feed nil, privileged, non-privileged, and host namespace configs. Local-pull tests mutate a default image config and call the checker.

## State and Persistence Behavior

Tests operate on in-memory config structs and assert intentional mutation such as CNI bin-dir migration, sandboxer defaulting, registry auth mapping, and `UseLocalImagePull` fallback.

## Dependencies and Integration Points

It depends on CRI runtime API types, deprecation warning values, cgroup mode helper, and platform-sensitive default image config behavior.

## Risks and Edge Cases

Expected outcomes can vary by cgroup mode and OS for cgroup writable and snapshot annotation fallback. Because validation mutates inputs, missing expected mutation coverage can hide behavioral drift.

## Test Signals

The file is the primary unit signal for config validation semantics and compatibility-preserving mutations.
