<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_reopen_log_test.go -->
# sources/cloud-native/cri-o/server/container_reopen_log_test.go

## Purpose

This suite validates an early failure path for log reopening.

## Important APIs, Types, and Functions

It calls `sut.ReopenContainerLog` with an empty `types.ReopenContainerLogRequest`.

## Control Flow

The test sets up the server and expects the empty request to fail during container lookup.

## State and Persistence Behavior

No state is persisted or changed.

## Dependencies and Integration Points

It depends on the shared server test harness and CRI runtime API types.

## Risks and Edge Cases

Coverage is minimal and does not exercise running-state validation or runtime reopen behavior.

## Test Signals

The test confirms invalid IDs are rejected before runtime log operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_reopen_log_test.go -->
