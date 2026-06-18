<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/rootless/specconv/specconv_linux.go -->
# sources/cloud-native/moby/daemon/internal/rootless/specconv/specconv_linux.go

Purpose: mutates OCI runtime specs to be compatible with rootless Docker and rootful-in-rootless Docker.

Important APIs and types: `ToRootfulInRootless`, `ToRootless`, `getCurrentOOMScoreAdj`, `toRootless`, `isHostNS`, `bindMountHostProcfs`, `bindMountHostIPC`, and `removeSysfs`.

Control flow: rootful-in-rootless only raises `OOMScoreAdj` to at least the daemon's current value. Full rootless conversion removes unsupported cgroup settings when no cgroup v2 controllers are delegated, prunes resource sections for missing controllers when delegated, clears devices/hugepage/network resources, raises OOMScoreAdj, detects host PID/IPC/network namespaces, bind-mounts host `/proc`, `/dev/shm`, and `/dev/mqueue` where needed, and removes sysfs mounts for host networking with RootlessKit detached netns.

State and persistence: mutates the passed `specs.Spec` in memory. Reads `/proc/self/oom_score_adj`, namespace symlinks, and RootlessKit state.

Dependencies and integration: used before creating rootless containers with runc. Depends on rootless namespace helpers, OCI specs, `/proc`, and Docker logging.

Risks: namespace detection compares symlink targets and returns host namespace if a namespace type is absent from the spec. Slice filtering mutates mount/path slices in place. Missing controller handling must stay aligned with runtime/kernel support. Removing sysfs is conditional on detecting an existing sysfs mount.

Test signals: no direct tests in this subset; high-value coverage would include cgroup controller pruning and host namespace mount rewrites.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/rootless/specconv/specconv_linux.go -->
