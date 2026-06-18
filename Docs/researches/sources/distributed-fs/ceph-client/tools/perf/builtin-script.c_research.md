# sources/distributed-fs/ceph-client/tools/perf/builtin-script.c

## Purpose

`builtin-script.c` implements `perf script`, the perf builtin that reads `perf.data` and prints samples, trace events, auxiliary trace synth events, statistics, and selected non-sample records in a script-friendly text form. It also runs language plugins, generated report scripts, dlfilters, and script-record/script-report helpers from perf's scripts directory.

The file is the main output-formatting and event-dispatch hub for perf data post-processing. It validates requested fields against recorded sample types, resolves symbols/maps/source lines/callchains, decodes branch stacks and instruction bytes, optionally emits per-event dump files, handles stat records and metrics, and forwards events to Python/Perl scripting backends when selected.

## Important APIs, Types, and Functions

`struct perf_script` is the command state. It embeds `struct perf_tool`, keeps the active `perf_session`, booleans for which record types to print, per-event dump and LBR stitching options, event-switch filtering state, optional CPU/thread maps for stat processing, and parsed time ranges.

Output fields are represented by `enum perf_output_field` bit values and the global `output[OUTPUT_TYPE_MAX]` table. Each output type tracks default fields, invalid fields, user-set fields, user-unset fields, wildcard state, and `print_ip_opts`. `all_output_options[]`, `parse_output_fields()`, `evsel__check_attr()`, `perf_session__check_output_opt()`, and `evsel__set_print_ip_opts()` implement field parsing and validation.

Per-event dump state is `struct evsel_script`, stored in `evsel->priv`. `evsel_script__new()` opens `<perf.data path>.<event name>.dump`, `evsel_script__fprintf()` reports size/sample count, and `perf_script__setup_per_event_dump()` either attaches a dump file per evsel or attaches a shared stdout wrapper.

Sample printing is split into small formatters: `perf_sample__fprintf_start()` prints comm, pid/tid, CPU, misc, time, TOD, machine PID, and VCPU prefixes; `perf_sample__fprintf_addr()` resolves address fields; `perf_sample__fprintf_bts()` prints branch trace samples; `perf_sample__fprintf_brstack*()` variants print branch stack addresses, symbols, offsets, or instruction blocks; `perf_sample__fprintf_insn()` prints raw instruction bytes, disassembly, and branch-stack instruction dumps; `perf_sample__fprintf_synth()` dispatches synthetic Intel PT and PowerPC VPA DTL records; `data_src__fprintf()` decodes memory data source; and `perf_sample__fprint_metric()` updates stat counts and prints derived metric values.

Script integration uses `struct scripting_ops *scripting_ops`. `setup_scripting()` registers available language backends, `parse_scriptname()` chooses a backend and script, `find_script()` locates scripts in the current directory or perf exec path, `scripting_ops->start_script()` starts a selected script, and `process_sample_event()` forwards samples to `scripting_ops->process_event()` when active. `flush_scripting()` and `cleanup_scripting()` finish backend output and teardown.

Script discovery uses `struct script_desc` and helpers such as `list_available_scripts()`, `read_script_info()`, `get_script_path()`, `has_required_arg()`, and suffix constants `-record` and `-report`. Dlfilter integration uses `dlfilter__new()`, `dlfilter__start()`, `dlfilter__filter_event_early()`, `dlfilter__filter_event()`, and `dlfilter__cleanup()`.

## Control Flow

`cmd_script()` is the entry point. It initializes scripting support, parses options and `record`/`report` subcommands, validates symbol filters, resolves script helper paths, handles live record/report script pipelines, configures dlfilters, initializes `perf_tool`, opens a `perf_session`, optionally prints headers, initializes symbols, configures itrace synthesis, parses CPU and time filters, starts external scripts, validates output fields, initializes event-switch filtering and zstd, then calls `__cmd_script()`.

