# subset-b-006897 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_hist.c -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_hist.c

## Purpose

`timerlat_hist.c` implements the `rtla timerlat hist` subcommand. It collects timer latency samples from the kernel `timerlat` tracer or the rtla BPF timerlat backend and renders per-CPU histograms for IRQ, timerlat thread, and optional user-thread return latency contexts.

## Important APIs, Types, and Functions

The main runtime structures are `struct timerlat_hist_cpu`, which owns per-context bucket arrays plus count/min/sum/max fields, and `struct timerlat_hist_data`, which records `entries` and `bucket_size`. Key functions are `timerlat_alloc_histogram()`, `timerlat_free_histogram()`, `timerlat_hist_update()`, `timerlat_hist_handler()`, `timerlat_hist_bpf_pull_data()`, `timerlat_print_stats()`, `timerlat_hist_parse_args()`, `timerlat_init_hist()`, and `timerlat_hist_main()`. The exported integration object is `timerlat_hist_ops`.

## Control Flow and Data Flow

Startup flows through `timerlat_hist_ops.parse_args`, `init_tool`, `apply_config`, `enable`, and `main`. Tracefs mode registers `timerlat_hist_handler()` for `ftrace:timerlat` events and updates bucket arrays from `context` and `timer_latency`. BPF mode waits for BPF threshold events, optionally runs threshold actions, restarts tracing when requested, detaches BPF, then pulls histogram and summary maps with `timerlat_bpf_get_hist_value()` and `timerlat_bpf_get_summary_value()`. Printing emits the header, bucket rows, overflow row, per-CPU summary, aggregate `ALL` summary, and missed-event report.

## State and Persistence Behavior

Histogram state is heap allocated per process and per CPU. Buckets include an extra overflow slot at `entries`. Minimum values are initialized to all-bits-one so the first sample wins. `output_divisor` converts nanoseconds to microseconds by default, or leaves nanoseconds under `--nano`. The file can persist stopped traces through configured trace-output actions, but histogram data itself is process-local.

## Dependencies and Integration Points

This file depends on `timerlat.h`, `timerlat_aa.h`, `timerlat_bpf.h`, `common.h`, libtraceevent handlers, tracefs/BPF timerlat support, global CPU state, threshold/end actions, auto-analysis, user/kernel workload setup, cgroup and scheduling configuration, and utility helpers from `utils.c`.

## Risks and Edge Cases

Large `--entries` values can allocate substantial memory because three arrays are allocated for every CPU. `--no-irq` and `--no-thread` together are rejected because no kernel contexts remain. `--no-index` without `--with-zeros` is rejected because sparse rows become ambiguous. BPF mode is downgraded to mixed mode when trace-output or auto-analysis is needed. Missing samples from tracefs buffer overflow are only reported after printing and can skew distributions.

## Test Signals

Useful tests include argument validation for bucket and entry bounds, `--nano` unit conversion, `--no-*` option combinations, tracefs event handling with synthetic `context` values, BPF map pull correctness for histogram/summary/overflow values, threshold action restart behavior, and runtime smoke tests that confirm per-CPU IRQ/thread/user columns appear when timerlat data is generated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_hist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_top.c -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_top.c

## Purpose

`timerlat_top.c` implements the `rtla timerlat top` subcommand. It provides a live per-CPU summary of timer latency, showing current, minimum, average, and maximum values for IRQ, timerlat thread, and optional user-thread return contexts.

## Important APIs, Types, and Functions

`struct timerlat_top_cpu` stores current/count/min/sum/max fields for IRQ, thread, and user contexts. `struct timerlat_top_data` owns the per-CPU array. Important functions are `timerlat_alloc_top()`, `timerlat_top_update()`, `timerlat_top_handler()`, `timerlat_top_bpf_pull_data()`, `timerlat_top_print()`, `timerlat_top_print_sum()`, `timerlat_print_stats()`, `timerlat_top_parse_args()`, `timerlat_init_top()`, and `timerlat_top_bpf_main_loop()`. `timerlat_top_ops` registers the subcommand with the shared rtla tool framework.

## Control Flow and Data Flow

After parsing and initialization, tracefs mode uses the shared `top_main_loop()`, while BPF mode calls `timerlat_top_bpf_main_loop()`. Tracefs samples arrive through `timerlat_top_handler()` and update per-CPU state unless `aa_only` is active. BPF mode periodically waits for either sleep interval expiry or a tracer stop, pulls current/count/min/max/sum maps, prints live output unless quiet, runs threshold handling when the tracer stops, and restarts BPF tracing if the session should continue.

## State and Persistence Behavior

All measurement state is volatile in `timerlat_top_data`. Minimum fields start at all-bits-one, averages are derived from sums and counts, and `cur_*` fields hold the latest sample or BPF current map value. Pretty terminal output is enabled only for a tty and non-quiet mode. Trace output may be persisted through action configuration; the top table itself is not persisted.

## Dependencies and Integration Points

The file integrates with the same timerlat/common stack as `timerlat_hist.c`: tracefs, libtraceevent, BPF timerlat maps, threshold and end actions, auto-analysis, workload dispatch, scheduler/cgroup helpers, timerlat tracer configuration, and the shared `tool_ops` dispatcher.

## Risks and Edge Cases

`--aa-only` suppresses normal sample parsing and output, so it depends on auto-analysis stop conditions rather than top-table data. `--no-aa` and `--aa-only` are mutually exclusive. BPF mode must detach after completion. Counts are per context; CPUs with no IRQ/thread count are treated as offline or inactive and skipped. Lost trace events can make current and aggregate statistics stale or incomplete.

## Test Signals

Tests should cover live and quiet modes, `--aa-only`, BPF map pull of all summary types, tracefs event updates for context 0/1/user, pretty-output gating on `isatty()`, user workload termination detection, threshold action restart behavior, and printed summaries with CPUs that have only one context populated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_top.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_u.c -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_u.c

## Purpose

`timerlat_u.c` implements the user-space workload side of rtla timerlat. It creates `timerlatu/<cpu>` processes pinned to monitored CPUs, opens each CPU's `osnoise/per_cpu/cpuN/timerlat_fd`, and blocks in reads so timerlat can measure user-space return latency.

