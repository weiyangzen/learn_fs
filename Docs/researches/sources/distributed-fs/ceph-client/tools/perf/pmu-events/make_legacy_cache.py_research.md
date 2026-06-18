<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/make_legacy_cache.py -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/make_legacy_cache.py
Purpose: Generates JSON event definitions for perf legacy hardware cache aliases. It expands known cache IDs, operations, and result names into `EventName`, `BriefDescription`, and `LegacyCacheCode` records.

Important APIs/types/functions: The data tables `hw_cache_id`, `hw_cache_op`, and `hw_cache_result` encode perf's legacy cache dimensions. `add_event()` is the only function; it filters names that would conflict with hardware events, adjusts descriptions and deprecation for L2 aliases, constructs the packed legacy cache code, and appends event dictionaries to `events`.

Control flow: Module top-level loops over cache IDs, aliases, supported operations, and results to emit base, operation, operation-result, and result-only names. The script prints the final JSON array to stdout.

State and persistence: All state is process-local in `events`; no input files are read and no output files are written except stdout. Deprecation flags are stored in generated JSON records.

Dependencies and integration points: Depends only on `json`. The output feeds the same PMU event JSON pipeline that `jevents.py` compiles into perf C tables.

Risks: The mapping is manually encoded and must stay synchronized with perf's `PERF_COUNT_HW_CACHE_*` constants. Alias generation intentionally deprecates many names, so user-facing compatibility depends on preserving those flags. `branch-misses` and `branches` are skipped to avoid priority conflicts.

Test signals: Compare generated JSON against expected legacy event names/codes, validate with `jevents.py`, and exercise `perf list`/`perf stat` legacy cache aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/make_legacy_cache.py -->
