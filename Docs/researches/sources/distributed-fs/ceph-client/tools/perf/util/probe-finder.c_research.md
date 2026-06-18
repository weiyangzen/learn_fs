# sources/distributed-fs/ceph-client/tools/perf/util/probe-finder.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/probe-finder.c` converts user-level perf probe expressions into concrete kprobe/uprobe trace events by walking DWARF debuginfo. It resolves functions, lines, lazy source patterns, inline instances, variable locations, type casts, field dereferences, source paths, available variables, and reverse address-to-probe descriptions.

## Important APIs, Types, and Functions

Public APIs are `is_known_C_lang`, `debuginfo__find_trace_events`, `debuginfo__find_available_vars_at`, `debuginfo__find_probe_point`, `debuginfo__find_line_range`, and `find_source_path`. Major internal flows are variable conversion (`convert_variable_location`, `convert_variable_type`, `convert_variable_fields`, `convert_variable`, `find_variable`), trace point conversion (`convert_to_trace_point`, `call_probe_finder`), scope/location lookup (`find_best_scope`, `find_probe_point_by_line`, `find_probe_point_lazy`, `find_probe_point_by_func`, `debuginfo__find_probe_location`, `debuginfo__find_probes`), special argument expansion (`expand_probe_args` for `$vars` and `$params`), trace-event collection (`add_probe_trace_event`, `fill_empty_trace_arg`), available-variable collection (`collect_variables_cb`, `add_available_vars`), reverse lookup (`debuginfo__find_probe_point`), line-range discovery, and source path lookup/debuginfod fallback.

## Control Flow

Trace-event resolution starts in `debuginfo__find_trace_events`, allocates an output array up to `probe_conf.max_probes`, initializes a `trace_event_finder`, and calls `debuginfo__find_probes`. The resolver reads ELF machine metadata and CFI, then searches DWARF compilation units. It tries a pubnames fast path for exact function names, then scans CUs, matching requested source file, function, line, absolute address, or lazy-line pattern. For each found address it selects a scope DIE, resolves frame base/CFI, calls the configured callback, and clears temporary frame state.

For each found location, `add_probe_trace_event` rejects duplicate addresses, enforces the max probe count, converts the subprogram to a trace point, records language and real inline name, expands `$vars`/`$params`, and converts each requested argument. Argument conversion finds local or global variables at the target address, maps DWARF locations to registers, frame-base references, static `@var` references, or immediate constants, then applies field/array/pointer dereference chains and tracefs type suffixes. When immediate values are supported, missing values across inline instances can be filled with `probe_conf.magic_num` if at least one instance resolved a type.

Available-variable resolution reuses the same probe location search with a different callback, collecting visible parameters/locals and optional external variables. Reverse lookup maps an address back to function/file/relative-line or offset, including inline function handling. Line-range lookup collects executable source lines for a file/function range. `find_source_path` tries debuginfod by build-id, compile directory, explicit source prefix, and progressive leading-directory trimming.

## State and Persistence Behavior

The module owns only transient allocations returned to callers: arrays of `probe_trace_event`, arrays of `variable_list`, copied strings in probe points and line ranges, and variable lists. It reads DWARF/ELF state from `struct debuginfo`, reads source files for lazy pattern matching, and consults `symbol_conf.source_prefix`. It uses `probe_conf` for behavior such as inlining, variable display, max probes, location ranges, and magic fallback values. No file-backed persistence is written here.

## Dependencies and Integration Points

The implementation depends on libdw/libelf debuginfo helpers, perf DWARF aux helpers, `dwarf-regs`, build-id/debuginfod support, `intlist`, `strbuf`, `strlist`, tracefs feature queries from `probe-file.c`, and probe event types from `probe-event.h`. It is the DWARF resolver behind `perf probe`, and architecture register mapping is supplied by `get_dwarf_regstr`.

## Risks and Edge Cases

DWARF location expressions beyond simple registers, base registers, frame-base references, static addresses, and constants are unsupported. Optimized-out variables, tail calls, inline definitions without instances, shared line addresses, and missing frame base/CFI all produce user-visible failures. Field conversion is sensitive to pointer-vs-struct semantics and unnamed member recursion. Lazy source matching depends on source file availability and can find multiple addresses. `find_source_path` mutates the raw path pointer while trimming leading components and must handle prefix/comp_dir/debuginfod failures correctly. The resolver allocates many nested objects, so error paths must clear partially created trace events.

## Test Signals

Strong tests include DWARF fixtures for function probes, file:line probes, relative-line probes, lazy pattern probes, inline functions with multiple instances, return probes at non-entry addresses, optimized-out variables, globals/statics, frame-base variables, pointer/array/field chains, string/ustring casts, bitfields, unsupported DW_OPs, `$vars`/`$params` expansion, available variable ranges, reverse address lookup, line-range lookup, debuginfod/source-prefix path resolution, and max-probe overflow.