## Important APIs, Types, and Functions

The file consumes `struct timerlat_u_params` from `timerlat_u.h`. `timerlat_u_main()` configures one child process, `timerlat_u_send_kill()` terminates child PIDs, and `timerlat_u_dispatcher()` is the pthread entry that forks and supervises one child per selected CPU.

## Control Flow and Data Flow

The dispatcher allocates a PID array sized by `nr_cpus`, iterates over the CPU set, forks one child per monitored CPU, names it `timerlatu/N`, and enters `timerlat_u_main()`. Each child sets affinity, applies either default SCHED_FIFO priority 95 or caller-provided scheduler attributes, optionally joins a cgroup, opens the per-CPU timerlat fd, and repeatedly reads until error/termination. The parent polls `waitpid(WNOHANG)` while `should_run` remains true, kills remaining children, waits for all exits, and marks `stopped_running`.

## State and Persistence Behavior

State is process-local and shared only through `timerlat_u_params` flags and forked child PIDs. The timerlat fd and scheduler/cgroup settings affect kernel runtime state while processes live. No measurement data is persisted here; the tracer records latency elsewhere.

## Dependencies and Integration Points

This code depends on tracefs timerlat per-CPU fd files, scheduler syscalls, pthread naming, `prctl(PR_SET_NAME)`, cgroup helpers from `utils.c`, `common.h` globals such as `nr_cpus`, and the surrounding timerlat tool that starts the dispatcher and flips `should_run`.

## Risks and Edge Cases

Affinity setup fails for offline CPUs. Default FIFO priority requires privilege. The cgroup error path uses `pthread_exit()` in child context and reports inverted success semantics carefully because `set_pid_cgroup()` returns nonzero on success. If any child exits early, the dispatcher eventually kills all remaining children. `SIGKILL` leaves little cleanup opportunity inside children.

## Test Signals

Test signals include process naming, one child per selected CPU, affinity and priority checks, failure on offline CPUs, cgroup placement, clean `stopped_running` transition when `should_run` is cleared, and timerlat sessions with `--user-threads` confirming user latency columns are populated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_u.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_u.h -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_u.h

## Purpose

`timerlat_u.h` declares the small interface used by timerlat tools to launch and control user-space timerlat workload processes.

## Important APIs, Types, and Functions

`struct timerlat_u_params` contains dispatcher control flags (`should_run`, `stopped_running`), the monitored CPU set, an optional cgroup name, and optional scheduler attributes. The only declared function is `timerlat_u_dispatcher(void *data)`, intended as a pthread entry point.

## Control Flow and Data Flow

Callers initialize the parameter structure, start the dispatcher thread, and later clear `should_run` to request teardown. The dispatcher writes back `stopped_running` after all child workload processes have exited.

## State and Persistence Behavior

The header defines shared in-process state only. The pointed-to CPU set, cgroup string, and scheduler attributes are caller-owned. Runtime persistence is limited to scheduler/cgroup effects created by `timerlat_u.c`.

## Dependencies and Integration Points

It depends on `cpu_set_t` and `struct sched_attr` being visible from included common headers in users. It is integrated by timerlat top/hist common setup when `--user-threads` or user workload mode is requested.

## Risks and Edge Cases

The structure is not internally synchronized, so callers must coordinate flag lifetime with the dispatcher thread. Pointer fields must outlive the dispatcher. Missing CPU set means the implementation treats all CPUs as candidates.

## Test Signals

Build tests should ensure the header compiles in timerlat users, and runtime tests should verify `should_run`/`stopped_running` transitions with dispatcher lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_u.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/trace.c -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/trace.c

## Purpose

`trace.c` provides rtla's tracefs/libtraceevent abstraction. It creates and destroys trace instances, starts/stops tracing, saves trace buffers, dispatches registered event handlers, tracks missed events, and manages user-requested trace events, filters, triggers, and trace buffer sizing.

## Important APIs, Types, and Functions

Public functions mirror `trace.h`: `enable_tracer_by_name()`, `disable_tracer()`, `create_instance()`, `destroy_instance()`, `save_trace_to_file()`, `collect_registered_events()`, `trace_instance_init()`, `trace_instance_start()`, `trace_instance_stop()`, `trace_instance_destroy()`, `trace_event_alloc()`, `trace_event_add_filter()`, `trace_event_add_trigger()`, `trace_events_enable()`, `trace_events_disable()`, `trace_events_destroy()`, and `trace_set_buffer_size()`.

## Control Flow and Data Flow

Tool initialization calls `trace_instance_init()`, which allocates a `trace_seq`, creates a tracefs instance, loads local event metadata, turns tracing off, and registers missed-event following. Event collection increments `processed_events` and delegates to libtraceevent handlers when present. Event enablement turns on tracefs events, then writes filters and triggers to event files. Disablement saves hist trigger output when applicable, writes `!trigger`/`!filter`, and disables events. Trace saving copies the instance `trace` file to a regular file using robust read/write loops.

## State and Persistence Behavior

`struct trace_instance` owns the tracefs instance, tep handle, trace sequence buffer, missed-event count, and processed-event count. Trace instances persist in tracefs until explicitly destroyed. `save_trace_to_file()` and `trace_event_save_hist()` persist trace or hist-trigger content to files in the current working directory.

## Dependencies and Integration Points

The file depends on libtracefs, libtraceevent, tracefs event files, `utils.h` allocation/error helpers, and rtla tool modules that register handlers. It integrates with timerlat/osnoise subcommands, threshold trace-output actions, user-selected `-e/--filter/--trigger`, and buffer-size options.

## Risks and Edge Cases

Filters and triggers only apply to single events, not whole systems, and are rejected otherwise. Hist trigger output file names are derived from system/event names. Missed events can saturate to `UINT64_MAX` when tracefs reports loss without a count. Event disable paths log failures but continue cleanup. File writes must handle `EINTR`; this file does so for trace and hist output loops.

## Test Signals

Tests should cover instance create/destroy, tracer enable failure for missing tracers, trace copy with interrupted reads/writes, event string parsing with and without `system:event`, filter/trigger validation, hist trigger save, missed-event accounting, and buffer-size write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/trace.h -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/trace.h

## Purpose

