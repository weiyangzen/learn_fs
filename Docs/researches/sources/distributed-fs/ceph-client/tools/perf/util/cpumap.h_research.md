# sources/distributed-fs/ceph-client/tools/perf/util/cpumap.h

Purpose: declares CPU map conversion, formatting, topology lookup, and aggregation-id APIs.

Important APIs/types: `struct aggr_cpu_id`, `struct cpu_aggr_map`, `aggr_cpu_id_get_t`, `cpu_aggr_map__for_each_idx`, cpumap creation/formatting, online map, max CPU/node, topology id accessors, aggregation map construction, and aggregation id constructors.

Control flow: stat/report code builds aggregation maps by passing a `perf_cpu_map` and getter such as socket, die, cluster, core, CPU, node, or global.

State and persistence: exposes in-memory CPU and aggregation map objects; implementation caches topology state.

Dependencies and integration: includes stdio, bool, and libperf cpumap. Used by perf stat aggregation, event headers, and topology display.

Risks: `cpu_map__is_dummy` assumes one `-1` entry. Aggregation ids use `-1` sentinels that must stay consistent across equality and empty checks.

Test signals: aggregation modes, dummy CPU maps, map formatting, and topology lookup callers.
