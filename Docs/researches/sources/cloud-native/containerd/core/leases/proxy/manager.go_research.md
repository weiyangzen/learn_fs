# sources/cloud-native/containerd/core/leases/proxy/manager.go

## Purpose

This file implements a `leases.Manager` backed by the generated gRPC leases service client. It lets callers use the core leases interface against a remote containerd service.

## Important APIs, Types, and Functions

`NewLeaseManager(client)` returns a `leases.Manager`. `proxyManager` implements `Create`, `Delete`, `List`, `AddResource`, `DeleteResource`, and `ListResources`. It converts between core `leases.Lease`/`leases.Resource` and API protobuf messages.

## Control Flow

`Create` applies lease options locally, sends a `CreateRequest`, converts gRPC errors to native errors, and maps the response timestamp through `protobuf.FromTimestamp`. `Delete` applies delete options and sends `DeleteRequest` with `Sync`. `List` sends filters and maps every response lease. Resource methods send the lease ID plus one resource or list response resources.

## State and Persistence Behavior

The proxy stores only the generated client. Persistent lease state lives on the remote service. Delete sync behavior is passed through to the server.

## Dependencies and Integration Points

It integrates generated leases API clients, core leases interfaces, `errgrpc.ToNative`, and protobuf timestamp conversion. It is used by clients communicating with containerd over gRPC.

## Risks and Edge Cases

The proxy trusts caller-provided lease/resource IDs and relies on server validation. It does not defensively copy label maps from responses. Only gRPC clients are supported here; ttrpc lease proxying would need a separate adapter. Option application errors stop before RPC.

## Test Signals

Tests should use a fake leases client to verify request fields, option application, timestamp conversion, error conversion, resource mapping, synchronous delete propagation, and list filter forwarding.
