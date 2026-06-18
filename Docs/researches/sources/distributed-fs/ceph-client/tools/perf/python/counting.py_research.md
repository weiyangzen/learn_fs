<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/python/counting.py -->
# sources/distributed-fs/ceph-client/tools/perf/python/counting.py
Purpose: Minimal example of using perf's Python binding to count events. It opens an event list, performs a small CPU-bound loop, reads counts per CPU/thread, and prints raw value/enabled/running fields.

Important APIs/types/functions: `main(event)` calls `perf.parse_events`, modifies each evsel `read_format` to include total enabled/running time, then uses `open`, `enable`, `disable`, `read`, and `close` on perf binding objects.

Control flow: CLI option `-e/--event` defaults to `cpu-clock,task-clock`. The script opens all parsed events, counts down from 100000, disables counting, iterates evsels, CPUs, and threads, then prints one line per read.

State and persistence: State is only the live perf event list and loop counter. No persistent output exists besides stdout.

Dependencies and integration points: Depends on local perf Python extension and kernel perf permissions. It is an example/diagnostic rather than library code.

Risks: Fails if event parsing or perf_event_open permissions fail. The measured workload is intentionally trivial and not a benchmark.

Test signals: Successful execution with default events and sensible nonzero read fields indicates basic counting bindings work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/python/counting.py -->
