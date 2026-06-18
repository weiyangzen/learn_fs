# sources/cloud-native/containerd/internal/cri/server/sandbox_run_test.go

## Purpose

This CRI service test file validates helper conversions used by sandbox network setup and runtime configuration selection.

## Important APIs, Types, and Functions

`TestToCNIPortMappings` verifies CRI port mappings convert to CNI mappings and host-port-less entries are skipped. `TestSelectPodIP` verifies IPv4 default, IPv6 preference, CNI order preference, and additional IP ordering. `TestDisablePauseImagePullConfig` validates runtime config plumbing for `DisablePauseImagePull`.

## Control Flow

Tests construct CRI objects or CNI IP configs, call pure helper functions, and assert exact output slices/fields.

## State and Persistence Behavior

No persistent state is used. The runtime config test mutates only an in-memory config object.

## Dependencies and Integration Points

It covers CNI option conversion helpers and CRI config runtime resolution used by `RunPodSandbox`.

## Risks and Test Signals

The tests catch common network option regressions but do not validate actual CNI plugin calls or full sandbox startup rollback.
