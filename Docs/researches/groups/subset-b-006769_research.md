# subset-b-006769 Research

Grouped source research for perf probe definition/tracefs/cache helpers, DWARF probe finding, small utility containers, record/sample support, s390 CPU-measurement decoding, and Perl/Python scripting bindings. Each listed source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/probe-event.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/probe-event.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/probe-event.h` is the central public contract for perf probe event parsing, conversion, display, and application. It defines both user-facing `perf probe` descriptions and kernel/uprobe-tracer command representations, plus line-range and variable-list containers used by probe discovery.

## Important APIs, Types, and Functions

Important state/configuration includes `struct probe_conf`, global `probe_conf`, global `probe_event_dry_run`, `DEFAULT_PROBE_MAGIC_NUM`, and `MAX_EVENT_INDEX`. Core tracefs-facing types are `struct probe_trace_point`, `struct probe_trace_arg_ref`, `struct probe_trace_arg`, and `struct probe_trace_event`. User-facing probe types are `struct perf_probe_point`, `struct perf_probe_arg_field`, `struct perf_probe_arg`, and `struct perf_probe_event`. Source and variable discovery use `struct line_range` and `struct variable_list`.

Declared APIs cover symbol map lifetime (`init_probe_symbol_maps`, `exit_probe_symbol_maps`), parser/synthesizer paths (`parse_perf_probe_command`, `parse_probe_trace_command`, `synthesize_perf_probe_command`, `synthesize_probe_trace_command`, `synthesize_perf_probe_arg`), conversion/application (`convert_perf_probe_events`, `apply_perf_probe_events`, `show_probe_trace_events`, `show_bootconfig_events`, `cleanup_perf_probe_events`), display queries (`show_perf_probe_event`, `show_perf_probe_events`, `show_line_range`, `show_available_vars`, `show_available_funcs`), architecture fixups (`arch__fix_tev_from_maps`, `arch__post_process_probe_trace_events`), and helper contracts (`e_snprintf`, `copy_to_probe_trace_arg`, `get_target_map`).

## Control Flow

This header has no executable flow. Its types describe the flow used elsewhere: parse a user command into `perf_probe_event`, optionally resolve/debug-info expand it into one or more `probe_trace_event` records, synthesize tracefs commands, and either apply them to tracefs or show them to the user.

## State and Persistence Behavior

The file owns no storage beyond declarations. The global configuration controls behavior across probe modules, including dry-run behavior, cache usage, inline handling, and maximum generated probe count. Persistent state is indirect through tracefs probe event files and probe cache files managed by other modules.

## Dependencies and Integration Points

The header depends only on compiler annotations and boolean support, while forward-declaring `intlist`, `nsinfo`, `symbol`, `strlist`, `strfilter`, and `map`. It is included by probe parsing, probe cache, DWARF resolver, and perf command code. It also forms an architecture extension point for map fixups and post-processing.

## Risks and Edge Cases

The structures encode ownership-sensitive strings and arrays, so callers must use the clear/copy helpers consistently. `probe_trace_arg_ref` chains carry dereference and user-access semantics that must match tracefs syntax. The `magic_num` fallback is used when some generated probe instances lack a variable location, so bad defaults can silently alter captured data. ABI drift with tracefs kprobe/uprobe command syntax is a recurring risk.

## Test Signals

Useful tests include parser/synthesizer round trips for perf-probe and trace-probe commands, memory cleanup tests for copied and cleared events, user/kprobe/uprobe conversion tests with and without variables, dry-run application checks, bootconfig display checks, and architecture-specific post-processing tests for map-relative addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/probe-event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/probe-file.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/probe-file.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/probe-file.c` implements perf probe interactions with tracefs/debugfs probe event files and the build-id-backed probe cache. It opens `kprobe_events` and `uprobe_events`, reads and filters installed probe names, writes synthesized probe commands, deletes probes, persists resolved probe mappings, scans SystemTap SDT ELF notes, and probes tracefs README feature availability.

## Important APIs, Types, and Functions

Tracefs APIs include `open_trace_file`, `probe_file__open`, `probe_file__open_both`, `probe_file__get_rawlist`, `probe_file__get_namelist`, `probe_file__add_event`, `probe_file__get_events`, and `probe_file__del_strlist`. Cache APIs include `probe_cache__new`, `probe_cache__purge`, `probe_cache__delete`, `probe_cache_entry__get_event`, `probe_cache__find`, `probe_cache__find_by_name`, `probe_cache__add_entry`, `probe_cache__scan_sdt`, `probe_cache__commit`, `probe_cache__filter_purge`, and `probe_cache__show_all_caches`. Feature probes include `probe_type_is_available`, `kretprobe_offset_is_supported`, `uprobe_ref_ctr_is_supported`, `user_access_is_supported`, `multiprobe_event_is_supported`, and `immediate_value_is_supported`.

Internal helpers include warning printers for common tracefs failures, `__probe_file__get_namelist`, `__del_trace_probe_event`, cache open/load/write/compare/show helpers, SDT note address/ref-counter extractors, SDT argument parsing/synthesis, and `scan_ftrace_readme`. `MAX_CMDLEN` reflects the tracefs command length budget.

## Control Flow

Opening a probe file builds a path under `tracing_path_mount()`, opens read-only unless write access is requested and dry-run is disabled, and emits targeted warnings for permission, missing tracefs, missing kprobe/uprobe support, or general open failure. Listing installed probes reads raw lines from the tracefs file, parses each line into a `probe_trace_event`, and returns either raw commands, event names, or group:event names.

Adding probes synthesizes a trace command from `probe_trace_event` and writes it to the selected tracefs file unless `probe_event_dry_run` is set. Deletion converts stored `group:event` names into tracefs delete syntax and writes one delete command per list entry.

Cache creation resolves a target build-id, creates or locates a build-id cache directory, opens the `probes` file, and loads entries. Cache load treats lines beginning with `#` as perf probe definitions, `%` as SDT definitions, and following lines as trace-probe commands. Adding a cache entry removes any matching existing entry, creates a new entry from the perf probe command, synthesizes each trace event command, and appends it. Commit rewinds/truncates the cache file, writes every entry, and rolls back file size if a partial write occurs.

When SDT note support is enabled, `probe_cache__scan_sdt` walks SDT notes in an ELF file, creates `sdt_PROVIDER:NAME` entries, synthesizes uprobe commands with optional reference counters and parsed operands, and stores them in the cache. Feature queries lazily scan tracefs `README` once with glob patterns and cache the booleans.

## State and Persistence Behavior

