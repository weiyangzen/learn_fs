<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hist.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/hist.c

## Purpose
`hist.c` implements perf's histogram aggregation engine: adding samples, merging equivalent entries, maintaining callchains, memory/branch/block metadata, applying filters, sorting/collapsing output trees, hierarchy navigation, diff pairing, event statistics, titles, and hists lifecycle.

## Important APIs, types, and functions
Public entry points include column width helpers, `hists__add_entry*`, `hist_entry_iter__add`, `hist_entry__delete`, `hists__collapse_resort`, output resort functions, hierarchy navigation functions, filter functions, stats incrementors, `hists__match/link/unlink`, `hist__account_cycles`, `evlist__fprintf_nr_events`, totals, title formatting, config parsing, `__hists__init`, `hists__init`, and `perf_hpp_list__init`. Four exported iterator operation tables implement normal, branch, memory, and cumulative sample handling.

## Control flow
Sample ingestion builds a temporary `hist_entry` in `__hists__add_entry`, resolves callchains through `hist_entry_iter__add`, and inserts or updates entries in `hists->entries_in` via `hists__findnew_entry`. Iterators specialize preparation and finish behavior for memory addresses, branch stacks, normal samples, or cumulative callchains. Collapse resort rotates input trees, merges by collapse keys into `entries_collapsed`, and optionally builds hierarchical trees. Output resort then sorts entries into `hists->entries`, sorts callchains, recomputes stats and column widths, and honors callbacks/progress.

## State and persistence
Histogram state is in-memory only. `struct hists` owns red-black trees, entry counts, filter pointers, stats, column widths, memory stat arrays, and hierarchy format lists. `struct hist_entry` owns references or copies of thread/map symbols, callchains, branch info, mem info, block/kvm info, srcline/srcfile, raw data, trace output, memory stats, diff pairs, hierarchy child trees, and optional custom allocation ops. Entries can move between input, collapsed, and output trees; hierarchy mode creates parent/child entries with `parent_he` and nested roots.

## Dependencies and integration points
The file depends on perf symbol/thread/map/session/callchain/sort/hpp infrastructure, memory and branch decoders, cgroup/namespace data, KVM/block info, annotation, source-line lookup, UI progress, and global `symbol_conf`. It is used by report/top/diff-style paths through `evsel__hists` and the evsel object extension registered by `hists__init`.

## Risks
Ownership is complex: insertion may clone or steal fields, hierarchy insertion intentionally nulls fields in source or new entries depending on active sort formats, and deletion must recursively release child trees and all optional metadata. Filter and hierarchy code mutates periods, filtered masks, folded UI state, and tree ordering; mistakes can produce wrong percentages or dangling rb-tree nodes. Cumulative callchain duplicate detection depends on comparator consistency. `random_max` assumes a nonzero reservoir size. `hists__filter_entry_by_parallelism` tests a bit indexed by `he->parallelism`; invalid values could read outside the intended bitmap if upstream data is not constrained.

## Test signals
Useful tests include normal/mem/branch/cumulative sample aggregation, callchain append/merge/sort, collapse with multiple sort keys, hierarchy reports with filters at different levels, diff pairing/link/unlink including dummy entries, column-width recalculation, decay/delete paths, memory-stat totals, source-line and trace-output ownership, lost/dropped sample stats, `hist.percentage` config parsing, and sanitizer runs for lifecycle-heavy report/top workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hist.c -->
