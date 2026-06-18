# sources/cloud-native/containerd/plugins/services/introspection/service.go

## Purpose
Registers the gRPC introspection service adapter.

## Important APIs, Types, And Functions
`server` wraps `introspection.Service` and implements `Register`, `Plugins`, `Server`, and `PluginInfo`.

## Control Flow
Startup loads the local introspection service, updates its root from the current plugin context, and returns the gRPC wrapper. RPC methods forward to local service and convert errors. `PluginInfo` unmarshals optional typeurl options before forwarding.

## State And Persistence
No direct state beyond updating the local service root. UUID persistence is handled by `local.go`.

## Dependencies And Integration Points
Requires service plugin, gRPC, typeurl, errgrpc, and introspection API types.

## Risks
Startup requires the service implementation to be `*Local`; alternative implementations fail. Malformed options cause request failure before plugin lookup.

## Test Signals
No direct tests.
