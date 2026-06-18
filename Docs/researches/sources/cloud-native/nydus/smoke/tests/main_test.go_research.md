# sources/cloud-native/nydus/smoke/tests/main_test.go

## Purpose
This file defines package-level smoke-test setup and teardown. It ensures a registry port is available, optionally starts a local Docker registry, configures logging, runs all tests, and removes the registry container afterward.

## Important APIs, Types, And Functions
Constants define `defaultSnapshotter` and `defaultSnapshotterSystemSock`. `TestMain` reads or defaults `REGISTRY_PORT` to `5077`, starts `tool.NewRegistry` unless `DISABLE_REGISTRY` is set, sets log flags/output, runs `m.Run`, destroys the registry if started, and exits with the test code.

## Control Flow
The setup runs before any package test. Environment defaults are set first because image preparation helpers depend on `REGISTRY_PORT`. The registry lifetime encloses `m.Run`.

## State And Persistence
The file mutates process environment and starts a Docker `registry:2` container. The registry container ID is held in memory and removed after tests. If the process is killed before teardown, Docker cleanup relies on the container's `--rm` behavior only when it exits.

## Dependencies And Integration Points
It integrates all image-based suites with `tool.Registry` and Docker. The default snapshotter constants are reused by takeover/performance-related tests.

## Risks
Starting a registry is global package state and may conflict with an existing service on the chosen port. `DISABLE_REGISTRY` shifts responsibility to the caller to provide a reachable registry. The teardown always exits the process, so deferred cleanup in `TestMain` itself is not used.

## Test Signals
No direct assertions are present, but a successful setup permits registry-backed image tests to run. Failures surface as fatal environment setting errors or registry command failures.
