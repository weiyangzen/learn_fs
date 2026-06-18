<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/manager_linux.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/manager_linux.go

## Purpose
Implements Linux-specific plugin lifecycle operations around OCI spec creation, executor start/restore/signal, propagated mounts, rootfs setup, shutdown, upgrade, and creation.

## Important APIs, Types, And Functions
Key functions are `enable`, `pluginPostStart`, `restore`, `shutdownPlugin`, `disable`, `Shutdown`, `upgradePlugin`, `setupNewPlugin`, `createPlugin`, and `recursiveUnmount`.

## Control Flow
Enable sets rootfs, builds the plugin OCI spec, records restart control, prepares propagated mount and init layer, invokes the executor, then dials the plugin socket before marking it enabled and calling handlers. Restore either reattaches or restarts depending on live-restore state. Shutdown sends SIGTERM then SIGKILL after timeout. Upgrade backs up rootfs, installs new rootfs/config, and rolls back on failure.

## State, Dependencies, And Integration Points
Mutates persisted plugin JSON and rootfs directories. Depends on OCI spec generation, init layer setup, mount propagation, container executor, Unix signals, plugin clients, and content-store config blobs.

## Risks And Test Signals
Socket readiness uses sleeps/retries. Forced disable with live mounts requires careful unmounting before upgrade/remove. Linux tests cover mount isolation, create failure cleanup, and live-restore startup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/manager_linux.go -->
