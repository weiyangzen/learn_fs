<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/controller.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/controller.go

Purpose: constructs the embedded BuildKit controller for either containerd snapshotter mode or legacy graphdriver mode.

Important APIs and control flow: `newController` dispatches by `UseSnapshotter`. `newSnapshotterController` creates history and cache stores, a containerd worker with normalized platforms, GC policy, registry hosts, labels, executor/proxy provider, frontends, cache import/export functions, entitlements, content store, lease manager, tracing, and GC callback. `newGraphDriverController` creates local content/metadata stores, custom graphdriver snapshotter and lease manager, cache manager, image source, executor, Moby exporter, cache/history stores, GC policy, worker, frontends, inline/local cache support, and disables BuildKit merge/diff caps for the legacy backend. Helper functions open history DBs, parse GC policy size strings, convert builder entitlements, add labels, and create CDI managers.

State and persistence: creates and owns BuildKit root directories, Bolt DBs, local content stores, cache metadata, history DBs, snapshot metadata, leases, and worker/controller resources. It cleans up opened resources on constructor errors.

Dependencies and integration: deeply integrates BuildKit control/worker/cache/frontend packages, containerd client/content/metadata, Moby graphdriver/layer/image/reference services, exporters, registry hosts, CDI, tracing, and daemon builder config.

Risks: resource cleanup on partial construction is critical because many DBs, proxy providers, and snapshotters are opened. Graphdriver mode uses a custom compatibility stack and explicitly disables capabilities that require the containerd image store. GC policy parsing depends on unit strings and filter conversion from `builder.go`.

Test signals: no direct tests in this subset; BuildKit controller startup/build/prune tests cover behavior. Local `go test` was unavailable due to missing `go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/controller.go -->
