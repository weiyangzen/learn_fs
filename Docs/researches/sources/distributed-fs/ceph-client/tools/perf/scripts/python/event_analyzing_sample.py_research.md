<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/event_analyzing_sample.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/event_analyzing_sample.py
Purpose: Example general perf sample analyzer that stores sample metadata in SQLite and prints grouped histograms for generic events and PEBS load-latency events.

Important APIs/types/functions: `trace_begin` creates `gen_events` and `pebs_ll` tables in `/dev/shm/perf.db`. `process_event` extracts sample attributes, raw buffer, comm, event name, DSO, and symbol; `create_event` from `EventClass.py` classifies raw buffers; `insert_db` writes rows. `trace_end` calls `show_general_events` and `show_pebs_ll`. `num2sym` renders logarithmic histograms.

Control flow: At import time the script opens SQLite in autocommit mode. During replay, every sample is classified and inserted. At the end, SQL group-by queries summarize generic events by comm/symbol/dso and PEBS LL events by comm/symbol/dse/latency.

State and persistence: Persists analysis data to `/dev/shm/perf.db` for the duration of the run and possibly after if not removed by the environment. `PerfEvent` class counters also accumulate in memory.

Dependencies and integration points: Depends on perf Python script context, SQLite, `/dev/shm`, and `EventClass.py`. Paired with record/report wrappers that allow arbitrary perf samples.

Risks: Fixed database path can collide with concurrent runs or stale data because tables are `create if not exists` and inserts do not clear old rows. Autocommit row-by-row insertion can be slow for large data despite tmpfs. Raw PEBS detection is heuristic.

Test signals: Record a known sample workload, run the report, and verify table counts and histograms reflect the sample mix; remove or isolate `/dev/shm/perf.db` to avoid stale-data false positives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/event_analyzing_sample.py -->