`__cmd_script()` installs optional record handlers according to the user's `--show-*` flags and scripting backend capabilities. It sets custom callbacks for task, mmap, switch, auxtrace error, namespace, cgroup, lost, round, BPF, and text-poke records. It sets up per-event output targets, processes the session with `perf_session__process_events()`, prints per-event dump stats if needed, and reports debug timestamp ordering counters.

The sample path begins at `process_sample_event()`. It initializes address locations, runs the early dlfilter, applies time-range, debug timestamp-order, CPU, machine/symbol, symbol-filter, graph-function, event-switch, and normal dlfilter gates. If a language script is active, it resolves the optional address location and calls the backend's `process_event()`. Otherwise it calls `process_event()` to print text.

`process_event()` increments the event's sample count, prints the standard prefix, prints period and event name, optionally prints sample flags, and then emits fields selected for the evsel's output type. Branch-trace events take the specialized BTS path and return early. Tracepoints are formatted through libtraceevent when available. Remaining fields include synthetic payloads, address, data source, weights, instruction latency, retire latency, cgroup, IP/symbol/callchain, interrupt/user registers, branch stack forms, BPF output, instruction bytes/disassembly, physical address, page sizes, IPC, source code, and metrics.

Non-sample records use dedicated wrappers. `process_comm_event()`, `process_fork_event()`, `process_exit_event()`, `process_mmap_event()`, `process_mmap2_event()`, `process_namespaces_event()`, `process_cgroup_event()`, `process_switch_event()`, `process_lost_event()`, `process_bpf_events()`, and `process_text_poke_events()` first update perf's machine/session state where needed and then print through `print_event()` or `print_event_with_time()`. `process_exit_event()` prints before deleting the thread from the machine.

Stat processing is handled through `process_stat_config_event()`, `process_thread_map_event()`, `process_cpu_map_event()`, `set_maps()`, `process_stat_round_event()`, `process_stat()`, and `process_stat_interval()`. Metric printing in sample context lazily maps PMU metric definitions onto the evlist and then updates per-CPU/thread counts from sample periods before calling perf stat shadow-stat formatting.

Auxtrace and instruction trace control is driven by option callbacks. `parse_insn_trace()`, `parse_call_trace()`, and `parse_callret_trace()` adjust output fields, request itrace synthesis, and enable nanosecond timestamps. `perf_script__process_auxtrace_info()` lets generic auxtrace setup run and then re-runs per-event dump setup because auxtrace can synthesize additional evsels.

## State and Persistence Behavior

This command reads `input_name` through `struct perf_data data` in read mode. It normally writes to stdout, but `--per-event-dump` creates one file per evsel using the pattern `<input path>.<event name>.dump`. Script record/report helper modes can exec shell scripts that themselves record or report data, and live pipeline mode forks a recorder script with stdout connected to a reporter script's stdin.

Global state includes selected script name/language, relative/delta timestamp state, initial/previous timestamps, debug timestamp counters, `no_callchain`, `latency_format`, `system_wide`, `print_flags`, CPU filter bitmap, branch block limit, dlfilter arguments, scripting backend pointer, output field table, script descriptors list, and perf globals such as `symbol_conf`, `stat_config`, `session_done`, `dump_trace`, `verbose`, `use_browser`, and `perf_guest`.

Per-session state is owned by `perf_session` and `evlist`. `cmd_script()` frees parsed time ranges, zstd state, evlist stats, the session, CPU/thread maps, dlfilter resources, and dlfilter arguments on exit. Per-event dump files are closed after processing. External script execution paths call `execvp()` and do not return in successful child/replacement processes.

Timestamp output can be absolute perf time, relative to the first printed sample (`--reltime`), delta from previous printed sample (`--deltatime`), or time-of-day (`tod`) reconstructed from clock metadata in the perf.data header. The `tod` field is rejected if the header lacks clock data.

## Dependencies and Integration Points

The file depends on most perf core subsystems: perf sessions, evlists, evsels, machines, maps, DSOs, symbol resolution, srcline/source lookup, callchains, branch stacks, auxtrace, itrace synthesis, stat/metric infrastructure, cgroups, event updates, thread and CPU maps, zstd decompression, pager/UI setup, and parse-options.

