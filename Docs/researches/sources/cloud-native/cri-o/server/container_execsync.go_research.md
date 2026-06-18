<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_execsync.go -->
# sources/cloud-native/cri-o/server/container_execsync.go

## Purpose

This file implements synchronous CRI command execution inside a container.

## Important APIs, Types, and Functions

`Server.ExecSync(ctx, req)` resolves the container, checks liveness, validates that a command is present, and delegates to `Runtime().ExecSyncContainer`.

## Control Flow

The method starts a tracing/log span, resolves a short container ID, maps missing or non-living containers to gRPC `NotFound`, rejects nil command slices with a plain error, and returns the runtime response including stdout, stderr, and exit code.

## State and Persistence Behavior

No durable state is changed. Runtime exec is transient and bounded by the request timeout passed through to the runtime.

## Dependencies and Integration Points

It integrates with CRI `ExecSyncRequest`, container lookup, container liveness logic, gRPC status codes, and the runtime exec-sync implementation.

## Risks and Edge Cases

The code only rejects `nil` command, not an empty non-nil command slice. Runtime timeout and output-size behavior are delegated. Error typing is mixed: container state errors are gRPC statuses, empty command is a regular error.

## Test Signals

The paired test covers invalid container ID only. Additional coverage should include stopped containers, nil versus empty commands, timeout propagation, runtime errors, and successful stdout/stderr/exit-code mapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_execsync.go -->
