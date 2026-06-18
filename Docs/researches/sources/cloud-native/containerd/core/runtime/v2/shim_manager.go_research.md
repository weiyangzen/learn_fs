# sources/cloud-native/containerd/core/runtime/v2/shim_manager.go

## Purpose
Registers and implements the v2 shim manager plugin, which resolves shim binaries, starts or reuses shim instances, tracks them by namespace, and exposes cleanup/delete operations.

## APIs, Flow, State, Dependencies, Risks, And Tests
`ShimConfig` configures environment and socket directory. Plugin init validates or chooses a short socket dir, opens metadata/event stores, and returns `NewShimManager`. `ManagerConfig` and `ShimManager` hold containerd addresses, env, runtime path cache, shim map, event exchange, container store, sandbox store, and shim info cache.

`Start` decides whether to reuse a sandbox shim or invoke a shim binary. It uses sandbox metadata/address/version when possible, writes `sandbox` and `bootstrap.json` into the task bundle for sandbox reuse, otherwise calls `startShim`. `startShim` resolves the runtime path, builds a shim binary command wrapper, starts it with runtime options, and installs dead-shim cleanup callbacks. `restoreBootstrapParams` migrates legacy `address` files into `bootstrap.json`. `resolveRuntimePath` accepts absolute executable paths, rejects relative paths, resolves runtime names to shim binary names, and caches results. `loadShimInfo` calls runtime `-info` and extracts mount types handled by custom shims.

Persistent state includes bundle files `sandbox`, `bootstrap.json`, optional legacy `address`, and runtime path cache in memory. Dependencies include plugin registry, metadata stores, events, sandbox store, shim binary helpers, typeurl, timeout, and versioned config migration.

Risks include socket path limits, stale runtime path cache after upgrades, misdetecting sandbox API support, duplicate cleanup callbacks, and legacy config migration surprises. Tests include runtime path resolution, sandbox reuse/invocation integration, bootstrap migration, mount annotation handling, and plugin config migration.
