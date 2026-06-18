# sources/cloud-native/buildkit/frontend/gateway/forwarder/forward.go

## Purpose

This file adapts an in-process `frontend.FrontendLLBBridge` into the public gateway `client.Client` interface. It lets Go frontends run locally against the BuildKit solver without going through the stdio gRPC protocol.

## Important APIs, Types, And Functions

- `LLBBridgeToGatewayClient` constructs a `BridgeClient`.
- `BridgeClient` embeds `FrontendLLBBridge` and implements `client.Client`.
- `Solve`, `ResolveImageConfig`, `BuildOpts`, `Inputs`, `Warn`, and `NewContainer` implement gateway client operations.
- `wrapSolveError` and `registerResultIDs` translate solver errors into gateway solve errors with result IDs.
- `toFrontendResult`, `discard`, and `discardMounts` convert returned client results back to frontend results and release resources.
- `ref` implements `client.Reference` over a `solver.ResultProxy`.

## Control Flow

`Solve` delegates to `FrontendLLBBridge.Solve`, rejects callback-based attestations, converts each solver result proxy to a gateway `ref`, and records refs for later cleanup. `NewContainer` resolves mount refs in parallel, builds server-side container mount requests, parses extra hosts, gets the default cache manager, and calls `container.NewContainer`. Reference filesystem methods lazily mount worker refs through `snapshot.LocalMounter` and call `cacheutil` read/stat helpers.

Error wrapping captures exec, file-action, and slow-cache errors, registers involved worker refs as IDs, and wraps the original error with solve subject metadata. `toFrontendResult` converts gateway references back to solver proxies by splitting result proxies so returned refs remain valid after bridge cleanup. `discard` releases containers, mounters, worker refs, result proxies, and on error also releases result proxy clones.

## State And Persistence Behavior

`BridgeClient` tracks refs, worker refs by ID, containers, and mounted snapshot mounters. A mutex protects ref registration and result conversion, while a separate mutex protects mount cache. State is per build invocation and must be discarded at the end. Mounters persist until `discardMounts`; repeated reads reuse the same mounter by result ID.

## Dependencies And Integration Points

It integrates frontend interfaces, gateway client interfaces, container implementation, solver error types, worker refs, sessions, cache utilities, snapshots, API caps, identity IDs, and source metadata resolver. `forwarder/frontend.go` uses it to implement `GatewayForwarder`.

## Risks And Edge Cases

Resource ownership is subtle: result proxies are split and released differently on success versus error; worker refs from solve errors are registered so clients can mount them later. NewContainer's loop captures range values using Go's per-iteration variables, which is safe in modern Go but would have been risky in older versions. `discardMounts` ignores unmount errors. Attestation callbacks cannot cross this boundary and fail solve/return conversion.

## Test Signals

Frontend integration tests exercise reference reads through this bridge. There are no direct unit tests for error wrapping, resource discard, or container creation in this subset; those would be valuable because lifecycle bugs can leak refs or mounts.
