<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/run/run_unix_test.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/run/run_unix_test.go

## Purpose
Unit tests for Unix GPU helper behavior used by `ctr run --gpus`.

## Important APIs, Types, And Functions
Defines `TestDetectGPUVendor` and `TestGpuDeviceNames`.

## Control Flow
Table-driven cases validate nil/empty/unknown vendor lists, NVIDIA/AMD precedence, multiple vendors, empty vendor errors, no IDs, and multiple GPU ID formatting.

## State And Persistence
No persistence; pure helper tests.

## Dependencies And Integration Points
Uses Go testing and `context.Background` against unexported package functions.

## Risks And Test Signals
Tests cover helper logic but not actual CDI registry refresh or OCI spec injection. Good regression signal for vendor precedence and CDI device name format. Source size reviewed: 156 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/run/run_unix_test.go -->
