# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_stop.go

## Purpose

This file stops a running sandbox pause container and cleans sandbox files while preserving exit-event driven task deletion semantics.

## Important APIs, Types, and Functions

`Stop` finds the cached sandbox, loads metadata, stops ready or unknown sandboxes, and calls platform cleanup. `stopSandboxContainerRetryOnConnectionClosed` retries shim ttrpc closed errors with quadratic backoff. `stopSandboxContainer` kills the task and waits for sandbox exit. `cleanupUnknownSandbox` reuses task-exit cleanup with an unknown exit code.

## Control Flow

Missing store entries return not-found; a nil container is already stopped. Unknown state starts a temporary exit monitor before killing so cleanup/status update still happen. Task not-found is tolerated except in unknown state, where cleanup is forced.

## State and Persistence Behavior

The method can send SIGKILL, wait for status to become not-ready, and unmount/remove platform sandbox files. Status mutation occurs through `waitSandboxExit` or `cleanupUnknownSandbox`.

## Dependencies and Integration Points

It integrates with containerd task APIs, errdefs, shim ttrpc error detection, Linux cleanup helpers, and the shared task-exit handler.

## Risks and Test Signals

Risks include indefinite waits if task exit is not observed, retry masking persistent shim failures, and cleanup races in unknown state. Integration stop/remove tests are needed for confidence.
