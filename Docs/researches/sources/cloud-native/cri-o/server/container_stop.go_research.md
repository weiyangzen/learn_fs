<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_stop.go -->
# sources/cloud-native/cri-o/server/container_stop.go

## Purpose

This file implements CRI container stopping, including idempotency, runtime-handler hooks, NRI stop notification, storage unmount, and state persistence.

## Important APIs, Types, and Functions

`StopContainer(ctx, req)` is the CRI RPC. `stopContainer(ctx, ctr, timeout)` performs the stop. `postStopCleanup(ctx, ctr, sb, hooks)` unmounts storage, runs post-stop hooks, sends NRI stop, and persists state.

## Control Flow

The RPC resolves the container by short ID. Missing IDs return success for CRI idempotency if the truncation index reports not-exist; other lookup errors become `NotFound`. It then calls `stopContainer`. The internal function retrieves the sandbox and hooks, runs `PreStop`, calls runtime `StopContainer` with the timeout, then runs cleanup. Cleanup attempts storage stop/unmount, logs post-stop hook errors without failing, sends NRI stop, and writes container state to disk last.

## State and Persistence Behavior

Runtime state changes to stopped through the runtime, storage is unmounted via storage runtime server, NRI state may be updated, and container state is persisted to disk after post-stop cleanup. No name/index removal happens here.

## Dependencies and Integration Points

It depends on CRI idempotency semantics, truncindex errors, runtime stop API, storage runtime stop API, runtime-handler hooks, NRI, sandbox lookup, and `ContainerStateToDisk`.

## Risks and Edge Cases

Pre-stop hook errors abort stopping. Post-stop hook and storage unmount errors are logged but do not prevent the response if runtime stop succeeded. Persisting state last avoids reporting stopped before cleanup but means a crash during cleanup can leave disk state stale.

## Test Signals

Tests cover a successful stop path with a mock runtime stop and idempotent success for a missing ID. They do not cover hook errors, storage unmount failures, NRI behavior, or timeout handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_stop.go -->
