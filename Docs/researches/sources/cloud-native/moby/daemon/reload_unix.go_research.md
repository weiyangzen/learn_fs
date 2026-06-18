# sources/cloud-native/moby/daemon/reload_unix.go

## Purpose
Provides Unix platform-specific daemon reload for runtimes, default shared memory size, cgroup namespace mode, and IPC mode.

## Important APIs, Types, And Functions
`reloadPlatform` mutates `configStore` fields and calls `setupRuntimes`. It builds event attributes for configured runtimes, default runtime, default shm size, default IPC mode, and default cgroup namespace mode.

## Control Flow
The hook applies supplied default runtime and runtime map, reconstructs the `Runtimes` runtime resolver, applies `default-shm-size`, `default-cgroupns-mode`, and `default-ipc-mode` when set, then renders runtime attributes by iterating configured runtime paths.

## State And Persistence
Only the reload copy (`newCfg`) is changed during prepare. The live daemon sees changes after `Reload` stores the new config. Runtime wrapper scripts may be created by `setupRuntimes`.

## Dependencies And Integration Points
Depends on daemon config and `runtime_unix.go` setup. It is called from `Daemon.Reload` only on Linux/FreeBSD builds.

## Risks And Edge Cases
Runtime setup is fallible and aborts the whole reload. Attribute rendering only includes `Config.Runtimes` entries and their paths, not implicit stock runtimes or type-only runtime options.

## Test Signals
Runtime setup and wrapper behavior are covered by `runtime_unix_test.go`; reload tests exercise general reload transaction paths.
