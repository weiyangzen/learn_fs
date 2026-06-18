# sources/cloud-native/containerd/plugins/services/images/service.go

## Purpose
Registers the gRPC images service adapter.

## Important APIs, Types, And Functions
`service` wraps `imagesapi.ImagesClient` and implements `Register`, `Get`, `List`, `Create`, `Update`, and `Delete`.

## Control Flow
Startup retrieves the local images service and returns a gRPC server wrapper. RPC methods forward directly to the local client.

## State And Persistence
No direct state; metadata persistence is handled by the local image service.

## Dependencies And Integration Points
Requires service plugin and registers with the gRPC server.

## Risks
All validation, GC, and storage behavior is delegated to the local client.

## Test Signals
No direct tests.
