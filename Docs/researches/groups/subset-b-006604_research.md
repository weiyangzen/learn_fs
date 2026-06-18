# subset-b-006604 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-kvm.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-kvm.c

## Purpose

`builtin-kvm.c` implements the `perf kvm` command family. At the top level it wraps ordinary `perf record`, `perf report`, `perf top`, `perf diff`, and `perf buildid-list` so host/guest defaults and KVM-specific data file names are applied. When libtraceevent support is available it also implements `perf kvm stat`, including offline `record`/`report` and timerfd-driven live reporting of KVM tracepoints such as VM exits, MMIO, and IO port events.

## Important APIs, Types, and Functions

The primary state type is `struct perf_kvm_stat` from `util/kvm-stat.h`, which carries the perf tool callbacks, session, evlist, target options, selected report event, sort key, VCPU filter, totals, event decoding operations, and live-display settings. `struct kvm_event` stores one histogram row with an event key, a `hist_entry`, total timing/count stats, per-VCPU stats, and a back pointer to the active `perf_kvm_stat`. `struct vcpu_event_record` is attached to each perf thread via `thread__priv()` and tracks the active begin event and timestamp for that VCPU thread.

Histogram output is configured through `struct kvm_dimension`, `struct kvm_fmt`, and the global `kvm_hists`. `kvm_hpp_list__parse()`, `get_format()`, and `kvm_hists__reinit()` adapt KVM dimensions to perf hpp columns and sort fields. KVM event matching flows through architecture hooks registered by `register_kvm_events_ops()`, which selects `kvm->events_ops` from `kvm_reg_events_ops(e_machine)`.

Important processing functions include `find_create_kvm_event()`, `handle_begin_event()`, `handle_child_event()`, `handle_end_event()`, `handle_kvm_event()`, `process_sample_event()`, `read_events()`, `kvm_events_report_vcpu()`, `kvm_events_record()`, `kvm_events_live()`, `perf_kvm__mmap_read()`, and `perf_kvm__handle_timerfd()`. Top-level dispatch is in `cmd_kvm()`, with wrapper helpers `__cmd_record()`, `__cmd_report()`, `__cmd_buildid_list()`, `__cmd_top()`, and `kvm_cmd_stat()`.

## Control Flow

`cmd_kvm()` parses global KVM options, defaults to guest collection unless host is explicitly requested, chooses a file name such as `perf.data.guest`, `perf.data.host`, or `perf.data.kvm`, then dispatches to the requested subcommand. The non-stat subcommands mostly build a new argv array and call the corresponding builtin. `__cmd_record()` and `__cmd_top()` add default architecture events through `kvm_add_default_arch_event(EM_HOST, ...)`; report and buildid-list add `-i <file>`.

`perf kvm stat record` builds a `perf record` invocation with raw samples, 1-sample period, 1024 mmap pages, the KVM tracepoints returned by `kvm_events_tp()`, and `-o kvm->file_name`. `perf kvm stat report` parses event, VCPU, PID, sort, force, and stdio options, initializes histograms, opens a `perf_session`, validates that the data contains KVM traces, selects architecture event ops, initializes CPU ISA decoding, processes samples, sorts histograms, and prints or browses results.

Sample handling first resolves the sample address, finds or creates the thread, obtains per-thread VCPU state on KVM entry, filters by requested VCPU and pid list, and asks architecture ops whether the sample is a begin, child, or end event. Begin events cache the timestamp and optional decoded key. End events match the active event, tolerate missing begin/end keys in some architectures, reject backward timestamps, optionally warn about long events, and update total and per-VCPU stats. Sorting collapses and resorts perf hist entries, filters zero-count rows, and prints count, time, min, max, mean, and percentage columns.

Live mode creates an evlist of host KVM tracepoints, opens and mmaps events with minimal sample bits, synthesizes threads, installs a timerfd and stdin pollfd, enables the evlist, repeatedly drains mmap buffers into ordered events, flushes by timestamp rounds, and on timer ticks sorts, prints, clears interval counters, and continues until `q` or a termination signal.

## State and Persistence Behavior

Persistent runtime state lives in `perf_kvm_stat`, global `kvm_hists`, per-thread `vcpu_event_record` objects, and allocated `kvm_event` histogram rows. Offline commands read and write perf data files only; live mode uses transient perf fds, mmap buffers, timerfd, and terminal state. Event stats are accumulated in memory and, in live mode, reset after each display interval by `clear_events_cache_stats()`.

