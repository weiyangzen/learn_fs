<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-diff.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-diff.c

## Purpose
Implements `perf diff`, the perf.data comparison command. It opens two or more perf.data inputs, builds histograms from samples, pairs matching events and histogram entries across files, and renders differential columns such as baseline percentage, period, delta, absolute delta, ratio, weighted difference, cycles block difference, and hot stream comparison.

## Important APIs, Types, and Functions
The command entry point is `cmd_diff()`, which initializes hist support, configures a `struct perf_tool`, parses options, initializes symbols and sorting, and calls `__cmd_diff()`. `struct perf_diff` stores the active perf tool, time filtering state, branch-stack availability, and stream mode. `struct data__file` wraps one input `perf_data`, its session, selected histograms, optional stream state, and per-file `diff_hpp_fmt` column objects. Core processing functions are `diff__process_sample_event()`, `data_init()`, `check_file_brstack()`, `__cmd_diff()`, `data_process()`, `stream_process()`, `hists__precompute()`, `hists__process()`, and `ui_init()`.

Computation helpers include `compute_delta()`, `compute_ratio()`, `compute_wdiff()`, `compute_cycles_diff()`, `formula_delta()`, `formula_ratio()`, `formula_wdiff()`, and the `hist_entry__cmp_*` sort callbacks. Output integration uses perf hpp callbacks such as `hpp__color_baseline()`, `hpp__color_delta()`, `hpp__color_ratio()`, `hpp__color_wdiff()`, `hpp__color_cycles()`, `hpp__color_cycles_hist()`, `hpp__entry_global()`, `hpp__header()`, and `hpp__width()`. Cycles mode uses `struct block_hist`, `block_info__process_sym()`, `hist__account_cycles()`, and per-block hists.

## Control Flow
`cmd_diff()` configures the tool handlers for samples, mmap/mmap2, comm, fork/exit, lost, namespaces, and cgroups, then reads `diff.*` config and CLI options. `data_init()` chooses default files (`perf.data.old` and `perf.data`, or host/guest defaults), validates `--order`, and creates the `data__files` array. `check_file_brstack()` briefly opens each session to require branch stack data for cycles or stream modes. Non-stream mode registers hpp columns with `ui_init()` and prepares sort keys; stream mode enables srcline callchain settings and changes `sort_order`.

`__cmd_diff()` opens each perf session, parses per-file absolute or percentage time filters, applies CPU filters, processes events through `diff__process_sample_event()`, and collapses histograms. Sample processing resolves addresses, skips samples outside the time or CPU filters, and either adds normal histogram entries, stream callchain entries, or cycles block entries. After all inputs are processed, `data_process()` iterates baseline evsels, matches equivalent evsels by attr type/config, links or pairs entries, precomputes requested metrics, and prints the baseline hists. `stream_process()` compares only the old/new stream sets. Cleanup deletes sessions, frees column headers, data arrays, and time ranges.

## State and Persistence Behavior
State is process-local and centered in static globals: `data__files`, `data__files_cnt`, `pdiff`, `force`, `show_period`, `show_formula`, `show_baseline_only`, `cycles_hist`, `sort_compute`, `compute`, weighted-diff weights, `cpu_list`, and `cpu_bitmap`. Persistent input is read from perf.data files; output is textual only. The command mutates in-memory histogram entries by adding pair links and storing computed diff fields in `hist_entry->diff`. It also changes global perf symbol/sort/callchain configuration for the current invocation.

Time filtering is transient: `pdiff.ptime_range` is parsed per file and freed after that file is processed. Branch-stack capability is detected by reopening headers before the main processing pass. In stream mode, `evlist_streams` is allocated per file and deleted through `data__free()`.

## Dependencies and Integration Points
This file integrates with perf's session, evlist/evsel, histogram, hpp column, symbol, sort, time-utils, annotation, map/srcline, branch block, stream, config, pager, and parse-options subsystems. It depends on perf.data event handlers to populate machines/maps before resolving samples. It uses `symbol__init()`, `setup_sorting()`, `sort__setup_elide()`, and `setup_pager()` from wider perf command infrastructure.

