<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_remove_test.go -->
# sources/cloud-native/cri-o/server/container_remove_test.go

## Purpose

This suite tests high-level `RemoveContainer` behavior.

## Important APIs, Types, and Functions

It calls `sut.RemoveContainer`, uses mock runtime delete expectations, sets container state, and manipulates sandbox stopped state to avoid the stop path in the success case.

## Control Flow

The success test creates a stopped container, expects runtime deletion, marks the sandbox stopped, and removes the container. The missing-container test passes a nonexisting ID and expects no error. The invalid request test passes an empty request and expects an error.

## State and Persistence Behavior

State is in-memory plus mock runtime calls. The suite does not assert storage deletion, index deletion, name release, or sandbox list mutation explicitly.

## Dependencies and Integration Points

It depends on gomock runtime server expectations, runtime-spec state, CRI request types, and the shared test harness.

## Risks and Edge Cases

The success case bypasses stop behavior, so pre-remove stop, post-stop cleanup, and NRI interactions are not tested.

## Test Signals

The key signal is CRI idempotency: removing an already missing container returns success.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_remove_test.go -->
