## sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/evsel.h

Purpose: Defines the internal libperf event-selector structure and related sample-ID/period storage.

Important APIs/types: `struct perf_sample_id_period`, `struct perf_sample_id`, and `struct perf_evsel`. Declarations cover lifecycle, FD/id allocation, read sizing, filters, per-thread period lookup, and attr flags.

Control flow: The safe period iterator macro supports freeing per-stream period nodes. `perf_sample_id` maps perf sample IDs back to evsels and carries stream metadata for mmap/AUX/sample processing.

State/persistence: Evsel state includes linked-list membership, perf attr, maps, FD/mmap/sample xyarrays, IDs, group leader, period list, member count, and PMU behavior flags.

Dependencies/integration: Uses Linux perf ABI, list/hlist, public/internal CPU map types, thread maps, and xyarray.

Risks: Struct comments expose subtle semantics around per-thread/global `PERF_SAMPLE_READ`. Any layout or flag change affects evlist/evsel/mmap integration. `nr_members` and `leader` must be maintained consistently for group reads.

Test signals: Group event tests, sample ID lookup tests, per-thread period storage tests, and build checks for public/internal header compatibility.