Tracefs probe state is external kernel state in `kprobe_events` and `uprobe_events`. Probe cache state is persistent under the perf build-id cache as a `probes` file, keyed by target build-id or kallsyms. `struct probe_cache` owns an open fd and an in-memory list of `struct probe_cache_entry` objects. Static feature state in `scan_ftrace_readme` is process-local and scanned once.

## Dependencies and Integration Points

The file integrates with tracefs/debugfs path helpers, build-id cache, namespace switching for target build-id lookup, ELF/SDT note helpers, strlist/strfilter, probe event parsing/synthesis, dwarf register SDT operand parsing, and perf debug/color output. Public prototypes are gated by `HAVE_LIBELF_SUPPORT`; SDT scanning is gated by `HAVE_GELF_GETNOTE_SUPPORT`.

## Risks and Edge Cases

Partial tracefs writes are reported but leave kernel state dependent on tracefs behavior. `probe_cache_entry__get_event` returns the number parsed even if a later parse fails, so callers must treat short results carefully. Cache fd cleanup only closes `fd > 0`, so fd 0 would not be closed, although cache files are normally not stdin. SDT argument parsing has architecture-specific operand assumptions and special Arm64 stack-operand concatenation. Feature detection depends on README wording and can be stale for the process after the first scan. Cache commit truncates before rewriting, making rollback logic important for corruption avoidance.

## Test Signals

Tests should cover permission/missing-file warning paths, dry-run add behavior, raw/name/group listing with duplicate names, deletion syntax conversion, cache load/commit round trips, cache replacement and filter purge, build-id target/kallsyms cache opening, SDT note synthesis with typed operands and reference counters, README feature probes on mocked README content, and failure injection for partial cache writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/probe-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/probe-file.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/probe-file.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/probe-file.h` declares the tracefs probe-file and probe-cache API implemented by `probe-file.c`. It provides the in-memory cache entry/container shapes and a compile-time feature boundary for builds without libelf support.

## Important APIs, Types, and Functions

The key types are `struct probe_cache_entry`, containing an SDT flag, copied `perf_probe_event`, synthesized perf command, and trace-event string list, and `struct probe_cache`, containing the cache fd and list of entries. `enum probe_type` names tracefs type suffix capabilities. Flags `PF_FL_UPROBE` and `PF_FL_RW` select uprobe and writable open modes. `for_each_probe_cache_entry` wraps list iteration.

When `HAVE_LIBELF_SUPPORT` is available, the header declares probe-file open/list/add/delete functions, cache lookup/update/commit/show functions, SDT scanning, and tracefs feature capability checks. Without libelf, only stubbed `probe_cache__new` and `probe_cache__delete` are provided.

## Control Flow

The header has no runtime flow. Callers use it to open tracefs files, inspect existing probes, add or delete trace events, load or mutate cache entries, and query tracefs syntax support before generating commands.

## State and Persistence Behavior

It defines ownership of cache entry members but does not allocate state itself. Persistent behavior is delegated to the implementation and the build-id cache `probes` files.

## Dependencies and Integration Points

It includes `probe-event.h` and forward-declares `strlist` and `strfilter`. It integrates probe cache operations with higher-level `perf probe` command code and SDT users. The libelf guard lets the rest of perf compile in reduced configurations while disabling cache-heavy operations.

## Risks and Edge Cases

Callers must respect the libelf guard; most APIs disappear when libelf is disabled. Cache entry lifetime is nontrivial because nested events, strings, and lists are owned by the implementation. `probe_type` availability is not purely compile-time and must be queried at runtime.

## Test Signals

Compile tests with and without `HAVE_LIBELF_SUPPORT`, API users that exercise both kprobe and uprobe flag modes, cache iteration tests, and feature-gated command synthesis tests are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/probe-file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/probe-finder.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/probe-finder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/probe-finder.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/probe-finder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/pstack.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/pstack.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/pstack.c` implements a small fixed-capacity stack of opaque pointers for perf utility code.

## Important APIs, Types, and Functions

The private `struct pstack` stores `top`, `max_nr_entries`, and a flexible `entries[]` array. Public functions are `pstack__new`, `pstack__delete`, `pstack__empty`, `pstack__remove`, `pstack__push`, and `pstack__peek`.

## Control Flow

Creation allocates a zeroed object sized for the requested entry count and records capacity. Push appends at `top` unless capacity is full, in which case it logs an error and drops the entry. Peek returns the last pushed pointer or `NULL`. Remove scans backward for pointer identity, shifts later entries down with `memmove`, decrements `top`, and logs an error if the key is absent. Delete frees the allocation.

## State and Persistence Behavior

State is entirely in-memory and caller-owned through the returned pointer. The stack does not own the objects referenced by entries. There is no synchronization and no persistence.

## Dependencies and Integration Points

It depends on `pstack.h`, perf debug logging, kernel `zalloc`, and libc allocation/string helpers. It is a generic utility for local traversal/context stacks.

## Risks and Edge Cases

Capacity and top are `unsigned short`, so very large requested capacities truncate at the API type. Underflow would occur in `pstack__remove` if called on an empty stack because `last_index` is initialized from `top - 1`; callers should avoid removing from an empty stack. Overflow and missing-key cases only log errors.

## Test Signals

Unit tests should cover allocation sizing, push/peek order, overflow logging/drop behavior, remove of top/middle/bottom entries, absent-key behavior, empty checks, and freeing without freeing pointed-to objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/pstack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/pstack.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/pstack.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/pstack.h` exposes the opaque pointer-stack API used by perf utility code.

## Important APIs, Types, and Functions

The header forward-declares `struct pstack` and declares `pstack__new`, `pstack__delete`, `pstack__empty`, `pstack__remove`, `pstack__push`, and `pstack__peek`.

## Control Flow

No runtime flow exists in the header. Callers create a stack with a fixed capacity, push pointer keys, optionally remove a specific key, peek the top entry, and delete the stack.

## State and Persistence Behavior

The stack object is opaque and in-memory only. Pointer payload ownership remains with callers.

## Dependencies and Integration Points

The only external include is `<stdbool.h>`. The API is intentionally generic and does not depend on perf-specific types in the header.

## Risks and Edge Cases

The capacity type is `unsigned short`, matching the implementation. There is no thread-safety contract and no ownership transfer for pushed pointers.

## Test Signals

Compile users against the opaque type, plus behavioral tests in `pstack.c`, are sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/pstack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/python.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/python.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/python.c` implements the `perf` Python extension module. It exposes perf events, CPU/thread maps, PMUs, counter values, event selectors, event lists, event parsing, metric parsing, metric metadata, and tracepoint lookup to Python scripts.

