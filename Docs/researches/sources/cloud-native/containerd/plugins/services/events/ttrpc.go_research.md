# sources/cloud-native/containerd/plugins/services/events/ttrpc.go

## Purpose
Implements the TTRPC subset of the events service, currently forwarding event envelopes.

## Important APIs, Types, And Functions
`ttrpcService` holds the exchange. `Forward` converts TTRPC request envelope and forwards it. `fromTProto` converts API envelope to core event envelope.

## Control Flow
TTRPC server invokes `Forward`, which delegates to exchange forwarding and returns an empty response or gRPC-compatible error.

## State And Persistence
No persistence; event exchange is in-memory.

## Dependencies And Integration Points
Registered from `events/service.go` via `RegisterTTRPC`. Uses TTRPC events API, core events, protobuf timestamps, and errgrpc conversion.

## Risks
Only forwarding is exposed over TTRPC, not subscribe/publish. Payload type compatibility is delegated to event consumers.

## Test Signals
No direct tests.
