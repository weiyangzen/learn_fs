# sources/cloud-native/containerd/plugins/services/streaming/service.go

## Purpose
This file implements the bidirectional streaming gRPC service used by containerd transfer and other stream-based APIs.

## Important APIs, Types, And Functions
The plugin ID is `streaming` and requires the streaming manager plugin. `service.Stream` registers a `serviceStream` with the `streaming.StreamManager`. `serviceStream` implements `Send`, `Recv`, and `Close` over `api.Streaming_StreamServer`. `emptyResponse` caches a marshalled empty protobuf response.

## Control Flow
The stream RPC expects the first received message to unmarshal as `api.StreamInit`. It registers the stream ID, sends an empty acknowledgement, then waits for either context cancellation or `serviceStream.Close`. `Send` and `Recv` normalize gRPC errors with `errgrpc.ToNative`.

## State And Persistence
All state is in-memory. A channel signals stream closure. No payload data is persisted by this service.

## Dependencies And Integration Points
It depends on `typeurl` marshalling, core streaming manager interfaces, gRPC stream APIs, and protobuf empty responses. Transfer progress uses this service to deliver progress events.

## Risks
There is no timeout waiting for the initial stream init message. Registering duplicate IDs depends on manager behavior. The double `errgrpc.ToNative` branch for non-EOF errors is harmless but redundant.

## Test Signals
No direct tests are included. Integration with transfer progress streams is the likely coverage.
