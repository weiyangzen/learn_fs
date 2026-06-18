# sources/cloud-native/buildkit/frontend/frontend.go

## Purpose

This file defines the core BuildKit frontend contracts shared by gateway and non-gateway frontends. It keeps the interface between solver, executor, session manager, source metadata resolver, and frontend implementations compact.

## Important APIs, Types, And Functions

- `KeySource` is the gateway frontend option key for the external frontend image/source.
- `KeyDevelDeprecated` rejects the old development gateway mode.
- `Result` aliases `result.Result[solver.ResultProxy]`.
- `Attestation` aliases `result.Attestation[solver.ResultProxy]`.
- `Frontend` is implemented by frontend backends and exposes `Solve`.
- `FrontendLLBBridge` combines source metadata resolution, solver `Solve`, and warning reporting.
- `SolveRequest`, `CacheOptionsEntry`, and `WarnOpts` alias gateway client request types.

## Control Flow

The file is declarative. Runtime control flow is in implementations such as `gatewayFrontend.Solve` and forwarders. The `Frontend.Solve` signature passes an LLB bridge, executor, option map, frontend inputs, session ID, and session manager to concrete frontends.

## State And Persistence Behavior

There is no mutable state. Type aliases stabilize package boundaries and avoid duplicate structures across frontend/gateway code.

## Dependencies And Integration Points

It integrates with `sourceresolver.MetaResolver`, BuildKit `executor`, gateway client types, sessions, solver result proxies, solver protobuf definitions, and digest-based warning APIs. It is the common contract used by gateway forwarding and image-based frontends.

## Risks And Edge Cases

Because aliases point to gateway client types, changes in gateway client request structures affect the general frontend interface. Implementations must honor session ID and session manager lifetimes because the interface exposes both.

## Test Signals

No direct tests are needed for the type alias file, but integration tests under `frontend_test.go` exercise frontend callbacks and gateway client behavior through this interface.
