# sources/distributed-fs/ceph-client/tools/perf/util/counts.c

Purpose: allocates, resets, and frees per-CPU/per-thread perf counter value arrays attached to evsels.

Important APIs/functions: `perf_counts__new`, `perf_counts__delete`, `perf_counts__reset`, `evsel__reset_counts`, `evsel__alloc_counts`, and `evsel__free_counts`.

Control flow: allocates `struct perf_counts`, then xyarrays for values and loaded flags. Evsel allocation sizes arrays from current CPU and thread maps. Reset zeroes both arrays; free deletes both and nulls `evsel->counts`.

State and persistence: `struct perf_counts` persists on an evsel in memory.

Dependencies and integration: depends on evsel CPU/thread maps, libperf thread maps, `xyarray`, zalloc, and libperf count value structures.

Risks: reset assumes non-NULL counts. Dimensions must match current maps; higher layers must reallocate after topology changes.

Test signals: dimensions, allocation failure unwinding, loaded reset, and evsel lifecycle.
