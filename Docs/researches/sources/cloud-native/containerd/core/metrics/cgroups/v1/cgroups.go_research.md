# sources/cloud-native/containerd/core/metrics/cgroups/v1/cgroups.go

Purpose: implements the cgroup v1 runtime task monitor, wiring the Prometheus collector and v1 OOM event monitor to runtime tasks.

Important APIs and types: `NewTaskMonitor`, `cgroupsMonitor`, `cgroupTask`, `Monitor`, `Stop`, and `trigger`.

Control flow: `NewTaskMonitor` creates the metrics collector and OOM collector. `Monitor` adds the task to the collector, then, if the task exposes `Cgroup()`, obtains the cgroup and registers OOM monitoring. Missing cgroups are ignored; unsupported memory OOM monitoring is logged as a warning and not fatal. `Stop` removes the task from metric collection. `trigger` publishes a `TaskOOM` event under the task namespace.

State and persistence: runtime-only state in collectors and OOM epoll registrations.

Dependencies and integration: integrates runtime tasks, cgroup1 objects, event publisher, namespaces, Docker metrics, errdefs, and the OOM collector.

Risks: `Stop` removes metrics but does not directly deregister OOM fds; OOM collector cleanup relies on cgroup deletion events/state in `oom.go`. Tasks not implementing `cgroupTask` get metrics but no OOM event monitoring.

Test signals: indirectly exercised by collector tests; OOM event path is not directly tested in this subset.
