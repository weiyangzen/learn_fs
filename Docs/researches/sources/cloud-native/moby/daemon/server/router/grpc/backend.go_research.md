# sources/cloud-native/moby/daemon/server/router/grpc/backend.go

## Purpose
`backend.go` defines the registration contract for services exposed through the deprecated `/grpc` upgrade endpoint.

## Important APIs, Types, And Functions
`Backend` has one method, `RegisterGRPC(*grpc.Server)`, allowing each service provider to register its gRPC service definitions.

## Control Flow
The gRPC router constructs a server and calls this method for each backend during router initialization.

## State And Persistence
The interface itself has no state. Registration mutates the in-memory `grpc.Server`.

## Dependencies And Integration Points
Depends only on `google.golang.org/grpc`.

## Risks
Registration order and duplicate service registration are implementation concerns hidden behind this interface.

## Test Signals
Compilation and endpoint integration tests validate that backends register cleanly.
