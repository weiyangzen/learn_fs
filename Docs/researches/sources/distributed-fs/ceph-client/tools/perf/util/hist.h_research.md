<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hist.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/hist.h

## Purpose
`hist.h` declares the data model and public APIs for perf histogram collection, output formatting, filtering, hierarchy traversal, TUI integration, and event statistics.

## Important APIs, types, and functions
Core types are `enum hist_filter`, `enum hist_column`, `struct hists`, `struct hist_iter_ops`, `struct hist_entry_iter`, `struct res_sample`, `struct he_stat`, `struct hist_entry_diff`, `struct hist_entry_ops`, `struct hist_entry`, `struct hists_evsel`, `struct perf_hpp`, `struct perf_hpp_fmt`, `struct perf_hpp_list`, `struct perf_hpp_list_node`, `struct hist_browser_timer`, and `struct block_hist`. It declares add/delete/resort/filter/match/link/stat/title APIs plus HPP registration, formatting, and dynamic-entry helpers.

## Control flow
Callers initialize histogram support with `hists__init` and per-hists state with `__hists__init`, add samples through `hist_entry_iter__add` or `hists__add_entry*`, collapse and output-sort entries, then render through HPP/TUI/stdio helpers. Filters update the same hists trees and stats. Hierarchy traversal helpers provide next/previous navigation over nested output trees.

## State and persistence
All state is runtime memory. `hists` stores input/collapsed/output trees, stats, filters, widths, memory-stat configuration, and hierarchy HPP formats. `hist_entry` is a large owning node with reference-counted thread/map symbol state, optional callchain storage as a flexible array, branch/memory/block/KVM metadata, UI fold state, diff data, raw/trace payloads, parent/child hierarchy roots, and custom allocator hooks.

## Dependencies and integration points
The header ties together callchain, color, events stats, evsel, map symbols, memory events, mutexes, samples, spark stats, stat helpers, UI progress, TUI/slang declarations, sort/HPP formatting, annotation, branch accounting, and parse-options config.

## Risks
Because many structs are exposed, ABI-like coupling inside perf is high. `struct hist_entry` requires `callchain` to remain last for flexible allocation. Inline helpers assume initialized list heads and non-null `hists`/`hpp_list`. TUI stubs return success when slang is disabled, so callers must understand that UI functionality may be compiled out.

## Test signals
Compile coverage with and without slang, unit-style tests for inline pair and percent helpers, report/top/diff integration tests, hierarchy navigation tests, HPP format registration tests, and memory sanitizer coverage around `hist_entry` flexible allocation are strong signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hist.h -->