The command mutates global perf configuration flags such as `perf_host`, `perf_guest`, `exclude_GH_default`, `use_browser`, `record_options`, and `symbol_conf` fields. Wrapper helpers allocate argv entries with `STRDUP_FAIL_EXIT()` and free them after the delegated builtin returns.

## Dependencies and Integration Points

This file integrates with perf sessions, evlists, evsels, ordered events, histograms, hpp formatting, browser UI, synthetic thread generation, target validation, symbol resolution, architecture KVM-stat hooks, KVM tracepoint descriptors, and ordinary perf builtins. Feature gates matter: most stat functionality requires `HAVE_LIBTRACEEVENT`, live mode additionally requires `HAVE_TIMERFD_SUPPORT`, and interactive browsing requires `HAVE_SLANG_SUPPORT`.

## Risks and Edge Cases

Several paths are compile-time gated, so option availability varies by build. Live mode processes copied ordered events from mmap buffers and limits events per mmap pass; regressions there can lose ordering or responsiveness. `kvm_event_expand()` reallocates per-VCPU arrays and frees the previous pointer on failure, which makes allocation failure fatal to that event state. Percentage printers use integer return types for double percentages, which can reduce comparator precision. `print_result()` divides by event count and total time after filtering; empty or partially corrupt data must avoid zero-count rows. KVM stat correctness depends heavily on architecture-specific begin/end/key hooks and tracepoint field names, especially for old kernels missing newer fields.

## Test Signals

Useful validation includes `perf kvm record/report/top/buildid-list` argv construction, stat record tracepoint selection, stat report on known KVM perf.data, VCPU and PID filtering, sort keys `sample`, `time`, `max_t`, `min_t`, `mean_t`, stdio and browser output, live mode timer refresh and `q` exit, lost-event reporting, long-duration event warnings, unsupported CPU/ISA handling, and builds with and without libtraceevent, timerfd, and slang.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-kvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-kwork.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-kwork.c

## Purpose

`builtin-kwork.c` implements `perf kwork`, a kernel work profiler for IRQ handlers, softirqs, workqueues, and scheduler activity. It can record the relevant tracepoints, report runtime totals, report raise-to-entry latency, print chronological time histories, and compute a top-like task CPU-usage view. Some report/top modes can also use BPF skeleton helpers when the build enables them.

## Important APIs, Types, and Functions

The central state object is `struct perf_kwork` from `util/kwork.h`. It owns the `perf_tool`, selected work classes, atom pages, comparison and sort lists, sorted output tree, profile filters, time window, CPU bitmap, report type, counters for lost and skipped events, and BPF integration hooks. `struct kwork_class` describes a supported work family with tracepoint names, class initialization, work identity extraction, and display-name generation. `struct kwork_work` is a per-work aggregate stored in RB trees. `struct kwork_atom` records individual raise/entry/exit timestamps; atoms are allocated from `struct kwork_atom_page` pools using a bitmap.

Important helpers include `setup_event_list()`, `setup_sorting()`, `sort_dimension__add()`, `work_findnew()`, `work_push_atom()`, `work_pop_atom()`, `profile_event_match()`, `perf_kwork__check_config()`, `perf_kwork__read_events()`, `perf_kwork__report()`, `perf_kwork__timehist()`, `perf_kwork__top()`, and `perf_kwork__record()`. Class-specific handlers map tracepoints to generic state transitions for IRQ, softirq, workqueue, and sched classes.

## Control Flow

`cmd_kwork()` initializes the static `perf_kwork`, registers mmap and sample callbacks, parses the subcommand, adds an `id` comparison for identity lookups, and dispatches. `record` selects default classes `irq, softirq, workqueue` unless overridden, then builds a `perf record -a -R -m 1024 -c 1` argv with each selected tracepoint as `-e`.

For offline reporting, `perf_kwork__read_events()` opens the input perf.data, initializes symbols, calls `perf_kwork__check_config()` to select operation handlers and register tracepoint handlers, parses CPU/time filters, validates callchain availability, optionally prints a timehist header, and processes the session. Tracepoint samples are routed through `perf_kwork__process_tracepoint_sample()` to the evsel handler installed by each class.

