<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerfs_linux.go -->
# sources/cloud-native/moby/daemon/containerfs_linux.go

Purpose: creates a private Linux mount-namespace view of a container filesystem so daemon code can run filesystem operations with the container root as `/`, while preserving mount safety and cleanup.

Important APIs and flow: `openContainerFS` mounts the container, sets up volume mounts, starts an unshared `CLONE_NEWNS` goroutine, makes `/` rslave, opens the container root with `os.OpenRoot`, resolves each mount destination through container symlinks, safely creates missing targets with `createIfNotExists`, bind/rbind mounts sources through pinned `/proc/self/fd/<fd>` targets, applies read-only and recursive read-only settings, makes mounts private, switches root with `mounttree.SwitchRoot`, and then processes serialized `future` work items. `RunInFS` synchronously runs a function in the view. `GoInFS` starts a function without waiting for completion. `Close` stops the worker and unmounts volumes/container. `Stat` performs an `Lstat` inside the view and resolves symlink targets in scope. `makeMountRRO` uses `mount_setattr` recursively.

State and persistence: holds a live container mount, private namespace mounts, per-view current working directory, and a goroutine/channel pair. The view is read-write for the container root but tmpfs/private mount behavior is isolated. A finalizer calls `Close` as a fallback.

Dependencies and integration: used by daemon filesystem APIs needing safe container-root context. Depends on daemon mount/setupMounts/unmount, container resource path resolution, `os.Root` protections, Moby mounttree/unshare helpers, sys mount APIs, and symlink scoped resolution.

Risks: this is security-sensitive TOCTOU code. It relies on fd-pinned bind mount targets to prevent symlink swaps, then real paths for remount/propagation because the kernel rejects those on `/proc/self/fd`. `GoInFS` does not wait for function completion. Closing while callers still hold the view can race with pending sends. Recursive read-only fallback logs unless force-recursive is required.

Test signals: `containerfs_linux_test.go` covers only `createIfNotExists`; mount namespace behavior needs privileged/integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerfs_linux.go -->
