# subset-b-006602 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/sched-pipe.c -->
# sources/distributed-fs/ceph-client/tools/perf/bench/sched-pipe.c

Purpose: implements `perf bench sched pipe`, a scheduler and IPC benchmark that ping-pongs integer tokens through two pipes between either two processes or two pthreads. It times `loops` round trips and reports elapsed time, usecs/op, and ops/sec using the global `bench_format`.

Important APIs, types, and functions: `struct thread_data` carries task index, pipe ends, optional epoll state, cgroup failure state, and pthread id. `parse_two_cgroups()` parses the `--cgroups SEND,RECV` option. `enter_cgroup()` and `exit_cgroup()` integrate with perf's `util/cgroup.h` helpers and cgroupfs files. `read_pipe()` handles blocking or epoll-assisted nonblocking reads. `worker_thread()` performs the ping-pong loop. `bench_sched_pipe()` parses options, creates pipes with `pipe2()`, forks or starts pthreads, joins/waits, and prints results.

Control flow: command options set `nonblocking`, `threaded`, `loops`, and optional cgroup names. Two pipes are arranged in opposite directions. In threaded mode both workers run under pthreads; in process mode the child runs one worker and the parent runs the other. Each worker optionally enters its assigned cgroup, optionally registers the read end with epoll, then repeatedly writes an int and reads one back.

State and persistence: all benchmark state is process-local except optional cgroup membership writes to `cgroup.threads`, `cgroup.procs`, or v1 `tasks`. The benchmark does not persist files. Failed cgroup entry sets `thread_data.cgroup_failed`; after timing it returns success without reporting numbers, so callers must inspect output.

Dependencies and integration points: depends on Linux pipes, fork, pthreads, epoll, cgroupfs, and perf bench's global `bench_format`. `builtin-bench.c` dispatches this through the `sched` collection.

Risks: `BUG_ON()` aborts on pipe, epoll, read, write, pthread, and syscall failures, so benchmark failures are hard exits. Nonblocking mode depends on epoll readiness and `EWOULDBLOCK` retry behavior. Cgroup path handling assumes preexisting cgroups and permissions. Process mode does not propagate child cgroup failure except through shared output and the child's exit status, because the child mutates its own copy of `threads[0]`.

Test signals: run `perf bench sched pipe`, `perf bench sched pipe -T`, `perf bench sched pipe -n`, and low-loop smoke tests. Exercise missing cgroup, valid cgroup, and unprivileged cases. Compare default and simple formats, and verify threaded cgroup writes use TIDs while process mode uses PIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/sched-pipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/sched-seccomp-notify.c -->
# sources/distributed-fs/ceph-client/tools/perf/bench/sched-seccomp-notify.c

Purpose: implements `perf bench sched seccomp-notify`, measuring seccomp user notification round-trip cost for intercepted `gettid` syscalls. It creates a seccomp filter with `SECCOMP_RET_USER_NOTIF`, forks a syscall-generating child, services notifications in the parent, and reports total time and per-call rate.

Important APIs, types, and functions: `seccomp()` wraps the raw `__NR_seccomp` syscall. `user_notif_syscall()` builds a BPF seccomp program that traps one syscall number and returns allow for the rest. `user_notification_sync_loop()` repeatedly receives `struct seccomp_notif`, validates the syscall, and replies with `struct seccomp_notif_resp` whose return value is `USER_NOTIF_MAGIC`. `bench_sched_seccomp_notify()` owns option parsing, filter installation, fork, optional sync wakeup flag, timing, child kill, and output.

Control flow: the parent sets `PR_SET_NO_NEW_PRIVS`, installs a filter using `SECCOMP_FILTER_FLAG_NEW_LISTENER`, then forks. The child sets `PR_SET_PDEATHSIG` and loops on `gettid`; as long as the intercepted syscall returns `USER_NOTIF_MAGIC`, it continues. The parent optionally enables `SECCOMP_USER_NOTIF_FD_SYNC_WAKE_UP`, services exactly `loops` notifications, kills the child, validates it died by `SIGKILL`, and prints in default or simple format.

