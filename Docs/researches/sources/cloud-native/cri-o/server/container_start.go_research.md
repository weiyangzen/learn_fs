<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_start.go -->
# sources/cloud-native/cri-o/server/container_start.go

## Purpose

This file implements CRI `StartContainer`, including normal runtime start and checkpoint restore start.

## Important APIs, Types, and Functions

`StartContainer(ctx, req)` resolves the container, branches on restore mode, runs runtime-handler hooks and NRI notifications, starts the runtime container, emits a CRI started event, and persists final state.

## Control Flow

For restore containers, it calls `ContainerRestore` with the container ID and empty checkpoint options. On restore failure it reloads the container, releases its name, deletes storage, removes in-memory state, and returns the error. For normal containers, it requires internal state `ContainerStateCreated`, retrieves the sandbox and hooks, sends NRI start, defers failure cleanup that sets start failure fields, runs pre-stop/NRI stop/remove cleanup, and always writes state to disk. It runs pre-start hooks, calls runtime `StartContainer`, generates a started event, sends NRI post-start, logs details, and returns success.

## State and Persistence Behavior

It mutates runtime state from created to running, writes container state to disk, may remove a failed container and its storage, releases names after failed restore, emits CRI events, and updates container status fields on start failure.

## Dependencies and Integration Points

It integrates with checkpoint restore metadata, runtime start and restore APIs, runtime-handler hooks, NRI, sandbox lookup, storage runtime deletion, CRI event generation, and `oci.Container` state helpers.

## Risks and Edge Cases

The logged PID comes from `state := c.State()` captured before runtime start, so it may not reflect the post-start PID unless runtime updates the same state object. Failure cleanup after normal start attempts removal in pod, which can cascade through stop/delete paths. Restore cleanup is separate and must remain aligned with import state.

## Test Signals

Tests cover invalid ID and invalid/non-created state. Successful start, hooks, NRI, restore success/failure, CRI event emission, and persisted state behavior need broader integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_start.go -->
