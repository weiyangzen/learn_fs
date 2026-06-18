# sources/cloud-native/cri-o/internal/lib/container_server.go

## Purpose
Implements CRI-O's core `ContainerServer`: runtime/storage service construction, sandbox/container restore from disk, name/ID indexes, in-memory state management, state persistence, resource updates, shutdown, storage repair/wipe helpers, and monitor probing.

## Important APIs, Types, And Functions
- `ContainerServer` holds runtime, storage, image/runtime services, registrars, truncindexes, hook manager, state stores, config, stats server, and monitor channel.
- Constructor/getters: `New`, `Runtime`, `Store`, `StorageImageServer`, `StorageRuntimeServer`, `CtrIDIndex`, `PodIDIndex`, and `Config`.
- Restore/load: `LoadSandbox`, `LoadContainer`, `restoreVolumes`, `ErrIsNonCrioContainer`.
- Persistence/indexing: `ContainerStateToDisk`, `ReserveContainerName`, `ReleaseContainerName`, `ContainerIDForName`, `ReservePodName`, `ReleasePodName`, `PodIDForName`.
- State operations: `AddContainer`, `AddInfraContainer`, `GetContainer`, `GetInfraContainer`, `HasContainer`, `RemoveContainer`, `RemoveInfraContainer`, `ListContainers`, `AddSandbox`, `GetSandbox`, `GetSandboxContainer`, `HasSandbox`, `RemoveSandbox`, `ListSandboxes`.
- Maintenance: `UpdateContainerLinuxResources`, `ShutdownWasUnclean`, `RemoveStorageDirectory`, `checkQuick`, `CheckReportHasErrors`, `probeMonitorProcesses`, and `Shutdown`.

## Control Flow
`New` validates config, gets storage, optionally repairs or wipes storage after unclean shutdown, creates image/runtime services, OCI runtime, hooks manager, state stores, stats server, and starts monitor probing. `LoadSandbox` reads OCI spec from disk, validates annotations and metadata, reserves pod/container names, reconstructs sandbox fields, creates/restores infra container, restores volumes and namespaces, reloads state from disk, writes state back, reserves labels/IDs, and uses defers to roll back partial state on error. `LoadContainer` reads persisted spec, rejects non-CRI-O containers, reconstructs metadata/image references/kube annotations, requires sandbox presence, creates OCI container, restores volumes/state/spec/runtime path, adds it to state, and indexes ID. State add/remove methods coordinate sandbox membership, stats cleanup, managed namespace cleanup, and platform-specific SELinux bookkeeping.

## State And Persistence
Persists container state JSON through atomic writes to `ctr.StatePath()`. Reads `config.json` and state from storage container directories. Maintains in-memory stores for containers, infra containers, sandboxes, process SELinux level reference counts, registrars, and truncindexes. Storage repair/wipe can mutate or delete the storage graph root. Shutdown closes monitor channel and storage. Monitor probing periodically inspects container monitor processes.

## Dependencies And Integration Points
Integrates CRI-O config, OCI runtime, containers/storage, image/runtime storage services, hooks, stats server, sandbox builder/model, annotations, v2 annotations, hostport mappings, SELinux, memorystore, registrar, truncindex, Kubernetes CRI types, and runtime-spec.

## Risks And Edge Cases
Restore correctness depends on trusted OCI annotations; many malformed annotation cases are guarded. Deferred rollback must release names, namespaces, and IDs on partial failure. `AddContainer` silently ignores containers whose sandbox is absent. `RemoveContainer` leaves a container in state if the sandbox is already gone. Storage wipe is destructive and guarded against running Podman/shared-storage layers unless forced. Monitor goroutine uses jitter but list access must remain safe through memorystore. `UpdateContainerLinuxResources` assumes non-nil `resources.CPU` and `resources.Memory` fields.

## Test Signals
`container_server_test.go` covers constructor failures, getters, sandbox/container load success and many malformed annotation/directory cases, non-CRI-O rejection, state write error, name reservation conflicts, shutdown behavior, add/remove/list state operations, and infra container store operations.
