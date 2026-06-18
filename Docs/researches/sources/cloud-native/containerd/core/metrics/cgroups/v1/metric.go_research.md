# sources/cloud-native/containerd/core/metrics/cgroups/v1/metric.go

Purpose: provides the small descriptor/value abstraction used by all cgroup v1 metric definition files.

Important APIs and types: `IDName`, `value`, `metric`, `(*metric).desc`, and `(*metric).collect`.

Control flow: `desc` creates a Prometheus descriptor in the provided Docker metrics namespace with common labels `container_id` and `namespace` plus metric-specific labels. `collect` calls the metric's `getValues`, then emits constant metrics either blocking or non-blocking depending on the caller's `block` flag.

State and persistence: no persistent state. Descriptor construction is repeated per collection call through the namespace helper.

Dependencies and integration: used by v1 CPU, memory, blkio, hugetlb, and pids metric definitions. Depends on Docker metrics namespace and Prometheus.

Risks: non-blocking mode can drop metrics when the channel is full. `MustNewConstMetric` will panic if descriptor/value/label cardinality is inconsistent, so metric definitions must keep labels aligned with emitted values.

Test signals: exercised indirectly by collector collection paths; no isolated tests.
