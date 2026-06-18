<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_events.go -->
# sources/cloud-native/cri-o/server/container_events.go

## Purpose

This file implements CRI container event streaming to connected clients.

## Important APIs, Types, and Functions

`containerEventConn` tracks one stream connection with a done channel, `sync.Once`, and stored error. `GetContainerEvents` registers a CRI stream client and waits until it should terminate. `broadcastEvents` fans events from `s.ContainerEventsChan` to all registered clients.

## Control Flow

If pod events are disabled, `GetContainerEvents` returns immediately. Otherwise, `containerEventStreamBroadcaster.Do` starts the single broadcast goroutine. Each client is stored in `containerEventClients`, waits on its connection channel, then is removed. The broadcaster ranges over `ContainerEventsChan`, sends each event to all current streams, records non-transport-close errors, and closes the affected connection. When the event channel closes, all clients are notified.

## State and Persistence Behavior

State is in-memory only: the client map, connection channels, stored send errors, and the event channel. There is no disk persistence. `done` uses `sync.Once` to avoid double-close panics.

## Dependencies and Integration Points

It integrates with CRI `RuntimeService_GetContainerEventsServer`, server config `EnablePodEvents`, `ContainerEventsChan`, and event generation in create/start/remove paths.

## Risks and Edge Cases

The broadcaster sends synchronously to all clients, so a slow or blocked stream can delay delivery to others. Closed transport errors are treated as expected, but other send errors are returned to that connection only after `wait` unblocks. Channel closure is the global shutdown signal.

## Test Signals

The event tests verify single-client delivery and multi-client fanout. They do not cover disabled events, send errors, slow clients, or channel shutdown races beyond the delayed close helper.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_events.go -->