## Important APIs, Types, and Functions

The module initializer is `PyInit_perf`. Event wrapper state is `struct pyrf_event`, with Python types for mmap, task, comm, throttle, lost, read, sample, and context-switch events. Map wrappers are `struct pyrf_cpu_map` and `struct pyrf_thread_map`. PMU wrappers are `struct pyrf_pmu` and `struct pyrf_pmu_iterator`. Counter values use `struct pyrf_counts_values`. Event selector/list wrappers are `struct pyrf_evsel` and `struct pyrf_evlist`.

Important methods include event `repr` functions, tracepoint field dynamic lookup for sample events when libtraceevent is available, CPU/thread sequence operations, PMU iteration and event enumeration, `evsel.open`, `evsel.cpus`, `evsel.threads`, `evsel.read`, `evlist.all_cpus`, `evlist.metrics`, `evlist.compute_metric`, `evlist.mmap`, `evlist.poll`, `evlist.get_pollfd`, `evlist.add`, `evlist.read_on_cpu`, `evlist.open`, `evlist.close`, `evlist.config`, `evlist.disable`, `evlist.enable`, module functions `tracepoint`, `parse_events`, `parse_metrics`, `metrics`, and `pmus`.

## Control Flow

Module initialization creates the Python module, readies all Python types, sets `page_size`, registers the exposed classes, and inserts `PERF_*` constants into the module dictionary. Event reading flows through `evlist.read_on_cpu`: find the mmap for a CPU, initialize mmap read, create a Python event object from the raw event, map the event to an evsel, consume the mmap entry, parse sample data into `perf_sample`, and return the event object.

`evsel` construction builds a `perf_event_attr` from Python keyword arguments, normalizes sample frequency/period union fields, assigns bitfields, and initializes a perf evsel. `evlist` construction wraps CPU/thread maps; adding an evsel inserts its embedded C evsel into the list. Default config builds a `record_opts` structure and calls `evlist__config`.

Metric parsing builds a temporary C evlist with `metricgroup__parse_groups`, clones it into Python-owned evlist/evsel objects, and fixes group leaders, metric leaders, and metric event references to point at cloned evsels. Metric computation finds the requested metric expression for a CPU/thread, reads backing counter deltas, scales by enabled/running time, evaluates the expression, and returns a float.

With libtraceevent, sample-event attribute lookup first checks tracepoint format fields and decodes numeric, string, dynamic array, and byte-array fields from raw sample data. If no tracepoint field matches, generic Python attribute lookup is used.

## State and Persistence Behavior

Python objects own or reference embedded perf structures. CPU and thread maps are reference-counted with `perf_cpu_map__get/put` and `perf_thread_map__put`. PMU objects reference globally owned PMUs and do not free them. `pyrf_event` stores a bounded copy of `union perf_event` plus parsed `perf_sample`; sample events free lazily allocated sample internals on deallocation. `evsel.read` persists previous raw counts in `prev_raw_counts` so it can return deltas across calls. No file-backed persistence is written, but opening/mmaping evlists creates perf event fds and mmaps.

## Dependencies and Integration Points

The module integrates Python C API, perf evlist/evsel/counts/mmap/cpumap/thread-map APIs, traceevent decoding, PMU scanning, metricgroup and expression parsing, record configuration defaults, and perf event parsing. It is consumed by Python perf scripting and tests that import `perf`.

## Risks and Edge Cases

`pyrf_event__new` copies raw events into a fixed `union perf_event` and rejects larger events, with a FIXME noting dynamic parsing would be better. Several error paths return without decrementing newly allocated Python objects, especially after type or argument validation failures. `pyrf_counts_values_set_values` does not cap list length against the backing fixed values array. `evlist.add` increments the Python evsel reference and embeds the evsel into the evlist, making ownership/lifetime subtle. `pyrf_evlist__item` returns a borrowed container object constructed from an embedded evsel address assumption. Tracepoint dynamic field access mutates `field->flags` by clearing `TEP_FIELD_IS_STRING` for non-printable arrays. The `overwrite` argument to `evlist.mmap` is parsed but not used. Import initialization returns a partially created module on setup failure, then sets ImportError only if a Python error is already pending.

## Test Signals

Tests should import the extension, validate constants and type registration, construct CPU/thread maps and sequence access, create/open/read evsels where permissions allow, parse simple events and metrics, clone metric evlists and compute metric deltas with mocked counts, exercise `read_on_cpu` with sample events, decode tracepoint dynamic string and byte-array fields, iterate PMUs and PMU events, and run reference-count/leak checks around evlist/evsel ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/python.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/rblist.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/rblist.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/rblist.c` implements a generic cached red-black-tree list wrapper with caller-provided node comparison, allocation, and deletion callbacks.

## Important APIs, Types, and Functions

Public functions are `rblist__init`, `rblist__exit`, `rblist__delete`, `rblist__add_node`, `rblist__remove_node`, `rblist__find`, `rblist__findnew`, and `rblist__entry`. The shared implementation for lookup and optional creation is `__rblist__findnew`.

## Control Flow

Add and find-new walk the cached RB tree from the root, compare each existing node with the candidate entry, choose left or right branches, and reject duplicates. Creation calls the user `node_new` callback, links the node with `rb_link_node`, inserts/rebalances with `rb_insert_color_cached`, and increments `nr_entries`. Removal erases from the cached tree, decrements count, and invokes the user delete callback. Exit walks from the cached first node, removes every entry, and leaves no nodes behind. Indexed lookup iterates in sorted order until the requested ordinal.

## State and Persistence Behavior

All state is in-memory in `struct rblist`: cached RB root and entry count. The wrapper owns tree membership but delegates node payload allocation/deletion to callbacks. There is no persistence or synchronization.

## Dependencies and Integration Points

It depends on Linux rbtree primitives and the callback contract in `rblist.h`. Many perf subsystems use this pattern for sorted unique containers.

## Risks and Edge Cases

Correct ordering depends entirely on a consistent `node_cmp`. If `node_new` or `node_delete` have side effects, tree operations inherit those risks. No NULL callback checks are performed. `rblist__entry` is O(n), not indexed-tree optimized. The container is not thread-safe.

## Test Signals

Unit tests should cover insert ordering, duplicate rejection with `-EEXIST`, allocation failure with `-ENOMEM`, find vs findnew behavior, leftmost cache correctness, entry count updates, removal callbacks, full exit/delete cleanup, and indexed iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/rblist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/rblist.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/rblist.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/rblist.h` declares the generic red-black-list wrapper used by perf code to build sorted unique collections with custom node payloads.

