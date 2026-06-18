# sources/cloud-native/cri-o/test/mocks/containereventserver/containereventserver.go

## Purpose
Generated GoMock for the CRI streaming server interface `RuntimeService_GetContainerEventsServer`.

## Important APIs, Types, And Functions
Generic `MockRuntimeService_GetContainerEventsServer[Res]` with methods `Context`, `RecvMsg`, `Send`, `SendHeader`, `SendMsg`, `SetHeader`, and `SetTrailer`.

## Control Flow
Delegates all gRPC server-stream operations to GoMock.

## State And Persistence
In-memory expectations only.

## Dependencies And Integration Points
Used by container event stream tests to verify `ContainerEventResponse` sending and gRPC metadata behavior.

## Risks And Test Signals
Mocks gRPC stream contracts but not real network backpressure or client cancellation beyond whatever context is provided by tests.
