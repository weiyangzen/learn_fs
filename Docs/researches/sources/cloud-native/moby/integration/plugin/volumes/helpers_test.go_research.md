# sources/cloud-native/moby/integration/plugin/volumes/helpers_test.go

## Purpose
Shared helper utilities for volume plugin integration tests. It builds local plugin binaries, creates plugin fixtures with a socket path, and marks plugin configs as Docker volume drivers.

## Important APIs, Types, And Functions
`pluginBuildLock` serializes per-binary builds. `ensurePlugin` resolves GOPATH (default `/go`), builds `./cmd/<name>` to `$GOPATH/bin/<name>` with static/GOPATH-mode settings, and returns the binary. `createPlugin` applies socket and binary options, wraps creation in a 60-second timeout, and calls fixture `plugin.Create`. `asVolumeDriver` sets capability `{Prefix:"docker", Capability:"volumedriver", Version:"1.0"}`.

## Control Flow
Tests request a plugin alias and binary; the helper builds if needed and creates a daemon plugin fixture. Timeout limits plugin fixture creation.

## State And Persistence Behavior
Built binaries persist under GOPATH. Created plugin fixtures persist in daemon state until removed by caller cleanup.

## Dependencies And Integration Points
Depends on the Go toolchain, GOPATH or `/go`, plugin fixture helpers, and Docker plugin capability metadata.

## Risks
Build environment issues can fail tests. GOPATH-mode build must remain compatible with the command sources. Shared binary output requires lock discipline.

## Test Signals
Failures surface as build errors or plugin fixture creation errors before caller tests proceed.
