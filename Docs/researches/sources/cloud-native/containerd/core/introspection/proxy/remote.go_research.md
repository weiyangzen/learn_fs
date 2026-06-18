# sources/cloud-native/containerd/core/introspection/proxy/remote.go

## Purpose

This file implements a remote introspection service proxy. It adapts supported gRPC or ttrpc client forms into the core `introspection.Service` interface.

## Important APIs, Types, and Functions

`NewIntrospectionProxy(client any)` accepts `api.IntrospectionClient`, `api.TTRPCIntrospectionService`, `grpc.ClientConnInterface`, or `*ttrpc.Client`, returning an `introspection.Service` or panicking on unsupported input. `introspectionRemote` implements `Plugins`, `Server`, and `PluginInfo`. `convertIntrospection` adapts the generated gRPC client to the ttrpc-shaped interface expected internally.

## Control Flow

Construction switches on concrete client type and normalizes it to an `api.TTRPCIntrospectionService`. `Plugins` logs filters and sends a `PluginsRequest`. `Server` sends an empty request. `PluginInfo` marshals non-nil options to protobuf `Any` via typeurl, sends a `PluginInfoRequest`, and converts transport errors to native errdefs errors.

## State and Persistence Behavior

The proxy stores only the remote client. It performs no local persistence and does not cache responses. All state comes from the remote introspection service.

## Dependencies and Integration Points

The proxy integrates generated introspection API clients, gRPC, ttrpc, `errgrpc.ToNative`, `typeurl` option encoding, protobuf `Any`/`Empty`, logging, and the core introspection interface. It is used by clients that need daemon introspection over a transport.

## Risks and Edge Cases

Unsupported client types panic rather than return an error. `PluginInfo` returns a wrapped marshal error before any RPC when options cannot be encoded. The gRPC adapter only forwards calls and relies on caller-provided contexts for deadlines/cancellation. Error conversion is applied to RPC errors, but marshaling errors remain ordinary Go errors.

## Test Signals

Tests should cover each accepted client type, unsupported-type panic, filters passed through `Plugins`, empty request for `Server`, options marshaling in `PluginInfo`, typeurl marshal failure, and gRPC error conversion to native errdefs.
