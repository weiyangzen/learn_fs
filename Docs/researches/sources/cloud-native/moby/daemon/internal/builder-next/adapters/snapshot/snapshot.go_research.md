<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/adapters/snapshot/snapshot.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/adapters/snapshot/snapshot.go

Purpose: implements a BuildKit snapshotter over Moby's graphdriver and layer store for the legacy image-store builder path.

Important APIs and control flow: `NewSnapshotter` opens `snapshots.db`, requires a layer store that can register graph IDs, initializes lease refs, and returns a namespaced lease manager. `Prepare` creates graphdriver active snapshots and records original parent. `getLayer` maps chain IDs or committed snapshot keys to layer refs and caches them. `Stat`, `Mounts`, `Commit`, `View`, `Usage`, and `Close` implement snapshotter behavior, with `Remove` forbidden externally and internal `remove` used by the lease manager. `mountable` memoizes mounts with ref counting and identity mapping.

State and persistence: persists snapshot metadata in Bolt buckets, creates/removes graphdriver layers, caches layer refs, creates temporary RW layers for committed layer mounts, and reads/writes cached usage sizes.

Dependencies and integration: used by `newGraphDriverController`, BuildKit cache manager, Moby graphdriver/layer store, and lease manager. It bridges containerd snapshot APIs to Docker graphdriver semantics.

Risks: external `Remove` is forbidden, so cleanup must flow through lease tracking. Bolt bucket names are raw snapshot keys and chain IDs. Mount release functions must be called by consumers or RW layers/graphdriver mounts can leak. The custom snapshotter has partial implementations such as no-op `Walk` and `Update` delegating to `Stat`.

Test signals: no direct tests in this subset; BuildKit graphdriver mode integration tests are the main coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/adapters/snapshot/snapshot.go -->
