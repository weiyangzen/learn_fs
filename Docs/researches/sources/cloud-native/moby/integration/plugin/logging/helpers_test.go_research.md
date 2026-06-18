# sources/cloud-native/moby/integration/plugin/logging/helpers_test.go

## Purpose
Shared helper utilities for logging plugin integration tests. It builds local plugin binaries, creates plugin fixtures, sets socket paths, and marks plugin configs as Docker log drivers.

## Important APIs, Types, And Functions
`pluginBuildLock` serializes builds by plugin name. `ensurePlugin` checks `$GOPATH/bin/<name>`, builds `./cmd/<name>` with `CGO_ENABLED=0` and `GO111MODULE=off` if missing, and returns the binary path. `withSockPath` mutates `plugin.Config.Interface.Socket`. `createPlugin` combines binary/socket options and calls fixture `plugin.Create`. `asLogDriver` sets capability `{Prefix:"docker", Capability:"logdriver", Version:"1.0"}`.

## Control Flow
Tests call `createPlugin`, which builds once per binary and creates a plugin fixture under the requested alias. The build lock prevents concurrent subtests from racing on the same output path.

## State And Persistence Behavior
Built binaries persist under `$GOPATH/bin`. Plugin fixture state is created in the daemon through `plugin.Create`.

## Dependencies And Integration Points
Depends on the Go toolchain, GOPATH, local command sources under `cmd/`, Moby plugin fixture helpers, and logdriver capability metadata.

## Risks
Builds use `GO111MODULE=off`, so command packages must be compatible with GOPATH mode. Missing GOPATH or write permissions can fail tests. Shared binary paths require the lock to avoid races.

## Test Signals
Failures surface as build errors, fixture creation errors, or later plugin enable failures in caller tests.
