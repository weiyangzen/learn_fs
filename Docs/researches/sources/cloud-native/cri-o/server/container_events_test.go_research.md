<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_events_test.go -->
# sources/cloud-native/cri-o/server/container_events_test.go

## Purpose

This Ginkgo suite validates container event fanout behavior.

## Important APIs, Types, and Functions

The tests use mock `RuntimeService_GetContainerEventsServer` streams, `sut.ContainerEventsChan`, and `sut.GetContainerEvents`.

## Control Flow

One test sends three events before calling `GetContainerEvents` for a single client and expects each `Send`. Another starts two clients in goroutines, waits for registration, sends the same events, and expects both clients to receive all events. A goroutine closes the event channel after two seconds to unblock stream waits.

## State and Persistence Behavior

All state is in memory. The tests rely on channel buffering/scheduling and mock expectations; no files are written.

## Dependencies and Integration Points

They depend on the server test harness and generated mocks from `test/mocks/containereventserver`.

## Risks and Edge Cases

The tests use sleeps, so timing can be fragile. They do not test send failures, client disconnect handling, disabled events, or cleanup of client map entries.

## Test Signals

The suite confirms that the broadcaster is shared and that events are delivered to all active clients, which is the core contract for CRI event streaming.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_events_test.go -->
