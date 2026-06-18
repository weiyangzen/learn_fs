# sources/cloud-native/stargz-snapshotter/fusemanager/fusemanager_test.go

## Purpose
Exercises the fuse manager client/server RPC path with a mocked filesystem implementation.

## Important APIs, Types, And Functions
`mockFileSystem` implements `snapshot.FileSystem` methods and records calls/errors. `mockServer` embeds `Server` and overrides `Init` to avoid constructing a real snapshot filesystem. `TestFuseManager` creates Unix sockets, registers the mock server, and runs table-driven client operations.

## Control Flow
For each case, the test sets mock error fields, creates a `NewManagerClient` which triggers `Init`, then for successful cases calls `Mount`, `Check`, and `Unmount`, asserting the mock filesystem methods were called. Init and mount error cases expect client creation or mount paths to return errors.

## State And Persistence
Uses a temporary directory for Unix sockets and Bolt fusestore path. Mock filesystem state is an in-memory mountpoint map. The test defers `fm.Close`, which removes the fusestore file.

## Dependencies And Integration
Depends on grpc, generated protobufs, service config, the real `NewFuseManager`, and real `Client` code. It validates RPC wiring without real FUSE mounts.

## Risks And Test Signals
Signals include successful gRPC init/mount/check/unmount flow and error propagation. Gaps include real `Server.Init`, Bolt restore behavior, process startup, signal shutdown, actual mountinfo checks, and real snapshot filesystem interaction.