Cycles mode depends on branch stacks and `util/block-info.h`; stream mode depends on callchain and branch callstack support. The `--symfs`, symbol, dso, comm, pid/tid, percentage, time, CPU, and kallsyms options share global symbol and sort configuration with other perf report-style commands.

## Risks and Edge Cases
This snapshot contains duplicated source fragments that would be compile-time risks if not hidden by the exact tree state: duplicated `for (i = 0; i < COMPUTE_MAX; i++)`, duplicated `struct data__file *d;`, and an extra `};` after `diff_usage`. Functional risks include event matching only by attr type/config, which can pair semantically different events if names or sample fields differ; divisions by histogram totals or old periods that rely on defensive fallbacks; stream/cycles modes failing silently when every file lacks branch stacks; and global sort/callchain state changes leaking across command setup paths in-process.

Time parsing is subtle because absolute ranges can be colon-separated per file, while percentage ranges are parsed against each session. `sort_compute` is one-based by default and must remain below the number of files. CPU filtering relies on `sample->cpu` being valid. Cycles block output relies on srcline lookup and block indexes lining up between paired block histograms.

## Test Signals
Useful tests include `perf diff` with default two files, multiple input files, a single explicit new file, host/guest default names, each compute mode (`delta`, `delta-abs`, `ratio`, `wdiff:w1,w2`, `cycles`), `--cycles-hist`, `--stream`, `--baseline-only`, `--period`, `--formula`, `--order`, `--time` absolute and percentage ranges, and `--cpu`. Regression signals are correct hpp columns and sort ordering, graceful rejection of cycles/stream without branch stacks, correct handling of missing event pairs, no callchain sorting in normal diff mode, and no leaks or crashes on invalid files or invalid time strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-diff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-evlist.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-evlist.c

## Purpose
Implements `perf evlist`, a small perf.data inspection command that prints the event selectors stored in an input file or pipe and optionally includes detailed event attribute, frequency, grouping, and tracepoint field information.

## Important APIs, Types, and Functions
The entry point is `cmd_evlist()`. `__cmd_evlist()` opens the `perf_data`, creates a `perf_session`, processes pipe headers if needed, iterates `session->evlist`, and prints each `evsel` with `evsel__fprintf()`. `process_header_feature()` is a pipe-mode callback that stops session processing once enough feature/header data has been read. The command uses `struct perf_attr_details` to pass display flags such as `verbose`, `freq`, `event_group`, `trace_fields`, and `force`.

## Control Flow
`cmd_evlist()` parses `--input`, `--freq`, `--verbose`, `--group`, `--force`, and `--trace-fields`. It rejects `--group` when combined with verbose or frequency output because grouped formatting is incompatible with those expanded views. `__cmd_evlist()` builds a read-mode `perf_data` object, initializes a minimally populated `perf_tool` for pipe attr/feature processing, and creates a session. For pipe input, it calls `perf_session__process_events()` to discover attrs. It then walks every evsel, prints it, and records whether any tracepoint or non-leader grouped event was seen so it can print user tips for `--trace-fields` or `-g`.

## State and Persistence Behavior
There is no persistent state beyond reading the input perf.data stream. State is local to `__cmd_evlist()` except for standard perf globals such as `input_name` and `session_done`, which `process_header_feature()` sets for pipe termination. The command does not mutate the perf.data file and does not store output.

## Dependencies and Integration Points
Depends on perf session and evlist/evsel APIs, `evsel_fprintf`, parse-events field formatting, `util/data`, `util/debug`, and parse-options. It integrates with pipe-mode perf data processing through `perf_event__process_attr` and a feature callback. Output is direct stdout text.

## Risks and Edge Cases
Pipe mode depends on receiving enough attr/feature events before `session_done` stops processing. The compatibility check for `--group` is intentionally strict and prevents combinations that might otherwise be useful. The tracepoint and group tips are heuristic and only print when the user did not ask for the expanded information. Errors from `perf_session__new()` are returned directly through `PTR_ERR()`.

## Test Signals
Run against regular perf.data and perf.data pipes, with and without tracepoint events, grouped events, frequency sampling, and verbose attributes. Verify `perf evlist -g -v` and `perf evlist -g -F` reject with usage, `--force` passes through to perf_data, and tips appear only when relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-evlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-ftrace.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-ftrace.c

