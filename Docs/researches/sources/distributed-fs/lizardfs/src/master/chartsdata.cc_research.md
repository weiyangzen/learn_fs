# sources/distributed-fs/lizardfs/src/master/chartsdata.cc

Purpose: collects periodic master statistics into the chart subsystem.

Important APIs/functions: `chartsdata_memusage`, `chartsdata_refresh`, `chartsdata_store`, `chartsdata_term`, `chartsdata_init`; chart definitions for CPU, chunk operations, filesystem operation counters, memory, packets, and bytes.

Control flow: initialization sets CPU timers where available, samples initial memory, registers periodic refresh every 60 seconds and store every hour, and initializes `stats.mfs`. Refresh builds a `CHARTS` array initialized to no-data, samples user/system CPU via interval timers, samples memory via `getrusage` and Linux `/proc/self/statm` fallback, pulls chunk delete/replication counts, filesystem operation stats, and client network stats, then calls `charts_add`.

State and persistence: static memory usage and chart subsystem state; persists chart data through `charts_store` to `stats.mfs`.

Dependencies and integration: depends on `common/charts.h`, event loop, `chunk_stats`, filesystem stats, and `matoclserv_stats`.

Risks: CPU measurement relies on resetting interval timers and has platform-specific quirks. Memory units differ by platform and are normalized in code. Chart indices must stay aligned with `FsStats::Size` and defined offsets.

Test signals: no direct tests in this subset; runtime monitoring and chart file generation are integration signals.
