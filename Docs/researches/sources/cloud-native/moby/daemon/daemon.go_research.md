# sources/cloud-native/moby/daemon/daemon.go

## Purpose
Defines the central `Daemon` object and most cross-platform daemon lifecycle orchestration: configuration snapshots, startup initialization, container load/restore, image and storage setup, network setup handoff, shutdown, mount/unmount wrappers, disk/network helpers, root creation, namespace remapping, and backend accessors.

## Important APIs, Types, And Functions
- `configStore` embeds `config.Config` plus resolved runtime configuration.
- `Daemon` owns container stores, image service, config pointer, volume service, events, libnetwork controller, containerd clients, plugin manager/store, NRI, CDI cache, metrics helpers, singleflight disk-usage groups, and shutdown/startup state.
- `loadContainers` reads container metadata directories concurrently and groups containers by storage driver.
- `restore` registers loaded containers, migrates old metadata, restores containerd tasks, handles live-restore, updates state, initializes networking with active sandboxes, restarts eligible containers, removes auto-remove/dead containers, and prepares mount points.
- `NewDaemon` wires registry, runtime, plugins, seccomp/AppArmor, containerd, image service, layer store or snapshotter, NRI, container stores, network restore, metrics, and startup completion.
- `Shutdown`, `Mount`, `Unmount`, `networkOptions`, `deriveULABaseNetwork`, `CreateDaemonRoot`, `RemapContainerdNamespaces`, `RawSysInfo`, and backend accessors expose daemon lifecycle and subsystem entrypoints.

## Control Flow
Startup validates daemon settings, resolves temp/root/user namespace paths, loads runtimes, initializes plugin management before restore, configures logging and volumes, verifies Linux devices cgroup when required, loads persisted containers, initializes NRI, selects graphdriver or containerd snapshotter image service, creates libcontainerd, restores containers for the active driver, closes `startupDone`, emits system warnings and engine metrics, then returns the ready daemon. Restore itself is multi-phase: load/register containers, migrate and checkpoint config, reconcile real containerd task state, initialize network controller with active sandboxes, register legacy links, restart containers with dependencies, auto-remove eligible containers, then prepare mount points.

## State And Persistence
This file manages persistent daemon root layout, `containers/` metadata, image stores under graphdriver or containerd, reference stores, distribution metadata, identity caches, plugin roots, tmp directories, policy verifier state, container checkpoint saves, network state, metrics, and event service lifetime. It also preserves daemon ID through `LoadOrCreateID` and may migrate image metadata from graphdriver to containerd snapshotter.

## Dependencies And Integration Points
It integrates with containerd, graphdriver/layer store, snapshotter service, image service, libcontainerd, libnetwork, plugin manager/executor, volume service, registry service, NRI, CDI, stats, OpenTelemetry/grpc interceptors, BuildKit/distribution backends, policy verifier, sysinfo, SELinux, AppArmor/seccomp platform hooks, and OS-specific helpers from Unix/Linux/Windows files.

## Risks And Edge Cases
Initialization order is delicate: plugins must exist before restore, networking waits for active sandbox discovery, and shutdown must stop containers/layers before plugins. Restore tolerates missing RW layers so users can remove broken containers. Live-restore intentionally preserves running containers and active sandboxes, but network config changes do not apply while active sandboxes exist. Snapshotter migration only occurs under strict no-container/size conditions. `prepareTempDir` asynchronously deletes old temp data. `Mount` treats inconsistent mount paths as fatal except on Windows.

## Test Signals
`daemon_test.go` covers container lookup/name ambiguity, config merge, invalid isolation, invalid port zero, network error typing, deterministic ULA derivation, and symlinked root resolution. Startup and restore are primarily integration-tested because they require containerd, graphdriver, networking, and plugin dependencies.