State and persistence: no persistent state is written. Kernel state includes a seccomp listener fd and a child under the inherited seccomp filter. The listener drives all timing state, and the child is intentionally killed after the measured loop.

Dependencies and integration points: requires Linux seccomp user notification support, BPF filter definitions, `ioctl(SECCOMP_IOCTL_NOTIF_RECV/SEND)`, `prctl`, fork, and perf bench globals. It is registered in `builtin-bench.c` under `sched`.

Risks: old kernels or headers may lack notification features, though fallback defines cover the sync flag constants. Any unexpected syscall number, ioctl failure, fork failure, or wait mismatch exits via `err()` or `errx()`. The usage string contains a typo (`secccomp-notify`). The child spins forever unless the parent completes or dies, so cleanup relies on `PDEATHSIG` and explicit `SIGKILL`.

Test signals: smoke test with a small `--loop`, with and without `--sync-mode`, and on kernels with seccomp notify enabled. Confirm simple output is just elapsed time, default output reports the requested loop count, and failure modes are clear on unsupported kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/sched-seccomp-notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/synthesize.c -->
# sources/distributed-fs/ceph-client/tools/perf/bench/synthesize.c

Purpose: implements `perf bench internals synthesize`, benchmarking perf's synthetic event generation for thread maps. It measures both single-threaded synthesis for the current process and multi-threaded synthesis for target CPU 0, reporting average runtime, standard deviation, event count, and time per event.

Important APIs, types, and functions: global options control `min_threads`, `max_threads`, `single_iterations`, `multi_iterations`, `run_st`, and `run_mt`. `process_synthesized_event()` is a dummy perf tool callback that increments `event_count`. `do_run_single_threaded()` invokes `__machine__synthesize_threads()` repeatedly against a fixed thread map. `run_single_threaded()` creates a perf session and `thread_map__new_by_pid(getpid())`. `do_run_multi_threaded()` creates a new session for each iteration and synthesizes without a prebuilt thread map. `run_multi_threaded()` toggles perf's single/multithreaded mode by requested worker count. `bench_synthesize()` dispatches selected modes.

Control flow: options are parsed and no positional arguments are accepted. If neither `--st` nor `--mt` is set, single-threaded mode is enabled. Single-threaded mode creates one session and one self pid thread map, then measures normal and data-mmap synthesis. Multi-threaded mode defaults `max_threads` to online CPUs, iterates from min to max, sets perf threading mode, and calls the synthesis helper for each thread count.

State and persistence: all state is in memory: perf sessions, perf environment, thread maps, stats accumulators, and an atomic event counter. No files are read beyond system proc/sysfs state needed by perf synthesis, and no output is persisted beyond stdout.

Dependencies and integration points: uses `util/session`, `synthetic-events`, `thread_map`, `target`, `stat`, `tool`, and perf thread-mode helpers. It is exposed by `builtin-bench.c` as `internals synthesize`.

Risks: large default `single_iterations` can be expensive. `max_threads < min_threads` silently produces no multi-threaded runs. Multi-thread mode targets CPU 0, so systems with unusual CPU availability can skew or fail. Division by `event_average` assumes synthesis emitted events. Error cleanup must delete sessions and release thread maps on all paths.

Test signals: run default mode, `--st`, `--mt -m 1 -M 2 -I 1`, and invalid positional arguments. Check that event counts are nonzero, sessions are deleted, and perf threading mode is restored to single-threaded after multi-threaded runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/synthesize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/syscall.c -->
# sources/distributed-fs/ceph-client/tools/perf/bench/syscall.c

Purpose: implements the `perf bench syscall` sub-benchmarks for `getppid`, `getpgid`, `fork`, and `execve`. It runs a selected syscall workload for a loop count and reports total elapsed time plus per-operation performance.

