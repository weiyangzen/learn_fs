# sources/cloud-native/cri-o/internal/config/node/cgroups_linux.go

Purpose: detects host cgroup mode and controller availability for Linux CRI-O configuration validation and resource application.

Important APIs/types/functions: `CgroupIsV2`, `CgroupHasMemorySwap`, `CgroupHasHugetlb`, `CgroupHasPid`, and `checkRelevantControllers`. Package globals cache results and errors via `sync.Once`: memory swap, controller lookup, hugetlb, pid, and cgroup v2 errors.

Control flow: `CgroupIsV2` calls `cgroups.IsCgroup2UnifiedMode` each time and stores the error. `CgroupHasMemorySwap` is once-only; on cgroup v2 it parses `/proc/self/cgroup` and checks `memory.swap.current` under `/sys/fs/cgroup`, while cgroup v1 checks `memory.memsw.limit_in_bytes`. `CgroupHasHugetlb` and `CgroupHasPid` call `checkRelevantControllers`, which reads all subsystems and marks `pids`/`hugetlb` when present.

State and persistence behavior: caches detection booleans/errors in package globals. Reads kernel pseudo-filesystems but writes nothing.

Dependencies/integration points: uses `github.com/opencontainers/cgroups` and `go.podman.io/common/pkg/cgroups`. `node.ValidateConfig` and container resource setup consume these booleans to fail early or skip unsupported resource fields.

Risks: once-only caching means controller state changes after startup are ignored. Error globals are package-level and can be overwritten for cgroup v2 detection. The cgroup v2 memory swap path assumes `cg[""]` from parsed `/proc/self/cgroup` maps correctly to the unified hierarchy.

Test signals: no local tests in this subset; behavior is indirectly exercised through configuration validation and container resource paths.
