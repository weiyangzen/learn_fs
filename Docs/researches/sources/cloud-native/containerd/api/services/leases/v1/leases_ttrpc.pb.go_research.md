# sources/cloud-native/containerd/api/services/leases/v1/leases_ttrpc.pb.go

## Purpose

This generated file binds the Leases service to ttrpc. It is the local lightweight transport equivalent of the gRPC binding.

## Important APIs, Types, and Functions

`TTRPCLeasesService` requires `Create`, `Delete`, `List`, `AddResource`, `DeleteResource`, and `ListResources`. `RegisterTTRPCLeasesService` registers service name `containerd.services.leases.v1.Leases` with method handlers. `TTRPCLeasesClient`, `ttrpcleasesClient`, and `NewTTRPCLeasesClient` implement client calls through `ttrpc.Client.Call`.

## Control Flow

Each server handler unmarshals into the concrete request type and delegates to the service. Each client method allocates the expected response type, calls the named method, and returns the response or error. All RPCs are unary.

## State and Persistence Behavior

No state is persisted here. The ttrpc binding transports lease operations to service code that manages metadata references and garbage-collection protection.

## Dependencies and Integration Points

Dependencies are `context`, `github.com/containerd/ttrpc`, and `emptypb`. It integrates with containerd ttrpc servers/clients and shares generated protobuf types with `leases.pb.go`.

## Risks and Test Signals

Risks include ttrpc/gRPC parity drift, method-name drift, and unmarshal failures that occur before service validation. Tests should cover all six methods over ttrpc, malformed payload handling, parity with gRPC, and compile/regeneration checks.
