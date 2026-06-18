# sources/cloud-native/containerd/internal/cri/server/podsandbox/events.go

## Purpose

This file implements the pod sandbox event handler used by the controller's event monitor. It handles task exit events for sandbox pause containers and delegates cleanup/status mutation to the shared task-exit helper.

## Important APIs, Types, and Functions

`handleEventTimeout` bounds per-event handling to ten seconds because the event monitor handles events serially. `podSandboxEventHandler` holds a controller pointer. `HandleEvent` recognizes `*eventtypes.TaskExit`, finds the sandbox by `TaskExit.ID`, skips absent or containerless entries, creates a namespaced timeout context, and calls `handleSandboxTaskExit`.

## Control Flow

Non-`TaskExit` events return nil. For task exits, the handler uses `ID` rather than `ContainerID` to avoid handling exec-process exits, then either ignores unrelated events or performs bounded cleanup.

## State and Persistence Behavior

The handler itself persists nothing. It can indirectly delete the containerd task and update the in-memory pod sandbox status through `handleSandboxTaskExit`.

## Dependencies and Integration Points

It integrates with containerd event types, the CRI namespaced context helper, the controller store, and the controller-level event monitor backoff mechanism.

## Risks and Test Signals

Risks are event loss when the sandbox is absent from the in-memory store and repeated backoff if task deletion keeps timing out. Tests are indirect through controller exit/recovery tests and event monitor behavior.
