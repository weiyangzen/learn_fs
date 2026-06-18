# sources/cloud-native/containerd/internal/cri/server/container_events.go

## Purpose
This file implements the CRI `GetContainerEvents` streaming RPC by forwarding events from the service’s container event queue to the gRPC stream.

## Important APIs, Types, and Functions
`(*criService).GetContainerEvents` subscribes to `c.containerEventsQ`, defers closing the subscription, and calls `s.Send(event)` for each event received.

## Control Flow, State, and Persistence
The method is a long-running stream. Its only state is the queue subscription and stream backpressure/error handling. It exits when the queue channel closes or when `Send` returns an error.

## Dependencies and Integration Points
It integrates with lifecycle methods that call `generateAndSendContainerEvent`, including create, start, remove, and exit handling. The public contract is Kubernetes CRI event streaming.

## Risks and Test Signals
Risks are missed close cleanup, stream error propagation, and queue backpressure. There are no direct tests in this subset; event generation is indirectly exercised by lifecycle code paths.