Important APIs, types, and functions: `loops` is configured by `--loop` after each workload sets a default. `test_fork()` forks and waits for a child that exits immediately. `test_execve()` forks, the child executes `/bin/true`, and the parent waits. `bench_syscall_common()` centralizes option parsing, timing, workload dispatch, name selection, and output. The exported bench entry points are `bench_syscall_basic()`, `bench_syscall_getpgid()`, `bench_syscall_fork()`, and `bench_syscall_execve()`.

Control flow: the wrapper passes a syscall number to `bench_syscall_common()`. Fork and exec defaults use 10000 loops to limit runtime; simple syscalls default to 10000000. Each iteration calls the relevant libc or syscall-related helper. After timing, a switch maps the syscall number to a printable name, and output follows `BENCH_FORMAT_DEFAULT` or `BENCH_FORMAT_SIMPLE`.

State and persistence: no persistent state is written. Fork and exec temporarily create child processes; exec assumes `/bin/true` exists and is executable. Locale-aware grouping is used in printf format strings if the caller configured locale in the bench frontend.

Dependencies and integration points: included by `builtin-bench.c` under the `syscall` collection. It uses perf bench output globals and standard Linux process APIs.

Risks: the `case __NR_execve:` branch lacks an explicit `break` before `default`, currently harmless because default is empty but fragile. `__NR_fork` may be `-1` on architectures without a fork syscall number, yet the benchmark wrapper still passes it and the switch may behave unexpectedly. `/bin/true` is hard-coded. Child failures call `exit(1)`, terminating the benchmark process path. Very high loop counts can heavily load the system.

Test signals: run each syscall benchmark with `-l 1` and a modest loop count, verify simple and default formats, test on architectures with and without `__NR_fork`, and validate `/bin/true` failure behavior in constrained environments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/uprobe.c -->
# sources/distributed-fs/ceph-client/tools/perf/bench/uprobe.c

Purpose: implements `perf bench uprobe` variants that time repeated `usleep(1000)` calls with no probe, empty uprobe/uretprobe BPF programs, or trace_printk uprobe/uretprobe programs attached system-wide to libc `usleep`.

Important APIs, types, and functions: `enum bench_uprobe` identifies the benchmark variant. When `HAVE_BPF_SKEL` is enabled, `bench_uprobe__setup_bpf_skel()` opens, loads, and attaches the generated `bench_uprobe` BPF skeleton using `bpf_program__attach_uprobe_opts()`. `bench_uprobe__teardown_bpf_skel()` destroys it. Stub versions make non-BPF builds compile. `bench_uprobe_format__default_fprintf()` tracks static baseline and previous timings and prints deltas. `bench_uprobe()` performs option parsing, setup, timing, output, and teardown. The exported wrappers map each bench name to an enum value.

Control flow: each wrapper calls `bench_uprobe()`. Non-baseline modes attempt BPF setup; on setup failure they return 0 without measured output. Timing uses `clock_gettime(CLOCK_REALTIME)` around `loops` calls to `usleep(USEC_PER_MSEC)`, converts nanoseconds to microseconds, and prints either detailed default output or a simple integer.

State and persistence: process-local static state includes `loops`, `skel`, and the default formatter's `baseline`/`previous` values. Kernel state includes temporary uprobe links when BPF skeleton support is compiled in. No persistent files are written.

Dependencies and integration points: depends on perf bench, libbpf skeleton generation, libc path resolution for `libc.so.6`, `usleep`, and global `bench_format`. `builtin-bench.c` exposes the variants under the `uprobe` collection.

Risks: baseline and previous are static across calls in the same process, so running collection `all` intentionally compares variants but repeated independent invocations do not share the same baseline. Setup failure returning success can hide missing BPF capability in automation. `CLOCK_REALTIME` can jump; monotonic time would be less sensitive. Hard-coded `"libc.so.6"` and function name `usleep` depend on loader/libc behavior.

Test signals: run baseline and each BPF variant with `-l 1`, with and without BPF skeleton support. Verify teardown removes links, simple output is numeric, default output reports baseline and previous deltas, and unsupported BPF environments do not crash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/uprobe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-annotate.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-annotate.c