The runtime report path records entry atoms and consumes them on exit, updating total runtime, max runtime, and count. The latency path records raise atoms and consumes them on entry, updating total latency, max latency, and count. The timehist path records raise and entry atoms, resolves optional callchains at entry time, and prints one line when the matching exit is seen. The top path uses scheduler switch events as task runtime spans, also tracks irq/softirq runtime, subtracts interrupt time from task time where possible, computes per-CPU totals and idle/load ratios, merges tasks by PID except idle tasks remain per CPU, sorts by rate/runtime/tid, and prints CPU summaries plus task rows.

## State and Persistence Behavior

State is in memory only, except for perf.data written by the record subcommand. Atom pages are never individually freed during processing; atoms are returned to page bitmaps as transitions complete. Unmatched atoms left on work lists are counted as skipped events during output. The static `perf_kwork` is initialized once per process invocation and carries selected class list, sort list, profile filters, and counters through the selected subcommand.

BPF modes start a live trace, wait for a signal using `pause()`, finish tracing, read BPF maps into the same aggregate structures, and clean up BPF resources. Time filtering updates `timestart` and `timeend` only when summary mode is enabled.

## Dependencies and Integration Points

The file depends on perf data/session/event APIs, libtraceevent tracepoint field decoding, symbol and callchain resolution, RB tree/list/bitmap helpers, `util/kwork.h`, optional BPF skeleton functions, pager setup, and ordinary `cmd_record()`. It integrates with kernel tracepoints `irq:irq_handler_entry/exit`, `irq:softirq_raise/entry/exit`, `workqueue:workqueue_activate_work/execute_start/execute_end`, and `sched:sched_switch`.

## Risks and Edge Cases

State matching is tracepoint-order sensitive. Missing raise, entry, or exit events produce skipped atom counts and can bias runtime or latency. `work_push_atom()` can overwrite a previous unmatched atom and count it as skipped. Filtering by name is disabled for top until all task runtime is collected, so later merge/filter behavior must be correct. Work identity differs by report type: IRQ and softirq use interrupt IDs for most reports but common pid in top mode. Workqueue names depend on kernel-address resolution and may be null. The class objects are static and linked into lists; duplicate setup in an unusual reentrant invocation would be unsafe. BPF behavior depends on build support and runtime privileges.

## Test Signals

Good tests include record argv contents for default and explicit `--kwork`, runtime reports over synthetic irq/softirq/workqueue traces, latency reports with raise/entry pairs, skipped-event accounting for missing pairs, CPU/name/time filters, timehist with and without callchains, top reports with scheduler-only and scheduler-plus-interrupt traces, BPF report/top smoke tests where available, invalid sort and event names, lost-event summaries, and builds without BPF skeleton support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-kwork.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-list.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-list.c

## Purpose

`builtin-list.c` implements `perf list`, the command that enumerates predefined perf events, PMU aliases, tracepoints, SDT probes, libpfm events when available, metrics, and metric groups. It supports default human output, raw name-only output, JSON output, optional descriptions and details, PMU/unit filtering, deprecated-event inclusion, and output redirection.

## Important APIs, Types, and Functions

`struct print_state` holds the common printing configuration: output stream, PMU glob, event glob, output style flags, metric toggles, duplicate tracking, and last printed topic/group. `struct json_print_state` embeds `print_state` and adds separator state for JSON arrays. Output is driven by `struct print_callbacks` from `util/print-events.h`; this file supplies default and JSON callbacks for start, end, event, metric, and duplicate-PMU behavior.

Key helpers include `wordwrap()` for pager-width aligned text wrapping, `default_print_event()`, `default_print_metric()`, `fix_escape_fprintf()` for JSON escaping of string fields, `json_print_event()`, `json_print_metric()`, `default_skip_duplicate_pmus()`, `json_skip_duplicate_pmus()`, and `cmd_list()`.

## Control Flow

`cmd_list()` parses options, selects either default or JSON callback tables, opens `--output` when supplied, and configures the pager for non-raw output. In default mode it initializes `last_topic`, a `visited_metrics` string list, and optional `pmu_glob` from `--unit` or the hidden compatibility `--cputype`. If no positional arguments are given, it enables metrics and metric groups unless a unit filter is active, then calls `print_events()`.

