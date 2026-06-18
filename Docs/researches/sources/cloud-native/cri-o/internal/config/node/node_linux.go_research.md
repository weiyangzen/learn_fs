# sources/cloud-native/cri-o/internal/config/node/node_linux.go

Purpose: performs early Linux node capability validation for CRI-O startup.

Important APIs/types/functions: `ValidateConfig` iterates a table of checks: hugetlb cgroup, pid cgroup, memory swap cgroup, cgroup v2, systemd `AllowedCPUs`, and `fs.may_detach_mounts`. Each entry has an init function, error pointer, activation pointer, and fatal flag.

Control flow: the function initializes cgroup mode first, then runs each table entry. If an error occurred, fatal entries return an error while nonfatal entries log warnings. If a fatal capability is not activated, it returns an error; if nonfatal inactive, it logs at info level. Successful activation is logged at debug level.

State and persistence behavior: triggers package-level singleton caches in cgroup, systemd, and sysctl helper files. It reads host state but writes nothing.

Dependencies/integration points: integrates with `CgroupHas*`, `CgroupIsV2`, `SystemdHasAllowedCPUs`, and `checkFsMayDetachMounts`. Startup configuration validation calls this to fail before container creation paths rely on missing kernel/systemd features.

Risks: depends on mutable package globals, so tests need isolation if added. Nonfatal checks may hide degraded behavior that later affects resource management. The fatal/nonfatal classification is policy-sensitive.

Test signals: no direct tests in this subset; behavior is indirectly depended on by server config validation.