Optional integrations include libtraceevent for tracepoint formatting and Perl scripting setup, Python scripting support, libcapstone for `disasm` field support, XED via pager piping for `--xed`, dlfilter shared objects, addr2line/source lookup, guest kernel symbol paths, and Intel PT/PowerPC synthetic event payload decoders.

`perf script` can call `cmd_record()` indirectly only through discovered record helper scripts or user workflows; direct record subcommand behavior is implemented by looking up `*-record` scripts. It also supports `perf script report <script>` by looking up `*-report` scripts under `PERF_EXEC_PATH`'s scripts directory.

## Risks and Edge Cases

Field validation is complex and central to correctness. If a user explicitly asks for a field missing from the recorded sample type, `evsel__check_attr()` usually fails; if the field was only a default, it is silently removed. AUX trace sessions get broader allowance for user-set fields because synthesis may provide them later. Changes to sample type semantics or new output fields need updates in `all_output_options[]`, defaults, invalid masks, parser help, validators, and printers.

Several functions use static formatting state (`initial_time`, `previous_time`, `last_timestamp`, `nr_unordered`, `maxlen`, callindent spacing, metric initialization), so the command is not reentrant. The output table is global and mutated by parsing and validation, so repeated use in a long-lived embedding would need reset logic.

Per-event dump filenames are derived from event names with `asprintf("%s.%s.dump", data->file.path, evsel__name(evsel))`. Event names containing path separators or unusual characters could produce awkward filenames. The code assumes short-lived command execution and does not sanitize those names here.

Branch stack instruction dumping is best-effort. `grab_bb()` refuses huge blocks, cross kernel/user blocks, unresolved maps, or unreadable DSO data. It can patch missing kernel transfers and may print mismatch diagnostics when LBR data and executable bytes do not line up. Disassembly depends on build-time support and available DSO bytes.

External script modes replace the current process with `/bin/sh` running discovered scripts, and live mode forks before exec. Argument partitioning depends on script metadata `args:` lines and `top` suffix detection. Bad metadata can cause confusing argument splits. `have_cmd()` parses record options only to determine whether collection should be system-wide.

Filtering order matters. Early dlfilters can see unresolved or partially resolved locations, while normal dlfilters run after symbol/time/CPU gates. `--graph-function` uses thread stack depth and branch flags; it can suppress events until a matching symbol is seen and depends on accurate call/return samples. `--reltime` and time-range parsing interact because relative ranges are parsed after the session is opened.

## Test Signals

Core smoke tests should include `perf script -i perf.data` on hardware, software, tracepoint, raw, and synthetic-event data, with and without callchains. Field tests should exercise `-F` global fields, type-qualified fields, `+field`, `-field`, invalid fields, missing sample attributes, `dsoff` implying `dso`, `tod` with and without clock metadata, and `disasm` on builds without libcapstone.

Filtering tests should cover `--cpu`, `--time`, `--pid`, `--tid`, `--comms`, `--dsos`, `--symbols`, `--addr-range`, `--graph-function`, `--stop-bt`, and event switch options. Debug mode should be tested with ordered and intentionally unordered fixtures to verify `nr_unordered` reporting.

Output mode tests should include stdout, `--per-event-dump`, `--header`, `--header-only`, `--show-task-events`, `--show-mmap-events`, `--show-switch-events`, `--show-namespace-events`, `--show-cgroup-events`, `--show-lost-events`, `--show-round-events`, `--show-bpf-events`, and `--show-text-poke-events`.

Integration tests should cover Python or Perl script execution, `-g/--gen-script`, script listing, `record`/`report` helper discovery, live record/report piping, dlfilter loading plus `--dlarg`, itrace options, `--insn-trace`, `--call-trace`, `--call-ret-trace`, `--stitch-lbr`, guest symbol options, stat round processing, and metric output.