Purpose: implements `perf annotate`, which reads `perf.data`, resolves samples to DSOs/symbols/source, accumulates histograms, and displays annotated assembly, source, branch, or data-type views through stdio, TUI, or GTK.

Important APIs, types, and functions: `struct perf_annotate` combines `perf_tool`, session pointer, UI mode flags, filters, branch-stack state, data-type/stat options, and CPU bitmap. `process_sample_event()` resolves each sample and filters by CPU. `evsel__add_sample()` handles symbol filtering, branch-stack processing, hist entry creation, and address sample increments. `process_branch_stack()` and `process_basic_block()` account branch coverage and prediction. `hists__find_annotations()` walks sorted hist entries and invokes stdio/TUI/GTK or data-type annotation. `__cmd_annotate()` processes events, collapses/sorts hists, handles event groups, and calls display. `cmd_annotate()` parses options, initializes session/tool/symbol/annotation state, configures sorting, and dispatches.

Control flow: options select input, symbols/DSOs, UI, objdump/addr2line, CPU filters, itrace, grouping, and data-type behavior. The command initializes hist and annotation subsystems, opens a read-mode perf session with ordered event callbacks, processes events, collapses and resorts per-evsel histograms, optionally links group members, then displays each eligible annotation.

State and persistence: primary state is in memory: perf session, hists, annotation data, branch ranges, symbol configuration, and global annotation options. It reads `perf.data`, symbol files, objdump output, debug info, source files, and optional auxtrace data, but writes no persistent output except terminal UI.

Dependencies and integration points: integrates with perf's event/session machinery, symbol resolver, hist/sort infrastructure, branch and block-range helpers, annotation backends, UI browser setup, itrace synthesis, and optional libdw/GTK/slang/tracing support.

Risks: many global knobs (`symbol_conf`, `annotate_opts`, `use_browser`, `sort_order`) make option interactions delicate. Symbol filtering can erase symbols from DSO rbtrees. Data-type mode requires DWARF support and changes source annotation settings. Large perf.data files are intentionally not deleted in release builds for faster exit. UI-specific branches rely on dynamic GTK symbols and slang key handling.

Test signals: run stdio and stdio2 annotation on a small perf.data, with symbol and CPU filters, branch-stack data, grouped events, `--data-type` with and without DWARF support, `--dump-raw-trace`, and explicit `--objdump`/`--addr2line`. Validate no-sample input reports an error and malformed options fail early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-annotate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-bench.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-bench.c

Purpose: implements the top-level `perf bench` command. It registers benchmark collections and individual benchmarks, parses common output/repeat options, prints usage, and dispatches to the selected benchmark function.

Important APIs, types, and functions: `bench_fn_t`, `struct bench`, and `struct collection` define the registry. Static arrays describe `sched`, `syscall`, `mem`, `numa`, `futex`, `epoll`, `internals`, `breakpoint`, and `uprobe` collections, with conditional compilation for optional libraries. `bench_format` and `bench_repeat` are exported globals consumed by benchmark modules. `dump_benchmarks()`, `print_usage()`, `bench_str2int()`, `run_bench()`, `run_collection()`, `run_all_collections()`, and `cmd_bench()` implement the frontend.

Control flow: `cmd_bench()` sets stdout unbuffered, configures locale, parses common options until the first non-option, validates format and repeat, then dispatches. `all` runs all collections; `<collection> all` runs every benchmark in one collection; `<collection> <benchmark>` renames the task via `prctl(PR_SET_NAME)` and calls the function with adjusted argv. Missing collection or benchmark prints contextual help.

State and persistence: persistent state is not written. Process state includes locale, stdout buffering, process comm name, and global `bench_format`/`bench_repeat`. Individual benchmarks may create their own external effects.

