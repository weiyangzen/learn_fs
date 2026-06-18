# sources/cloud-native/containerd/integration/duplicate_name_test.go

## Purpose

This test validates CRI name uniqueness enforcement for pod sandboxes and containers. It ensures duplicate create attempts fail instead of overwriting or aliasing existing objects.

## Important APIs, Types, And Functions

- `TestDuplicateName` is the only test.
- `PodSandboxConfigWithCleanup` creates the first sandbox with metadata.
- `runtimeService.RunPodSandbox` and `runtimeService.CreateContainer` are called twice with the same configs.

## Control Flow

The test creates a sandbox, then attempts to run another sandbox with the same config and requires an error. It ensures the Pause image exists, creates one container in the sandbox, then attempts to create the same container again and requires an error.

## State And Persistence Behavior

The state under test is CRI metadata indexing by sandbox/container names within the relevant scope. No explicit cleanup is needed for the duplicate failures beyond the initial sandbox cleanup.

## Dependencies And Integration Points

It depends on CRI metadata validation and image availability. It integrates with containerd CRI name reservation logic for both sandbox and container records.

## Risks And Edge Cases

The test only checks that an error occurs, not its type or message. It does not test name reuse after removal, which is covered by restart tests.

## Test Signals

Passing confirms duplicate sandbox and container names are rejected while originals exist.
