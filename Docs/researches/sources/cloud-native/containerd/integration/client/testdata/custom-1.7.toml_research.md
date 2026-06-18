<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/testdata/custom-1.7.toml -->
# sources/cloud-native/containerd/integration/client/testdata/custom-1.7.toml

## Purpose
Fixture representing a customized containerd 1.7-era config used to verify migration into the current default config while preserving selected user-provided values.

## APIs, Types, And Functions
This is TOML consumed by `containerd -c testdata/custom-1.7.toml config migrate` from `migration_test.go`. It uses version 2 config tables for root/state, cgroup, debug, grpc, metrics, CRI, CNI, runtime, registry, NRI, snapshotters, stream processors, timeouts, and ttrpc.

## Control Flow And State
There is no executable flow inside the fixture. Migration reads the file, drops removed settings, normalizes plugin layout, applies new defaults, and preserves custom values such as `sandbox_image = "custom.io/pause:3.10.2"`, `stream_idle_timeout = "2h0m0s"`, `stream_server_address = "127.0.1.1"`, `stream_server_port = "15000"`, and `enable_tls_streaming = true`.

## Persistence And Integration Points
The fixture models persistent daemon configuration. Comments mark settings that were removed or changed in later releases, including tracing, runtime v1, zfs/aufs, CriuPath, NoPivotRoot, SystemdCgroup, and transfer unpack config defaults.

## Risks And Test Signals
Its value is as a regression oracle: if it drifts from expected historical shape, migration tests may fail for fixture reasons rather than code reasons. It specifically signals whether migration preserves user intent while removing obsolete keys and adopting newer defaults like CDI/NRI enablement.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/testdata/custom-1.7.toml -->
