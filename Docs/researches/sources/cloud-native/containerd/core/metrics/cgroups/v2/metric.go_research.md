# sources/cloud-native/containerd/core/metrics/cgroups/v2/metric.go

Purpose: provides the descriptor/value abstraction used by all cgroup v2 metric definition files.

Important APIs and types: `IDName`, `value`, `metric`, `(*metric).desc`, and `(*metric).collect`.

Control flow: `desc` creates descriptors with common labels `container_id` and `namespace` plus metric-specific labels. `collect` calls `getValues` and emits constant metrics either blocking or non-blocking.

State and persistence: no persistent state.

Dependencies and integration: used by v2 CPU, memory, IO, and pids metric files. Depends on Docker metrics namespace and Prometheus.

Risks: label cardinality mismatches panic through `MustNewConstMetric`. Non-blocking mode can drop samples when used.

Test signals: indirectly exercised by v2 collector paths.
