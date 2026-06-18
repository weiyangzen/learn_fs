# sources/cloud-native/containerd/core/introspection/introspection.go

## Purpose

This file defines the core introspection service interface used by containerd components. It abstracts access to plugin listings, server metadata, and plugin-specific information.

## Important APIs, Types, and Functions

`Service` is the only exported type. It requires `Plugins(context.Context, ...string)`, `Server(context.Context)`, and `PluginInfo(context.Context, string, string, any)`, returning API protobuf response types from `api/services/introspection/v1`.

## Control Flow

There is no implementation control flow in this file. Concrete local or remote services implement the interface.

## State and Persistence Behavior

The interface owns no state. Implementations may read daemon plugin registry state or remote API responses, but this file only defines the contract.

## Dependencies and Integration Points

It depends on the introspection API protobuf package and `context`. The proxy implementation in `core/introspection/proxy/remote.go` adapts gRPC or ttrpc clients to this interface.

## Risks and Edge Cases

The `PluginInfo` options parameter is `any`, so implementations must agree on typeurl/protobuf encoding and return useful errors for unsupported option types. The variadic filters rely on the API's filter grammar rather than typed filter objects.

## Test Signals

Compile-time conformance of implementations, proxy round trips for all methods, filter propagation, and option marshaling failures are the main signals for this contract.