## Important APIs, Types, and Functions

`struct rblist` stores `struct rb_root_cached entries`, `nr_entries`, and callbacks `node_cmp`, `node_new`, and `node_delete`. Public APIs mirror the implementation: init, exit, delete, add, remove, find, find-or-create, and indexed entry lookup. Inline helpers are `rblist__empty` and `rblist__nr_entries`.

## Control Flow

The header has no runtime flow beyond inline count checks. Callers embed `struct rblist`, initialize callbacks, then use the implementation to maintain the tree.

## State and Persistence Behavior

State is in-memory and callback-owned. The wrapper tracks count and tree root but does not define payload layout.

## Dependencies and Integration Points

It includes Linux rbtree support and `<stdbool.h>`. The comments document the expected embedding pattern for node and list structs.

## Risks and Edge Cases

The API requires callback initialization before use. Inline helpers assume non-NULL `rblist`. Payload ownership and ordering are not enforced by the type system.

## Test Signals

Compile-time embedding tests and runtime coverage from `rblist.c` operations validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/rblist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/record.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/record.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/record.c` implements shared perf record option configuration helpers. It normalizes sampling frequency/period, configures evlists/evsels for recording, handles leader sampling rules, chooses sample-id formats, tests event selectability, and parses `-F/--freq` style frequency options.

## Important APIs, Types, and Functions

Public functions are `evlist__config`, `record_opts__config`, `evlist__can_select_event`, and `record__parse_freq`. Internal helpers include `evsel__read_sampler`, `evsel__config_term_mask`, `evsel__config_leader_sampling`, `get_max_rate`, and `record_opts__config_freq`.

## Control Flow

`evlist__config` sets `no_inherit` when no user CPU is requested, detects `comm_exec` support, configures each evsel with `evsel__config`, sets tracking comm-exec where possible, then applies leader sampling adjustments after sample types are known. It enables sample identifiers when full auxtrace or explicit sample identifiers are requested, or when multi-event evlists have divergent sample types, then computes id positions.

Leader sampling handles grouped events where the group leader samples reads. If the leader is an AUX event, topdown sample-read event, or mem-loads AUX event, the sampler is the next group member. Non-sampler members without explicit frequency/period terms have sampling disabled and inherit sampler/leader sample type bits so synthesized group samples can be reported consistently.

`record_opts__config_freq` rejects simultaneous user frequency and period, folds user-provided values into defaults, refuses zero frequency/period, reads `kernel/perf_event_max_sample_rate`, throttles or rejects over-limit frequencies depending on `strict_freq`, and clamps defaults. `evlist__can_select_event` parses a temporary event, chooses a CPU, tries `perf_event_open`, retries with pid 0 on `EACCES` from pid -1, and returns true if an fd can be opened. `record__parse_freq` accepts `"max"` or numeric strings and stores `user_freq`.

## State and Persistence Behavior

The file mutates caller-owned `record_opts`, `evlist`, `evsel`, and `perf_event_attr` structures. It reads sysctl state and may transiently open a perf event fd for capability probing. No persistent files are written.

## Dependencies and Integration Points

It integrates with evlist/evsel configuration, parse-events, perf syscall wrapper, perf API probes, topdown and memory event helpers, cpumaps, parse-options, and record option declarations in `record.h`.

## Risks and Edge Cases

Frequency parsing uses `atoi`, so malformed non-`max` strings become 0 and are rejected later only if configured. `evlist__can_select_event` uses the first requested or online CPU and may not represent all CPUs. Leader sampling rules are subtle for AUX/topdown/memory events and can accidentally suppress samples if config term detection misses a user override. Reading max sample rate failure is treated as nonfatal in config but fatal for `"max"` parsing.

## Test Signals

Tests should cover frequency vs period conflict, strict and non-strict max-rate behavior, zero defaults, `"max"` parsing, invalid strings, evlist sample-id decisions for homogeneous and heterogeneous sample types, AUX/topdown leader sampling, explicit config-term preservation, and selectability probing with mocked `perf_event_open` errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/record.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/record.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/record.h` defines shared recording options and declarations used by perf record-like commands and Python record configuration.

## Important APIs, Types, and Functions

`struct record_opts` contains target selection, inheritance, sampling toggles, address/page-size/weight/data-source flags, auxtrace settings, namespace/cgroup/switch/data mmap options, callchain/user/kernel flags, overwrite/build-id/kcore/text-poke toggles, sampling frequency/period fields, register masks, branch stack mask, clockid settings, control fds, synthesis/threading settings, compression, affinity, and off-CPU threshold. It declares `record_usage`, `record_options`, `record__parse_freq`, and inline `record_opts__no_switch_events`.

## Control Flow

The header has no executable flow except the inline switch-event helper, which reports an explicit request to disable switch events.

## State and Persistence Behavior

`record_opts` is a caller-owned configuration aggregate. It controls runtime recording behavior but does not persist state itself.

## Dependencies and Integration Points

It includes time, bool, Linux perf event types, and `util/target.h`. It is consumed by record command option parsing, evsel/evlist configuration, auxtrace setup, and scripting wrappers.

## Risks and Edge Cases

The structure is broad and field interactions are complex; defaults must be initialized carefully before calling configuration helpers. Several boolean `*_set` fields distinguish default false from explicit user false. Control fd defaults must be invalid values when unused.

## Test Signals

Compile and configuration tests should validate initialized defaults, switch-event explicit-disable behavior, auxtrace option combinations, frequency/period fields, and record option parsing integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/record.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/rlimit.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/rlimit.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/rlimit.c` contains small helpers for increasing process resource limits needed by perf workloads, especially BPF map creation and many open perf fds.

## Important APIs, Types, and Functions

The public functions are `rlimit__bump_memlock` and `rlimit__increase_nofile`.

## Control Flow

`rlimit__bump_memlock` reads `RLIMIT_MEMLOCK`, multiplies current and max values by four, tries `setrlimit`, then halves that attempted increase and retries once if the first set fails. If both fail, it logs a debug warning. `rlimit__increase_nofile` uses an `enum rlimit_action` state pointer: first call raises current to max, second raises both current and max by 1000, later calls do nothing. It preserves the caller's `errno` across attempts and returns whether a limit was successfully changed.

## State and Persistence Behavior

The helpers mutate process resource limits. Changes are process-local and inherited by child processes according to normal rlimit semantics. The nofile helper advances caller-owned action state.

## Dependencies and Integration Points

It depends on libc `getrlimit/setrlimit`, perf debug logging, and declarations in `rlimit.h`. It supports perf trace/BPF tests and high-fd recording sessions.

## Risks and Edge Cases

Multiplying infinite or very large rlimit values can overflow `rlim_t`. Raising hard limits usually requires privilege and can fail silently except for debug output. `rlimit__increase_nofile` assumes adding 1000 to `rlim_max` is meaningful and permitted. Preserving `errno` is useful for callers but can hide failure details unless debug logging is enabled.

## Test Signals

Tests should mock or isolate rlimit calls for success, first-fail-second-success, complete failure, nofile state progression, errno preservation, and overflow/`RLIM_INFINITY` handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/rlimit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/rlimit.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/rlimit.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/rlimit.h` declares perf resource-limit helper APIs.

