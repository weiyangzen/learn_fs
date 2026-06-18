# sources/cloud-native/containerd/core/metrics/metrics.go

Purpose: initializes core containerd metrics metadata and default timeout settings.

Important APIs and data: constant `ShimStatsRequestTimeout` and package `init`.

Control flow: `init` creates a `containerd` metrics namespace, registers a labeled `build_info` counter with `version` and `revision`, increments it once, registers the namespace globally, and sets the shim stats request timeout to two seconds.

State and persistence: global metrics registry state and global timeout registry state; no disk persistence.

Dependencies and integration: depends on containerd version data, Docker metrics, and timeout package. The cgroup v1/v2 collectors use `ShimStatsRequestTimeout` when calling task stats.

Risks: initialization has global side effects at import time. Consumers relying on stats calls need to account for the two-second timeout.

Test signals: indirectly used by collector tests through timeout context creation; no direct tests in subset.