Dependencies and integration points: includes `bench/bench.h`, which declares all benchmark functions. It is the central integration point for the bench files in this subset: sched pipe, seccomp notify, synthesize, syscall, and uprobe are all reachable through this registry.

Risks: collection `all` can call entries whose `benchmarks` pointer is NULL, relying on `for_each_bench` short-circuit behavior. Optional collections depend on compile-time macros and can alter user-visible availability. `run_collection()` supplies minimal argv, so benchmarks must tolerate defaults. `bench_repeat` is validated but not used by all benchmarks. Process name allocation uses `BUG_ON` on allocation failure.

Test signals: run `perf bench`, unknown collection, unknown benchmark, each collection help path, `--format default/simple`, invalid format, `--repeat 0`, `all`, and representative individual benchmarks. Confirm conditional collections appear only when compiled in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-buildid-cache.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-buildid-cache.c

Purpose: implements `perf buildid-cache`, managing perf's build-id cache by adding, removing, purging, updating, listing, finding missing DSOs, and storing kcore snapshots.

Important APIs, types, and functions: kcore helpers include `build_id_cache__kcore_buildid()`, `build_id_cache__kcore_existing()`, and `build_id_cache__add_kcore()`. File operations are `build_id_cache__add_file()`, `build_id_cache__remove_file()`, `build_id_cache__purge_path()`, `build_id_cache__purge_all()`, `build_id_cache__update_file()`, and `build_id_cache__show_all()`. Missing-cache reporting uses `dso__missing_buildid_cache()` and `build_id_cache__fprintf_missing()`. `perf_buildid_cache_config()` reads `buildid-cache.debuginfod`. `cmd_buildid_cache()` parses options and orchestrates actions.

Control flow: config is read first to configure debuginfod, then options are parsed. The command rejects missing action/list and list combined with mutations. Optional namespace context is created from `--target-ns`. Missing-cache mode opens a perf session for the supplied perf.data file. Symbol initialization and pager setup occur before executing the requested list/add/remove/purge/update/kcore actions.

State and persistence: this command directly mutates `buildid_dir`, adding files keyed by build-id, removing entries, purging all entries, and writing kcore snapshots under `[kernel.kcore]/<buildid>/<timestamp>`. It may also use debuginfod settings and namespace mount context. It reads perf.data when reporting missing cache entries.

Dependencies and integration points: relies on perf build-id utilities, namespace helpers, symbol/session code, kcore copy helpers, proc module comparison, strlist parsing, debuginfod setup, and config loading.

Risks: partial kcore copy failures attempt best-effort recursive cleanup but can leave cache fragments. Multiple actions can be specified together, so ordering matters. Many helper failures only warn and continue, with `ret` not always reflecting per-file failures. Namespace entry must bracket build-id reads correctly. `errno`-based diagnostics after helper calls may be stale if helpers do not preserve errno.

Test signals: test add/remove/update/purge/list on temporary ELF files, `--purge-all` on an isolated buildid dir, missing-cache reporting from small perf.data, kcore add with forced and duplicate detection paths, target namespace behavior, and debuginfod config parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-buildid-cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-buildid-list.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-buildid-list.c

Purpose: implements `perf buildid-list`, printing build IDs from an ELF file, a perf.data file, the running kernel, or current kernel/module maps.

Important APIs, types, and functions: `buildid__map_cb()` prints build IDs and address ranges for kernel maps. `buildid__show_kernel_maps()` constructs a host machine and iterates kernel maps. `sysfs__fprintf_build_id()` reads the running kernel build ID from sysfs. `filename__fprintf_build_id()` attempts direct ELF build-id extraction. `dso__skip_buildid()` filters by hit state. `perf_session__list_build_ids()` handles perf.data and pipe input, processing events as needed to mark hit DSOs. `cmd_buildid_list()` parses frontend options.

Control flow: command options select input, force, kernel-only, kernel maps, with-hits, and verbosity. Kernel modes bypass perf.data. Otherwise, the implementation first tries to treat the input as an ELF and print its build ID. If not, it opens a read-mode perf session with event callbacks that populate DSOs and mark hits, processes events when hits or pipe mode require it, and prints DSO build IDs.

