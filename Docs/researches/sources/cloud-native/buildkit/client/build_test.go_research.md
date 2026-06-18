# sources/cloud-native/buildkit/client/build_test.go

## Purpose

This file is a broad integration test suite for the client gateway build API and gateway container/debug APIs. It validates custom frontend execution, build ID scoping, warnings, result handling, container lifecycle, exec and TTY behavior, mounts, secrets, error debugging, entitlements, networking, credential cancellation, and empty-result/image edge cases.

## Important APIs, Types, and Functions

- `TestClientGatewayIntegration` registers the main Linux gateway integration matrix.
- Gateway solve tests: `testClientGatewaySolve`, `testWarnings`, `testClientGatewayFailedSolve`, `testClientGatewayEmptySolve`, `testNoBuildID`, and `testUnknownBuildID`.
- Container lifecycle and exec tests: `testClientGatewayContainerCancelOnRelease`, pipe tests, PID1 failure/exit tests, TTY tests, signal tests, and `testPrompt`.
- Mount/secret/platform tests: `testClientGatewayContainerMounts`, `testClientGatewayContainerSecretEnv`, and `testClientGatewayContainerPlatformPATH`.
- Debug/error tests: `testClientSlowCacheRootfsRef`, `testClientGatewayExecError`, `testClientGatewaySlowCacheExecError`, and `testClientGatewayExecFileActionError`.
- Entitlement/network tests: security mode and host networking variants.
- Registry/auth edge test: `testClientGatewayCanceledCredentialsCallbackReturns` with `blockingAuthProvider`.
- Result edge tests: `testClientGatewayNilResult` and `testClientGatewayEmptyImageExec`.

## Control Flow and State

The suite creates BuildKit clients against integration sandboxes, then invokes `Client.Build` with custom gateway build functions. The basic solve test checks product and frontend attrs, solves an LLB graph, reads the result through the gateway ref, exports locally, and checks final content. Warning tests capture status messages and verify warning fields including source info, ranges, detail, URL, and level.

Container tests solve `busybox`, create gateway containers with bind/cache/tmpfs/secret/SSH/local mounts, start PID1 and exec processes, pipe stdio, resize TTYs, send signals, release containers, and verify cancellation/resource cleanup through `checkAllReleasable`. Debug tests intentionally fail solve operations and use returned `SolveError` mount/input IDs to recreate containers over failed exec or file-operation refs and inspect intermediate filesystem state.

Entitlement tests run the same container API with security and network modes while toggling allowed entitlements, expecting success or explicit validation errors. The credential cancellation test sets up a registry proxy and a blocking auth session provider to ensure canceled image config resolution does not remain stuck behind credentials callbacks. Edge tests cover nil results from merge-diff and executing from an intentionally empty pushed image.

State includes temporary directories, local session mounts, SSH agent sockets, secret providers, registry fixtures, HTTP proxy fixtures, and interactive pipe buffers. All state should be released by each test through client close, container release, process wait, and integration cleanup.

## Dependencies and Integration Points

The suite depends on the public `client` package, gateway client interfaces, LLB builders, solver error definitions, protobuf mount/security/network types, session auth/secrets/SSH providers, fsutil local mounts, integration worker feature gates, mirrored images, registry fixtures, echoserver fixtures, gRPC status helpers, and Linux process semantics.

## Risks and Edge Cases

The tests are integration-heavy and Linux-centric; many skip outside Linux or without feature gates. TTY tests use prompt polling and fixed timeouts, which can be sensitive to slow workers. Host networking tests are disabled unless `BUILDKIT_RUN_NETWORK_INTEGRATION_TESTS` is set. Several tests intentionally return errors from build functions and assert the outer build error, so cleanup paths are as important as success paths. The auth cancellation test has a deliberately blocking provider and time-based fallback, making it useful for deadlock detection but sensitive to timing.

## Test Signals

This file is the primary behavioral signal for `client/build.go` and a broad regression suite for gateway APIs. It validates build ID metadata routing, capability gating, warning propagation, filesystem reads/stats, container process semantics, entitlement enforcement, debug ref reconstruction, and release hygiene.