## Purpose
Implements `perf ftrace`, a wrapper around kernel ftrace tracefs/debugfs facilities. It supports the default trace subcommand, function latency histograms, and function profiling, while sharing perf target parsing for PID/TID/CPU/workload selection.

## Important APIs, Types, and Functions
The entry point is `cmd_ftrace()`. Runtime command paths are `__cmd_ftrace()` for live trace_pipe streaming, `__cmd_latency()` for function or event-pair latency histograms, and `__cmd_profile()` for per-function duration aggregation. Important setup and tracefs helpers include `check_ftrace_capable()`, `is_ftrace_supported()`, `init_tracing_instance()`, `exit_tracing_instance()`, `get_tracing_instance_file()`, `write_tracing_file()`, `append_tracing_file()`, `read_tracing_file_to_stdout()`, `read_tracing_file_by_line()`, `reset_tracing_files()`, `reset_tracing_options()`, `set_tracing_options()`, and `select_tracer()`.

Filtering and option helpers include `parse_filter_func()`, `parse_filter_event()`, `parse_buffer_size()`, `parse_func_tracer_opts()`, `parse_graph_tracer_opts()`, `parse_sort_key()`, and `opt_list_avail_functions()`. Latency/profile helpers include `make_histogram()`, `display_histogram()`, `prepare_func_latency()`, `start_func_latency()`, `stop_func_latency()`, `cleanup_func_latency()`, `prepare_func_profile()`, `parse_func_duration()`, `add_func_duration()`, `cmp_profile_data()`, and `print_profile_result()`. BPF latency integration is selected through `perf_ftrace__latency_*_bpf()` when available and requested.

## Control Flow
`cmd_ftrace()` initializes filter lists, installs signal handlers, checks CAP_PERFMON or CAP_SYS_ADMIN/root capability, verifies ftrace support by probing `set_ftrace_pid`, loads `ftrace.tracer` config, chooses the `trace`, `latency`, or `profile` option table, and parses target/workload options. If no target or workload is supplied, it defaults to system-wide tracing. It validates target constraints, creates an evlist and maps, optionally prepares a workload, and dispatches to the selected command function.

`__cmd_ftrace()` creates a per-run trace instance under `tracing/instances/perf-ftrace-XXXXXX`, resets files/options, clears the trace buffer, writes filters/options, selects `current_tracer`, opens `trace_pipe` nonblocking, prints trace headers, enables tracing immediately or after the requested delay, starts the workload, polls trace_pipe until a signal marks `done`, disables tracing, drains remaining output, and removes the trace instance.

`__cmd_latency()` prepares ftrace function_graph or BPF latency measurement, allocates histogram buckets, starts tracing, runs the workload, parses function_graph duration lines into buckets with `make_histogram()`, optionally reads BPF buckets, and prints a histogram plus aggregate stats. `__cmd_profile()` forces function_graph with tail comments, parses every duration line into a hashmap keyed by function name, sorts by total/avg/max/count/name, prints results, frees profile entries, and removes the trace instance.

## State and Persistence Behavior
Global state includes `workload_exec_errno`, `done`, `latency_stats`, and `tracing_instance`. Command state lives in `struct perf_ftrace`, which carries tracer selection, target, evlist, filter lists, graph/function options, latency bucket settings, BPF flag, and profile hashmap. Trace configuration is written into a temporary tracefs instance and should be removed at exit; the command also resets common ftrace files and options before each run. Output is streamed to stdout or pager; no perf.data is written.

## Dependencies and Integration Points
Depends on Linux tracing filesystem APIs via `api/fs/tracing_path.h`, perf target/evlist/thread/cpumap utilities, capability helpers, stat helpers, strfilter, hashmap, parse-sublevel-options, units parsing, and optional BPF skeleton support. It integrates with the kernel's `function` and `function_graph` tracers, tracefs option files, CPU masks, `set_ftrace_pid`, function filters, graph filters, trace_pipe, and `available_filter_functions`.