State and persistence: no persistent state is written. It reads sysfs, ELF files, perf.data, and possibly compressed data through zstd session state. In pipe mode, build IDs are discovered by consuming the event stream.

Dependencies and integration points: uses perf session/data/header APIs, DSO and build-id helpers, symbol ELF initialization, machine kernel maps, pager support, and zstd initialization.

Risks: direct ELF detection means an ELF input short-circuits perf.data handling. AUXTRACE perf.data disables with-hit filtering because trace decoding is intentionally skipped. If zstd initialization fails, output may be incomplete but command continues with a warning. `with_hits` is forced when HEADER_BUILD_ID is absent. Kernel-map output depends on host symbol discovery.

Test signals: run against a known ELF, a perf.data with build-id header, perf.data without hits, pipe-mode data, `--kernel`, `--kernel-maps`, `--with-hits`, and compressed input. Validate force handling and warning behavior on damaged files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-buildid-list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-c2c.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-c2c.c

Purpose: implements `perf c2c record` and `perf c2c report` for cache-to-cache and false-sharing analysis. Record builds a `perf record` invocation with memory load/store events and physical address sampling. Report reads perf.data, decodes memory-source records, aggregates cacheline statistics, and displays shared cacheline tables through stdio or TUI.

Important APIs, types, and functions: `struct perf_c2c` holds global report state, node topology, mem2node mapping, display options, and output field strings. `struct c2c_hist_entry` extends `hist_entry` with c2c stats, CPU/node bitmaps, per-node stats, physical address tracking, and nested per-cacheline hists. `process_sample_event()` resolves samples, callchains, and memory info, decodes c2c stats, and populates top-level and nested histograms. Dimension functions define output columns, comparators, percentages, means, and node displays. `setup_nodes()`, `setup_coalesce()`, `build_cl_output()`, `setup_callchain()`, and `ui_quirks()` prepare report behavior. `perf_c2c__report()` owns session processing and display. `perf_c2c__record()` constructs record arguments. `cmd_c2c()` dispatches record/report prefixes.

Control flow: report parses options, opens perf.data with ordered callbacks, defaults display to peer on arm64 and total HITM elsewhere, initializes coalescing and hists, maps NUMA nodes and physical addresses, processes events, builds output/sort fields, collapses and resorts hists, computes shared-cacheline summaries, and displays statistics plus tables. Record chooses supported PMU memory events, adds `-d`, `--phys-data`, `--sample-cpu`, optional privilege filters, and invokes `cmd_record()`.

State and persistence: report state is in memory and derived from perf.data, symbols, topology, and memory maps. Record persists perf.data through `perf record`. Global flags such as `chk_double_cl`, `callchain_param`, `symbol_conf`, and `use_browser` are modified during execution.

Dependencies and integration points: integrates with perf mem-events PMU support, sessions, hists, sorting, callchains, mem-info, mem2node, symbols, annotation, UI browsers, pager, and record command.

Risks: topology assumptions can fail if NUMA data is missing or CPU-to-node mapping is inconsistent. Report has no pipe support. Many output dimensions are global mutable objects, so repeated runs in-process can inherit adjusted widths/headers. Physical address zero and missing sample CPU are tolerated but reduce attribution quality. Percentage printing can divide by zero in display stats for LLC misses. Record depends on PMU event availability.

Test signals: record with `-e list`, default record, user/kernel filters, and unsupported PMUs. Report on known c2c perf.data with `--stdio`, TUI, `--stats`, `--display tot/lcl/rmt/peer`, `--coalesce`, `--double-cl`, `--no-source`, and callgraph options. Validate output fields, shared-line counts, node info levels, and no-pipe error path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-c2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-check.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-check.c

Purpose: implements `perf check feature`, a small command that reports whether selected optional perf build features are compiled in and exits successfully only if all requested features are available.

