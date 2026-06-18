# sources/cloud-native/containerd/core/runtime/v2/shim_load.go

## Purpose
Reloads existing shim processes from the runtime state directory after containerd restarts and cleans stale work directories.

## APIs, Flow, State, Dependencies, Risks, And Tests
`LoadExistingShims` scans namespace directories in `stateDir`, calls `loadShims` per namespace, and then `cleanupWorkDirs` in the persistent root. `loadShims` scans bundle directories concurrently, skips hidden entries, drops empty or unreadable bundles, and calls `m.loadShim`. `m.loadShim` resolves the runtime from `shim-binary-path` or container metadata, reconnects to the shim via `loadShimTask`, and cleans leaked shims that have no sandbox record and no process list. `loadShimTask` verifies task service connectivity via `PID`, downgrading client version on `ErrNotImplemented`. `cleanupWorkDirs` removes root work dirs that have no live shim.

State inputs are filesystem bundle directories, optional `shim-binary-path`, bootstrap files, metadata container records, sandbox records, and the in-memory namespace shim map. Cleanup mutates bundle/work directories and may publish cleanup events through dead-shim cleanup.

Dependencies include namespaces, mount unmounting, errgroup concurrency, runtime `GOMAXPROCS`, metadata stores, shim binary deletion, and timeouts.

Risks include deleting bundles that are temporarily unreadable, failing to load one namespace while continuing others, races with live shim exit, wrong runtime resolution after metadata loss, and stale workdir removal after state loss. Tests should cover restart reload, empty bundle cleanup, legacy bootstrap migration, leaked shim cleanup, and namespace isolation.
