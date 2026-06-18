# sources/cloud-native/containerd/core/metrics/cgroups/v2/cgroups.go

Purpose: implements the cgroup v2 runtime task monitor, wiring tasks into the v2 Prometheus collector.

Important APIs and types: `NewTaskMonitor`, `cgroupsMonitor`, `Monitor`, and `Stop`.

Control flow: `NewTaskMonitor` creates a v2 collector and returns a monitor with context and publisher fields. `Monitor` adds the runtime task to the collector. `Stop` removes it from collection.

State and persistence: runtime-only collector task map; no persistent state. The publisher field is stored for parity with v1 but not used in this file.

Dependencies and integration: integrates runtime `TaskMonitor`, event publisher type, Docker metrics namespace, and the v2 collector.

Risks: cgroup v2 OOM is collected from memory events stats rather than event-published through this monitor, so behavior differs from v1. The unused publisher/context fields may mislead readers expecting v2 task OOM event publication here.

Test signals: indirectly exercised by collector concurrency test on unified cgroup hosts.
