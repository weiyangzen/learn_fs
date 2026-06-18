# sources/cloud-native/containerd/core/sandbox/proxy/store.go

## Purpose
Implements `sandbox.Store` by proxying sandbox metadata operations to the containerd sandbox store gRPC API.

## APIs, Flow, State, Dependencies, Risks, And Tests
`NewSandboxStore` wraps an API `StoreClient`. `Create`, `Update`, `Get`, `List`, and `Delete` build corresponding gRPC requests, convert sandbox metadata to/from protobuf with `sandbox.ToProto` and `sandbox.FromProto`, and convert gRPC errors to native errdefs.

The proxy holds no persistent local state; all metadata persistence is remote. Dependencies are sandbox service API, errgrpc, and internal sandbox helper conversion.

Integration points are clients managing sandbox records over the API service. Risks include conversion panics on malformed protobufs, field mask mismatch in `Update`, and remote filtering semantics in `List`. Test signals are fake store client tests for request shapes, error conversion, list conversion, and field path forwarding.
