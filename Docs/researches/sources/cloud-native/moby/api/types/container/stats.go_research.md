<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/container/stats.go -->
# sources/cloud-native/moby/api/types/container/stats.go

## Purpose
Defines the container stats stream payload covering CPU, memory, block I/O, network, PID, and
storage counters.

## Important APIs, Types, And Functions
- Exported types: ThrottlingData, CPUUsage, CPUStats, MemoryStats, BlkioStatEntry, BlkioStats, StorageStats, NetworkStats, PidsStats, StatsResponse.
- `ThrottlingData` fields include Periods, ThrottledPeriods, ThrottledTime.
- `CPUUsage` fields include TotalUsage, PercpuUsage, UsageInKernelmode, UsageInUsermode.
- `CPUStats` fields include CPUUsage, SystemUsage, OnlineCPUs, ThrottlingData.
- `MemoryStats` fields include Usage, MaxUsage, Stats, Failcnt, Limit, Commit, CommitPeak, PrivateWorkingSet.
- `BlkioStatEntry` fields include Major, Minor, Op, Value.
- Wire JSON fields include blkio_stats, commitbytes, commitpeakbytes, cpu_stats, cpu_usage, current, endpoint_id, failcnt, id, instance_id, io_merged_recursive, io_queue_recursive, io_service_bytes_recursive, io_service_time_recursive, io_serviced_recursive, io_time_recursive, io_wait_time_recursive, limit, and others.
- Source comments highlight: ThrottlingData stores CPU throttling stats of one running container. CPUUsage stores All CPU stats aggregated since container inception. CPUStats aggregates and wraps all CPU related info of container
- The structs are pure wire contracts populated by the daemon and decoded by clients for `docker stats` and API consumers.

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `time`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Carries timestamp or duration fields that must remain JSON-compatible across daemon/client boundaries.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.
- Duration and timestamp fields need stable units and timezone/zero-value behavior across API versions.

## Test Signals
- Package-level tests include `config_test.go`, `health_test.go`, `hostconfig_test.go`, `hostconfig_unix_test.go`, `state_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/container/stats.go -->