## Important APIs, Types, and Functions

`enum rlimit_action` has states `NO_CHANGE`, `SET_TO_MAX`, and `INCREASED_MAX` used by `rlimit__increase_nofile`. Declared functions are `rlimit__bump_memlock` and `rlimit__increase_nofile`.

## Control Flow

No runtime flow exists in the header. Callers maintain an `enum rlimit_action` value across retry attempts.

## State and Persistence Behavior

The only modeled state is the caller-owned nofile action enum. Actual process rlimit changes are performed by the implementation.

## Dependencies and Integration Points

The header is lightweight but uses `bool`, relying on include order or transitive includes to provide it in consumers.

## Risks and Edge Cases

Consumers should include a boolean definition before this header if not already present. The state enum represents a progression and should not be reset accidentally between retries.

## Test Signals

Compile coverage and `rlimit.c` behavioral tests validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/rlimit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/rwsem.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/rwsem.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/rwsem.c` implements perf's read/write semaphore abstraction over `pthread_rwlock_t`, with an optional mutex-backed error-checking mode.

## Important APIs, Types, and Functions

Public functions are `init_rwsem`, `exit_rwsem`, `down_read`, `up_read`, `down_write`, and `up_write`.

## Control Flow

In normal mode, initialization and destruction call pthread rwlock init/destroy. Read and write acquisition call `pthread_rwlock_rdlock` and `pthread_rwlock_wrlock`; unlock calls `pthread_rwlock_unlock`. If global `perf_singlethreaded` is true, lock/unlock operations are no-ops returning success. In `RWS_ERRORCHECK` mode, all operations use the embedded perf mutex instead.

## State and Persistence Behavior

State is in-memory inside caller-owned `struct rw_semaphore`. There is no persistence. Locking state is process/thread runtime state.

## Dependencies and Integration Points

It depends on `util.h` for `perf_singlethreaded`, `rwsem.h`, pthread rwlocks, and optionally perf mutex helpers. It provides a Linux-kernel-like naming style for userspace perf code.

## Risks and Edge Cases

No-op behavior under `perf_singlethreaded` assumes no concurrent access. Error-check mode collapses reader/writer distinction into a mutex. Return values from pthread functions are propagated but many callers may not check them. Destroying a locked rwlock remains caller misuse.

## Test Signals

Tests should cover normal init/destroy, parallel readers, writer exclusion, `perf_singlethreaded` no-op behavior, error-check mode compile coverage, and error propagation from invalid lifecycle usage where practical.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/rwsem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/rwsem.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/rwsem.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/rwsem.h` declares perf's userspace read/write semaphore abstraction and lock-analysis annotations.

## Important APIs, Types, and Functions

`struct rw_semaphore` contains either a `struct mutex` in `RWS_ERRORCHECK` mode or a `pthread_rwlock_t` in normal mode. Declared APIs are init/exit and read/write down/up operations. Annotation macros mark shared, exclusive, and unlock functions.

## Control Flow

The header has no runtime flow beyond compile-time selection of the backing lock type.

## State and Persistence Behavior

The semaphore is caller-owned in-memory synchronization state.

## Dependencies and Integration Points

It includes pthread and perf mutex support. The annotations integrate with thread-safety analysis where available.

## Risks and Edge Cases

Changing `RWS_ERRORCHECK` changes semantics and performance. Consumers must initialize before use and destroy after all users have released the lock.

## Test Signals

Compile checks for both backing modes and runtime locking tests through `rwsem.c` validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/rwsem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumcf-kernel.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumcf-kernel.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumcf-kernel.h` mirrors s390 CPU Measurement Counter Facility raw data structures and event constants needed by perf userspace decoders.

## Important APIs, Types, and Functions

Constants include `S390_CPUMCF_DIAG_DEF`, `PERF_EVENT_CPUM_CF_DIAG`, `PERF_EVENT_CPUM_SF_DIAG`, `PERF_EVENT_PAI_CRYPTO_ALL`, `PERF_EVENT_PAI_NNPA_ALL`, and counter-set identifiers `CPUMF_CTR_SET_BASIC`, `USER`, `CRYPTO`, `EXT`, and `MT_DIAG`. Types are `struct cf_ctrset_entry` for an 8-byte counter-set header and `struct cf_trailer_entry` for the 64-byte trailer with flags, versions, CPU speed, TOD timestamp/base, programming usage fields, and machine type.

## Control Flow

There is no executable flow. Decoders cast raw big-endian buffers to these layouts and convert fields before validation/printing.

## State and Persistence Behavior

The header defines raw event layouts only. It owns no storage and persists no state.

## Dependencies and Integration Points

It is used by `s390-sample-raw.c` and `s390-cpumsf.c` to decode counter-set diagnostic raw samples and combined sampling/counter events. The structures must match the kernel/perf ABI for s390 PMU data.

## Risks and Edge Cases

Bitfield layout and endian interpretation are architecture-sensitive. Any drift from kernel layout breaks raw decoding. User-space code must convert big-endian fields explicitly when running on other endian hosts.

## Test Signals

Binary fixture tests with known counter-set headers/trailers, endian conversion checks, struct size/layout checks against kernel ABI, and decoder validation tests are appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumcf-kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumsf-kernel.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumsf-kernel.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumsf-kernel.h` mirrors s390 CPU Measurement Sampling Facility AUX trace sample block structures for userspace decoding.

## Important APIs, Types, and Functions

Constants are `S390_CPUMSF_PAGESZ` and `S390_CPUMSF_DIAG_DEF_FIRST`. Types are `struct hws_basic_entry` for basic-sampling data, `struct hws_diag_entry` for diagnostic data with flexible payload, `struct hws_combined_entry` for adjacent basic+diagnostic entries, and `struct hws_trailer_entry` for per-page trailer metadata, descriptor sizes, overflow count, timestamp, TOD base, and programming usage fields.

## Control Flow

