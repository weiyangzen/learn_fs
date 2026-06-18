# sources/distributed-fs/ceph-client/tools/perf/util/annotate-data.h

## Purpose
Declares the data-type annotation model and public APIs used by perf annotate. It defines type-state kinds, annotated member/type structures, histograms, data-location inputs, debug statistics, and libdw-dependent lookup/update functions.

## Important APIs, Types, and Functions
`enum type_state_kind` identifies invalid, regular type, per-CPU base, constant, per-CPU pointer, pointer, and stack-canary states.
`struct annotated_member` models nested data members with names, offsets, sizes, and children.
`struct annotated_data_type` stores a DSO RB-tree node, root member metadata, histogram count, and per-event histograms.
`struct data_loc_info` is the lookup input/result carrier for architecture, thread, map-symbol, IP, global address, CPU mode, operand location, debuginfo, frame base, and final type offset.
`struct type_state_reg`, `struct type_state_stack`, and `struct type_state` define the instruction-tracking state table when libdw is enabled.
Public functions include `find_data_type()`, `annotated_data_type__update_samples()`, tree deletion helpers, TTY/TUI printers, member-name lookup, stack-state helpers, global-variable helpers, and debug type-name printing.

## Control Flow
Callers fill `data_loc_info` from an annotated instruction operand and call `find_data_type()`. Architecture update functions mutate `type_state` while `annotate-data.c` walks basic blocks. Successful types can be sampled with `annotated_data_type__update_samples()` and displayed through TTY/TUI functions.

## State and Persistence
The header describes process-local RB-trees, per-type histograms, debug counters, and transient instruction-tracking state. When libdw is unavailable, static inline stubs return failure or no-op values, preserving build compatibility without type annotation behavior.

## Dependencies and Integration Points
Includes `dwarf-regs.h` and `annotate.h`, with optional `debuginfo.h` under `HAVE_LIBDW_SUPPORT`. Used by `annotate.c`, `annotate-data.c`, and architecture files such as x86 and PowerPC.

## Risks
`TYPE_STATE_MAX_REGS` is fixed at 32 to cover supported architectures; future architectures with larger register numbering need changes. Stub behavior can silently disable feature paths in builds without libdw. Histogram sizing depends on type size and can be memory-heavy.

## Test Signals
Build with and without `HAVE_LIBDW_SUPPORT` and `HAVE_SLANG_SUPPORT`. Validate ABI expectations for `data_loc_info`, type-state register bounds, tree deletion, histogram updates, and member-name lookup.
