# sources/cloud-native/containerd/plugins/services/containers/service.go

## Purpose
Registers the gRPC containers service as a thin adapter over the local containers client.

## Important APIs, Types, And Functions
`service` embeds `UnimplementedContainersServer` and implements `Register`, `Get`, `List`, `ListStream`, `Create`, `Update`, and `Delete`.

## Control Flow
Startup gets the local containers service by ID and wraps it. gRPC methods forward to the local client. `ListStream` receives from the local stream until EOF or context cancellation and sends each item to the gRPC stream.

## State And Persistence
No direct state. Persistence is handled by the local containers service.

## Dependencies And Integration Points
Requires service plugin, registers with the main gRPC server, and bridges API server/client interfaces.

## Risks
Context cancellation in `ListStream` returns nil, which can hide client-side cancellation details. All validation is delegated to local service.

## Test Signals
No direct tests here.
