# sources/distributed-fs/ceph-client/tools/perf/util/counts.h

Purpose: defines the perf counts container and inline accessors for per-CPU/per-thread counter values and loaded flags.

Important APIs/types: `struct perf_counts`, inline `perf_counts`, `perf_counts__is_loaded`, `perf_counts__set_loaded`, and lifecycle declarations.

Control flow: users index xyarrays by CPU map index and thread index.

State and persistence: in-memory count matrices attached to evsels.

Dependencies and integration: includes Linux types, internal xyarray, libperf evsel values, and bool. Used by stat/read paths.

Risks: inline accessors do no bounds or NULL checks.

Test signals: matrix dimension tests and loaded flag transitions around counter reads.