`trace.h` declares the tracefs support interface used by rtla tools. It exposes trace instance state, trace event configuration state, and helper functions for tracer control, event handling, and trace persistence.

## Important APIs, Types, and Functions

`struct trace_events` is a linked-list node containing system, event, filter, trigger, and enabled-state flags. `struct trace_instance` stores the tracefs instance, tep metadata handle, trace sequence buffer, missed-event count, and processed-event count. The function prototypes cover lifecycle, event enable/disable/destroy, filter/trigger attachment, file saving, and buffer sizing.

## Control Flow and Data Flow

Tool modules include this header, allocate or embed a `trace_instance`, call initialization and start/stop helpers, register libtraceevent callbacks against `trace->tep`, and use `trace_events` lists for command-line `-e`, `--filter`, and `--trigger` requests.

## State and Persistence Behavior

The header itself stores no state but defines ownership contracts: callers pass mutable `trace_instance` and `trace_events` objects to implementation functions, and destroy helpers release tracefs/tep/sequence resources.

## Dependencies and Integration Points

It depends on `<tracefs.h>` and `<stddef.h>` and is included by rtla C files that interact with tracefs. It is a central boundary between command implementations and the low-level tracefs API.

## Risks and Edge Cases

Because `trace_events` uses raw pointers and linked-list ownership, callers must avoid reusing freed event nodes. Filter/trigger enabled flags matter during cleanup. Any code embedding `trace_instance` must call destroy on all error paths to avoid leaked tracefs instances.

## Test Signals

Compile-time tests should ensure declarations match `trace.c`. Runtime tests should exercise a full instance lifecycle plus event enable/disable through command-line options in rtla tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/utils.c -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/utils.c

## Purpose

`utils.c` implements shared rtla helpers for logging, fatal allocation, number and duration parsing, CPU-set parsing, scheduler policy setup, procfs process discovery, cgroup assignment, CPU DMA latency, optional cpupower idle-state control, automatic housekeeping affinity, optional-argument parsing, and strict integer conversion.

## Important APIs, Types, and Functions

Important public functions include `err_msg()`, `debug_msg()`, `fatal()`, `get_llong_from_str()`, `get_duration()`, `parse_cpu_set()`, `parse_stack_format()`, `parse_seconds_duration()`, `parse_ns_duration()`, `parse_prio()`, `__set_sched_attr()`, `set_comm_sched_attr()`, `set_cpu_dma_latency()`, cpupower helpers, `set_pid_cgroup()`, `set_comm_cgroup()`, `auto_house_keeping()`, `parse_optional_arg()`, `strtoi()`, `calloc_fatal()`, `reallocarray_fatal()`, and `strdup_fatal()`.

## Control Flow and Data Flow

Parsing helpers convert command strings into numeric seconds, nanoseconds, CPU masks, stack-format enums, or `sched_attr` fields. Scheduler helpers discover PIDs by scanning `/proc/*/comm` for a prefix and apply `sched_setattr`. Cgroup helpers locate the cgroup v2 mount in `/proc/mounts`, derive either the caller's cgroup or a named cgroup, then write PIDs into `cgroup.procs`. Housekeeping computes CPUs available to rtla but outside monitored CPUs and sets process affinity there.

## State and Persistence Behavior

`config_debug` controls debug logging globally. `set_cpu_dma_latency()` persists latency constraints while its fd remains open. Cpupower support stores idle disable state in static arrays so later restoration can return CPUs to their prior state. Scheduler, affinity, and cgroup changes persist in kernel process state until changed or processes exit.

## Dependencies and Integration Points

The file depends on libc, `/proc`, cgroup v2, Linux scheduler syscalls, `/dev/cpu_dma_latency`, optional libcpupower, and `common.h` globals like `nr_cpus`. It is used by rtla command parsing, timerlat user threads, tracer workload setup, and tests.

## Risks and Edge Cases

`get_llong_from_str()` accepts trailing nonnumeric text because it only checks conversion start and errno. `parse_seconds_duration()` ignores unknown suffixes rather than failing. `parse_ns_duration()` is stricter and supports colon-delimited deadline specs. `/proc` scanning races with process exit. Cgroup helpers assume cgroup v2. Cpupower state restoration must run on cleanup paths or idle states can remain disabled. `auto_house_keeping()` fails when no non-monitored CPU remains in affinity.

## Test Signals

Existing Check tests cover `strtoi()`, `parse_cpu_set()`, and `parse_prio()`. Additional useful tests include duration parsing, optional argument parsing, cgroup path derivation with mocked files, procfs prefix matching, `auto_house_keeping()` CPU-mask cases, cpupower save/restore error paths, and allocation-fatal behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/utils.h -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/utils.h

## Purpose

`utils.h` exposes shared constants, inline helpers, scheduler structures, enums, and utility prototypes for rtla source files.

## Important APIs, Types, and Functions

Constants include `BUFF_U64_STR_SIZE`, `MAX_PATH`, `MAX_NICE`, `MIN_NICE`, `ARRAY_SIZE`, `STRING_LENGTH`, and `strncmp_static`. Inline helpers include `str_has_prefix()`, `container_of()`, `update_min()`, `update_max()`, and `update_sum()`. The header defines `struct sched_attr` when the libc headers do not, `enum stack_format`, and `enum result`.

## Control Flow and Data Flow

There is no runtime control flow beyond inline functions. The update helpers mutate aggregate statistics in caller-owned storage, and the parsing/scheduling/cgroup prototypes connect command modules to `utils.c`.

## State and Persistence Behavior

The header declares external `config_debug` and functions that affect persistent process/kernel state, but it stores no state itself. The fallback cpupower inline functions return unsupported defaults when libcpupower support is not compiled in.

## Dependencies and Integration Points

It depends on standard integer, string, time, scheduler, boolean, and allocation headers. It is included broadly by rtla modules, including tracing, timerlat tools, and unit tests.

## Risks and Edge Cases

`container_of()` requires correct member pointers and type pairing. The update helpers do no overflow checking. The compile-time `struct sched_attr` fallback must stay ABI-compatible with kernel expectations. Feature-conditional cpupower stubs make unsupported builds fail at runtime rather than compile time.

## Test Signals

