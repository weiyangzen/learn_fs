# sources/cloud-native/cri-o/server/rootless_linux.go

Purpose: adjusts generated OCI specs for rootless CRI-O execution on Linux.

Important APIs and functions: `hasNetworkNamespace`, `makeOCIConfigurationRootless`, and `getAvailableV2Controllers`.

Control flow: removes device cgroup rules, then prunes memory/CPU/cpuset/pids/io/rdma/hugetlb resource settings when cgroup v2 delegation lacks the required controller. It clears OOM score and AppArmor profile, removes `gid=` mount options, bind-mounts host `/sys` read-only when no network namespace is present, and clears Linux cgroups path.

State and persistence: mutates the in-memory OCI generator spec. Reads `/proc/self/cgroup` and `/sys/fs/cgroup/.../cgroup.controllers` to detect delegated controllers.

Dependencies and integration: uses opencontainers cgroups/runtime-spec/generate, CRI-O cgroup manager paths, and rootless environment handling in sandbox creation.

Risks: missing or unreadable cgroup controller files cause nil controller maps and broad resource pruning. The hugetlb warning text says RDMA limit, likely a copy-paste issue. Rootless behavior depends on accurate namespace detection.

Test signals: no direct tests in this subset.