## Risks and Edge Cases
This snapshot contains duplicated lines and an extra brace in local helper code (`strncpy(tracing_instance, ...)`, duplicated buffer-reset comment, and a stray `}` after `parse_filter_func()`), which are compile-time risk signals in this source copy. Runtime risks include tracefs option availability varying by kernel; some resets intentionally ignore errors for older files; `exit_tracing_instance()` only removes the instance directory and logs on failure; signal-driven `done` state also handles workload exec failures; and ftrace text parsing assumes function_graph output format and `" us"` duration units. `__write_tracing_file()` duplicates `val` with `strdup()` and then writes `val_copy[size] = '\n'`, which relies on the NUL terminator slot as spare capacity and is easy to misread.

Latency event-pair mode requires BPF, while function latency can use function_graph. CPU masks and PID filters are mutually shaped by `target__has_cpu()`. Buffer size parsing enforces at least 1 KiB. Profile mode stores dynamically allocated function-name keys and data in a hashmap that must be freed after printing.

## Test Signals
Test `perf ftrace trace`, legacy no-subcommand invocation, `latency`, and `profile` with PID, TID, CPU, all-CPU, workload, and delayed-start targets. Verify function filters, notrace filters, graph filters, graph options (`depth`, `thresh`, `args`, `retval`, `retaddr`, `tail`, `verbose`, `noirqs`, `nosleep-time`), function options (`call-graph`, `irq-info`), buffer sizes, list-functions filtering, profile sort keys, latency bucket/min/max validation, BPF and non-BPF paths, cleanup of trace instances after errors, and workload exec error reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-ftrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-help.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-help.c

## Purpose
Implements `perf help`, including common command listing, all-command listing, and dispatch to man, info, or HTML/web documentation viewers.

## Important APIs, Types, and Functions
The entry point is `cmd_help()`. `enum help_format` tracks selected output (`man`, `info`, `web/html`, or none). Viewer configuration is stored in linked lists `man_viewer_list` and `man_viewer_info_list`. Important helpers are `parse_help_format()`, `perf_help_config()`, `add_man_viewer()`, `add_man_viewer_info()`, `add_man_viewer_path()`, `add_man_viewer_cmd()`, `exec_viewer()`, `show_man_page()`, `show_info_page()`, `show_html_page()`, `get_html_page_path()`, `setup_man_path()`, `cmd_to_page()`, and `list_common_cmds_help()`.

Viewer-specific launchers include `exec_man_man()`, `exec_woman_emacs()`, `exec_man_konqueror()`, `exec_man_cmd()`, and platform-overridable `open_html()`. `check_emacsclient_version()` probes `emacsclient --version` before using Emacs woman mode.

## Control Flow
`cmd_help()` loads the command list with `load_command_list("perf-", ...)`, applies config through `perf_config(perf_help_config, &help_format)`, parses subcommands and help format options, and then either prints all commands, prints usage plus common commands, or opens documentation for the requested command. `show_man_page()` builds the man page name (`perf` or `perf-<cmd>`), prepends perf's man path to `MANPATH`, tries configured viewers in order, tries `PERF_MAN_VIEWER`, and finally tries `man`. `show_info_page()` sets `INFOPATH` and execs `info perfman <page>`. `show_html_page()` validates `PERF_HTML_PATH`, constructs `<page>.html`, and delegates to `open_html()`.

## State and Persistence Behavior
State is process-local: viewer linked lists are populated from config, command lists are loaded for listing, and environment variables `MANPATH` or `INFOPATH` are set before exec. Successful viewer paths replace the process with `execlp()`/`execl()`; failures return and try the next viewer. The command does not persist data or modify repository files.

## Dependencies and Integration Points
Depends on perf config/cache/system-path helpers, subcmd command discovery and parse-options, run-command, strbuf, debug/util helpers, and platform `open_html` overrides. It integrates with installed perf documentation directories (`PERF_MAN_PATH`, `PERF_INFO_PATH`, `PERF_HTML_PATH`), external programs (`man`, `info`, `emacsclient`, `kfmclient`, custom viewer commands, `web--browse`), and config keys `help.format`, `man.viewer`, `man.<tool>.path`, and `man.<tool>.cmd`.

