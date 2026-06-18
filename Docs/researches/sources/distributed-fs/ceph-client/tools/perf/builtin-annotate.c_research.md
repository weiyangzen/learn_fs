# sources/distributed-fs/ceph-client/tools/perf/builtin-annotate.c

Purpose: implements `perf annotate`, which reads `perf.data`, resolves samples to DSOs/symbols/source, accumulates histograms, and displays annotated assembly, source, branch, or data-type views through stdio, TUI, or GTK.

Important APIs, types, and functions: `struct perf_annotate` combines `perf_tool`, session pointer, UI mode flags, filters, branch-stack state, data-type/stat options, and CPU bitmap. `process_sample_event()` resolves each sample and filters by CPU. `evsel__add_sample()` handles symbol filtering, branch-stack processing, hist entry creation, and address sample increments. `process_branch_stack()` and `process_basic_block()` account branch coverage and prediction. `hists__find_annotations()` walks sorted hist entries and invokes stdio/TUI/GTK or data-type annotation. `__cmd_annotate()` processes events, collapses/sorts hists, handles event groups, and calls display. `cmd_annotate()` parses options, initializes session/tool/symbol/annotation state, configures sorting, and dispatches.

Control flow: options select input, symbols/DSOs, UI, objdump/addr2line, CPU filters, itrace, grouping, and data-type behavior. The command initializes hist and annotation subsystems, opens a read-mode perf session with ordered event callbacks, processes events, collapses and resorts per-evsel histograms, optionally links group members, then displays each eligible annotation.

State and persistence: primary state is in memory: perf session, hists, annotation data, branch ranges, symbol configuration, and global annotation options. It reads `perf.data`, symbol files, objdump output, debug info, source files, and optional auxtrace data, but writes no persistent output except terminal UI.

Dependencies and integration points: integrates with perf's event/session machinery, symbol resolver, hist/sort infrastructure, branch and block-range helpers, annotation backends, UI browser setup, itrace synthesis, and optional libdw/GTK/slang/tracing support.

Risks: many global knobs (`symbol_conf`, `annotate_opts`, `use_browser`, `sort_order`) make option interactions delicate. Symbol filtering can erase symbols from DSO rbtrees. Data-type mode requires DWARF support and changes source annotation settings. Large perf.data files are intentionally not deleted in release builds for faster exit. UI-specific branches rely on dynamic GTK symbols and slang key handling.

Test signals: run stdio and stdio2 annotation on a small perf.data, with symbol and CPU filters, branch-stack data, grouped events, `--data-type` with and without DWARF support, `--dump-raw-trace`, and explicit `--objdump`/`--addr2line`. Validate no-sample input reports an error and malformed options fail early.