There is no executable flow. AUX trace decoders validate page-sized buffers, read basic/diagnostic entries, and use trailer metadata to determine sizes and timestamps.

## State and Persistence Behavior

The header defines raw binary layouts only. It owns no memory or persistent state.

## Dependencies and Integration Points

It is consumed by `s390-cpumsf.c` for AUX trace dump and sample synthesis. Its layout must remain aligned with the s390 kernel PMU AUX trace ABI.

## Risks and Edge Cases

Bitfield order, endian conversion, page trailer positioning, and variable diagnostic descriptor sizes are high-risk areas. Older hardware may omit descriptor sizes, forcing decoder fallback by machine type.

## Test Signals

Tests should validate struct sizes and field extraction on known raw SDB pages, old-machine descriptor fallback cases, trailer timestamp conversion, invalid descriptor detection, and little-endian host decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumsf-kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumsf.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumsf.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumsf.c` implements s390 CPU Measurement Sampling Facility AUX trace support. It registers an auxtrace decoder, validates and dumps raw sampling-data blocks, queues per-CPU AUX buffers, orders decoding by timestamps, synthesizes perf sample events from hardware sampling entries, handles lost AUX data, and optionally logs AUX/counter raw data to files.

## Important APIs, Types, and Functions

Public APIs are `s390_cpumsf_process_auxtrace_info` and, through `s390-cpumsf.h`, `s390_cpumsf_recording_init` from the broader subsystem. Primary state containers are `struct s390_cpumsf` for auxtrace instance state and `struct s390_cpumsf_queue` for per-queue buffer/log state.

Important internal functions include counter logging `s390_cpumcf_dumpctr`, entry display helpers `s390_cpumsf_basic_show`, `s390_cpumsf_diag_show`, `s390_cpumsf_trailer_show`, validation `s390_cpumsf_validate`, trailer checks/timestamps `s390_cpumsf_reached_trailer`, `trailer_timestamp`, `get_trailer_time`, dumping `s390_cpumsf_dump`, sample synthesis `s390_cpumsf_make_event`, decoding `s390_cpumsf_samples`, `s390_cpumsf_run_decoder`, queue setup/update/process functions, lost/error synthesis, auxtrace callbacks, config handling, and itrace option validation.

## Control Flow

`s390_cpumsf_process_auxtrace_info` validates the AUXTRACE_INFO record, allocates `struct s390_cpumsf`, checks supported `--itrace` options, reads optional `auxtrace.dumpdir`, initializes auxtrace queues, fills session/machine/type metadata, installs auxtrace callbacks on the session, and processes the auxtrace index unless dump mode is active.

During report processing, `s390_cpumsf_process_event` is called for timestamped events. It ignores dump mode, requires ordered events, dumps raw counter-set samples for `PERF_EVENT_CPUM_CF_DIAG`, synthesizes lost-buffer errors for truncated AUX records, then updates queues and processes queued AUX data up to the event timestamp. Queue processing uses an auxtrace heap ordered by the next timestamp; it pops the earliest queue, decodes one or more pages until the timestamp boundary, updates partial buffer state when a later page is not ready, and re-adds the queue with the next timestamp.

Decoding validates that AUX data is page-sized, begins with a basic entry, and has descriptor sizes from the trailer or old-machine fallback. It iterates basic and diagnostic entries, skips trailers at page ends, converts basic entries into `perf_sample` objects with IP, pid/tid, CPU, period, and cpumode heuristics, then delivers synthetic sample events through `perf_session__deliver_synth_event`. Dump mode prints basic, diagnostic, and trailer records instead of synthesizing samples.

## State and Persistence Behavior

Runtime state is attached to `session->auxtrace` and owns auxtrace queues, heap, per-queue private objects, optional log directory string, and optional open log files. AUX buffers may be mmaped/read from perf.data and partially consumed via `use_data` and `use_size`. Optional logging writes `aux.smp.XX` and `aux.ctr.XX` files in the configured dump directory or current directory. Cleanup closes logs, frees queue private data, frees queues and heap, clears `session->auxtrace`, and frees the instance.

## Dependencies and Integration Points

The file integrates with perf auxtrace infrastructure, ordered events, perf sessions/data files, machines, evlists/evsels, PMU raw event constants from s390 headers, config parsing, sample delivery, and dump/color/debug output. It assumes host machine support only and sets `sf->machine` to `session->machines.host`.

## Risks and Edge Cases

Timestamp ordering is central; unordered tools are rejected. Invalid trailer TOD clock base makes a queue skip or error with max timestamp. Descriptor-size fallback depends on machine type parsed from cpuid and may reject unknown old hardware. Endian/bitfield decoding has separate little-endian fixups. `s390_cpumcf_dumpctr` writes `raw_size - 4`; malformed small raw samples would underflow if called without upstream validation. Optional log-file failures disable or degrade logging but continue processing. KVM support is explicitly absent. Heap re-addition after decoder errors can keep a queue alive with max timestamps.

## Test Signals

Tests should include AUXTRACE_INFO validation, unsupported itrace option rejection, config dumpdir handling, queue/index setup, timestamp-ordered partial page decoding, invalid page size/basic/trailer cases, old hardware descriptor fallback, little-endian field extraction, sample cpumode heuristics for native/guest/old hardware, lost AUX error synthesis, dump mode output, log file creation/write failures, and cleanup closing all resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumsf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumsf.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumsf.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumsf.h` declares the s390 CPU Measurement Sampling Facility auxtrace recording and report-processing entry points.

## Important APIs, Types, and Functions

It forward-declares `union perf_event`, `struct perf_session`, and `struct perf_pmu`, then declares `s390_cpumsf_recording_init` and `s390_cpumsf_process_auxtrace_info`.

## Control Flow

No executable flow exists in the header. Recording code calls the recording initializer for the s390 cpumsf PMU, and report/inject code calls the AUXTRACE_INFO processor to install decoding callbacks.

## State and Persistence Behavior

State is created by the implementation and attached to recording or session auxtrace machinery. The header itself owns no state.

## Dependencies and Integration Points

It is the public integration point between architecture-specific s390 auxtrace support and generic perf record/report auxtrace code.

## Risks and Edge Cases

Callers must only use these functions when the matching s390 PMU/AUXTRACE type is present. Error reporting is through integer return codes and an out-parameter for recording initialization.

## Test Signals

