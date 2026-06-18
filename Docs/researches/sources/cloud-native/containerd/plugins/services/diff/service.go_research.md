# sources/cloud-native/containerd/plugins/services/diff/service.go

## Purpose
Registers the gRPC diff service adapter.

## Important APIs, Types, And Functions
`service` wraps a `diffapi.DiffClient` and implements `Register`, `Apply`, and `Diff`.

## Control Flow
Startup gets the local diff service by ID, wraps it, and the main gRPC server later calls `Register`. RPC methods forward directly to the local client.

## State And Persistence
No direct state; underlying diff service and differ implementations perform state changes.

## Dependencies And Integration Points
Requires service plugin and registers with gRPC. Bridges remote API calls to local differ chain.

## Risks
All validation and fallback logic are delegated to the local client.

## Test Signals
No direct tests.
