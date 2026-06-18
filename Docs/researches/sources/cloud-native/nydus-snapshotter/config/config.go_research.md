# sources/cloud-native/nydus-snapshotter/config/config.go

Purpose: central TOML schema, default merging, validation, CLI override, and cgroup config parsing.

APIs/types: defines daemon modes, recover policies, fs drivers, failover policies, and nested `SnapshotterConfig` sections for daemon, logging, snapshot, remote auth/mirrors, cache, metrics, system controller, cgroup, image, and experimental tarfs/stargz/index detection.

Flow/state: `LoadSnapshotterConfig` requires version 1. `MergeConfig` uses mergo defaults. `ValidateConfig` checks signature keys, root length, fs driver, recover/failover policy, thread limit, auth exclusivity, and mirror dir. `ParseParameters` applies CLI overrides. `ParseCgroupConfig` converts memory settings using total memory.

Integration points: main binary, tests, global config, daemonconfig.

Risks/tests: zero-value merge behavior means explicit false/zero TOML values can be hard to distinguish. Tests cover loading, merge, log-to-stdout override, processing, and root length.
