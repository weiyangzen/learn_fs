# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run.go

## Purpose

This file implements the pod sandbox controller's create/start path for pause-container-backed sandboxes.

## Important APIs, Types, and Functions

`CleanupErr` marks cleanup failures joined with startup errors. `Start` creates root directories, loads the pause image, resolves sandbox runtime, builds the OCI spec, creates a container and task, sets up files, invokes deprecated NRI create hooks, starts the task, updates status, returns `sandbox.ControllerInstance`, and starts an exit waiter. `Create` stores metadata from sandbox extensions. `getSandboxImageName` selects the pinned sandbox image or default.

## Control Flow

`Start` is a staged resource acquisition function with defers for rollback. Each cleanup defer runs only on later error and joins cleanup failures separately. It records SELinux labels, handles privileged sysfs changes, chooses runtime snapshotter, marshals the final task spec, and starts a background wait goroutine after task start.

## State and Persistence Behavior

It creates sandbox filesystem directories, containerd snapshots/containers/tasks, metadata extensions, runtime labels, and in-memory status. On failure it attempts to unwind directories, files, tasks, containers, labels, and snapshots.

## Dependencies and Integration Points

It integrates with CRI config, image service config, containerd client APIs, OCI spec options, snapshot labels, NRI, SELinux, warning/deprecation service, and the controller store.

## Risks and Test Signals

Risks include partial cleanup, deprecated NRI behavior, SELinux label leaks, and cleanup order dependencies. Tests cover spec generation and metadata typeurl; full safety needs runtime integration tests.