With positional filters, the command handles well-known selectors. `tracepoint` temporarily restricts the PMU glob to tracepoints. `hw`, `sw`, `cache`, and `pmu` map to legacy event globs or ABI-excluding PMU listings. `sdt` calls `print_sdt_events()`. `metric` and `metricgroup` toggle metric callbacks and call `metricgroup__print()`. `pfm` calls libpfm printing when compiled in. Arguments containing `:` are treated as tracepoint-style globs and are also used to search SDT and metrics. All other arguments are wrapped in `*...*` and used as broad event, SDT, and metric globs.

Default event printing filters deprecated events, PMU names, ABI PMUs, event names, aliases, and topics before printing topic headers, names, aliases, type descriptions, descriptions, and detailed encodings. Metric printing filters by metric or group name, emits group headers, deduplicates metric names in raw mode, and optionally prints descriptions, expressions, and thresholds. JSON callbacks apply similar filters and emit an array of event/metric objects with escaped fields.

## State and Persistence Behavior

There is no persistent repository or kernel state. Runtime state consists of allocated glob strings, last-topic/group strings, visited metric names, optional output `FILE *`, and JSON separator state. `cmd_list()` frees `pmu_glob`, `last_topic`, `last_metricgroups`, and `visited_metrics` and closes the output file at exit. It does not validate `fopen()` failure before using `ps->fp`, which is an important operational edge case.

## Dependencies and Integration Points

The file integrates with perf PMU discovery (`perf_pmus__print_pmu_events()`, `perf_pmus__pmu_for_pmu_filter()`), event printing (`print_events()`), SDT printing, metric groups (`metricgroup__print()`, `describe_metricgroup()`), optional libpfm, pager utilities, parse-options, string glob helpers, strlist, strbuf, and global `verbose`.

## Risks and Edge Cases

JSON is manually emitted, so escaping or separator regressions can break machine consumers. `fix_escape_fprintf()` supports only `%s` and `%S`; unexpected format characters log an error but still writes literal output. `default_print_event()` allocates a unit-augmented description with `asprintf()` and relies on positive length to choose it. Pager setup is called twice in some non-raw paths. The default mode skips duplicate PMUs unless long descriptions are requested, while JSON intentionally does not, so output size and duplicate semantics differ. `--output` failure can leave a null stream. Metric raw-mode deduplication requires `visited_metrics` initialization and only applies to default output.

## Test Signals

Useful tests include default output with no args, `--raw-dump`, `--json`, `--desc` and `--long-desc`, `--details`, `--deprecated`, `--unit`, hidden `--cputype`, output to a file, selectors for hardware/software/cache/pmu/tracepoint/sdt/metric/metricgroup, colon tracepoint globs, arbitrary globs, JSON escaping of quotes, backslashes, and newlines, metric deduplication in raw output, and behavior when no PMU matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-lock.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-lock.c

## Purpose

`builtin-lock.c` implements `perf lock`, including recording lock tracepoints, reporting legacy lockdep/lock_stat sequences, printing lock metadata, delegating `script`, and reporting lock contention from either recorded `lock:contention_*` tracepoints or live BPF collection. It can aggregate by lock address, task, caller, or cgroup, filter by lock type/address/symbol/callstack/cgroup, show owner stacks, and emit stdio or CSV-style output.

## Important APIs, Types, and Functions

Global command state includes the active `perf_session`, `target`, output stream, option booleans, lock filters, injected delays, aggregation mode, RB roots for thread stats and sorted results, and the global `lockhash_table` from lock-contention utilities. `struct thread_stat` and `struct lock_seq_stat` track per-thread lock state machines for legacy lockdep events. `struct lock_stat` aggregates counts, wait times, names, flags, callstacks, and broken-state information. `struct lock_key` defines selectable sort/output fields.

Important functions include `thread_stat_findnew_*()`, `get_seq()`, legacy handlers `report_lock_acquire_event()`, `report_lock_acquired_event()`, `report_lock_contended_event()`, `report_lock_release_event()`, contention handlers `report_lock_contention_begin_event()` and `report_lock_contention_end_event()`, callchain helpers `lock_contention_caller()`, `callchain_id()`, `get_callstack()`, report orchestration `__cmd_report()`, contention orchestration `__cmd_contention()`, recorder `__cmd_record()`, filter parsers, and top-level `cmd_lock()`.

## Control Flow