Important APIs, types, and functions: `supported_features[]` is a table of `struct feature_status` entries populated by `FEATURE_STATUS` and `FEATURE_STATUS_TIP`, mapping user-visible names to compile-time macros and optional build tips. `on_off_print()` colorizes status. `feature_status__printf()` prints one feature with macro and tip. `has_support()` performs case-insensitive lookup by name or macro. `subcommand_feature()` parses a single comma-separated feature list. `cmd_check()` dispatches subcommands.

Control flow: top-level parsing recognizes the `feature` subcommand and a global `--quiet` option. The feature subcommand requires exactly one argument, duplicates it because `strtok()` mutates the string, then checks every comma-separated token. The boolean result is an AND across requested features, and the return value is inverted so missing or unknown features produce a nonzero exit status.

State and persistence: no persistent state is written. State comes from compile-time configuration macros in `tools/config.h` and the global `quiet` flag. Output goes to stdout/stderr with perf color helpers.

Dependencies and integration points: uses perf parse-options subcommand support, color output, debug error printing, and the shared `struct feature_status` type also used by perf version/build-options code.

Risks: unknown features are treated the same as disabled features in the exit status. The status string is lowercase `"on"` for enabled and uppercase `"OFF"` for disabled, and `on_off_print()` keys only on `"OFF"`. The final `free(check_usage[0])` path is unreachable after `usage_with_options()` exits, but documents parser ownership expectations. Comma parsing does not trim whitespace.

Test signals: run known enabled and disabled features, macro-name aliases, mixed comma lists, unknown feature, quiet mode, missing argument, too many arguments, and color/no-color output environments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-config.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-config.c

Purpose: implements `perf config`, listing, reading, and setting perf configuration variables in the user or system config file.

Important APIs, types, and functions: `use_system_config`, `use_user_config`, and `actions` capture option state. `set_config()` rewrites a config file from a `perf_config_set`. `show_spec_config()` prints one `section.name=value`. `show_config()` prints all collected values. `parse_config_arg()` validates and splits `section.name[=value]`. `perf_config__set_variable()` is an exported helper for setting one variable. `cmd_config()` is the command entry point.

Control flow: command options choose list, system config, or user config. The command rejects simultaneous system and user selection, determines `config_exclusive_filename`, creates a config set, and then either lists all values, shows selected variables, or collects updates and writes the config file once if anything changed. With no action and no args it falls through to list behavior.

State and persistence: this command rewrites the selected config file, defaulting to `$HOME/.perfconfig` unless `--system` or `--user` overrides. `set_config()` writes an auto-generated first line and serializes sections/items while optionally skipping system-origin entries when not writing system config.

Dependencies and integration points: uses perf config set collection and iteration APIs, cache path helpers, parse-options, and global `config_exclusive_filename`. Other perf code can call `perf_config__set_variable()`.

Risks: writes are not atomic and can clobber formatting/comments beyond the auto-generated line. `mkpath(... getenv("HOME"))` assumes `HOME` is set. `parse_config_arg()` uses `strchr(arg, '.')`, despite the variable name `last_dot`, so section parsing splits at the first dot. Empty value validation uses `strcmp(*value, "=")`, which is unusual pointer/string logic but detects a bare equals. The config set is not explicitly collected before `show_config()`, relying on constructor behavior.

Test signals: list empty and populated configs, get one variable, set one or multiple variables, use `--user`, `--system`, both options together, malformed names, missing values, unset `HOME`, and verify rewritten file contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-daemon.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-daemon.c

Purpose: implements `perf daemon`, a config-driven supervisor for long-running `perf record` sessions. It can start a daemon, list sessions, send `SIGUSR2`, stop the daemon, and ping session control FIFOs.

