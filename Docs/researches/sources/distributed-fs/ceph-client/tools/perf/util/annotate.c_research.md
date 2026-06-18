# sources/distributed-fs/ceph-client/tools/perf/util/annotate.c

## Purpose
Provides the core perf annotate implementation: sample accounting by symbol offset, disassembly orchestration, percentage calculation, IPC/basic-block/branch-counter aggregation, TTY/file rendering, data-type lookup integration, annotation options/config, operand-location extraction, debuginfo caching, and basic-block path discovery.

## Important APIs, Types, and Functions
Global state includes `annotate_opts`, `ann_data_stat`, pseudo data types `stackop_type` and `canary_type`, and `ann_insn_stat`.
Sample accounting flows through `hist_entry__inc_addr_samples()`, `addr_map_symbol__inc_samples()`, and `__symbol__inc_addr_samples()`.
Cycle and branch-counter accounting flows through `addr_map_symbol__account_cycles()`, `symbol__account_cycles()`, `annotation__compute_ipc()`, and branch-counter formatting helpers.
Disassembly flows through `thread__get_arch()`, `symbol__annotate()`, and `symbol__annotate2()`.
Rendering uses `hist_entry__annotate_printf()`, `hist_entry__tty_annotate()`, `hist_entry__tty_annotate2()`, `map_symbol__annotation_dump()`, and `annotation_line__write()`.
Data-type integration uses `annotate_get_insn_location()`, `hist_entry__get_data_type()`, `__hist_entry__get_data_type()`, `annotate_calc_pcrel()`, and debuginfo cache helpers.
Control-flow discovery uses `annotate_get_basic_blocks()` and related BFS helpers.

## Control Flow
Samples increment per-symbol histograms keyed by `(offset << 16 | evsel index)`. When annotation is requested, `symbol__annotate()` discovers the thread architecture, prepares `annotated_source`, sets display base address, and calls `symbol__disassemble()`. `symbol__annotate2()` then calculates percentages, indexes lines, marks jump targets, computes IPC/cycles/branch counters, initializes column widths, and marks the symbol as annotate2-ready. Rendering walks `annotation_line` entries and prints percentages, source/disassembly, arrows, cycle data, branch counters, and optional data-type comments.

## State and Persistence
Each symbol has an adjacent `struct annotation` containing `annotated_source` and optional `annotated_branch`. `annotated_source` stores disassembly/source lines, per-event histograms, sparse sample entries in a hashmap, and column widths. `annotated_branch` stores cycle histograms and branch counter arrays sized by symbol size. A sharded mutex protects annotation state. The debuginfo cache stores one DSO/debug-info pair and is intended for single-threaded data-type lookup. Annotation dump writes a `<symbol>.annotation` file when requested.

## Dependencies and Integration Points
Integrates almost every perf profiling subsystem: disassembler backends, DSO/map/symbol/thread, evsel/evlist/hists, srcline, BPF, branch stacks, debuginfo/DWARF registers, UI browser, config, and architecture registry. Architecture files provide instruction operations, parser conventions, fusion callbacks, and type-state updaters.

## Risks
Memory scales with symbol size for cycle and branch-counter arrays. Basic-block discovery uses heuristic jump conditional detection (`strstr("jmp")`). Operand-location extraction assumes objdump syntax, especially AT&T x86 memory forms. Debuginfo cache asserts single-threaded use. Error handling around sparse sample hashmap insertion can leak an entry if adding fails after allocation.

## Test Signals
Run annotate in stdio and browser paths with grouped events, empty-event skipping, source-line summaries, full-address toggles, branch stacks with cycles, branch counters, data-type comments, BPF symbols, and multiple disassembler backends. Include tests for local/external jumps, PLT symbols, lock-prefixed instructions, PC-relative calculation at the last instruction, and basic-block path discovery.
