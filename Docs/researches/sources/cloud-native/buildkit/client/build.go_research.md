# sources/cloud-native/buildkit/client/build.go

## Purpose

This file implements the high-level client `Build` API and the build-scoped gateway client wrapper. It lets callers run a custom frontend/gateway build function inside a BuildKit solve while ensuring gateway RPCs carry the active build ID and respect negotiated capabilities.

## Important APIs, Types, and Functions

- `Client.Build` prepares frontend options, worker metadata, a gateway callback, and delegates to `c.solve`.
- `gatewayClientForBuild` wraps `gatewayapi.LLBBridgeClient` with a build ID and optional capability set.
- `GatewayClientForBuild` exposes a build-scoped gateway client for advanced callers.
- Gateway wrapper methods include `ResolveImageConfig`, `ResolveSourceMeta`, `Solve`, `ReadFile`, `ReadDir`, `StatFile`, `Evaluate`, `Ping`, `Return`, `Inputs`, container lifecycle, container filesystem, `ExecProcess`, and `Warn`.

## Control Flow and State

`Build` always closes `statusChan` when it returns. It captures frontend attrs, clears `opt.Frontend` so the custom build function drives the frontend, defaults the product string, and lists workers to pass worker metadata into the gateway client. The callback passed to `solve` merges frontend options from the daemon into the caller's frontend attrs, constructs a gateway client scoped to the build reference, creates a grpc gateway frontend client, stores negotiated capabilities on the wrapper, and runs the caller's `buildFunc`.

Every gateway RPC appends the build ID to outgoing gRPC metadata through `buildid.AppendToOutgoingContext`. Some methods check capabilities before making the RPC. `Evaluate` has a compatibility fallback: when `CapGatewayEvaluate` is missing but `CapStatFile` exists, it uses `StatFile` on `.` to force evaluation and returns an empty evaluate response.

State is mostly per-call. The wrapper holds the build ID and a pointer to negotiated capabilities.

## Dependencies and Integration Points

This API integrates the public client package, gateway frontend client, gRPC bridge protobuf API, build ID metadata helpers, session handling, API capability sets, worker listing, and the lower-level `solve` method defined elsewhere. It is heavily exercised by gateway integration tests in `build_test.go`.

## Risks and Edge Cases

`feOpts` points to `opt.FrontendAttrs` and is mutated by `maps.Copy`, so caller-provided maps can be modified. `Build` calls `ListWorkers` before running the build function; worker-list failure prevents custom frontend execution. Capability checks are wrapper-side and must be updated as new gateway methods are added. The `Warn` method ignores variadic call options when forwarding, unlike most other methods.

## Test Signals

`build_test.go` validates successful gateway solve, build option propagation, missing/unknown build ID behavior, warnings, gateway filesystem and container APIs, capability-gated paths, and many failure/release scenarios.