## Risks and Edge Cases
This snapshot contains a duplicated `if (!strcmp(subkey, ".path")) {` in `add_man_viewer_info()`, a compile-time risk signal. Viewer command execution is intentionally shell-based for custom commands (`/bin/sh -c`), so config values are trusted. `cmd_to_page()` allocates with `asprintf()` for non-`perf` commands and callers intentionally leak when they exec; non-exec failure paths may also leak small strings. `exec_man_konqueror()` may duplicate and modify a path string without freeing before exec/fallback. `add_man_viewer()` and `do_add_man_viewer_info()` do not check allocation failures before `strcpy()`/`strncpy()`.

Behavior depends heavily on documentation installation paths and external viewer availability. The built-in common command list is manually maintained and conditioned by compile-time features, so it can drift from actual commands.

## Test Signals
Test `perf help`, `perf help --all`, `perf help <cmd>`, `--man`, `--info`, `--web`, config-driven `help.format`, multiple `man.viewer` entries, `PERF_MAN_VIEWER`, supported and unsupported `man.<viewer>.path/cmd` settings, missing HTML documentation, absent `DISPLAY` for konqueror, old or missing `emacsclient`, and command-list feature guards (`HAVE_LIBELF_SUPPORT`, `HAVE_LIBTRACEEVENT`).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-help.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-inject.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-inject.c

## Purpose
Implements `perf inject`, a perf.data stream/file rewriting command. Its baseline behavior repipes events from input to output, while optional modes inject build IDs, rewrite mmap records with build IDs, merge sched switch/stat data, synthesize instruction trace events, strip non-synthesized events, merge guest perf.data into host data with time/id translation, copy kcore directories, process jitdump, and convert DWARF stack samples into callchain samples.

## Important APIs, Types, and Functions
The entry point is `cmd_inject()`, with main execution in `__cmd_inject()`. `struct perf_inject` holds the active `perf_tool`, input/output perf data, session, build-id rewrite style, mode flags, output byte count, AUX state, sched samples list, itrace options, copied feature sections, known build IDs, mmap evsel, raw callchain buffer, and embedded guest session. `enum build_id_rewrite_style` selects no rewrite, header injection (lazy/all), or mmap2 build-id rewrite (lazy/all).

Core repipe functions are `output_bytes()`, `perf_event__repipe_synth()`, `perf_event__repipe_sample()`, `perf_event__repipe_attr()`, `perf_event__repipe_auxtrace()`, `perf_event__repipe_mmap()`, `perf_event__repipe_mmap2()`, and process-plus-repipe wrappers for fork/comm/namespaces/exit/tracing data. Build-id logic is in `findnew_dso()`, `inject__mmap_evsel()`, `perf_event__repipe_common_mmap()`, `dso__read_build_id()`, `tool__inject_build_id()`, `tool__inject_mmap2_build_id()`, `mark_dso_hit()`, `perf_event__inject_buildid()`, and known-build-id parsing/lookup helpers. Sched-stat merging uses `perf_inject__sched_switch()`, `perf_inject__sched_process_exit()`, and `perf_inject__sched_stat()`.

Guest merge logic is represented by `struct guest_session`, `guest_id`, `guest_tid`, `guest_vcpu`, and `guest_event`. Important helpers include `guest_session__start()`, `host_peek_vm_comms()`, `guest_session__map_ids()`, `guest_session__add_attrs()`, `synthesize_id_index()`, `guest_session__add_build_ids()`, `guest_session__fetch()`, `guest_session__convert_time()`, `guest_session__inject_events()`, `host__finished_init()`, `host__finished_round()`, and `host__context_switch()`. Feature/header copying uses `save_section_info()`, `keep_feat()`, `feat_copy_cb()`, and `perf_session__inject_header()`. DWARF conversion uses `perf_event__convert_sample_callchain()` and `evsel__has_dwarf_callchain()`.

## Control Flow
`cmd_inject()` initializes default stdin/stdout perf data, parses mode options, validates incompatible modes such as `--strip` without `--itrace`, opens output unless doing in-place update, chooses the build-id style, initializes a `perf_tool` mostly as direct repipe callbacks, creates the input session, saves original feature section offsets, writes a pipe header if needed, parses known build IDs, validates DWARF callchain conversion preconditions, enables JIT-specific handlers if compiled, initializes symbols, and calls `__cmd_inject()`.