Compile coverage across supported libc/kernel header combinations is important. Unit tests indirectly exercise `update_*`, parsing prototypes, scheduler attr layout, and unsupported cpupower stubs through `utils.c` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/src/utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/tests/bpf/bpf_action_map.c -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/tests/bpf/bpf_action_map.c

## Purpose

`bpf_action_map.c` is a minimal BPF program used by rtla tests to verify that timerlat BPF action programs can be loaded, attached, and mutate a BPF map when a timerlat action tracepoint fires.

## Important APIs, Types, and Functions

It declares `rtla_test_map`, a one-entry `BPF_MAP_TYPE_ARRAY` keyed by `unsigned int` with `unsigned long long` values. `action_handler()` is attached to `SEC("tp/timerlat_action")` and writes value `42` at key `0`. `LICENSE` is GPL.

## Control Flow and Data Flow

When the `timerlat_action` tracepoint runs, the BPF handler updates the test map with `bpf_map_update_elem(..., BPF_ANY)` and returns 0. User-space test code can read the map to confirm the action ran.

## State and Persistence Behavior

State persists in the BPF map while the program/map are loaded. The source file itself has no user-space lifecycle logic.

## Dependencies and Integration Points

The program depends on kernel BPF tracepoint support, `linux/bpf.h`, `bpf/bpf_tracing.h`, the `timerlat_action` tracepoint type, and rtla's `--bpf-action` loading path.

## Risks and Edge Cases

The tracepoint struct is forward-declared and unused, so ABI changes matter only for attach compatibility. The fixed value tests action execution but not argument parsing. Loading requires appropriate privileges and BPF tooling support.

## Test Signals

