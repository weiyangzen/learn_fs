<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/nri/nri.go -->
# sources/cloud-native/moby/daemon/internal/nri/nri.go

Purpose: integrates Docker daemon container creation and state synchronization with containerd's NRI framework, allowing trusted plugins to observe containers and apply a limited set of create-time adjustments.

Important APIs and types: `NRI`, `ContainerLister`, `Config`, `NewNRI`, `GetInfo`, `Shutdown`, `PrepareReload`, `CreateContainer`, `syncFn`, `updateFn`, `setDefaultPaths`, `nriOptions`, `containerToNRI`, `stateToNRI`, `applyAdjustments`, `checkForUnsupportedAdjustments`, `applyEnvVars`, and `applyMounts`.

Control flow: startup checks `DaemonConfig.Enable`, fills default plugin/config paths based on rootless state, installs the logging shim, creates an adaptation instance, and starts it. Create notifications convert Docker container state to NRI pod/container objects, call `CreateContainer`, reject update/evict responses, and apply supported adjustments. Plugin sync takes a write lock, snapshots all containers from `ContainerLister`, converts them while locking each container state, invokes the NRI sync callback, and rejects returned updates. Reload prepares a new adaptation and swaps it under lock before starting.

State and persistence: `NRI` holds config and the active adaptation behind an RW mutex. Plugin state is external; Docker container config/hostconfig may be mutated by env and mount adjustments before container creation. Default paths depend on rootless environment.

Dependencies and integration: depends on containerd NRI adaptation, Docker container types, daemon opts, rootless/homedir helpers, Docker version, and system-info API types.

Risks: implementation is intentionally incomplete: many NRI fields are nil/empty, asynchronous updates are not implemented, and most plugin adjustments are rejected. Plugins are trusted and can influence container env/mounts. `stateToNRI` logs at error level for every mapping, which may be noisy. Lock ordering with container state must remain careful during sync.

Test signals: no tests in this subset; coverage should include supported adjustments, rejected unsupported adjustments, reload, rootless path defaults, and sync ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/nri/nri.go -->
