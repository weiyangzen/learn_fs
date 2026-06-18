<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_portforward_test.go -->
# sources/cloud-native/cri-o/server/container_portforward_test.go

## Purpose

This suite tests basic port-forward endpoint creation and an early stream failure.

## Important APIs, Types, and Functions

It calls `sut.PortForward` with CRI `PortForwardRequest` and `testStreamService.PortForward`.

## Control Flow

One case requests a streaming endpoint with a sandbox ID and port and expects success. Another omits the sandbox ID and expects setup failure. The stream callback is invoked with a sandbox ID that is not present and should return an error.

## State and Persistence Behavior

Only the in-memory test harness is used. No network namespace or runtime forwarding is established.

## Dependencies and Integration Points

The tests depend on the server test harness and CRI runtime API types.

## Risks and Edge Cases

They do not test sandbox readiness, empty netns paths, stream draining, or successful runtime forwarding.

## Test Signals

The tests confirm that the endpoint setup validates required request fields and that the stream path does not proceed without a resolved sandbox.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_portforward_test.go -->
