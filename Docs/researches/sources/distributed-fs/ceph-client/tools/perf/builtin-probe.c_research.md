# sources/distributed-fs/ceph-client/tools/perf/builtin-probe.c

## Purpose

`builtin-probe.c` implements `perf probe`, the frontend for defining, listing, deleting, previewing, and exploring kprobes/uprobes. It parses user probe definitions, optional executable/module targets and namespaces, source-line and variable queries when DWARF support is available, function filters, cache operations, bootconfig output, and symbol configuration, then delegates the actual conversion and tracefs/cache mutation to probe utility libraries.

## Important APIs, Types, and Functions

The command state is held in a heap-allocated static `params` object. It stores the selected command, whether uprobes are active, whether the current target was consumed, number of probe events, an array of `struct perf_probe_event`, a `struct line_range`, target path/module, `struct strfilter`, and namespace info. Major helpers are `init_params()`, `cleanup_params()`, `parse_probe_event()`, `parse_probe_event_argv()`, `set_target()`, `opt_set_target()`, `opt_set_target_ns()`, `params_add_filter()`, `perf_add_probe_events()`, `perf_del_probe_events()`, `del_perf_probe_caches()`, `__cmd_probe()`, and `cmd_probe()`.

The implementation depends heavily on utility APIs such as `parse_perf_probe_command()`, `convert_perf_probe_events()`, `apply_perf_probe_events()`, `show_probe_trace_events()`, `show_bootconfig_events()`, `show_perf_probe_events()`, `show_available_funcs()`, `show_line_range()`, `show_available_vars()`, and probe-file/cache helpers.

## Control Flow

`cmd_probe()` allocates and initializes `params`, calls `__cmd_probe()`, then clears all parsed events, line ranges, filters, namespace references, and target strings. `__cmd_probe()` builds the option table, applies exclusivity rules, disables DWARF-only options when libdw support is absent, parses options, reconciles quiet/verbose, and handles remaining positional probe definitions. A leading absolute non-`.ko` path can become an implicit executable target; remaining words are joined into one probe definition string.

Option callbacks set `params->command` and populate state. `--add` and `--definition` parse probe events. `--del`, `--list`, `--funcs`, and `--filter` build `strfilter` expressions. `--line` parses a line range, and `--vars` parses a probe point while rejecting arguments. `--exec` and `--module` set target type and normalize paths with namespace-aware realpath for uprobes or explicit paths. `--target-ns` creates namespace info from a pid if setns is needed.

After parsing, symbol arguments are validated, default max probes are set, vmlinux build-id checks are relaxed for offline informational commands, and a switch executes the selected command. Listing refuses `--exec`. Function, line, and variable queries call the corresponding display helper. Deletion either purges probe caches or opens kprobe/uprobe event files, gathers matching events, deletes them, and warns if nothing matched. Add/definition conversion initializes symbol maps, converts perf probe events to trace events, optionally prints definitions or bootconfig, otherwise applies events and prints how to use the last added event.

## State and Persistence Behavior

Adding and deleting probes mutates kernel tracing state through kprobe/uprobe event files unless cache mode is selected. Cache mode mutates probe cache entries under build-id cache storage. Definition mode prints generated definitions without applying them. Bootconfig mode emits bootconfig-compatible definitions and rejects uprobes. In-memory state includes parsed probe events, namespace references, filters, target strings, and line-range data; cleanup releases these at command exit. Each `perf_probe_event` receives a target copy and namespace reference when applicable.

## Dependencies and Integration Points

The file integrates with perf probe-finder/probe-event/probe-file libraries, build-id cache helpers, namespace handling, symbol configuration and validation, strfilter parsing, Linux tracefs probe event files, optional libdw source/variable discovery, demangling options, symfs handling, and parse-options. It is the user-facing command wrapper around lower-level probe conversion and application APIs.

## Risks and Edge Cases

`parse_probe_event()` increments `nevents` before checking `MAX_PROBES`, so the boundary condition is delicate and relies on later cleanup behavior. Several callbacks return negative errno-style values that are later printed through `pr_err_with_code()`. Target ordering is user-visible: `-x`/`-m` must follow probe definitions for that target, and an unused final target is treated as an error. `set_target()` only treats absolute paths specially and infers uprobes from non-`.ko` suffixes. Deletion opens both kprobe and uprobe files and must handle partial success. Cache deletion iterates all build IDs and warns per failed cache. DWARF-only commands compile out with `NO_LIBDW=1`, changing option availability. Namespace realpath and setns behavior can fail for inaccessible target processes.

## Test Signals

Useful tests include add, definition-only, bootconfig definition, delete by filter, list, funcs, line, vars, cache deletion, executable and module targets, namespace target resolution, positional absolute target parsing, rejection of `-` input, quiet/verbose exclusivity, unused final target errors, DWARF-disabled option handling, maximum probe count, missing symbol/vmlinux validation, deletion with no matches, and add failures that must not double-free parsed events during cleanup.