Pass signals are successful BPF compilation/loading, action attachment, timerlat threshold/action execution, and a map value of `42` at key `0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/tests/bpf/bpf_action_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/tests/engine.sh -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/tests/engine.sh

## Purpose

`engine.sh` is the shared shell harness for rtla tests. It provides TAP-style counting/output, rtla command execution, osnoise/timerlat tracefs reset, timeout configuration, and locale normalization.

## Important APIs, Types, and Functions

Functions are `test_begin()`, `reset_osnoise()`, `check()`, `check_with_osnoise_options()`, `set_timeout()`, `unset_timeout()`, `set_no_reset_osnoise()`, `unset_no_reset_osnoise()`, and `test_end()`. It uses environment variables `RTLA`, `TEST_COUNT`, `TIMEOUT`, and `NO_RESET_OSNOISE`.

## Control Flow and Data Flow

On first invocation, tests call `test_begin()` and emit checks without `TEST_COUNT`, which only increments a counter. `test_end()` re-execs the script with `TEST_COUNT` set so the second pass emits TAP plan and actually runs commands. `check()` resets tracefs unless disabled, runs `$RTLA` under optional timeout via `eval stdbuf -oL`, captures output and exit code, then validates expected/unexpected regexes.

## State and Persistence Behavior

`reset_osnoise()` mutates `/sys/kernel/tracing` by removing known rtla instances and restoring osnoise defaults. Harness state is shell variables. Test output is TAP-style stdout.

## Dependencies and Integration Points

It depends on bash, tracefs mounted at `/sys/kernel/tracing`, `timeout`, `stdbuf`, `grep`, `col`, and the rtla binary. It is sourced by rtla shell tests.

## Risks and Edge Cases

Use of `eval` means quoted test commands must be constructed carefully. Reset requires tracefs permissions. The two-pass counting model can hide side effects during count-only pass if tests do work outside `check()`. Regex validation uses grep extended regexes.

## Test Signals

Harness tests should confirm correct TAP count, command exit-code handling, output matching and nonmatching, osnoise reset side effects, timeout kill behavior, and `NO_RESET_OSNOISE` preservation for option-reset tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/tests/engine.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/tests/scripts/check-priority.sh -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/tests/scripts/check-priority.sh

## Purpose

`check-priority.sh` verifies that processes matching a command-name regex have expected scheduler class and priority values according to `chrt -p`.

## Important APIs, Types, and Functions

The script takes three positional arguments: a `pgrep` pattern, expected first `chrt` field value, and expected last `chrt` field value. It uses `pgrep`, `chrt -p`, `cut`, `head`, `tail`, and `grep`.

## Control Flow and Data Flow

It resolves PIDs with `pgrep ^$1`, exits 1 if none are found, loops over each PID, and validates the first and last colon-separated fields from `chrt -p` output. If all checks pass, it prints `Priorities are set correctly`.

## State and Persistence Behavior

The script is read-only and does not modify scheduler state. Its result depends on live process state at the moment it runs.

## Dependencies and Integration Points

It integrates with rtla tests that set tracer or workload priorities and then need an external assertion. It depends on util-linux `chrt` output format.

## Risks and Edge Cases

Unquoted regex input to `pgrep` and grep can surprise callers. `chrt` output format is locale/tool-version sensitive. If a process exits between `pgrep` and `chrt`, the loop may fail. It does not emit detailed diagnostics for which PID failed.

## Test Signals

Tests should run it against known SCHED_FIFO/SCHED_RR/SCHED_OTHER processes and against a missing process name to confirm nonzero failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/tests/scripts/check-priority.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/tests/unit/unit_tests.c -->
# sources/distributed-fs/ceph-client/tools/tracing/rtla/tests/unit/unit_tests.c

## Purpose

`unit_tests.c` contains Check-based unit tests for selected rtla utility functions, currently strict integer parsing, CPU-set parsing, and scheduler-priority parsing.

## Important APIs, Types, and Functions

The test cases are `test_strtoi`, `test_parse_cpu_set`, and `test_parse_prio`. `utils_suite()` builds the Check suite and `main()` runs it. A local `int nr_cpus` satisfies `utils.c` parsing dependencies.

## Control Flow and Data Flow

Each Check test calls a utility function with valid and invalid inputs, then asserts return values and selected output fields. `test_parse_cpu_set` sets `nr_cpus = 8` and inspects `CPU_ISSET` results. `test_parse_prio` checks FIFO, RR, OTHER, DEADLINE, and invalid policy/bounds cases.

## State and Persistence Behavior

The test mutates only local variables and the test-global `nr_cpus`. It does not apply scheduler attributes; it only parses into `struct sched_attr`.

## Dependencies and Integration Points

It depends on the Check framework, libc scheduler macros, `utils.h`, and the rtla test build system. It guards behavior used by command-line parsing across rtla tools.

## Risks and Edge Cases

Coverage is intentionally narrow. It does not test duration suffix edge cases, trailing text accepted by `get_llong_from_str()`, cgroup helpers, procfs scanning, or actual `sched_setattr` syscalls. CPU-set tests do not cover trailing commas or reversed ranges beyond basic invalid cases.

## Test Signals

Passing the suite indicates the main parser contracts for CPU masks, priorities, and strict integer conversion are intact. Failures point directly to command-line behavior regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/tracing/rtla/tests/unit/unit_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/unittests/kdoc-test-schema.yaml -->
# sources/distributed-fs/ceph-client/tools/unittests/kdoc-test-schema.yaml

## Purpose

`kdoc-test-schema.yaml` defines the JSON Schema used to validate dynamic kernel-doc test cases in `kdoc-test.yaml`.

## Important APIs, Types, and Fields

The schema describes a top-level `tests` array. Each test object has required `name`, `fname`, and `expected` fields, with optional `description`, `source`, and `exports`. Expected entries may contain a `kdoc_item` object, `rst` string, and/or `man` string. `kdoc_item` properties mirror `KdocItem` data: name, type, declaration line, sections, parameter lists/descriptions/types, and `other_stuff`.

## Control Flow and Data Flow

There is no executable control flow. `test_kdoc_test_schema.py` loads this file with YAML, creates a `Draft7Validator`, and validates the dynamic test YAML before parser/output tests consume it.

## State and Persistence Behavior

The file persists the contract for test data shape. It does not store test results.

## Dependencies and Integration Points

It depends on JSON Schema draft-07 semantics and Python `jsonschema` when available. It integrates with kernel-doc parser/output unit tests and the YAML test corpus.

## Risks and Edge Cases

The schema is permissive in places, especially `other_stuff` and expected-output strings. The `anyOf` block appears intended to require either `kdoc_item` or `source`, but indentation/shape must be validated carefully because YAML-to-JSON-schema mistakes can silently weaken checks. The schema requires `expected` but not necessarily every output flavor.

## Test Signals

Pass signals are successful schema loading and no validation errors for `kdoc-test.yaml`. Negative schema tests would be useful for missing required fields, malformed `kdoc_item`, and invalid expected entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/unittests/kdoc-test-schema.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/unittests/kdoc-test.yaml -->
# sources/distributed-fs/ceph-client/tools/unittests/kdoc-test.yaml

## Purpose

`kdoc-test.yaml` is the dynamic test corpus for the Python kernel-doc parser and output generators. It supplies C snippets, expected parsed `KdocItem` values, and expected reStructuredText/man-page output.

## Important APIs, Types, and Fields

The file has 34 named tests. Common fields are `name`, `fname`, `description`, `source`, optional `exports`, and `expected`. Expected entries exercise `kdoc_item`, `rst`, and `man` outputs. Covered cases include basic functions, exported symbols, DOC blocks, complex/simple tables, ASCII artwork, variables of multiple declarations, guarded/private declarations, lock annotations, struct groups, and kernel-doc output formatting.

## Control Flow and Data Flow

`test_kdoc_parser.py` reads the YAML, dynamically creates parser and output tests, and either parses `source` into items or converts expected items into `RestFormat`/`ManFormat` output. The YAML is data-driven: each entry expands into one or more unittest methods.

## State and Persistence Behavior

The file persists expected behavior for kernel-doc parsing and formatting. Test runs do not modify it. Some expected man output includes dates that are normalized by the test helper.

## Dependencies and Integration Points

It depends on the schema file, PyYAML, kernel-doc parser classes, output classes, and transform rules. It is the main integration point between real-ish C examples and Python unit tests.

## Risks and Edge Cases

Large literal expected blocks are sensitive to whitespace and formatter changes. Because many cases validate source-to-output without an explicit `kdoc_item`, parser regressions can be localized less precisely. The corpus intentionally includes tricky transform cases such as lock annotations and struct-group private regions.

## Test Signals

The strongest signal is all dynamically generated parser, RST, and man tests passing. Schema validation passing confirms shape, while failures in individual generated method names identify the scenario name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/unittests/kdoc-test.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/unittests/run.py -->
# sources/distributed-fs/ceph-client/tools/unittests/run.py

## Purpose

`run.py` is the top-level unittest discovery runner for tests under `tools/unittests`.

## Important APIs, Types, and Functions

It computes `TOOLS_DIR`, prepends it to `sys.path`, imports `TestUnits` from `lib.python.unittest_helper`, discovers `test*.py` modules under `tools/unittests`, and runs the resulting suite.

## Control Flow and Data Flow

When executed as `__main__`, it creates a `unittest.TestLoader`, discovers tests, and delegates execution/output formatting to `TestUnits().run("", suite=suite)`.

## State and Persistence Behavior

It mutates only Python import path for the process. It writes no persistent state.

## Dependencies and Integration Points

It depends on the repository's Python helper library and Python unittest discovery. It is the convenient entry point for kernel-doc and tokenizer unit tests.

## Risks and Edge Cases

Discovery depends on file names matching `test*.py`. Import path insertion assumes the script remains one level below `tools`. Missing optional dependencies are handled by individual tests rather than this runner.

## Test Signals

A successful run reports all discovered unit tests passing. Useful smoke tests invoke this file from different working directories to confirm `TOOLS_DIR` resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/unittests/run.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/unittests/test_cmatch.py -->
# sources/distributed-fs/ceph-client/tools/unittests/test_cmatch.py

## Purpose

`test_cmatch.py` tests `kdoc.c_lex.CMatch`, especially matching and rewriting C-like macro invocations with nested parentheses and kernel-doc transform patterns.

## Important APIs, Types, and Functions

Test classes include `TestSearch`, `TestSubMultipleMacros`, `TestSubSimple`, and `TestSubWithLocalXforms`. Helpers include `TestCaseDiff.assertLogicallyEqual()` and `apply_transforms()`, which mimics selected `kdoc_parser` transform passes. It imports `CMatch`, `KernRe`, and `run_unittest`.

## Control Flow and Data Flow

Search tests call `CMatch(...).search()` on sample lines. Substitution tests call `.sub()` with replacement strings containing backreferences like `\0`, `\1`, and greedy `+` suffixes. Transform tests apply ordered CMatch rules for structs, functions, and variables to realistic kernel snippets.

## State and Persistence Behavior

The tests are pure in-memory transformations. No files are written.

## Dependencies and Integration Points

The suite protects the parser transform layer used by kernel-doc. It covers annotations such as `__acquires`, `__guarded_by`, `struct_group*`, bitmap declarations, KFIFO macros, flex arrays, DMA unmap macros, and list heads.

## Risks and Edge Cases

The test file includes duplicate `TestCaseDiff` class definitions and duplicate `test_struct_kcov` names, so Python's later definitions shadow earlier ones. Some comments document known limitations around `struct_group_tagged` with extra commas. Whitespace normalization can mask formatting-only differences but improves semantic matching.

## Test Signals

Passing tests indicate nested macro matching, backreference substitution, count limiting, invalid greedy replacements, and kernel transform examples are stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/unittests/test_cmatch.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/unittests/test_kdoc_parser.py -->
# sources/distributed-fs/ceph-client/tools/unittests/test_kdoc_parser.py

## Purpose

`test_kdoc_parser.py` validates the Python kernel-doc parser and output formatters, using both hand-written self-tests and dynamically generated tests from `kdoc-test.yaml`.

## Important APIs, Types, and Functions

Key helpers are `clean_whitespc()`, `MockLogging`, `MockKdocConfig`, `GenerateKdocItem.run_test()`, `cleanup_timestamp()`, and `gen_output()`. Dynamic test classes include `CToKdocItem`, `KdocItemToMan`, `KdocItemToRest`, `CToMan`, and `CToRest`. `KernelDocDynamicTests.create_tests()` attaches methods at import time.

## Control Flow and Data Flow

Parser tests patch `open()` with mocked source, construct `KernelDoc`, parse entries and export tables, and compare normalized `KdocItem` dictionaries. Output tests either render expected items or parse source then render to man/RST. The main entry point accepts `--yaml-file` and passes environment overrides to `TestUnits`.

## State and Persistence Behavior

Tests run in memory using mocked file reads. The selected YAML path can be passed through an environment dictionary. Logging is captured in a custom handler for possible warning assertions.

## Dependencies and Integration Points

It depends on PyYAML, unittest/mock, `KdocConfig`, `KdocItem`, `KernelDoc`, `RestFormat`, `ManFormat`, `CTransforms`, and `TestUnits`. It is the primary integration test between parsing, transform, export-symbol handling, and output generation.

## Risks and Edge Cases

Whitespace cleanup and timestamp normalization intentionally relax some output differences. Dynamic test creation assumes the YAML has already been schema-valid and can generate method-name collisions if scenario names repeat. Several `@expectedFailure` tests validate that the harness fails on empty or incomplete expectations.

## Test Signals

Passing tests confirm exported-symbol parsing, section/parameter extraction, dynamic YAML scenarios, RST rendering, man rendering, and source-to-output pipelines. Running with alternate `--yaml-file` verifies corpus extensibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/unittests/test_kdoc_parser.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/unittests/test_kdoc_test_schema.py -->
# sources/distributed-fs/ceph-client/tools/unittests/test_kdoc_test_schema.py

## Purpose

`test_kdoc_test_schema.py` validates that `kdoc-test.yaml` conforms to `kdoc-test-schema.yaml` when the optional `jsonschema` package is available.

## Important APIs, Types, and Functions

The central class is `TestYAMLSchemaValidation`. `setUpClass()` imports `Draft7Validator`, loads the schema, and stores a validator. `test_kdoc_test_yaml_followsschema()` loads test data, collects validation errors, and fails with all messages if any exist.

## Control Flow and Data Flow

At runtime the test attempts to import `jsonschema`. If unavailable, it prints a warning and skips validation by returning from the test. If available, schema and test YAML files are loaded with `yaml.safe_load()` and checked.

## State and Persistence Behavior

The test reads YAML files only and writes no state. Class attributes cache the validator.

## Dependencies and Integration Points

It depends on PyYAML, optional `jsonschema`, unittest, and repository path layout. It complements `test_kdoc_parser.py` by checking data shape before dynamic parser tests use the corpus.

## Risks and Edge Cases

Missing `jsonschema` turns validation into a soft skip, so CI environments without the package lose this signal. The method name has a typo (`followsschema`) but is still discovered. Schema permissiveness can still allow semantically poor expected data.

## Test Signals

The key pass signal is zero schema validation errors. A warning about missing `jsonschema` means parser tests may still run but schema coverage is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/unittests/test_kdoc_test_schema.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/unittests/test_tokenizer.py -->
# sources/distributed-fs/ceph-client/tools/unittests/test_tokenizer.py

## Purpose

`test_tokenizer.py` tests the C tokenizer used by kernel-doc, including token kinds, nesting-level accounting, unexpected-token logging, and removal of private struct sections.

## Important APIs, Types, and Functions

Helpers include `tokens_to_list()`, `make_tokenizer_test()`, `make_private_test()`, `setUp()`, and `build_test_class()`. Data tables `TESTS_TOKENIZER` and `TESTS_PRIVATE` define dynamically generated unittest classes. It imports `CToken`, `CTokenizer`, and `run_unittest`.

## Control Flow and Data Flow

For token tests, the file tokenizes source snippets, strips space tokens, and compares `(kind, value, level)` tuples. For private/public tests, it stringifies the tokenizer output and compares whitespace-normalized trimmed source. Dynamic class creation turns table entries into methods at import time.

## State and Persistence Behavior

Tests are pure in-memory operations. Unexpected-token tests use `assertLogs()` to verify logging output.

## Dependencies and Integration Points

It depends on `kdoc.c_lex` and Python unittest. It protects parser behavior for nested braces/parentheses/brackets, comments, illegal tokens, and kernel-doc `private:`/`public:` comment trimming used before item extraction.

## Risks and Edge Cases

Dynamic method names are derived from human-readable keys that include spaces, which works but is unusual. Whitespace normalization can hide formatting differences. Private-section tests cover balanced and unbalanced cases, including nested structs and `struct_group_tagged`.

## Test Signals

Passing tests indicate token classification, nesting levels, illegal-token logging, and private/public trimming behavior are stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/unittests/test_tokenizer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/Makefile -->
# sources/distributed-fs/ceph-client/tools/usb/Makefile

## Purpose

`tools/usb/Makefile` builds and installs the main Linux USB user-space tools in this tree: `testusb` and `ffs-test`.

## Important APIs, Types, and Targets

Important variables are `bindir`, `srctree`, `CFLAGS`, `LDFLAGS`, `ALL_TARGETS`, and `ALL_PROGRAMS`. Targets include `all`, per-program links for `$(OUTPUT)testusb` and `$(OUTPUT)ffs-test`, `clean`, `install`, and `FORCE`.

## Control Flow and Data Flow

The Makefile locates `srctree` when unset, disables built-in rules with `MAKEFLAGS += -r`, exports build variables, includes `tools/build/Makefile.include`, recursively builds object aggregates in `testusb` and `ffs-test` subdirectories, then links final binaries with pthread support.

## State and Persistence Behavior

Build artifacts are written under `$(OUTPUT)` when set, otherwise the current directory. `install` copies binaries into `$(DESTDIR)$(bindir)`. `clean` removes programs and object/dependency/cmd files.

## Dependencies and Integration Points

It depends on the kernel tools build framework, compiler/linker variables, pthread, `tools/include`, and subdirectory build descriptions. It is invoked by kernel tools build targets and manual `make` in `tools/usb`.

## Risks and Edge Cases

Incorrect `srctree` or `OUTPUT` breaks include paths and artifact placement. The `clean` find expression depends on operator precedence and may be surprising. Link flags are globally appended with `-lpthread`. Installing requires destination permissions.

## Test Signals

Build tests should run `make -C tools/usb`, verify both binaries exist under `OUTPUT`, run `make clean`, and test `DESTDIR` installation layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/ffs-aio-example/multibuff/device_app/aio_multibuff.c -->
# sources/distributed-fs/ceph-client/tools/usb/ffs-aio-example/multibuff/device_app/aio_multibuff.c

## Purpose

`aio_multibuff.c` is a FunctionFS device-side example that submits many asynchronous bulk IN transfers using two rotating buffer groups. It demonstrates high-throughput AIO on a USB gadget endpoint.

## Important APIs, Types, and Functions

It defines FunctionFS descriptors and strings, constants `BUF_LEN`, `BUFS_MAX`, and `AIO_MAX`, and `struct io_buffer` containing arrays of buffers/iocbs plus request counters. Functions are `display_event()`, `handle_ep0()`, `init_bufs()`, `delete_bufs()`, and `main()`.

## Control Flow and Data Flow

`main()` opens `ep0`, writes descriptors and strings, opens `ep1`, creates an AIO context sized for all requests, opens an eventfd, allocates two `io_buffer` groups, and enters a select loop on `ep0` and eventfd. When FunctionFS reports ENABLE, each idle buffer group is prepared with `io_prep_pwrite()` requests to `ep1`, eventfd notifications are attached, and all iocbs are submitted. Eventfd completions are drained with `io_getevents()`, decrementing the active group's request count and rotating when complete.

## State and Persistence Behavior

Descriptors and strings configure the FunctionFS function while `ep0` is open. AIO context, eventfd, endpoint fd, iocbs, buffers, and `requested` counters are process-local. The loop is infinite until an error breaks it.

## Dependencies and Integration Points

It depends on mounted FunctionFS endpoints, Linux native AIO (`libaio.h`), eventfd, select, USB FunctionFS headers, and a gadget configuration exposing endpoint files. It pairs with the multibuff host `test.c`.

## Risks and Edge Cases

`ready` is not explicitly initialized before the loop. Memory allocation results in `init_bufs()` are not checked. Partial `io_submit()` is treated as success but records only submitted count. The code submits only IN writes on one endpoint despite descriptors advertising two endpoints. Infinite operation requires external termination.

## Test Signals

Signals include descriptor/string writes succeeding, ENABLE/DISABLE events toggling readiness, `submit: N requests buf: I` output, eventfd completions draining, and host-side bulk reads receiving data continuously.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/ffs-aio-example/multibuff/device_app/aio_multibuff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/ffs-aio-example/multibuff/host_app/Makefile -->
# sources/distributed-fs/ceph-client/tools/usb/ffs-aio-example/multibuff/host_app/Makefile

## Purpose

This Makefile builds the multibuffer FunctionFS host-side test program from `test.c`.

## Important APIs, Types, and Targets

Variables include `CC`, `LIBUSB_CFLAGS`, `LIBUSB_LIBS`, `WARNINGS`, `CFLAGS`, and `LDFLAGS`. Targets are `all`, pattern rule `%: %.c`, and `clean`.

## Control Flow and Data Flow

`pkg-config` supplies libusb compiler and linker flags. `all` builds `test`; the pattern rule compiles a matching `.c` source into an executable and links libusb. `clean` removes `test`.

## State and Persistence Behavior

The only artifact is the `test` binary in the host_app directory.

## Dependencies and Integration Points

It depends on gcc, pkg-config, and libusb-1.0 development files. It is paired with `multibuff/device_app/aio_multibuff.c`.

## Risks and Edge Cases

Missing pkg-config or libusb development headers causes build failure. The generic pattern rule can build other one-file tools if added, but there is only `test.c` here.

## Test Signals

`make` should emit a `test` binary linked against libusb; `make clean` should remove it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/ffs-aio-example/multibuff/host_app/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/ffs-aio-example/multibuff/host_app/test.c -->
# sources/distributed-fs/ceph-client/tools/usb/ffs-aio-example/multibuff/host_app/test.c

## Purpose

This host-side libusb test finds the FunctionFS gadget device and continuously performs bulk reads from its first endpoint, matching the multibuffer device example that streams IN data.

## Important APIs, Types, and Functions

Constants define Linux Foundation test gadget IDs `VENDOR 0x1d6b`, `PRODUCT 0x0105`, and `BUF_LEN 8192`. `struct test_state` stores libusb device, context, handle, and kernel-driver attachment state. Functions are `test_init()`, `test_exit()`, and `main()`.

## Control Flow and Data Flow

`test_init()` initializes libusb, enumerates devices, finds the matching VID/PID, opens it, claims interface 0, detaching a kernel driver if necessary. `main()` reads config descriptor 0, selects endpoint 0 address from interface altsetting 0, then loops forever calling `libusb_bulk_transfer()` with a 500 ms timeout.

## State and Persistence Behavior

The libusb context and claimed interface persist until process exit. `attached` records whether the kernel driver should be reattached in `test_exit()`, though the infinite loop means normal cleanup is not reached without external control.

## Dependencies and Integration Points

It depends on libusb-1.0 and a connected/configured gadget with matching IDs. It integrates with the multibuffer device app and the host Makefile.

## Risks and Edge Cases

The device list is not freed on the success path, and the config descriptor is not freed. Endpoint ordering is assumed. Bulk transfer errors and byte counts are ignored, so disconnects or stalls do not produce diagnostics. Infinite loop requires interruption.

## Test Signals

A useful run finds the gadget, claims interface 0, and repeatedly completes bulk IN transfers. Failure messages identify libusb init, descriptor, open, detach, or claim issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/ffs-aio-example/multibuff/host_app/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/ffs-aio-example/simple/device_app/aio_simple.c -->
# sources/distributed-fs/ceph-client/tools/usb/ffs-aio-example/simple/device_app/aio_simple.c

## Purpose

`aio_simple.c` is a FunctionFS device-side example that runs one asynchronous bulk IN write and one asynchronous bulk OUT read at a time, using eventfd notifications for completions.

## Important APIs, Types, and Functions

It defines FunctionFS descriptor/string blobs for full-speed and high-speed operation, `BUF_LEN`, `display_event()`, `handle_ep0()`, and `main()`. It uses native AIO types `io_context_t`, `struct iocb`, and `struct io_event`.

## Control Flow and Data Flow

`main()` opens `ep0`, writes descriptors and strings, opens `ep1` and `ep2`, sets up an AIO context for two requests, creates an eventfd, allocates buffers/iocbs, then waits on `ep0` and eventfd. `handle_ep0()` handles FunctionFS events, acknowledges SETUP, and toggles readiness. Once ready, the loop submits a pwrite to IN endpoint and a pread from OUT endpoint if not already pending. Eventfd completions clear `req_in`/`req_out`.

## State and Persistence Behavior

Descriptors configure the USB function for the lifetime of `ep0`. AIO request state is tracked by `req_in` and `req_out`. Buffers and iocbs are heap allocated and freed on loop exit.

## Dependencies and Integration Points

It depends on FunctionFS endpoint files, `libaio.h`, eventfd/select, USB FunctionFS headers, and a gadget setup using this function. It pairs with the simple host `test.c`, which performs IN and OUT transfers.

## Risks and Edge Cases

`ready` is not initialized before use. Buffer and iocb allocation failures are not checked. The endpoint direction naming can be confusing: endpoint descriptor addresses are from host perspective, while device code writes to IN and reads from OUT. Infinite operation requires external termination. Eventfd read count is not used to drain multiple completions beyond `io_getevents()`.

## Test Signals

Success signals include descriptor/string writes, ENABLE events, `submit: in/out` messages, `ev=in/out` completion messages, and host-side bidirectional bulk transfers completing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/ffs-aio-example/simple/device_app/aio_simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/ffs-aio-example/simple/host_app/Makefile -->
# sources/distributed-fs/ceph-client/tools/usb/ffs-aio-example/simple/host_app/Makefile

## Purpose

This Makefile builds the simple FunctionFS host-side test program from `test.c`.

## Important APIs, Types, and Targets

It defines compiler, pkg-config-derived libusb flags, warning flags, and `all`, pattern, and `clean` targets. `all` builds `test`.

## Control Flow and Data Flow

The pattern rule compiles any matching `.c` file into an executable using `$(CC) $(CFLAGS)` and links `$(LDFLAGS)` from libusb. `clean` removes the produced `test` binary.

## State and Persistence Behavior

The Makefile creates and removes only the local `test` executable.

## Dependencies and Integration Points

It depends on gcc, pkg-config, and libusb-1.0 development files. The produced binary is intended to exercise `simple/device_app/aio_simple.c`.

## Risks and Edge Cases

Builds fail when libusb pkg-config metadata is missing. There is no install target or cross-compile handling.

## Test Signals

`make` producing `test` and `make clean` removing it are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/ffs-aio-example/simple/host_app/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/ffs-aio-example/simple/host_app/test.c -->
# sources/distributed-fs/ceph-client/tools/usb/ffs-aio-example/simple/host_app/test.c

## Purpose

This host-side libusb test pairs with the simple FunctionFS AIO device example by continuously performing bulk transfers on the gadget's first two endpoints.

## Important APIs, Types, and Functions

It uses `VENDOR 0x1d6b`, `PRODUCT 0x0105`, `BUF_LEN 8192`, `struct test_state`, `test_init()`, `test_exit()`, and `main()`.

## Control Flow and Data Flow

Initialization mirrors the multibuffer host: create libusb context, enumerate devices, locate VID/PID, open, detach kernel driver if needed, and claim interface 0. `main()` reads the config descriptor, takes endpoint addresses 0 and 1 from interface altsetting 0, and loops forever doing a bulk transfer from the IN endpoint followed by a bulk transfer to the OUT endpoint with the same buffer.

## State and Persistence Behavior

The claimed interface and optional detached-kernel-driver state persist during the process. Normal cleanup is defined but unreachable in the infinite loop without external interruption.

## Dependencies and Integration Points

It depends on libusb-1.0 and the FunctionFS gadget enumerating with expected IDs and two endpoints. It integrates with `aio_simple.c` and the simple host Makefile.

## Risks and Edge Cases

Endpoint ordering is assumed to match device descriptors. Bulk transfer return codes are ignored. Device list and config descriptor are not freed on success. There is no signal handler for graceful cleanup.

## Test Signals

A working setup continuously completes bidirectional bulk transfers. Init failures produce diagnostics for no devices, descriptor reads, open, detach, or claim failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/ffs-aio-example/simple/host_app/test.c -->
