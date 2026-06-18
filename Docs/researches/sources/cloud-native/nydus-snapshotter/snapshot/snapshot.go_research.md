<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/snapshot.go -->
## sources/cloud-native/nydus-snapshotter/snapshot/snapshot.go

Purpose: implements the containerd `snapshots.Snapshotter` for nydus. It wires config, daemon managers, cache, metrics, system controller, tarfs/stargz/index/referrer features, and the snapshot lifecycle operations.

Important APIs/types: `snapshotter`, `NewSnapshotter`, `Cleanup`, `Stat`, `Update`, `Usage`, `Mounts`, `Prepare`, `View`, `Commit`, `Remove`, `Walk`, `Close`, path helpers, parent-layer finders, snapshot creation/recovery helpers, tarfs merge, mount builders, cleanup helpers, and `treatAsProxyDriver`.

Control flow and state: `NewSnapshotter` initializes signature verification, Bolt store, recovery policy, optional cgroups, per-driver managers, metrics, filesystem, cache manager, optional index/referrer/tarfs managers, credential renewal, system controller/pprof, d_type validation, metadata store, snapshot root, and removal flags. `Prepare` creates an active snapshot then delegates behavior to `chooseProcessor`, committing skipped read-only layers when needed. `Mounts` and `View` detect nydus/tarfs/proxy/index/referrer cases and choose remote or native mounts. `Commit` records disk usage and commits active snapshots. `Remove` deletes metadata and optionally synchronously cleans orphan directories. `Cleanup` removes orphan snapshot dirs and unused cache blobs. `createSnapshotWithRecovery` can recreate proxy-mode placeholder parents when the local metadata DB lost a parent known to containerd.

Dependencies/integration: central integration with containerd storage, filesystem/daemon managers, labels, config globals, cache, metrics, system API, tarfs, cgroups, signature verification, and Linux filesystem behavior.

Risks and test signals: broad blast radius. Cgroup error condition uses `&&` where `||` may have been intended, potentially returning on supported fallback errors. Lazy parent recovery only supports proxy mode. Cleanup of cache blobs depends on filename parsing and daemon RAFS `UnderlyingFiles`. Tests in `snapshot_test.go` cover only `mountNative` and volatile option behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/snapshot.go -->
