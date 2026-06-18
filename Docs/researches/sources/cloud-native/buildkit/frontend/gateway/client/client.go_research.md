# sources/cloud-native/buildkit/frontend/gateway/client/client.go

## Purpose

This file defines the public gateway client API implemented by in-process forwarders and by the gRPC frontend client. It is the contract external frontends use to solve LLB, resolve image metadata, access inputs, create containers, read refs, and emit warnings.

## Important APIs, Types, And Functions

- `Result` and `Attestation` alias generic result types parameterized by gateway `Reference`.
- `BuildFunc` is the callback signature for gateway frontends.
- `NewResult` returns an empty result.
- `Client` includes metadata resolution, `Solve`, image config resolution, build options, inputs, `NewContainer`, and `Warn`.
- `NewContainerRequest`, `Mount`, `Container`, `StartRequest`, `ContainerProcess`, and `WinSize` define gateway exec behavior.
- `Reference`, `ReadRequest`, `ReadDirRequest`, and `StatRequest` define filesystem operations on solved refs.
- `SolveRequest.Clone` deep-copies mutable solve request fields.
- `BuildOpts` exposes option map, session ID, worker info, product, and API/LLB capabilities.
- `WarnOpts` carries warning source ranges, detail, and URL.

## Control Flow

This file mainly declares interfaces and value objects. `SolveRequest.Clone` performs the only substantial control flow: it clones the definition, frontend options, frontend input definitions including nil preservation, cache import entries and their attributes, and source policies.

## State And Persistence Behavior

The types are request/response carriers. Persistent state is held by concrete implementations. `Clone` prevents unintended aliasing of nested mutable maps, slices, definitions, and source policies when callers need to mutate a request copy.

## Dependencies And Integration Points

The API bridges `llb`, `sourceresolver`, solver protobuf definitions, source policies, API capabilities, Open Containers platforms, filesystem stat structures, and process I/O. Both `forwarder.BridgeClient` and `grpcclient.grpcClient` implement this contract.

## Risks And Edge Cases

Implementations must honor capability checks for optional features. `Mount` permits either `Ref` or `ResultID`, so concrete implementations need type and existence validation. `Clone` must stay current as fields are added; missing deep copies would cause mutation leaks. `ContainerProcess` exposes asynchronous resize/signal operations, so lifecycle race handling belongs to implementations.

## Test Signals

`client_test.go` verifies `SolveRequest.Clone` deep-copies `FrontendInputs`, preserves nil entries, clones `FrontendOpt`, and prevents metadata mutation in clones from leaking to originals.
