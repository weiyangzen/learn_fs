# sources/distributed-fs/ceph-client/tools/perf/util/sort.h

## Purpose

`sort.h` declares the sort subsystem contract used by perf report, top, diff, memory, branch, and tracepoint views. It exposes sort modes, stable sort-key identifiers, configurable global state, the `struct sort_entry` callback interface, and setup/helper functions implemented in `sort.c`.

## Important APIs, Types, and Functions

`enum sort_mode` distinguishes normal, branch, memory, top, diff, and tracepoint contexts. `enum sort_type` enumerates common keys, branch-stack keys, and memory-specific keys; the ordering matches the implementation arrays in `sort.c`. `struct sort_entry` carries the column header plus callback pointers for comparison, collapse comparison, display sorting, row formatting, filtering, and per-hist-entry initialization. Exported sort entries include common symbols such as `sort_comm`, `sort_dso`, `sort_sym`, `sort_parent`, branch entries, `sort_srcline`, and `sort_type`.

The header declares `setup_sorting()`, `setup_output_field()`, `reset_output_field()`, `sort__setup_elide()`, `perf_hpp__set_elide()`, `sort_help()`, `report_parse_ignore_callees_opt()`, `is_strict_order()`, `hpp_dimension__add_output()`, `reset_dimensions()`, `sort_dimension__add()`, `output_field_add()`, address comparators, `_sort__sym_cmp()`, `hist_entry__srcline()`, and `sort__comm_nodigit_len()`.

## Control Flow and Data Flow

Consumers set globals such as `sort_order`, `field_order`, `sort__mode`, `parent_pattern`, and `chk_double_cl`, then call `setup_sorting()` to materialize callback-backed hpp fields. Later report rendering uses the registered callbacks rather than calling most functions directly.

## State and Persistence Behavior

The header exposes mutable process-global configuration. There is no on-disk persistence; state lasts for the perf command lifetime and is reset by `reset_output_field()` and `reset_dimensions()`.

## Dependencies and Integration Points

It depends on `hist.h`, regex support, and `struct perf_env`/`struct evlist` forward declarations. The API is consumed by report, top, diff, mem, trace, annotation, and hists code that needs a stable shared sorting contract.

## Risks and Edge Cases

Adding new `enum sort_type` values requires keeping implementation arrays and hpp column indexes coherent. Exposed globals can be mutated by option parsing before setup, so initialization order matters. Callback return semantics are signed 64-bit comparisons; implementers must avoid incompatible comparator directions.

## Test Signals

Compile-time coverage should catch missing declarations. Runtime signals are successful parsing of every documented sort key, correct help-string generation, and reset/setup idempotence across multiple report modes in one process.
