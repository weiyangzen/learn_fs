# sources/distributed-fs/ceph-client/tools/perf/util/probe-finder.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/probe-finder.h` declares the DWARF-backed probe finder API and internal finder state structures used to resolve perf probe points, variables, and line ranges.

## Important APIs, Types, and Functions

The header defines limits `MAX_PROBE_BUFFER`, `MAX_PROBES`, and `MAX_PROBE_ARGS`, special argument names `PROBE_ARG_VARS` and `PROBE_ARG_PARAMS`, and helper `is_c_varname`. With `HAVE_LIBDW_SUPPORT`, it declares `is_known_C_lang`, `debuginfo__find_trace_events`, `debuginfo__find_probe_point`, `debuginfo__find_line_range`, `debuginfo__find_available_vars_at`, and `find_source_path`.

Internal state containers include `struct probe_finder` for current event, CU/scope state, address/line/source search state, CFI/frame-base state, ELF machine metadata, and current variable conversion; `struct trace_event_finder` for collected trace events; `struct available_var_finder` for variable-list collection; and `struct line_finder` for line-range discovery.

## Control Flow

The header itself has no executable flow. It describes callback-driven resolver flow: a `probe_finder` searches DWARF, stores the current address and scope, and invokes a callback to add trace events or variable lists.

## State and Persistence Behavior

No state is persisted. Finder structs own transient resolver context, including one owned `.eh_frame` CFI handle and per-search caches. Result allocations are returned through public APIs.

## Dependencies and Integration Points

It includes `intlist.h`, `build-id.h`, `probe-event.h`, and `linux/ctype.h`, and conditionally includes `dwarf-aux.h` and `debuginfo.h`. When libdw support is absent, `is_known_C_lang` is stubbed false, forcing callers to avoid DWARF-dependent functionality.

## Risks and Edge Cases

`is_c_varname` only checks the first character, so full identifier validation lives elsewhere or is intentionally permissive. The finder structures expose many internal fields, making callback correctness dependent on established invariants. Builds without libdw have dramatically reduced capabilities.

## Test Signals

Compile tests with and without libdw support, API-level DWARF resolution tests, max limit checks, and callback-state tests for trace-event, available-variable, and line-range finders are relevant.
