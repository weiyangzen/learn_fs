# sources/cloud-native/containerd/integration/truncindex_test.go

## Purpose

`truncindex_test.go` verifies that CRI APIs accept unambiguous truncated IDs for images, sandboxes, and containers.

## Important APIs, Types, and Functions

- `genTruncIndex` returns the leading half of an ID.
- `TestTruncIndex` exercises image status, sandbox status/port-forward/stop/remove, container create/status/start/stats/update/exec/execsync/stop/remove/status error paths using truncated identifiers.

## Control Flow

The test pulls busybox, queries image status by truncated image ID, runs a sandbox and addresses it by truncated ID, creates a container in that sandbox, then starts, stats, updates resources, executes commands, stops/removes, and verifies post-removal status/stat calls fail.

## State and Persistence Behavior

The test relies on CRI ID indexes resolving truncated IDs while objects exist and rejecting them after removal. It exercises live runtime state and cleanup callbacks.

## Dependencies and Integration Points

It uses CRI runtime/image services, image fixtures, OS-specific resource update structs, exec/port-forward paths, and common container config helpers.

## Risks and Edge Cases

It does not test ambiguous truncated IDs, which is noted in TODOs. Because it truncates to half length, it assumes the selected IDs remain unambiguous in the test environment.

## Test Signals

Failures reveal truncindex lookup regressions across CRI image, sandbox, container, stats, exec, and resource update APIs.