Compile coverage, recording initialization tests on s390-capable PMU fixtures, and AUXTRACE_INFO processing tests validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/s390-cpumsf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/s390-sample-raw.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/s390-sample-raw.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/s390-sample-raw.c` implements the s390 architecture-specific raw sample dump callback. It validates and prints CPU Measurement Counter Facility diagnostic raw data and PAI crypto/NNPA raw counter records when perf displays raw samples.

## Important APIs, Types, and Functions

The public callback is `evlist__s390_sample_raw`. Internal helpers include `ctrset_size`, `ctrset_valid`, `s390_cpumcfdg_testctr`, `s390_cpumcfdg_dumptrail`, `get_counterset_start`, PMU event-name lookup/cache helpers `get_counter_name_callback`, `get_counter_name_hash_fn`, `get_counter_name_hashmap_equal_fn`, `get_counter_name`, counter dump `s390_cpumcfdg_dump`, PAI validation `s390_pai_all_test`, and PAI dump `s390_pai_all_dump`.

## Control Flow

The callback ignores non-sample events, maps the raw event to an evsel, and returns if no raw data is present. For `PERF_EVENT_CPUM_CF_DIAG`, it ensures the `cpum_cf` PMU is available, validates the raw counter-set byte stream, and dumps counter sets plus trailer. Validation walks big-endian counter-set headers and accepts the known 4-byte padding offset before the trailer. For PAI NNPA or crypto events, it validates minimum record size, finds the PMU by type if needed, then dumps 10-byte event/value records until no full record remains.

Counter names are resolved by scanning PMU event metadata for matching `event=HEX` strings and cached in a static hashmap keyed by constructed event number.

## State and Persistence Behavior

The file maintains a static counter-name cache tied to the last PMU pointer. It mutates `evsel->pmu` lazily when it finds the needed PMU. It writes formatted output to stdout/stderr only and persists no files.

## Dependencies and Integration Points

It depends on perf evlist/evsel mapping, sample raw callback setup from `sample-raw.c`, s390 counter facility ABI structures, PMU metadata iteration, hashmap utilities, color output, and big-endian conversion helpers.

## Risks and Edge Cases

The static cache is not synchronized and assumes one active PMU identity. PAI validation only checks a minimum size, so malformed trailing bytes can be silently ignored by loop bounds. Counter-set parsing depends on raw data alignment and the special 4-byte padding rule. PMU event string parsing assumes `event=%x` appears in metadata. Output-only behavior means errors are reported but do not fail report processing.

## Test Signals

Tests should feed known-good and malformed CPUM_CF raw buffers, trailer padding cases, PAI crypto/NNPA record streams, unknown counter names, PMU cache hit/miss paths, missing evsel/PMU cases, and endian conversion fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/s390-sample-raw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/sample-raw.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/sample-raw.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/sample-raw.c` selects architecture/vendor-specific raw sample interpreters for a perf evlist based on perf.data environment metadata.

## Important APIs, Types, and Functions

The public function is `evlist__init_trace_event_sample_raw`.

## Control Flow

The function reads architecture and CPUID strings from `perf_env`. If the architecture is `s390`, it installs `evlist__s390_sample_raw`. If the architecture is `x86`, CPUID starts with `AuthenticAMD`, and the evlist has AMD IBS events, it installs `evlist__amd_sample_raw`. Otherwise no callback is set.

## State and Persistence Behavior

It mutates the caller-owned `evlist->trace_event_sample_raw` function pointer. No persistent state is written.

## Dependencies and Integration Points

It depends on perf env metadata, evlist helpers, AMD IBS detection, and s390 raw-sample support declared in `sample-raw.h`. It is part of perf report/script raw sample display setup.

## Risks and Edge Cases

Selection depends on recorded environment strings; missing or unexpected arch/CPUID values leave raw samples uninterpreted. AMD detection is both vendor and event-list dependent. Only one callback is selected.

## Test Signals

Tests should cover s390 selection, AMD x86 IBS selection, x86 non-AMD no-op, AMD without IBS no-op, missing env fields, and callback pointer preservation/overwrite expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/sample-raw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/sample-raw.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/sample-raw.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/sample-raw.h` declares architecture-specific raw sample callbacks and the selector that installs them on an evlist.

## Important APIs, Types, and Functions

It forward-declares `struct evlist`, `union perf_event`, and `struct perf_sample`. Declared functions are `evlist__s390_sample_raw`, `evlist__has_amd_ibs`, `evlist__amd_sample_raw`, and `evlist__init_trace_event_sample_raw`.

## Control Flow

The header has no executable flow. It establishes the callback signatures used by raw sample display code.

## State and Persistence Behavior

No state is owned by the header. Implementations mutate evlist callback state or print raw sample data.

## Dependencies and Integration Points

It connects generic sample raw initialization with s390 and AMD IBS implementations.

## Risks and Edge Cases

The closing include-guard comment names `__PERF_EVLIST_H`, which is only a comment mismatch but can confuse maintainers. Callers must pass samples whose raw data layout matches the selected callback.

## Test Signals

Compile coverage and selector tests from `sample-raw.c` validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/sample-raw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/sample.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/sample.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/sample.c` implements lifecycle helpers for `struct perf_sample` and an instruction-fetch helper that copies the sampled instruction bytes from a thread's address space.

## Important APIs, Types, and Functions

Public functions are `perf_sample__init`, `perf_sample__exit`, `perf_sample__user_regs`, `perf_sample__intr_regs`, and `perf_sample__fetch_insn`. Internal helper `elf_machine_max_instruction_length` maps ELF machine types to maximum instruction byte lengths.

## Control Flow

Initialization either zeroes the entire sample or resets only pointer/lifetime fields for reuse. Exit frees lazily allocated user/intr register dumps and a merged callchain if owned. Register accessors lazily allocate `regs_dump` objects and log allocation failures.

`perf_sample__fetch_insn` returns early if there is no IP or an instruction is already present. It determines the thread's ELF machine, chooses a maximum length, copies bytes from the thread/machine at the sample IP, stores the copied length, and refines x86/x86_64 length using the x86 instruction decoder when possible.

## State and Persistence Behavior

The functions mutate caller-owned `struct perf_sample`. Some sample members are pointers into an original perf event and are not owned here; only lazily allocated register dumps and merged callchains are freed. No persistent state is written.

## Dependencies and Integration Points

It depends on sample definitions, perf debug, thread/machine memory access, Linux zalloc, ELF machine constants, and the x86 instruction decoder. It is used by event parsing, scripting, auxtrace, and reporting paths that need normalized sample state.

## Risks and Edge Cases

Partial initialization with `all=false` requires the rest of the sample to already be in a known state. Instruction length is architecture heuristic except for x86 decoder refinement. Failed memory reads silently leave `insn_len` zero. The helper uses `MAX_INSN` as a fallback and must not overrun the fixed `insn` array.

