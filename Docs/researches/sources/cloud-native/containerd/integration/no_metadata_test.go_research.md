# sources/cloud-native/containerd/integration/no_metadata_test.go

## Purpose

This file verifies that invalid CRI requests missing required metadata fail gracefully and do not break runtime service health.

## Important APIs, Types, And Functions

- `TestRunPodSandboxWithoutMetadata` calls `RunPodSandbox` with an empty `PodSandboxConfig`.
- `TestCreateContainerWithoutMetadata` calls `CreateContainer` with an empty `ContainerConfig`.
- `runtimeService.Status` checks service health after each expected error.

## Control Flow

The sandbox test submits an empty config and requires an error, then requires `Status` to succeed. The container test creates a valid sandbox, submits an empty container config against it, requires an error, and again checks `Status`.

## State And Persistence Behavior

The invalid requests should not persist sandbox/container metadata. The valid sandbox in the second test is cleaned up through `PodSandboxConfigWithCleanup`.

## Dependencies And Integration Points

It integrates with CRI validation paths for required metadata and the runtime status endpoint.

## Risks And Edge Cases

The tests only assert that an error occurs, not a specific validation code/message. They validate service survival but not absence of partial metadata records.

## Test Signals

Passing means malformed metadata requests are rejected without making the CRI plugin unhealthy.