`cmd_lock()` allocates and initializes the lock hash table, sets the default output to stderr, parses global options, and dispatches. `record` first checks whether legacy lock tracepoints are valid. If not, it falls back to contention tracepoints and adds a frame-pointer call graph. It then builds `perf record -R -m 1024 -c 1 --synth task` plus selected `-e` tracepoints and delegates to `cmd_record()`.

`report` uses legacy lock tracepoints. It opens perf.data, initializes symbols, installs tracepoint handlers, configures output fields and sort key, processes events, optionally combines locks with the same class name, sorts hash-table entries into a result RB tree, and prints acquired/contended/wait columns. The legacy state machine follows acquire -> contended -> acquired -> release transitions, handles read-lock nesting, updates wait time totals/min/max, and marks broken sequences when events arrive out of order.

`info` reuses the report processing path but prints thread IDs and/or lock address-to-name maps. `contention` selects aggregation mode from options, validates incompatible combinations, sets up a `lock_contention` object, and either prepares live BPF tracing or opens perf.data and installs contention tracepoint handlers. After collection or event processing it sorts by the selected contention key and prints rows according to aggregation mode. Caller aggregation hashes callchains and can save/print representative call stacks; address filters may defer symbol names until kernel maps are loaded.

## State and Persistence Behavior

Recording writes perf.data through `cmd_record()`. Reporting is in-memory: lock stats are stored in `lockhash_table`, thread state is stored in `thread_stats`, result ordering uses RB roots, and filters/delays are dynamically allocated then released by `lock_filter_finish()`. `--output` opens a file and redirects report output. BPF contention mode creates an evlist, optional workload, BPF maps/programs through `lock_contention_prepare()`, waits for a signal, reads BPF results, and cleans up.

Global state is significant and mostly process-lifetime: `trace_handler`, `sort_key`, `output_fields`, `aggr_mode`, `symbol_conf.field_sep`, and filter arrays are mutated during command parsing. `process_event_update()` reinstalls tracepoint handlers as event metadata updates arrive.

## Dependencies and Integration Points

The file depends on perf sessions, evlists, evsels, tracepoint validation, libtraceevent field access, symbol and callchain resolution, target and cgroup helpers, `util/lock-contention.h`, BPF skeleton lock data, pager and parse-options, and the ordinary `cmd_record()`/`cmd_script()` builtins. It consumes kernel tracepoints `lock:lock_acquire`, `lock:lock_acquired`, `lock:lock_contended`, `lock:lock_release`, `lock:contention_begin`, and `lock:contention_end`.

## Risks and Edge Cases

Legacy lock-stat reporting depends on CONFIG_LOCKDEP/CONFIG_LOCK_STAT tracepoints and exact event ordering; missing events produce broken sequences and skewed counts. Contention reporting has two data sources with different failure modes: perf.data requires recorded contention tracepoints, while BPF requires build support, privileges, and target validation. Caller aggregation hashes callchain IPs, so collisions are possible and unresolved callchains become unknown callers. Address and symbol filters require kernel map loading and can silently ignore unknown symbols. CSV separators are restricted because symbols and type strings use common punctuation. Some option-error paths return before freeing the lock hash table or closing output files. `add_lock_slab()` leaks the duplicated string if the realloc fails.

## Test Signals

Useful validation includes record fallback when legacy tracepoints are absent, report on known legacy lock traces, info thread/map output, contention report from recorded contention events, BPF contention smoke tests with and without workloads, aggregation modes for caller/task/address/cgroup, lock type/address/symbol/callstack/cgroup filters, owner-stack output, CSV output and separator rejection, `--entries` limiting while footer totals remain correct, broken-sequence histograms under verbose mode, injected-delay parsing limits, and builds without BPF skeleton support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-mem.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-mem.c

## Purpose

`builtin-mem.c` implements `perf mem`, a focused frontend for memory access sampling. The `record` subcommand configures memory-load/store events and delegates to `perf record`; the `report` subcommand delegates to `perf report --mem-mode` or dumps raw memory samples in text form. It also handles memory-operation selection, CPU filtering, physical address capture/reporting, data page size capture/reporting, and memory data-type profiling.

## Important APIs, Types, and Functions