`__cmd_inject()` rewires the `perf_tool` according to the selected mode. Build-id and sched-stat modes enable mmap processing. Lazy build-id modes make samples trigger DSO/map hit marking. `--sched-stat` installs per-evsel handlers for sched tracepoints. `--itrace` sets session synthesis options, drops AUX-only records where appropriate, reserves output header room, and optionally strips non-synthesized samples. `--guest-data` starts a separate guest session into a temporary file, then uses ordered host callbacks to inject guest attrs/build IDs/events at `FINISHED_INIT` and guest events at each ordered flush timestamp. `--convert-callchain` replaces sample handling and later rewrites event attrs to remove stack/register sample bits.

After handler setup, non-pipe file output seeks past a reserved header area and `perf_session__process_events()` drives all event callbacks. Remaining guest events are flushed. For file output, the command updates header feature bits, data offset/size, clears or sets AUX/branch/build-id features as needed, copies selected original feature sections, injects the new header, and optionally copies host or guest kcore directories.

## State and Persistence Behavior
The command writes a new perf.data stream/file or updates in place for VM time correlation. `bytes_written` tracks output data size for header injection. Feature section metadata is saved before features are changed so selected original sections can be copied. Build-id modes mutate in-memory DSO/map hit flags to avoid duplicate injection. Sched-stat mode keeps pending sched_switch events in `inject.samples` keyed by TID until a matching sched_stat event or process exit. AUX/itrace mode can remove AUX sample payloads, drop AUX records, synthesize new events, and update header feature bits.

Guest mode persists temporary guest events in `/tmp/perf-inject-guest_session-XXXXXX` because perf cannot process two sessions simultaneously. It maps guest sample IDs to newly allocated host IDs, maps guest VCPUs to host CPUs using host COMM and context-switch records, converts guest timestamps through TSC conversion plus offset/scale, rewrites ID samples, and appends guest events into host time order. Cleanup deletes the guest session, temporary file, hlist mappings, buffers, output data, zstd state, known-build-id list, and raw callchain/event-copy buffers.

## Dependencies and Integration Points
This file is tightly integrated with perf session/tool callbacks, perf.data I/O, event synthesis, auxtrace, JIT dump support, DSO/build-id/symbol/map/machine/thread namespaces, ordered events, zstd decompression, TSC conversion, callchain resolution, and header feature copying. Optional paths depend on `HAVE_JITDUMP`, `HAVE_LIBTRACEEVENT`, and `HAVE_LIBDW_SUPPORT`. It also uses filesystem helpers such as `has_kcore_dir()`, shell `cp` for kcore directory copying, temporary files, and namespace-aware build-id reads.

## Risks and Edge Cases
This snapshot contains duplicated declarations/conditions (`struct machine *machine);`, duplicate `if (ret)`, duplicate `HEADER_TOTAL_MEM`) that are source-quality risk signals. Mode interactions are complex: the last build-id option wins, some modes replace tool handlers wholesale, JIT and lazy build-id ordering cannot be combined freely, and pipe input/output has special attr/header behavior. `parse_guest_data()` stores a pointer returned from `strsep()` into a duplicated buffer without preserving the base pointer for later free, so ownership is fragile. Kcore copying uses shell commands built from paths. Lazy mmap2 build-id mode drops unused mmap events, so missing sample hits can remove mappings needed by later consumers.

Guest merge correctness depends on QEMU/libvirt thread names matching `"CPU %u/KVM"`, context-switch samples carrying CPU, valid time conversion metadata, non-conflicting allocated IDs, and ordered `FINISHED_ROUND` events. Build-id reads can fail in mount namespaces or for anonymous/hugetlb/no-DSO maps. DWARF callchain conversion assumes samples contain stack, regs, and callchain with `exclude_callchain_user`, and cannot preserve inlined callchains. In-place update is only allowed through VM time correlation and requires force unless dry-run.