Important APIs, types, and functions: `struct daemon_session` stores session name, run arguments, base directory, control FIFO path, child pid, state, and start time. `struct daemon` stores config/base paths, sessions, output, perf executable path, signal fd, and daemon start time. Config parsing uses `session_config()`, `server_config()`, and `client_config()`. Session lifecycle uses `daemon_session__run()`, `daemon_session__control()`, `daemon_session__kill()`, `daemon__reconfig()`, and cleanup helpers. IPC uses `setup_server_socket()`, `setup_client_socket()`, `handle_server_socket()`, and command handlers for list, signal, stop, and ping. `__cmd_start()` runs the server loop; `send_cmd()` implements clients.

Control flow: start resolves config, loads sessions, optionally daemonizes, locks `BASE/lock`, creates Unix control socket, watches config directory with inotify, blocks SIGCHLD into signalfd, and polls socket/config/signal fds. Reconfiguration marks existing sessions for kill, reloads config, starts changed sessions as `perf record --control=fifo:control,ack`, and removes deleted sessions. Client commands load base config, connect to `BASE/control`, write a fixed-size `union cmd`, and stream the response.

State and persistence: persistent runtime state lives under daemon base: `lock`, daemon `output`, Unix `control` socket, and per-session directories with `output`, `control`, and `ack` FIFOs. It reads perf config files and writes session output logs. Child `perf record` processes produce their normal data outputs in session directories.

Dependencies and integration points: uses perf config APIs, `perf_exe()`, `cmd_record` via exec, fdarray polling, inotify, Unix sockets, signalfd, fork/setsid, FIFOs, lock files, and signal handling.

Risks: command IPC sends raw `union cmd`, so client/server ABI must match. `daemon_session__run()` builds a command string then `argv_split()`s it, making quoting in config `run` values important. Several child error paths return instead of `_exit()`, though final exec failure exits. Base path length is limited by Unix socket path size. Reconfig kills and restarts changed sessions, so config edits can interrupt recording.

Test signals: start foreground and background with temporary base/config, list normal and CSV formats, ping all and missing sessions, signal one/all sessions, stop daemon, edit config to add/change/remove sessions, simulate child exit, verify lock exclusion, and inspect FIFO ack timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-daemon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-data.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-data.c

Purpose: implements `perf data convert`, dispatching conversion of perf.data into JSON or CTF formats depending on build support.

Important APIs, types, and functions: `data_cmd_fn_t` and `struct data_cmd` define subcommand dispatch. `data_cmds[]` currently contains only `convert`. `data_options[]` defines shared and convert options: verbosity, input, `--to-json`, optional `--to-ctf`, `--tod`, force, all events, and time range. `opts` is a `struct perf_data_convert_opts` passed to converters. `cmd_data_convert()` validates conversion options and calls `bt_convert__perf2json()` or `bt_convert__perf2ctf()`. `cmd_data()` parses the subcommand and dispatches.

Control flow: `cmd_data()` uses `parse_options_subcommand()` with `convert` as the only recognized subcommand. `cmd_data_convert()` re-parses convert options, rejects positional leftovers, rejects both JSON and CTF at once, requires an available output format, and invokes the selected converter. If CTF support or traceevent support is missing, it reports a build-support error.

State and persistence: input defaults through global `input_name`; output paths come from `--to-json` or `--to-ctf`. The command writes converted output through converter helpers. Option state is held in file-static globals, so repeated in-process calls can retain values unless reinitialized by process startup.

Dependencies and integration points: depends on `data-convert.h` converter APIs, parse-options subcommand support, global `verbose` and `input_name`, and optional `HAVE_LIBBABELTRACE_SUPPORT` plus `HAVE_LIBTRACEEVENT`.

Risks: shared `data_options` are parsed at both top-level and subcommand levels, so option placement needs coverage. The non-babeltrace error block has unusual indentation, increasing maintenance risk. JSON and CTF converter behavior is external to this file. Static globals make in-process repeated invocations potentially surprising.

Test signals: convert small perf.data to JSON, reject both `--to-json` and `--to-ctf`, reject no output format, test CTF builds with and without required libraries, validate `--all`, `--time`, `--force`, `--tod`, top-level option placement, unknown subcommands, and positional leftovers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-data.c -->