`struct perf_mem` stores command state: embedded `perf_tool`, input name, sort key, booleans for unresolved-symbol hiding, raw dumping, force, physical address, page size, all-kernel/all-user, data type mode, selected load/store operations, CPU list, and CPU bitmap. `parse_record_events()` selects and configures PMU memory events from `-e`. `__cmd_record()` builds delegated record arguments. `dump_raw_samples()`, `process_sample_event()`, and `report_raw_events()` implement raw sample reporting. `get_sort_order()` builds default report sort keys. `__cmd_report()`, `parse_mem_ops()`, and `cmd_mem()` orchestrate command behavior.

## Control Flow

`cmd_mem()` initializes defaults to `perf.data` and both load/store sampling, parses common options and the `record` or `report` subcommand, resolves stdin pipe input when no input name is set, and dispatches on a prefix match for `record` or `report`.

`record` first locates a PMU supporting perf memory events and initializes memory-event support. It parses record-specific options while keeping unknown options for `cmd_record()`. It allocates enough argv space for all memory PMUs and optional CPU filtering, starts with `record`, decides whether the combined load-store event can satisfy both requested operations, otherwise enables separate load/store records, adds `-W` when weight sampling is needed and always adds `-d` for data source sampling. It appends `--phys-data`, `--data-page-size`, generated PMU event arguments from `perf_mem_events__record_args()`, all-user/all-kernel flags, CPU list, and remaining user arguments before calling `cmd_record()`.

`report` parses report options. If `--dump-raw-samples` is set it creates a perf session, configures a tool that resolves mmap/comm/fork/attr/build-id/auxtrace metadata, optionally builds a CPU bitmap, initializes symbols, prints a raw header, and processes events through `dump_raw_samples()`. Otherwise it builds `report --mem-mode -n`, appends a generated default `--sort=...` when needed, passes remaining arguments through, and calls `cmd_report()`.

`dump_raw_samples()` resolves the sample address, applies unresolved-symbol filtering, marks the DSO as hit, prints PID/TID/IP/data address, optional physical address and data page size, local weight, data source encoding, DSO, and symbol using the configured field separator.

## State and Persistence Behavior

The only persistent artifact is perf.data written by `record`; `report` reads perf.data or stdin. Runtime state is contained in `struct perf_mem`, global `input_name`, `symbol_conf.field_sep`, global memory-event configuration such as `perf_mem_record[]` and `perf_mem_events__loads_ldlat`, and temporary delegated argv arrays. Raw reporting creates and deletes a `perf_session`; delegated report/record leave persistence to those builtins.

## Dependencies and Integration Points

This file integrates with perf PMU memory-event helpers, perf record/report builtins, perf sessions, auxtrace synthesis, symbol resolution, address-location and DSO helpers, CPU bitmap parsing, sort key help for `SORT_MODE__MEMORY`, parse-options, and memory data source fields in perf samples. It relies on PMU support for memory events and on `perf_mem_events__record_args()` to emit architecture/PMU-specific event selectors.

## Risks and Edge Cases

No PMU support or failed memory-event initialization aborts record. `parse_record_events()` calls `exit()` for list/parse failures rather than returning an error, which is consistent with some perf option callbacks but makes it hard to recover. `get_sort_order()` uses a fixed 128-byte buffer and appends optional keys; current strings fit but future sort expansions need care. Store-only reports omit weight-oriented columns because stores have no cost. Raw output mutates `symbol_conf.field_sep` to a space when none is supplied. The non-field-separator IP/address format contains a suspicious `0x016` literal for the data address field, which may be a formatting bug. Combined load-store event selection depends on PMU tags and requested operation bits.

## Test Signals

Useful tests include `perf mem record` with default load/store, load-only, store-only, `-e list`, custom event strings, CPU lists, all-user/all-kernel, physical address and page-size flags, report default sort generation for load/store/data-type modes, `--sort` overriding while preserving `type` for data-type profile, raw dumping with and without field separators, hide-unresolved behavior, CPU filtering on raw reports, stdin input detection, and no-memory-PMU failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-probe.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-probe.c

## Purpose

`builtin-probe.c` implements `perf probe`, the frontend for defining, listing, deleting, previewing, and exploring kprobes/uprobes. It parses user probe definitions, optional executable/module targets and namespaces, source-line and variable queries when DWARF support is available, function filters, cache operations, bootconfig output, and symbol configuration, then delegates the actual conversion and tracefs/cache mutation to probe utility libraries.

## Important APIs, Types, and Functions

