<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_start_test.go -->
# sources/cloud-native/cri-o/server/container_start_test.go

## Purpose

This suite checks early `StartContainer` validation failures.

## Important APIs, Types, and Functions

It calls `sut.StartContainer` with known and empty container IDs using the shared test harness.

## Control Flow

Cases create a container that is not in created state and expect `StartContainer` to fail, and pass an empty request to expect lookup failure.

## State and Persistence Behavior

Only in-memory test state is used. Runtime start is not invoked in these tests.

## Dependencies and Integration Points

It depends on CRI `StartContainerRequest` and the shared server test setup.

## Risks and Edge Cases

Coverage does not include successful start, start failure cleanup, hooks, events, NRI calls, or restore mode.

## Test Signals

The tests confirm the start path enforces a created-state precondition.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_start_test.go -->
