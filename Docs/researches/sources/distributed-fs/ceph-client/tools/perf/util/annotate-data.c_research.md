# sources/distributed-fs/ceph-client/tools/perf/util/annotate-data.c

## Purpose
Converts sampled memory-access instructions into annotated data types using DWARF debug information. It resolves global, stack, register, pointer, per-CPU, and inferred instruction-tracked types, builds per-DSO type/member trees, records type histograms, and prints type-centric annotation reports.

## Important APIs, Types, and Functions
`find_data_type()` is the public lookup entry: it initializes default type offset, finds a DWARF type DIE via `find_data_type_die()`, then interns it in the DSO data-type tree with `dso__findnew_data_type()`.
`find_data_type_die()` maps sampled IP to DWARF PC, finds the CU, handles PC-relative globals, discovers frame base/CFA, searches lexical scopes for variable-by-address or variable-by-register matches, and falls back to instruction tracking.
`find_data_type_block()` and `find_data_type_insn()` build shortest-path basic blocks and update a `type_state` through instructions until the sampled instruction is reached.
`update_var_state()` seeds register and stack state from DWARF variable locations.
`check_matching_type()` checks the sampled operand against current register/stack/per-CPU/global state and returns detailed match status.
`get_global_var_type()`, `get_global_var_info()`, and `global_var__collect()` maintain a DSO RB-tree cache of global variable ranges.
`dso__findnew_data_type()`, `add_member_types()`, and `annotated_data_type__get_member_name()` intern type names/sizes and recursively record struct/union members.
`annotated_data_type__update_samples()` allocates and updates byte-level histograms per evsel.
`hist_entry__annotate_data_tty()` prints type annotation output.

## Control Flow
The high-level flow starts in `hist_entry__get_data_type()` in `annotate.c`, which extracts operand location and calls `find_data_type()`. This file converts runtime IP to objdump/DWARF PC, locates the CU, searches direct DWARF variables, tries alternate registers for multi-register operands, and, on x86/PowerPC, walks basic blocks to reconstruct type movement through registers and stack slots. Successful matches are interned by type name and size, optionally expanded with members, then sample counts are added to histograms for the accessed byte offset.

## State and Persistence
State is process-local. DSO RB-trees store interned `annotated_data_type` nodes and `global_var_entry` ranges. Type histograms are allocated lazily per event and per type size. `struct type_state` is transient per lookup and contains register and stack-variable state. Global counters in `ann_data_stat` and `ann_insn_stat` record debug statistics. No files are persisted.

## Dependencies and Integration Points
Requires libdw support for real functionality; the header provides stubs otherwise. Depends on perf debuginfo, DWARF register mapping, symbol/map/thread lookup, evsel/evlist data, and common annotate basic-block discovery. Architecture integration is through `arch->update_insn_state` and operand metadata produced by `annotate_get_insn_location()`.

## Risks
Accuracy depends on DWARF completeness, objdump/disassembly alignment, frame-base correctness, and architecture-specific instruction tracking. Global variable collection scans all CUs and can be expensive. Type histograms allocate one entry per byte of type size per event, which can be costly for huge types. The debuginfo cache used by `hist_entry__get_data_type()` is asserted single-threaded, so concurrent use would be unsafe.

## Test Signals
Exercise binaries with full and partial DWARF, globals, locals, inlined scopes, frame-base CFA, struct/union members, pointer dereferences, stack stores/loads, per-CPU variables, and x86/PowerPC instruction-tracked register moves. Validate `ann_data_stat` counters for failure modes and compare printed type histograms against expected member offsets.
