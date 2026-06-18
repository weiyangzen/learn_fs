<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/ttrpcutil/client.go -->
# sources/cloud-native/containerd/pkg/ttrpcutil/client.go

## Purpose
Reconnectable TTRPC client wrapper for containerd daemon services.

## Important APIs, Types, And Functions
Client, NewClient, Reconnect, EventsService, Client, and Close.

## Control Flow
NewClient builds a connector that dials with a five-second timeout. Client lazily connects under a mutex. Reconnect closes old client and reconnects unless closed. EventsService wraps the current client.

## State And Persistence
Maintains in-memory ttrpc client pointer, connector, mutex, and closed flag. Network connection is external state.

## Dependencies And Integration Points
Used by shim RemoteEventsPublisher to forward events to containerd ttrpc services.

## Risks And Edge Cases
Close marks closed, but Client does not check closed before lazy initial connect; Reconnect does. Connector nil would make Reconnect fail.

## Test Signals
No direct tests in subset; publisher paths exercise it indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/ttrpcutil/client.go -->