## Test Signals
Test plain repipe for file and pipe input/output, each build-id mode (`--build-ids`, `--buildid-all`, `--mmap2-buildids`, `--mmap2-buildid-all`), `--known-build-ids`, sched-stat merging, JIT dump injection, itrace synthesis with and without `--strip`, VM time correlation dry-run and forced in-place update, guest-data merge with kcore copying, and DWARF callchain conversion. Verify header data offsets/sizes, feature bits, attr updates, AUX index handling, build-id deduplication, namespace build-id lookup, ordered event handling, cleanup of temporary files, and correct rejection of unsupported pipe/DWARF or option combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-kallsyms.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-kallsyms.c

## Purpose
Implements `perf kallsyms`, a small command that searches the running kernel and loaded modules for named symbols and prints their mapped and original address ranges.

## Important APIs, Types, and Functions
The entry point is `cmd_kallsyms()`. `__cmd_kallsyms()` initializes a `perf_env`, records the command line into that env, creates a kernel-symbol `machine` with `machine__new_kallsyms()`, then resolves each requested symbol through `machine__find_kernel_symbol_by_name()`. For successful hits it uses `map__dso()`, `dso__short_name()`, `dso__long_name()`, and `map__unmap_ip()` to print module/DSO names and address ranges.

## Control Flow
`cmd_kallsyms()` parses only `-v/--verbose`, requires at least one symbol name, enables `symbol_conf.try_vmlinux_path` when no explicit vmlinux was supplied, initializes symbols, and delegates to `__cmd_kallsyms()`. The helper creates the kallsyms-backed machine, loops over input names, prints either `<name>: not found` or a formatted symbol line, then deletes the machine and exits the perf environment.

## State and Persistence Behavior
State is local to one process invocation. The command reads `/proc/kallsyms` and optional vmlinux/module symbol data through perf symbol infrastructure, but writes no persistent output. `perf_env__set_cmdline()` stores the searched symbol names in the temporary environment object.

## Dependencies and Integration Points
Depends on perf symbol, machine, map, DSO, env, debug, and parse-options infrastructure. It integrates with the live host kernel symbol source and global `symbol_conf`, especially vmlinux path selection and verbosity.

## Risks and Edge Cases
The command requires access to `/proc/kallsyms`; kernel pointer restrictions or permissions can reduce symbol fidelity. A failure to create the machine returns a generic `-1`. Symbols are looked up by exact name and duplicate names resolve according to machine symbol lookup behavior. Output includes both unmapped and raw symbol addresses, so users need to understand module address translation.

## Test Signals
Test known kernel symbols, known module symbols, unknown names, restricted `/proc/kallsyms` environments, explicit and implicit vmlinux path behavior, and verbose mode. Cleanup signals are no leaked machine/env objects and correct nonzero return on initialization failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-kallsyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-kmem.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-kmem.c

## Purpose
Implements `perf kmem`, including `perf kmem record` and `perf kmem stat`. It records or analyzes kernel memory allocation tracepoints for slab allocations and page allocator activity, producing per-allocation, per-callsite, live-page, GFP flag, migration-type, fragmentation, ping-pong, and summary statistics.

## Important APIs, Types, and Functions
The entry point is `cmd_kmem()`. Recording is implemented by `__cmd_record()`, which builds a `perf record` argv for slab and/or page tracepoints. Analysis is implemented by `__cmd_kmem()`, with sample dispatch in `process_sample_event()`. Slab state uses `struct alloc_stat` and rb-trees `root_alloc_stat`, `root_caller_stat`, and sorted variants; handlers are `evsel__process_alloc_event()` and `evsel__process_free_event()`. Page state uses `struct page_stat`, live/alloc/caller rb-trees, sort-input lists, `order_stats`, and handlers `evsel__process_page_alloc_event()` and `evsel__process_page_free_event()`.

Callsite discovery for page allocations uses `build_alloc_func_list()` to collect kernel allocation functions by regex from the kernel map and `find_callsite()` to walk callchains until the first non-allocation function. GFP formatting uses `struct gfp_flag`, `parse_gfp_flags()`, `compact_gfp_flags()`, `compact_gfp_string()`, and the static compact-name table. Output and sorting are handled by `sort_result()`, `__sort_slab_result()`, `__sort_page_result()`, `__print_slab_result()`, `__print_page_alloc_result()`, `__print_page_caller_result()`, `print_gfp_flags()`, `print_slab_summary()`, `print_page_summary()`, and many `*_cmp()` sort-dimension callbacks.

