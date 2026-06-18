# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_delete.go

## Purpose

This file implements sandbox controller shutdown and low-level pause task/container cleanup.

## Important APIs, Types, and Functions

`Shutdown` removes sandbox root and volatile directories, deletes the sandbox task if present, deletes the container with snapshot cleanup, and removes the sandbox from the controller store. `cleanupSandboxTask` deletes the task and, when shim/task caches diverge, calls the task service `Delete` API to ensure the shim is shut down.

## Control Flow

Missing sandbox IDs are treated as successful no-ops. Cleanup removes filesystem state before container deletion. Task deletion tolerates not-found, then performs task-service cleanup to handle leaked shims after canceled or partially completed shim deletes.

## State and Persistence Behavior

It deletes root/state directories, containerd task state, snapshots, container metadata, and in-memory store entries.

## Dependencies and Integration Points

It integrates with `ensureRemoveAll`, containerd container/task APIs, the tasks service gRPC API, errdefs conversion, and NRI delete hooks in other delete paths.

## Risks and Test Signals

Risks include leaving shims when task-service cleanup fails and losing diagnostic state after directory removal. End-to-end remove and restart tests are needed because this file touches real runtime cleanup behavior.
