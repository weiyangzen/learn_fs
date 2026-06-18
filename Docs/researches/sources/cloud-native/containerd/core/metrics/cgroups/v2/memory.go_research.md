# sources/cloud-native/containerd/core/metrics/cgroups/v2/memory.go

Purpose: declares cgroup v2 memory and memory-events metrics for usage, swap, file/page activity, reclaim, slab, transparent huge page, working set, and OOM counts.

Important APIs and data: `memoryMetrics` includes `memory_usage`, `memory_usage_limit`, `memory_swap_usage`, `memory_swap_limit`, file dirty/writeback/mapped metrics, page activation/refill/scan/steal/fault metrics, active/inactive anon/file, anon/file/kernel/slab/socket/shmem fields, THP counters, workingset counters, and `memory_oom` from `MemoryEvents.Oom`.

Control flow: each metric checks `stats.Memory` or `stats.MemoryEvents` before reading fields and emits one unlabeled gauge value.

State and persistence: no state; stateless projection from cgroup v2 stats payloads into Prometheus samples.

Dependencies and integration: depends on v2 stats aliases, Docker metrics units, Prometheus gauges, and v2 collector.

Risks: like v1, many kernel counters are exposed under bytes units due to existing metric conventions. `memory_oom` is a gauge of the cgroup v2 events counter, not the eventfd-based counter used by v1.

Test signals: not directly value-tested; nil-safe behavior is indirectly covered by empty stats collection.
