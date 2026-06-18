<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/manager.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/manager.go

## Purpose
Defines the core plugin manager: configuration, executor abstraction, persisted plugin reload, event handling, saving, garbage collection, logging streams, and privilege comparison.

## Important APIs, Types, And Functions
Important items are `Executor`, `EndpointResolver`, `ManagerConfig`, `Manager`, `controller`, `NewManager`, `HandleExitEvent`, `reload`, `loadPlugin`, `save`, `GC`, `makeLoggerStreams`, `validatePrivileges`, and `normalizePrivileges`.

## Control Flow
`NewManager` creates root/exec/tmp directories, creates an executor and local content store, reloads saved plugin directories, and initializes pubsub. Reload scans full 64-character IDs, loads `config.json`, restores enabled plugins, migrates propagated mounts, saves updated state, and may re-enable when live restore is off. Exit events remove exec bundles, close exit channels, restart or unmount, and GC removes unused blobs.

## State, Dependencies, And Integration Points
Persists plugin JSON under manager root and blob content under `storage`. Integrates with containerd local content store, runtime executors, Docker events, authorization, pubsub, and atomic writer.

## Risks And Test Signals
Reload and exit handling are concurrency-sensitive. Privilege comparison sorts names and values for order-insensitivity. Tests cover privilege comparison and Linux restore/remove paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/manager.go -->
