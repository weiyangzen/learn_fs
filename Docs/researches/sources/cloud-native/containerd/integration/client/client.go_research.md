# sources/cloud-native/containerd/integration/client/client.go

## Purpose
This file provides shared integration client test globals and helpers.

## Important APIs, Types, and Functions
Constants and variables define `testNamespace`, address flag, stdio path, test snapshotter, and daemon handle. `testContext` creates a namespace-scoped context and optional test logger. `createShimDebugConfig` writes a temporary containerd config enabling runtime v1 shim debug.

## Control Flow
`init` registers the `-address` flag. `testContext` uses `context.WithCancel`, sets namespace, and attaches `logtest` when a test is provided. `createShimDebugConfig` writes TOML and exits the process on failure.

## State and Persistence
The shim debug config is a temp file. Globals are shared across integration tests and initialized by `TestMain` in `client_test.go`.

## Dependencies and Integration Points
Used by all integration client tests, daemon setup, and platform-specific defaults.

## Risks
`createShimDebugConfig` exits directly on file errors. Context creation cannot use `t.Context` yet, as noted by the comment.

## Test Signals
Harness support file; correctness is indicated by the integration suite starting and using the expected namespace/config.
