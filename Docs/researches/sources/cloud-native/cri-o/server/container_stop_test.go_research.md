<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_stop_test.go -->
# sources/cloud-native/cri-o/server/container_stop_test.go

## Purpose

This suite tests high-level `StopContainer` behavior.

## Important APIs, Types, and Functions

It calls `sut.StopContainer`, sets container state, and expects mock runtime `StopContainer`.

## Control Flow

The success case creates a container, sets stopped state, expects runtime stop, and calls the RPC. The idempotency case passes a nonexisting ID and expects no error.

## State and Persistence Behavior

State is in-memory plus mocked runtime behavior. The tests do not inspect disk state persistence.

## Dependencies and Integration Points

They depend on gomock, runtime-spec state, CRI stop requests, and the shared harness.

## Risks and Edge Cases

The tests do not exercise pre/post hooks, storage unmount, NRI stop, or timeout propagation.

## Test Signals

The key signal is that CRI stop is idempotent for already removed or unknown containers.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_stop_test.go -->
