<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_exec_test.go -->
# sources/cloud-native/cri-o/server/container_exec_test.go

## Purpose

This suite tests CRI exec endpoint setup and the streaming exec callback.

## Important APIs, Types, and Functions

It uses `sut.Exec`, `testStreamService.Exec`, `testContainer.StartExecCmd`, and a local `mockExecStarter` implementing the exec starter interface.

## Control Flow

The tests verify endpoint setup succeeds for a known container and fails for an empty request. Stream tests verify missing containers fail, running containers pass the `Living` gate even if the mock runtime later errors, stopped containers fail the living check, and exec start is allowed while a container is marked stopping but before the kill loop has begun.

## State and Persistence Behavior

State is in the test harness in-memory container and sandbox maps. No persistent files are written.

## Dependencies and Integration Points

The suite depends on CRI types, runtime-spec state constants, remotecommand resize channels, and internal `oci.Container` state behavior.

## Risks and Edge Cases

It does not exercise the websocket runtime-handler path, stdin/stdout/stderr plumbing, tty resize handling, or actual runtime exec success.

## Test Signals

The most important signal is that exec eligibility follows container liveness and termination-state semantics rather than only the high-level CRI request path.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_exec_test.go -->