The command state is held in a heap-allocated static `params` object. It stores the selected command, whether uprobes are active, whether the current target was consumed, number of probe events, an array of `struct perf_probe_event`, a `struct line_range`, target path/module, `struct strfilter`, and namespace info. Major helpers are `init_params()`, `cleanup_params()`, `parse_probe_event()`, `parse_probe_event_argv()`, `set_target()`, `opt_set_target()`, `opt_set_target_ns()`, `params_add_filter()`, `perf_add_probe_events()`, `perf_del_probe_events()`, `del_perf_probe_caches()`, `__cmd_probe()`, and `cmd_probe()`.

The implementation depends heavily on utility APIs such as `parse_perf_probe_command()`, `convert_perf_probe_events()`, `apply_perf_probe_events()`, `show_probe_trace_events()`, `show_bootconfig_events()`, `show_perf_probe_events()`, `show_available_funcs()`, `show_line_range()`, `show_available_vars()`, and probe-file/cache helpers.

## Control Flow

`cmd_probe()` allocates and initializes `params`, calls `__cmd_probe()`, then clears all parsed events, line ranges, filters, namespace references, and target strings. `__cmd_probe()` builds the option table, applies exclusivity rules, disables DWARF-only options when libdw support is absent, parses options, reconciles quiet/verbose, and handles remaining positional probe definitions. A leading absolute non-`.ko` path can become an implicit executable target; remaining words are joined into one probe definition string.

Option callbacks set `params->command` and populate state. `--add` and `--definition` parse probe events. `--del`, `--list`, `--funcs`, and `--filter` build `strfilter` expressions. `--line` parses a line range, and `--vars` parses a probe point while rejecting arguments. `--exec` and `--module` set target type and normalize paths with namespace-aware realpath for uprobes or explicit paths. `--target-ns` creates namespace info from a pid if setns is needed.

After parsing, symbol arguments are validated, default max probes are set, vmlinux build-id checks are relaxed for offline informational commands, and a switch executes the selected command. Listing refuses `--exec`. Function, line, and variable queries call the corresponding display helper. Deletion either purges probe caches or opens kprobe/uprobe event files, gathers matching events, deletes them, and warns if nothing matched. Add/definition conversion initializes symbol maps, converts perf probe events to trace events, optionally prints definitions or bootconfig, otherwise applies events and prints how to use the last added event. The add path also guards that the last `-x`/`-m` target option must follow the probe definitions it should affect.

## State and Persistence Behavior

Adding and deleting probes mutates kernel tracing state through kprobe/uprobe event files unless cache mode is selected. Cache mode mutates probe cache entries under build-id cache storage. Definition mode prints generated definitions without applying them. Bootconfig mode emits bootconfig-compatible definitions and rejects uprobes. In-memory state includes parsed probe events, namespace references, filters, target strings, and line-range data; cleanup releases these at command exit. Each `perf_probe_event` receives a target copy and namespace reference when applicable.

## Dependencies and Integration Points

The file integrates with perf probe-finder/probe-event/probe-file libraries, build-id cache helpers, namespace handling, symbol configuration and validation, strfilter parsing, Linux tracefs probe event files, optional libdw source/variable discovery, demangling options, symfs handling, and parse-options. It is the user-facing command wrapper around lower-level probe conversion and application APIs.

## Risks and Edge Cases

`parse_probe_event()` increments `nevents` before checking `MAX_PROBES`, so the boundary condition is delicate and relies on later cleanup behavior. Several callbacks return negative errno-style values that are later printed through `pr_err_with_code()`. Target ordering is user-visible: `-x`/`-m` must follow probe definitions for that target, and an unused final target is treated as an error. `set_target()` only treats absolute paths specially and infers uprobes from non-`.ko` suffixes. Deletion opens both kprobe and uprobe files and must handle partial success. Cache deletion iterates all build IDs and warns per failed cache. DWARF-only commands compile out with `NO_LIBDW=1`, changing option availability. Namespace realpath and setns behavior can fail for inaccessible target processes.

## Test Signals

Useful tests include add, definition-only, bootconfig definition, delete by filter, list, funcs, line, vars, cache deletion, executable and module targets, namespace target resolution, positional absolute target parsing, rejection of `-` input, quiet/verbose exclusivity, unused final target errors, DWARF-disabled option handling, maximum probe count, missing symbol/vmlinux validation, deletion with no matches, and add failures that must not double-free parsed events during cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-probe.c -->
