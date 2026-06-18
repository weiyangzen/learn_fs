<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/python/ilist.py -->
# sources/distributed-fs/ceph-client/tools/perf/python/ilist.py
Purpose: Textual TUI for browsing PMUs, events, and metrics interactively and displaying live counts/sparklines for a selected item. It is an interactive replacement/demo for `perf list` plus quick counter reads.

Important APIs/types/functions: `TreeValue` abstracts tree entries with `name`, `description`, `matches`, `parse`, and `value`. `Metric` resolves metric descriptions with `perf.metrics()`, parses via `perf.parse_metrics`, and computes values via `evlist.compute_metric`. `PmuEvent` resolves PMU event descriptions through `perf.pmus()` and parses event strings. UI classes include `ErrorScreen`, `SearchScreen`, `Counter`, `CounterSparkline`, and `IListApp`.

Control flow: `IListApp.compose()` builds a PMU tree and a metric-group tree. Search actions collect matching nodes and navigate through them. Selecting a leaf closes any old evlist, opens the new event/metric, adds counters and sparklines for total and each CPU, and periodic `update_counts()` disables the evlist, reads per-CPU/thread values, updates labels/sparklines, and reenables counting.

State and persistence: UI state includes `selected`, `evlist`, search result nodes, and current search cursor. Counter samples are kept in each sparkline's in-memory data list and trimmed by visible width. No persistent files are written.

Dependencies and integration points: Depends on perf Python bindings and the `textual` framework. Integrates with perf's PMU/event/metric discovery and event opening APIs.

Risks: It broadly catches exceptions around metric computation and event opening, so failures can appear as zero values or modal errors. Runtime depends on Textual API compatibility and perf permissions. Tree construction repeatedly calls `perf.metrics()` and `perf.pmus()`, which may be expensive on systems with many PMUs.

Test signals: Manual TUI smoke tests should verify tree population, search, event selection, counter updates, metric computation, and clean close/reopen behavior across PMUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/python/ilist.py -->
