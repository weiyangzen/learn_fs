# sources/cloud-native/containerd/plugins/services/events/service.go

## Purpose
Registers the gRPC events service and exposes event publish, forward, subscribe, and TTRPC forwarding.

## Important APIs, Types, And Functions
`NewService` returns an `api.EventsServer`. `service.Register`, `RegisterTTRPC`, `Publish`, `Forward`, `Subscribe`, `toProto`, and `fromProto` implement event service behavior.

## Control Flow
Startup gets the event exchange plugin and returns the service. Publish sends raw topic/event to exchange. Forward converts an envelope and forwards it. Subscribe creates an exchange subscription with filters, loops sending protobuf envelopes until an error or completion.

## State And Persistence
Events are in-memory exchange messages. No persistence is handled by this service.

## Dependencies And Integration Points
Requires event exchange. Registers with both gRPC and TTRPC server plugins. Uses typeurl and protobuf timestamp conversion.

## Risks
Subscribe blocks per stream and returns send/subscription errors. Event payloads depend on typeurl marshaling compatibility.

## Test Signals
No direct tests in this subset.
