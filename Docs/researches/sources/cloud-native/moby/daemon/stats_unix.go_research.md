# sources/cloud-native/moby/daemon/stats_unix.go

## Purpose
`stats_unix.go` converts containerd/cgroups metrics into Docker API stats responses on non-Windows platforms and reads host CPU counters.

## Important APIs, Types, And Functions
`stats` obtains a running task and dispatches metrics to `statsV1` or `statsV2`. `copyBlkioEntry`, `statsV1`, `statsV2`, `getNetworkSandboxID`, `getNetworkStats`, `getSystemCPUUsage`, and `readSystemCPUUsage` implement conversion and host/network augmentation.

## Control Flow
The daemon locks the container long enough to obtain a running task, reads task stats, builds a `StatsResponse`, then converts cgroup v1 or v2 metrics. Network stats resolve container-network namespace sharing chains before querying libnetwork sandbox statistics. CPU usage scans `/proc/stat`, sums aggregate CPU ticks, converts to nanoseconds, and counts per-CPU lines.

## State And Persistence
No state is persisted. It reads containerd metrics, libnetwork sandbox stats, and `/proc/stat`; it uses `daemon.machineMemory` to cap memory limit reporting.

## Dependencies And Integration Points
Depends on containerd cgroups v1/v2 stats, containerd errdefs, API container stats, daemon containers, libnetwork sandbox statistics, and `/proc/stat` format.

## Risks
Metric schema differences between cgroup v1 and v2 are substantial. Missing task stats map to not-found for API compatibility. Network-mode container chains can fail if referenced containers disappear. CPU parsing assumes cpu lines are at the start and fields are valid integers.

## Test Signals
`stats_unix_test.go` verifies `/proc/stat` parsing. Docker stats integration tests cover cgroup conversion and network stats.
