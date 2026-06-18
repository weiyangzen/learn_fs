# sources/distributed-fs/ceph-client/tools/perf/util/block-info.h

Purpose: declares data structures and APIs for block-level perf reports.

Important APIs and types: `struct block_info` captures symbol, start/end offsets, sampled and aggregate cycles, sparkline buckets, total cycles, hit counts, branch counters, and owning evsel. `struct block_fmt` wraps `perf_hpp_fmt` with block-specific widths and totals. The enum lists supported block report columns. `struct block_report` contains a `block_hist`, cycle total, registered formatters, and formatter count.

Control flow: no implementation flow; callers create reports, browse block hists, free reports, compare entries, and compute total cycle percentages through declarations here.

State and persistence: structures are in-memory report state owned by callers and hist entries.

Dependencies and integration points: includes hist, symbol, sort, and UI headers so block reports integrate with perf's existing hists/hpp output path.

Risks: embedding `perf_hpp_fmt` means lifetime of `block_fmt` must outlive hpp list use. `block_info` ownership is split through hist entries, so free paths must know whether `block_info__delete()` is registered/used by hist cleanup.

Test signals: compile and runtime coverage for every enum column, report creation/free cycles, and percentage calculations with zero and nonzero totals.
