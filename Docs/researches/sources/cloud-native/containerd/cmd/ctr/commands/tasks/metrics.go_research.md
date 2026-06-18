<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/metrics.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/metrics.go

## Purpose
Fetches and renders a single task metrics sample for cgroup v1, cgroup v2, or Windows stats.

## Important APIs, Types, And Functions
Defines `metricsCommand`, format constants, and table renderers for cgroup and Windows metrics.

## Control Flow
Loads container/task, calls `task.Metrics`, chooses the concrete Any payload by typeurl, unmarshals, then prints table or JSON.

## State And Persistence
Read-only metrics query; no persistence.

## Dependencies And Integration Points
containerd metrics API, typeurl, cgroups v1/v2 stats, hcsshim Windows stats, JSON/tabwriter.

## Risks And Test Signals
Unsupported metric payloads fail hard; table output only prints selected fields. No direct tests here. Source size reviewed: 204 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/metrics.go -->
