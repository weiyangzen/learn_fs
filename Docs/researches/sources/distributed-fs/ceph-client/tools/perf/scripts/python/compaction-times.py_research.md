<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/compaction-times.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/compaction-times.py
Purpose: Python perf-script report that measures time and scanner/migration work for Linux memory compaction events.

Important APIs/types/functions: Option classes `popt` and `topt` define display modes. `comm_filter` and `pid_filter` implement filtering. `pair` stores paired counters, `cnode` stores one compaction interval, and `chead` manages per-pid heads plus global totals. Event handlers cover `mm_compaction_begin`, `end`, `migratepages`, `isolate_freepages`, and `isolate_migratepages`.

Control flow: CLI options are parsed at import time after `--`. Begin events create a pending `cnode` for the pid unless filtered. Intermediate events increment pending migration/free/migrate scanner stats. End events complete the pending interval, add elapsed time to global and optional per-process totals, and store verbose interval entries when requested. `trace_end` prints global totals and optional per-process details.

State and persistence: Global option variables, `chead.heads`, `chead.val`, and each head's pending/list state persist for one replay. Output is stdout; no files are written.

Dependencies and integration points: Paired with `bin/compaction-times-record` and report wrapper. Depends on compaction tracepoints and perf script Python handler naming.

Risks: Missing begin/end ordering produces stderr warnings. Filtering is decided when a head is first created, so later command-name changes for a pid are not reconsidered. Time formatting rounds microseconds when `-u` is selected.

Test signals: Force compaction via `/proc/sys/vm/compact_memory`, record the listed tracepoints, and verify total/per-process compaction time and scanner/migration counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/compaction-times.py -->
