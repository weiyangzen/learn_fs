# sources/cloud-native/buildkit/frontend/gateway/forwarder/frontend.go

## Purpose

This file wraps a gateway `client.BuildFunc` as a BuildKit `frontend.Frontend`. It is the lightweight in-process frontend adapter.

## Important APIs, Types, And Functions

- `NewGatewayForwarder` returns a `frontend.Frontend` backed by worker info and a build callback.
- `GatewayForwarder` stores worker info and the callback.
- `(*GatewayForwarder).Solve` constructs a `BridgeClient`, invokes the callback, and converts the result back to a frontend result.

## Control Flow

`Solve` calls `LLBBridgeToGatewayClient`, defers `c.discard(retErr)` so resources are released after result conversion or error, runs the callback, returns callback errors directly, and converts successful gateway results using `toFrontendResult`.

## State And Persistence Behavior

The forwarder itself only stores worker info and callback. Per-build state is held in `BridgeClient` and discarded at the end of `Solve`.

## Dependencies And Integration Points

It connects the generic frontend interface, executor, session manager, solver protobuf definitions, worker info, and gateway client build callbacks. It is used when BuildKit embeds a Go gateway frontend rather than launching a frontend image.

## Risks And Edge Cases

The deferred discard receives named return values so resource release can know whether the build failed. If result conversion returns an error, cloned result proxies are released by discard. Returning nil gateway results is allowed and converts to nil frontend results.

## Test Signals

`frontend_test.go` validates nil and empty gateway frontend results through integration builds.