## Test Signals

Tests should cover full and partial initialization, exit freeing only owned fields, lazy register allocation failure/success, instruction fetch for fixed-length and variable-length architectures, x86 decoder refinement, no-IP early return, already-populated early return, and failed `thread__memcpy` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/sample.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/sample.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/sample.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/sample.h` defines the normalized `struct perf_sample` used throughout perf to represent variable-length `PERF_RECORD_SAMPLE` payloads and auxiliary sample metadata.

## Important APIs, Types, and Functions

Important helper types are `struct regs_dump`, `struct stack_dump`, `struct sample_read_value`, `struct sample_read`, `struct aux_sample`, and `struct simd_flags`. Enums `simd_op_flags` and `simd_pred_flags` describe ARM SIMD operation/predicate metadata. Helpers include `sample_read_value_size`, `next_sample_read_value`, `sample_read_group__for_each`, `perf_sample__init`, `perf_sample__exit`, `perf_sample__user_regs`, `perf_sample__intr_regs`, `perf_sample__fetch_insn`, and inline `perf_sample__synth_ptr`.

`struct perf_sample` contains event identity, timing, IP/address, pid/tid/cpu, period, weights, transaction/data-source/page-size/cgroup fields, branch/callchain pointers, register/stack dumps, raw and AUX data pointers, instruction bytes, deferred/merged callchain state, guest machine ids, cpumode/misc, SIMD flags, and read-format counter data.

## Control Flow

The header mostly defines data shape. Inline read-format helpers compute per-value stride based on `PERF_FORMAT_LOST`, iterate grouped read values, and calculate synthetic raw-data pointer alignment.

## State and Persistence Behavior

`perf_sample` is transient runtime state. Many pointer fields alias the original perf event buffer, so the sample lifetime must be shorter than that buffer unless a field is explicitly copied and marked owned, such as merged callchains or lazy regs dumps.

## Dependencies and Integration Points

It includes Linux perf event and type definitions, and forward-declares evsel/machine/thread. It is a central contract for evsel sample parsing, auxtrace synthesis, reporting, scripting, Python/Perl bindings, and raw sample decoders.

## Risks and Edge Cases

Ownership is mixed and must be respected by initialization and exit helpers. The register cache is bounded by a 64-bit mask. `perf_sample__synth_ptr` assumes raw data is four bytes from an eight-byte boundary. Read-format layout changes must stay aligned with kernel perf ABI. Adding fields can affect scripting bindings that pack or expose the struct.

## Test Signals

Tests should verify sample parsing for each `PERF_SAMPLE_*` field, read-format stride with and without lost values, group iteration, raw-data alignment for synthesized events, lifetime cleanup, register cache use, stack/raw/AUX pointer lifetimes, and scripting binding compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/sample.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/scripting-engines/trace-event-perl.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/scripting-engines/trace-event-perl.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/scripting-engines/trace-event-perl.c` embeds a Perl interpreter for `perf script`, delivers perf events and tracepoint fields to Perl handlers, exposes callchain/context data, and generates starter Perl scripts for available tracepoints.

## Important APIs, Types, and Functions

The exported scripting engine descriptor is `perl_scripting_ops`. Interpreter bootstrap uses `xs_init`, `boot_Perf__Trace__Context`, `boot_DynaLoader`, and global `INTERP my_perl`. Event-symbol setup uses `define_symbolic_value`, `define_symbolic_values`, `define_symbolic_field`, `define_flag_value`, `define_flag_values`, `define_flag_field`, and `define_event_symbols`. Runtime delivery uses `perl_process_callchain`, `perl_process_tracepoint`, `perl_process_event_generic`, and `perl_process_event`. Lifecycle functions are `perl_start_script`, `perl_flush_script`, and `perl_stop_script`. Code generation is handled by `perl_generate_script`.

## Control Flow

Startup stores the current `perf_session` in `scripting_context`, builds a Perl command line from the script and arguments, allocates/constructs/parses/runs the interpreter, checks `ERRSV`, and calls optional `main::trace_begin`. Shutdown calls optional `main::trace_end`, destructs, and frees the interpreter.

For each event, `perl_process_event` updates the global scripting context, then attempts tracepoint-specific delivery and generic raw delivery. Tracepoint delivery only handles `PERF_TYPE_TRACEPOINT` evsels. It obtains the traceevent format, builds a handler name `system::event`, defines symbolic/flag metadata once for that invocation path, computes seconds/nanoseconds, pushes common arguments, callchain data, and all event fields onto the Perl stack, and calls the handler if it exists. If not, it calls `main::trace_unhandled` when available. Generic delivery calls `process_event` with packed bytes for `union perf_event`, `perf_event_attr`, `perf_sample`, and raw data.

Callchain processing resolves the sample callchain through the thread and evsel, then builds a Perl array of hashrefs with IP, optional symbol metadata, and optional DSO name. Script generation writes an output `.pl` file with imports, begin/end hooks, per-tracepoint handler skeletons, flag/symbol formatting helpers, backtrace printing, unhandled handler, and a generic packed `process_event` example.

## State and Persistence Behavior

The file owns the embedded Perl interpreter for the active script run and updates the global `scripting_context`. It uses static `cur_field_name` and `zero_flag_atom` while walking print formats. Generated scripts are written to `<outfile>.pl`. Runtime event handling writes only through Perl script side effects and stdout/stderr unless the script persists data.

## Dependencies and Integration Points

It depends on libperl, libtraceevent, perf callchain/thread/map/dso/symbol/event/evsel infrastructure, scripting context helpers, and generated Perl modules under `Perf-Trace-Util`. It registers itself as the Perl implementation of perf's scripting engine.

## Risks and Edge Cases

`events_defined` is declared inside `perl_process_tracepoint`, so symbolic definitions are not truly persisted across events despite the bitset check. Handler names are built with `sprintf` into a 256-byte static buffer. Field extraction assumes raw data matches traceevent format and performs direct unaligned casts for dynamic offsets. `cur_field_name` is static and overwritten during recursive format walking; allocation cleanup is limited. Error handling in Perl calls does not deeply inspect exceptions after each handler. Script generation uses `sprintf` for the output path and writes generated Perl source with field names from trace metadata.

## Test Signals

Tests should cover interpreter start/stop errors, optional begin/end hooks, tracepoint handler invocation with numeric/string/dynamic fields, unhandled fallback, generic `process_event`, callchain hash contents with/without symbols/maps, symbolic and flag metadata callbacks, generated script content for representative events, long event names/path handling, and Perl exception behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/scripting-engines/trace-event-perl.c -->
