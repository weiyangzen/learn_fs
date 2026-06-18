# sources/cloud-native/soci-snapshotter/service/service.go

Purpose: this file is the service-level constructor for the SOCI snapshotter. It converts `config.ServiceConfig` and optional dependency injection into a configured filesystem plus snapshotter implementation.

Important APIs and types: `Option` mutates private `options`. `WithCredsFuncs` adds registry credential providers. `WithCustomRegistryHosts` allows a caller to override registry resolution entirely. `WithFilesystemOptions` passes lower-level filesystem options through to `fs.NewFilesystem`. `NewSociSnapshotterService` is the main constructor. `Supported` delegates host capability checks to overlay snapshotter support. `snapshotterRoot` and `fsRoot` define the root subdirectories.

Control flow: constructor options are applied first. If registry hosts are not supplied, it constructs a `resolver.RegistryManager` from retry and resolver config. It detects whether overlay should use `userxattr`, then maps that to SOCI layer opaque-marker handling. It builds source resolution from default labels plus registry hosts and appends filesystem options for source lookup, overlay opaque type, pull modes, and optional max concurrency. After `socifs.NewFilesystem`, it builds snapshotter options: asynchronous remove by default, optional min layer size, restart invalid-mount tolerance, parallel pull, and experimental parallel-pull-as-fallback. Finally it calls `snapshot.NewSnapshotter`.

State and persistence: service state is delegated to filesystem root `<root>/soci` and snapshotter root `<root>/snapshotter`. The service itself persists no additional data.

Dependencies and integration points: integrates config, resolver, `fs`, `fs/layer`, `fs/source`, `snapshot`, and containerd overlay utilities. The resulting value implements containerd `snapshots.Snapshotter` and is intended to be registered by the daemon plugin.

Risks: constructor errors from filesystem or snapshotter creation are logged with `Fatalf`, which exits the process rather than returning an error in those cases. The warning for experimental parallel fallback correctly surfaces GC edge cases when lazy-load and parallel-pull share a content store. User xattr detection failures continue with the default boolean value, so mount behavior depends on overlayutils defaults.

Test signals: no direct test in this subset. Behavior is indirectly exercised by snapshot and filesystem tests. Constructor-level tests would be useful for option propagation, fatal paths, and root path derivation.