## Control Flow
`cmd_kmem()` loads `kmem.default` config, parses subcommands and options, defaults to slab or page analysis when neither was requested, and dispatches `record` by synthesizing a `perf record -a -R -c 1` command with the relevant tracepoints. Slab record includes legacy `_node` tracepoints only when exposed. Page record adds `-g` so stat mode can resolve callsites from callchains.

For `stat`, the command opens the input perf.data session with ordered events, verifies required tracepoints exist, gets page size from traceevent metadata for page mode, enables callchains for page mode, initializes symbols, parses time filters, sets locale and CPU-to-node mapping, installs default sort keys and page grouping keys, then calls `__cmd_kmem()`. `__cmd_kmem()` verifies trace data, registers tracepoint handlers by name, detects `pfn` versus `page` field naming, processes events, sorts accumulated rb-trees, and prints selected reports plus summaries.

Slab allocation events aggregate by allocation pointer and callsite, update total requested/allocated bytes and NUMA cross-allocation counts. Slab free events find the pointer, add freed bytes, and record cross-CPU ping-pong if freed on a different CPU. Page allocation events parse page/PFN, order, GFP flags, migration type, allocation bytes, and callsite, then update live, allocation, caller, and order/migration trees. Page free events match the live page, account unmatched frees, update free bytes, and in live mode remove or decrement live allocation records.

## State and Persistence Behavior
Analysis state is entirely in static globals for the invocation: mode flags, line limits, sort lists, rb-trees, counters, GFP cache, callsite function list, page size, time filter, and `kmem_session`. Input perf.data is read-only. `record` writes perf.data through `cmd_record()` using synthesized tracepoint options. `stat` writes text to stdout/pager. The command mutates rb-tree membership when sorting by moving nodes from raw trees to sorted trees, so printing is terminal for the accumulated state.

## Dependencies and Integration Points
Depends on perf session/tool/evsel tracepoint handler infrastructure, traceevent/libtraceevent field decoding, kernel symbol maps, callchain resolution, CPU-to-NUMA mapping, rbtree/list utilities, parse-options subcommands, perf time filtering, locale-aware printing, and `cmd_record()` from the perf record command. It integrates with kernel tracepoints `kmem:kmalloc`, `kmem:kfree`, `kmem:kmem_cache_alloc`, `kmem:kmem_cache_free`, optional legacy node allocation tracepoints, `kmem:mm_page_alloc`, and `kmem:mm_page_free`.

## Risks and Edge Cases
This snapshot contains duplicated source fragments (`kmem_cache_alloc` handler entry, duplicated `while (true)`, duplicated `else`) that are compile-time or maintenance risk signals. Page migration type indexes are used directly against a fixed six-entry string/table and `order_stats[MAX_PAGE_ORDER][MAX_MIGRATE_TYPES]`, so unexpected kernel values can index out of bounds. GFP compaction can return NULL for unknown flags, yet printing uses the returned string with `%s`. `process_sample_event()` returns early on time-skip without `thread__put(thread)`, which is a leak risk in this source. `parse_filter_event()`-style ownership is not present here, but many sort dimensions are duplicated with `memdup()` and not freed before process exit.

Accounting is tracepoint-format sensitive: field names changed from `page` to `pfn`, slab node fields are optional, legacy tracepoints may or may not exist, and page callsite attribution requires callchains and successfully loaded kernel symbols. Live page mode changes semantics by decrementing/removing records on free rather than aggregating total alloc/free. Unmatched frees and allocation failures are tracked but can skew summary interpretation.

## Test Signals
Test `perf kmem record --slab`, `--page`, both modes, and legacy-tracepoint detection. For `stat`, test slab-only, page-only, combined, `--caller`, `--alloc`, custom `--sort`, `--line`, `--raw-ip`, `--live`, and `--time`. Validate NUMA cross allocation counts, ping-pong counts, fragmentation math, page/PFN field detection, GFP compact legend generation, migration/order summary, unmatched free and allocation failure counts, symbolized and raw callsites, default `kmem.default` config, and graceful error messages when required tracepoints are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-kmem.c -->
