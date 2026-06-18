# sources/distributed-fs/ceph-client/tools/perf/util/block-info.c

Purpose: builds and renders perf block-level reports from annotated branch/cycle histograms. It converts per-symbol cycle histogram entries into `hist_entry` rows representing program block ranges and registers report columns for text or TUI browsing.

Important APIs and functions: `block_info__process_sym()` extracts block records from a symbol's `annotation->branch->cycles_hist`. `block_info__create_report()` creates one block report per evsel. `block_info__free_report()` releases reports. `report__browse_block_hists()` displays block hists through stdio or TUI. Column callbacks include total cycles percent, sampled cycles, average cycles percent, average cycles, block range, DSO, and branch counter formatting.

Control flow: for each evsel's hists, `process_block_report()` initializes a dedicated `block_hist`, registers requested columns, walks existing histogram entries, and calls `block_info__process_sym()` for entries with symbols and maps. Each populated cycle histogram offset creates a `block_info`, copies cycle and branch-counter data, adds a block hist entry, accumulates aggregate cycles, then resorts output.

State and persistence: `block_info` instances are heap allocated and owned by hist entries. `block_report` arrays are heap allocated per evlist and must be freed with `block_info__free_report()`. The code mutates `symbol_conf.report_individual_block` while browsing. It persists no files.

Dependencies and integration points: depends on annotation data, symbols, maps, DSOs, srcline lookup, perf hpp formatting, hists, evlist/evsel, and optional slang browser support. It consumes branch counter metadata from annotations and evlist.

Risks: `block_avg_cycles_entry()` divides by `bi->num_aggr`; construction only creates entries when `num_aggr` is nonzero, but future callers must preserve that invariant. Srcline lookups can be expensive and unavailable. Branch counter arrays require correct `br_cntr_nr` sizing. Sorting and formatting assume `he->block_info` is populated.

Test signals: report generation with and without symbols, with unknown srclines, with branch counters, text and TUI browser modes, multiple evsels, zero total cycles, and memory cleanup under allocation failures.
