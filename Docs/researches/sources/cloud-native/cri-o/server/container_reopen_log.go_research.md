<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_reopen_log.go -->
# sources/cloud-native/cri-o/server/container_reopen_log.go

## Purpose

This file implements CRI log reopening for a running container, used by log rotation workflows.

## Important APIs, Types, and Functions

`ReopenContainerLog(ctx, req)` resolves a container, verifies runtime liveness, and delegates to `Runtime().ReopenContainerLog`.

## Control Flow

The method starts a span, resolves the short container ID, asks the runtime whether the container is alive, returns an error if not running, and then calls the runtime reopen operation.

## State and Persistence Behavior

It does not mutate CRI-O state directly. The runtime is expected to reopen the log file descriptor, affecting subsequent container log writes.

## Dependencies and Integration Points

It integrates with container lookup, runtime liveness probing, runtime log reopening, and CRI `ReopenContainerLogRequest`.

## Risks and Edge Cases

There is a race between the alive check and runtime reopen. Stopped containers return a generic error. Runtime-specific log path or conmon behavior is delegated.

## Test Signals

The paired test covers invalid container ID. Additional tests should cover not-running containers, liveness check errors, runtime reopen errors, and successful reopen.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_reopen_log.go -->
