# sources/control-plane/rook/pkg/daemon/ceph/client/config_test.go

Purpose: validates default Ceph config rendering and config override merging.

Important test cases: `TestCreateDefaultCephConfig` constructs a `ClusterInfo` with FSID, monitor secret, namespace, and two internal monitors, then verifies `CreateDefaultCephConfig()` fills `MonMembers` and `MonHost`. `TestGenerateConfigFile` creates a temporary config directory and fake Kubernetes ConfigMap named `rook-config-override`, then calls `generateConfigFile()` and reloads the result with `ini.Load()` to confirm both default `fsid` and override `bluestore_min_alloc_size_hdd` exist. Helpers `verifyConfig()` and `verifyConfigValue()` perform order-tolerant checks.

Control flow and dependencies: tests use `test.New()` fake clientset, `go-ini`, `t.TempDir()`, and direct construction of `ClusterInfo`. The override path exercises Kubernetes API reads inside `mergeDefaultConfigWithRookConfigOverride()`.

Risks and coverage gaps: the tests cover happy paths for config generation but not failure paths for invalid ConfigMap INI, missing clientset, filesystem permission failures, `ROOK_CEPH_VERSION` parsing, out-of-quorum monitor exclusion, v2-only monitor formatting, or `WriteCephConfig()` copying to the default config path. `verifyConfig()` accepts a `loggingLevel` argument that is unused, suggesting leftover behavior from older logging config tests. The tests correctly avoid assuming map iteration order for monitors.
