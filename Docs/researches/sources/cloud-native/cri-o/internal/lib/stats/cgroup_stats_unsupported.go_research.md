# sources/cloud-native/cri-o/internal/lib/stats/cgroup_stats_unsupported.go

Purpose: non-Linux placeholder for cgroup statistics. It defines an empty `CgroupStats` type so packages compile where opencontainers cgroup stats are unavailable. There are no functions, state, or persistence. Integration is selected by `!linux` build tag and paired with unsupported statsserver behavior. Risks are callers expecting populated fields on unsupported platforms, so platform-specific code must avoid Linux-only conversions. Test signals are compile-time platform coverage rather than runtime assertions.
