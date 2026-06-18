# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_runnetwork_test.go

## Purpose
This file validates Dockerfile `RUN --network` modes and global network forcing. It registers `runNetworkTests` into `networkTests` and uses an environment variable gate for tests that require host networking behavior.

## Important APIs, Types, and Functions
Tests are `testRunDefaultNetwork`, `testRunNoNetwork`, `testRunHostNetwork`, and `testRunGlobalNetwork`. They use `echoserver.NewTestServer`, `entitlements.EntitlementNetworkHost`, `AllowedEntitlements`, `FrontendAttrs{"force-network-mode": "host"}`, sandbox values such as `network.host`, `workers.IsTestDockerd`, and rootless/platform skips.

## Control Flow and Assertions
Default/no-network tests build BusyBox Dockerfiles that inspect `eth0`, with rootless conditions handled specially. Host-network tests start a local echo server, run `nc 127.0.0.1 <port>` in a `RUN --network=host` step, and optionally assert a normal RUN cannot reach it. The solve includes network-host entitlement and then branches on sandbox policy: granted must succeed, denied must fail with an entitlement error except in dockerd-specific behavior. The global network test forces host mode through frontend attrs, then checks explicit `--network=none` still blocks the connection.

## State, Persistence, and Dependencies
State is transient: temp Dockerfiles and a local echo server. Tests depend on Linux networking, sandbox network policy labels, worker entitlement enforcement, BusyBox `ip`/`nc`, and an opt-in environment variable for some network integration cases.

## Integration Points
The file tests frontend parsing of `--network`, frontend attr forced network mode, solver entitlement checks, worker network namespace behavior, rootless differences, and dockerd integration differences.

## Risks and Test Signals
Risks include host entitlement bypass, `--network=none` not isolating, forced network mode overriding explicit none, rootless behavior drifting, and test flakiness from local port reachability. Signals are solve success/failure, exact entitlement error text, and real TCP echo-server reachability.
