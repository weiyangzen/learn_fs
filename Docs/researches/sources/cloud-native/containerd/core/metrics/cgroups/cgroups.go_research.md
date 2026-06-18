# sources/cloud-native/containerd/core/metrics/cgroups/cgroups.go

Purpose: registers the Linux cgroups task monitor plugin and selects the cgroup v1 or v2 monitor implementation at initialization time.

Important APIs and types: `Config` with `NoPrometheus`, package `init` registering `plugins.TaskMonitorPlugin` ID `cgroups`, and `New` as plugin init function.

Control flow: plugin registration declares an event plugin dependency and migrates the previous plugin config name into the current task monitor config key. `New` creates a Docker metrics namespace unless Prometheus is disabled, obtains the event publisher, selects v2 when `cgroups.Mode() == cgroups.Unified` otherwise v1, registers metrics namespace when enabled, records the default platform, and returns the task monitor.

State and persistence: no persistent state. Runtime state is the selected monitor and registered Prometheus namespace.

Dependencies and integration: integrates with containerd plugin registry, events publisher, runtime task monitor interface, Docker metrics registry, cgroups mode detection, config migration, and platform metadata.

Risks: metrics namespace registration is global and should not be duplicated unexpectedly in tests. Selection depends on host cgroup mode, so behavior differs by environment. Disabling Prometheus still returns a monitor but collectors become inert.

Test signals: indirectly covered by `metrics_test.go`, which instantiates v1/v2 collectors based on cgroup mode; plugin registration itself is not directly tested here.
