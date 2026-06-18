# Research: subset-b-006757

This grouped report covers the perf utility BPF counter, tracing, lock, off-CPU, branch, BTF, build-id, cacheline, and call-path sources requested for subset B. Each source section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_counter.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_counter.c

Purpose: this file is the main user-space bridge between perf events and BPF-backed counter collection. It chooses one of three counter implementations for an `evsel`: BPF program profiling from explicit BPF program ids, shared `bperf` hardware-counter aggregation, or cgroup-expanded `bperf` via the externally defined `bperf_cgrp_ops`. It also owns the common wrapper API invoked by perf stat open/enable/disable/read/destroy paths.

Important APIs and functions: `set_max_rlimit()` raises `RLIMIT_MEMLOCK` for BPF maps/programs; `bperf_trigger_reading()` invokes `BPF_PROG_TEST_RUN` on a raw tracepoint program for a specific CPU; `bpf_counter__load()`, `bpf_counter__install_pe()`, `bpf_counter__enable()`, `bpf_counter__disable()`, `bpf_counter__read()`, and `bpf_counter__destroy()` dispatch through `struct bpf_counter_ops`. The BPF-program profiler path uses `bpf_target_prog_name()`, `bpf_program_profiler_load_one()`, and `bpf_program_profiler__read()` with `bpf_prog_profiler.bpf.c`. The bperf path uses `bperf_lock_attr_map()`, `bperf_reload_leader_program()`, `bperf_attach_follower_program()`, `bperf_sync_counters()`, and `bperf__read()` with the leader/follower skeletons.

Control flow: `bpf_counter__load()` selects profiling when `target->bpf_str` is set, cgroup mode when expanded cgroup events and `--use-bpf` are active, otherwise bperf for `--use-bpf`, explicit `evsel->bpf_counter`, or known BPF-counter-compatible event names. The profiling path parses comma-separated program ids, opens target programs, discovers the target BTF function name, retargets fentry/fexit skeleton programs, installs perf-event fds per CPU, attaches on enable, and accumulates per-CPU deltas on read. The shared bperf path pins or opens a global `perf_event_attr` map under bpffs, locks it with `flock()`, reloads a leader if the stored link id is stale, opens system-wide perf events for the leader, attaches a per-session follower fexit program, loads filters for CPU/PID/TGID/global modes, test-runs the leader before reads, and folds map values into perf counts.

State and persistence: `struct bpf_counter` list nodes hang off `evsel->bpf_counter_list` for program profiling. bperf persists cross-session state in a pinned attr map whose values include leader link/map ids. `evsel` stores leader program/link fds, transient leader skeleton during perf-event installation, and follower skeleton for the session. The file-scope `filter_entry_cnt` is shared by the bperf read path, so concurrent independent bperf loads in one process would depend on serialized perf stat behavior.

Dependencies and integration: it depends on libbpf, perf `evsel`/`evlist`, CPU/thread maps, target parsing, bpffs mount discovery, and generated skeleton headers for `bpf_prog_profiler`, `bperf_leader`, and `bperf_follower`. It integrates directly with perf stat by replacing direct perf-event reads with BPF map aggregation while preserving `struct perf_counts_values`.

Risks: BTF is required for BPF program profiling target attachment; missing BTF produces hard failures. bperf assumes no event groups and only certain target modes. The pinned attr map must have the exact key/value layout, and stale link ids trigger reload logic. Several assert-heavy paths assume successful map/link fd recovery once a link id is valid. Kernel support for test-run on raw tracepoint programs is checked and failure aborts bperf in this implementation. The global `filter_entry_cnt` and shared pinned map should be reviewed carefully for multi-evsel/multi-session edge cases.

Test signals: exercise `perf stat --use-bpf` for system-wide, CPU, PID, TGID, inherited and non-inherited targets; verify fallback/error messages for unsupported groups; run with a stale pinned attr map; profile a BPF program with and without BTF; and compare BPF-backed counts against ordinary perf-event counts across CPU hotplug-like possible-vs-online CPU layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_counter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_counter.h -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_counter.h

Purpose: this header declares the perf BPF counter abstraction used by `evsel` code. It exposes a small lifecycle/install/read API while hiding whether the implementation is program profiling, shared bperf counters, cgroup bperf, or a no-op build without BPF skeleton support.

Important APIs and types: `struct bpf_counter_ops` holds `load`, `enable`, `disable`, `read`, `destroy`, and `install_pe` callbacks. Public functions mirror those callbacks: `bpf_counter__load()`, `bpf_counter__enable()`, `bpf_counter__disable()`, `bpf_counter__read()`, `bpf_counter__destroy()`, and `bpf_counter__install_pe()`. `bperf_trigger_reading()` and `set_max_rlimit()` are also exported for cgroup counter code.

Control flow and state: when `HAVE_BPF_SKEL` is defined, the header declares real functions implemented in `bpf_counter.c` and `bpf_counter_cgroup.c`. Otherwise, inline stubs allow the rest of perf to compile and degrade cleanly: load/enable/disable/install succeed, reads return `-EAGAIN`, and destroy is empty.

Dependencies and integration: the header forward declares `struct evsel` and `struct target`, uses `linux/err.h` for the non-BPF stub read result, and is included by perf stat/BPF utility files that should not depend on concrete skeleton types.

Risks: callers must treat `-EAGAIN` as a signal to use normal perf reading or to report unavailable BPF data. New counter backends must fill every callback or wrapper calls will dereference null function pointers once `evsel->bpf_counter_ops` is set.

Test signals: build perf with and without `HAVE_BPF_SKEL`; verify normal perf stat still works without BPF skeleton support; and compile any new backend with strict warnings to catch signature drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_counter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_counter_cgroup.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_counter_cgroup.c

Purpose: this file implements `bperf_cgrp_ops`, the BPF counter backend used when perf stat expands events across multiple cgroups. It opens one uncgrouped copy of each event per CPU, attaches a BPF program to cgroup-switch events, and aggregates deltas into per-cgroup/per-event maps.

Important APIs and functions: `setup_rodata()` sizes BPF maps and sets cgroup v1/v2 mode; `test_max_events_program_load()` validates verifier loadability for maximum configured events in debug builds; `bperf_load_program()` opens the skeleton, attaches `on_cgrp_switch` to `PERF_COUNT_SW_CGROUP_SWITCHES`, populates `events` and `cgrp_idx`, and checks raw tracepoint test-run support; `bperf_cgrp__enable()`, `bperf_cgrp__disable()`, and `bperf_cgrp__read()` synchronize counters and transfer `cgrp_readings` into perf counts.

Control flow: the first evsel load calls `bperf_load_program()` once via a static `bperf_loaded` flag. The code opens a software cgroup-switch event on all CPUs and attaches the BPF program to each fd. It then walks the evlist, opens a single non-cgroup instance for each leader cgroup group of events, installs fds into the BPF `events` perf-event array by event index and CPU, maps each cgroup id to an ordinal index, and later reads only from the first evsel invocation while iterating all evsels.

State and persistence: `skel` and `cgrp_switch` are static process-wide pointers. Map sizes depend on `nr_cgroups`, evlist entry count, and `cpu__max_cpu()`. BPF global `enabled` gates delta accumulation. The evsel's `follower_skel` is set to a casted non-null value solely to bypass `bpf_counter_skip()`, so it is a sentinel rather than a real follower skeleton.

Dependencies and integration: this code depends on cgroup id helpers, perf CPU maps, event opening, libbpf skeleton `bperf_cgroup`, and `bperf_trigger_reading()` from `bpf_counter.c`. It integrates with the cgroup-expanded evlist where entries are ordered by event and cgroup.

Risks: static global lifetime implies one cgroup BPF counter instance per process. `evlist_size % nr_cgroups` is enforced with `BUG_ON`, so malformed expansion is fatal. The read path allocates an array sized by `cpu__max_cpu().cpu`, which assumes CPU ids are bounded as expected. Missing cgroup ids are mapped to zero after a debug message, risking aggregation ambiguity. Kernel lack of test-run support only warns, so final reads may be less fresh.

Test signals: run `perf stat --for-each-cgroup ... --use-bpf` on cgroup v1 and v2 systems, with multiple events and CPUs; verify counts against normal cgroup perf; test unsupported/max-event verifier boundaries; and run cleanup under valgrind/ASAN to confirm the static skeleton and cgroup-switch evsel are released once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_counter_cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_ftrace.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_ftrace.c

Purpose: this file provides the user-space side of BPF-powered `perf ftrace latency`. It configures the `func_latency` skeleton either for a single function kprobe/kretprobe pair or for a pair of raw tracepoint events, then reads histogram buckets and summary statistics.

Important APIs and functions: `perf_ftrace__latency_prepare_bpf()` validates the target, sizes CPU/task filter and latency maps, populates rodata thresholds, loads and attaches the skeleton, and returns a dummy fd for polling. `perf_ftrace__latency_start_bpf()` and `perf_ftrace__latency_stop_bpf()` toggle the BPF `enabled` flag. `perf_ftrace__latency_read_bpf()` folds per-CPU histogram arrays and copies BPF-maintained `count`, `total`, `min`, and `max` into `struct stats`. `perf_ftrace__latency_cleanup_bpf()` destroys the skeleton.

Control flow: prepare accepts either exactly one function filter or exactly two event filters. It populates CPU filters from `user_requested_cpus` when a CPU list is supplied and task filters from the evlist thread map when a task target or no explicit target is used. Function mode attaches a kprobe and kretprobe to the same symbol; event-pair mode attaches raw tracepoint begin/end programs to the two configured event names.

State and persistence: the skeleton is a static pointer. BPF global state holds histogram buckets, aggregate totals, and min/max values for the session. The code initializes BPF `min` to `INT64_MAX` before starting. No persistent filesystem state is used.

Dependencies and integration: it depends on perf ftrace configuration structures, CPU/thread maps, stats helpers, `set_max_rlimit()`, and the generated `func_latency` skeleton. It integrates with the ftrace command's latency output by filling caller-provided bucket arrays and stats.

Risks: nested function/event invocations overwrite the per-thread timestamp in the BPF map, so recursive or reentrant targets may undercount outer latencies. The dummy `/dev/null` fd is only for poll plumbing and does not reflect BPF readiness. Static skeleton lifetime makes concurrent latency sessions in one process unsafe. Bucket accumulation does not clear `buckets[]`, so callers must provide zeroed storage.

Test signals: test single function latency and two-event latency, CPU and task filters, nanosecond and microsecond modes, bucket range/min/max options, invalid filter counts, and nested target behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_ftrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_kwork.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_kwork.c

Purpose: this file is the user-space loader/reader for BPF-backed `perf kwork report` tracing. It selects tracepoint programs for IRQ, softirq, and workqueue classes, applies CPU/name filters, and converts BPF report-map rows into perf `kwork_work` objects.

Important APIs and functions: `perf_kwork__trace_prepare_bpf()` opens `kwork_trace`, disables all autoload programs, re-enables programs matching selected classes and report mode, sets rodata filter flags, loads, filters, and attaches. `perf_kwork__trace_start()` and `perf_kwork__trace_finish()` record wall-clock monotonic bounds and toggle `enabled`. `perf_kwork__report_read_bpf()` iterates `perf_kwork_report`, uses `add_work()` to populate runtime or latency totals, and `perf_kwork__report_cleanup_bpf()` destroys the skeleton.

Control flow: each `kwork_class_bpf` entry owns a class pointer, a load-preparation hook, and a work-name lookup hook. Runtime report mode enables entry/exit programs; latency mode enables raise/activate to execute/entry programs where applicable. During read, each map key is decoded as type/cpu/id, optional names are fetched from `perf_kwork_names`, class pointers are restored from the supported-list table, and aggregate timing fields are copied into the kwork model.

State and persistence: `skel`, `ts_start`, and `ts_end` are static. BPF maps retain timestamp, name, and report rows until cleanup. `kwork->timestart` and `kwork->timeend` are set from user-space monotonic timestamps, not from the BPF event timestamps.

Dependencies and integration: it relies on `util/kwork.h` class/report enums staying synchronized with the BPF enum and map structs in `kwork_trace.bpf.c`, libbpf map operations, perf CPU map parsing, and the `kwork->add_work` callback.

Risks: BPF map capacity `KWORK_COUNT` is fixed in the skeleton and may drop distinct work items in busy systems. Name filters reject names at or above `MAX_KWORKNAME`. Static class pointers in `kwork_class_bpf_supported_list` are session state. The read loop returns on first lookup/add error and can leak a duplicated name if downstream ownership assumptions change.

Test signals: run runtime and latency reports for IRQ, softirq, and workqueue classes; exercise CPU and name filters; compare BPF totals with tracepoint/raw perf outputs; and stress high-cardinality workqueues to observe map-capacity behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_kwork.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_kwork_top.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_kwork_top.c

Purpose: this file loads and reads the BPF implementation for `perf kwork top`, providing live runtime aggregation for IRQ, softirq, and scheduler work classes. It maps BPF per-work/per-CPU runtime rows into `kwork_work` objects and enriches scheduler rows with task metadata.

Important APIs and functions: `perf_kwork__top_prepare_bpf()` opens the `kwork_top` skeleton, disables all autoload, enables only selected class programs, configures CPU filters, loads, attaches, and stores class pointers. `perf_kwork__top_start()` and `perf_kwork__top_finish()` set BPF session timestamps and toggle `enabled`. `perf_kwork__top_read_bpf()` iterates `kwork_top_works` and calls `add_work()` for every nonzero per-CPU runtime. `read_task_info()` pulls `tgid`, kernel-thread flag, and command from `kwork_top_tasks`.

Control flow: selected classes decide which tp_btf programs attach: scheduler uses `sched_switch`, IRQ uses handler entry/exit, softirq uses entry/exit. The read path allocates a possible-CPU-sized array because `kwork_top_works` is per-CPU. Each key encodes class type, pid, and task pointer, while CPU is represented by the per-CPU array slot.

State and persistence: static `skel` and static supported-list class pointers hold process/session state. BPF maps store task local timestamps, IRQ/softirq timestamp rows, task metadata, runtime rows, and CPU filter entries. BPF globals `from_timestamp` and `to_timestamp` bound runtime fallback calculations.

Dependencies and integration: the user-space structs must stay in sync with `kwork_top.bpf.c`. Integration is via perf kwork's class list and `add_work` callback. It uses libbpf and perf CPU map helpers.

Risks: `perf_kwork__top_read_bpf()` can return early without freeing `data` on lookup or add-work errors. Runtime fallback to `from_timestamp` can overstate work if an entry timestamp is missing. Task names are allocated with `strdup()` and rely on downstream ownership. BPF map cardinality is capped at `MAX_ENTRIES`.

Test signals: run kwork top with scheduler-only, IRQ-only, softirq-only, and combined classes; test CPU filters; verify task names/tgids for user and kernel threads; and stress context-switch/interrupt-heavy workloads to catch map capacity and cleanup issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_kwork_top.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_lock_contention.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_lock_contention.c

Purpose: this file is the user-space controller for BPF lock contention tracing. It configures filters and aggregation mode, resolves kernel symbols and slab/NUMA metadata, starts/stops BPF collection, accounts unfinished waits at stop time, converts BPF maps into perf `lock_stat` objects, and releases auxiliary state.

Important APIs and functions: `lock_contention_prepare()` is the central setup routine. It sizes maps, sets rodata for CPU/task/type/address/cgroup/slab filters, resolves symbol filters and delay injections, initializes BTF-dependent slab and NUMA data, loads and attaches the skeleton, populates filter maps, and optionally reads all cgroups. `lock_contention_start()`/`stop()` toggle `enabled`; `mark_end_timestamp()` uses `BPF_PROG_TEST_RUN` to capture a BPF timestamp; `account_end_timestamp()` accounts outstanding begin events; `lock_contention_read()` merges BPF `lock_stat` rows into perf's RB-tree stats; `pop_owner_stack_trace()` drains owner-stack rows; `lock_contention_finish()` destroys BPF and cgroup/BTF/slab state.

Control flow: preparation first loads the kernel map for symbol lookup, then configures maps according to `struct lock_contention`. CPU/task/type/address/cgroup/slab filters become BPF hash maps. Symbol names in filters and delay specifications are resolved to kernel addresses. Optional slab-cache iteration is enabled only when vmlinux BTF contains `bpf_iter__kmem_cache`. At read time, outstanding timestamps are converted to stats, address aggregation may test-run a BPF program to collect runqueue and zone lock symbols, and each BPF stat row is named according to aggregation mode.

State and persistence: the skeleton, slab-iterator availability, and slab cache hashmap are static. `con->btf` persists loaded vmlinux BTF until finish. BPF maps hold timestamps, per-CPU timestamps, stack traces, task comms, slab cache ids, lock symbol classes, owner stack data, delay settings, cgroup filters, and final contention stats. The perf-side global lock stat tree is updated via `lock_stat_find*`.

Dependencies and integration: it depends on perf machine/symbol/map APIs, cgroup helpers, target/thread maps, libbpf, vmlinux BTF, BPF kfunc availability for slab/owner stack features, and shared structs in `lock_data.h`. It integrates with `perf lock contention` aggregation by task, caller, address, or cgroup.

Risks: many features are kernel-version dependent: BTF, slab iterators, `bpf_get_kmem_cache`, `bpf_task_from_pid`, runqueue symbol layout, and zone layout. Some failures only reduce data quality counters. The file uses static state, so concurrent sessions can conflict. `lock_contention_prepare()` returns on load failure without destroying the opened skeleton. Address naming has two repeated `lock_syms` lookups and depends on flags encoding for special locks. Delay injection intentionally burns CPU and must be used carefully.

Test signals: test all aggregation modes, with and without call stacks and owner tracing; run on kernels with/without BTF slab iterator and cgroup v2; validate symbol/slab/name filters; check outstanding contention accounting after forced stop; compare fail counters; and run with small map sizes to exercise full-map paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_lock_contention.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_off_cpu.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_off_cpu.c

Purpose: this file wires BPF off-CPU time tracking into `perf record`. It adds a `bpf-output` event, loads the off-CPU skeleton, installs record-start/end hooks, and writes aggregated BPF off-CPU records into the perf data file as synthetic samples.

Important APIs and functions: `off_cpu_config()` adds the `OFFCPU_EVENT` bpf-output event and marks it system-wide. `check_sched_switch_args()` inspects vmlinux BTF to determine whether `sched_switch` tp_btf includes `prev_state`. `off_cpu_prepare()` configures CPU/task/cgroup filters, cgroup recording, thresholding, loads and attaches BPF, and registers hooks. `off_cpu_start()` fills the BPF perf-event array and enables collection. `off_cpu_finish()` disables and destroys the skeleton. `off_cpu_write()` emits aggregated map contents as `PERF_RECORD_SAMPLE` records.

Control flow: prepare always creates the output evsel first. Target mode controls BPF filter map size and whether task keys are pid or tgid. For `target__none`, the start hook adds the workload pid into the task filter after fork. On record start, the output map is populated from the evsel fd array per CPU. On write, the code validates supported sample types, builds a sample buffer containing id/ip/tid/time/cpu/period/raw/cgroup fields as requested, reads the BPF stack map for callchains, and writes records with increasing dummy timestamps near the end of time ordering.

State and persistence: static `skel` is the active session. BPF maps store task-storage timestamps, stack ids, aggregated off-CPU durations, and optional direct output payloads. `OFF_CPU_TIMESTAMP` intentionally places synthetic samples late in sorting. No persistent filesystem state exists beyond the perf data file written by `off_cpu_write()`.

Dependencies and integration: it depends on perf hooks, evlist parsing, record options, cgroup helpers, thread/CPU maps, perf session I/O, and the `off_cpu` skeleton. It integrates with perf record by adding a bpf-output evsel and with later analysis through raw sample payload layout.

Risks: `off_cpu_write()` disables BPF but assumes the skeleton remains valid until after writing; hook ordering is important. Only sample types in `OFFCPU_SAMPLE_TYPES` are supported. Stack collection can produce zero or negative stack ids, and raw payload layout must remain synchronized with parsers. Threshold behavior splits direct perf-output samples from map-aggregated samples, so tests must cover both paths. BTF absence weakens sched_switch signature detection.

Test signals: record off-CPU with pid, tid, workload, CPU, cgroup, and record-cgroup options; test kernels before and after the `prev_state` sched_switch change; verify thresholded direct output and aggregated map output; inspect resulting perf data with report/script; and compare cgroup ids on cgroup v1/v2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_off_cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/augmented_raw_syscalls.bpf.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/augmented_raw_syscalls.bpf.c

Purpose: this BPF program augments `raw_syscalls` enter/exit events with pointed-to user data so `perf trace` can display filenames, sockaddr data, perf_event_attr contents, timespecs, and configured "beauty" arguments rather than raw pointer values.

Important APIs, maps, and programs: maps include `__augmented_syscalls__` perf-event array, `syscalls_sys_enter`/`syscalls_sys_exit` program arrays, `pids_filtered`, `augmented_args_tmp`, `beauty_map_enter`, and `beauty_payload_enter_map`. Entry augmenters include `sys_enter_connect`, `sys_enter_sendto`, `sys_enter_open`, `sys_enter_openat`, `sys_enter_rename`, `sys_enter_renameat2`, `sys_enter_perf_event_open`, `sys_enter_clock_nanosleep`, and `sys_enter_nanosleep`. Root programs are raw tracepoint `sys_enter` and `sys_exit`.

Control flow: root `sys_enter` filters configured pids, copies the raw syscall arguments into per-CPU scratch storage, attempts generic `augment_sys_enter()` based on `beauty_map_enter`, and falls back to a syscall-number-indexed tail call. Specific augmenters read user memory safely, set size/error fields, align variable-length strings where needed, and emit augmented payloads to the current CPU perf-output event. `sys_exit` tail-calls into exit augmenters but this file mainly provides the enter path and unaugmented fallback.

State and persistence: all state is in BPF maps configured by user space. Scratch payload maps are per-CPU arrays to avoid BPF stack limits. The pid filter map suppresses perf's own helper pids. Program arrays persist tail-call routing until user space updates them.

Dependencies and integration: user space in `bpf_trace_augment.c` loads and attaches only root programs, configures the perf-output map, and exposes program/map fds for perf trace. The BPF code depends on the hand-maintained `vmlinux.h`, BPF helpers for user reads and perf output, and syscall tracepoint layouts.

Risks: verifier constraints drive several bounds tricks; changes in syscall argument ordering or tracepoint ABI would break augmentation. `getpid()` truncates `bpf_get_current_pid_tgid()` to pid_t, which is intentional for current pid matching but should be reviewed for namespace semantics. Failed output returns nonzero so callers may record unaugmented data; silent drops can happen if tail-call maps are not populated. Buffer augmentation is capped at 32 bytes.

Test signals: run `perf trace` for open/openat/rename/connect/sendto/perf_event_open/nanosleep, with beauty-map driven augmentations and pid filters; verify fallback unaugmented events; and test verifier load on supported clang/kernel combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/augmented_raw_syscalls.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bench_uprobe.bpf.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bench_uprobe.bpf.c

Purpose: this small skeleton provides BPF programs for `perf bench uprobe`, measuring empty uprobes/uretprobes and trace-printing variants.

Important APIs and functions: `BPF_UPROBE(empty)`, `BPF_UPROBE(trace_printk)`, `BPF_URETPROBE(empty_ret)`, and `BPF_URETPROBE(trace_printk_ret)` are attached externally as uprobe/uretprobe programs. Globals `nr_uprobes` and `nr_uretprobes` count trace-print invocations.

Control flow: empty probes immediately return. Trace-print probes increment the relevant counter and call `bpf_trace_printk()` with a fixed format.

State and persistence: only BPF global counters are maintained for the life of the loaded skeleton. No maps are declared.

Dependencies and integration: depends on libbpf tracing macros and the perf bench harness that attaches the sections to user-space symbols.

Risks: `bpf_trace_printk()` is intentionally expensive and suitable only for benchmarking/debug behavior. Counter globals are not atomic and are used for approximate benchmark signaling.

Test signals: run perf bench uprobe modes for entry/return, empty/trace_printk variants, and compare overhead with expected relative cost.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bench_uprobe.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_cgroup.bpf.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_cgroup.bpf.c

Purpose: this in-kernel BPF program implements cgroup-aware bperf aggregation. It reads shared perf-event counters on cgroup switches or explicit trigger reads and accumulates deltas into per-cgroup readings.

Important maps and globals: `events` is a perf-event array holding one global event set per CPU. `cgrp_idx` maps cgroup ids to perf evlist cgroup indexes. `prev_readings` stores per-CPU previous event values, and `cgrp_readings` stores per-cgroup/event per-CPU accumulated values. Volatile rodata `num_events`, `num_cpus`, and `use_cgroup_v2` are set by user space; BSS `enabled` gates accumulation.

Control flow: `on_cgrp_switch` and `trigger_read` both call `bperf_cgroup_count()`. That helper finds matching ancestor cgroups for the current task using either cgroup v2 helper ids or cgroup v1 perf_event subsystem ancestry, reads each configured event for the current CPU, computes deltas from `prev_readings`, and adds deltas to every matching cgroup's `cgrp_readings` row only when enabled. Previous readings are always refreshed.

State and persistence: BPF per-CPU maps retain previous and aggregate readings across context switches until the skeleton is destroyed. `perf_subsys_id` is lazily initialized for cgroup v1.

Dependencies and integration: user space sizes maps and populates `events`/`cgrp_idx` in `bpf_counter_cgroup.c`. It relies on CO-RE field handling for old/new cgroup structures and on constants in `bperf_cgroup.h`.

Risks: loops are bounded by `BPERF_CGROUP__MAX_EVENTS` and `BPERF_CGROUP__MAX_LEVELS`; increasing constants may exceed verifier limits. Missing cgroup map entries skip aggregation for that ancestor. Because previous readings refresh even when disabled, enable/disable semantics intentionally avoid counting disabled time but depend on trigger cadence.

Test signals: validate cgroup v1/v2 aggregation, nested cgroup ancestry, multi-event map sizing, enable/disable boundaries, and verifier loading at maximum event constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_cgroup.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_cgroup.h -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_cgroup.h

Purpose: this shared header defines verifier-sensitive constants for cgroup bperf BPF code and user-space sizing.

Important definitions: `BPERF_CGROUP__MAX_LEVELS` caps cgroup ancestor traversal at 10 levels. `BPERF_CGROUP__MAX_EVENTS` caps events per cgroup at 128.

Control flow and state: there is no executable logic. The constants bound BPF loops and user-space maximum test loads.

Dependencies and integration: included by `bperf_cgroup.bpf.c` and `bpf_counter_cgroup.c`; both must agree on these limits.

Risks: changing either value affects verifier code size and runtime coverage. Lowering them can silently exclude deep cgroup ancestors or too many events; raising them can make the BPF program unloadable.

Test signals: run the debug max-event load path and cgroup stat sessions near both configured limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_cgroup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_follower.bpf.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_follower.bpf.c

Purpose: this BPF program is the per-session follower for shared bperf counters. Attached as fexit to the shared leader, it filters each leader delta by global/CPU/PID/TGID scope and accumulates matching deltas into the session's map.

Important maps and globals: `diff_readings` is reused from the leader, `accum_readings` is the per-session per-filter accumulator, and `filter` maps CPU/pid/tgid keys to accumulator indexes plus exit state. BSS globals `type`, `enabled`, and `inherit` control behavior.

Control flow: `fexit_XXX()` exits unless enabled, chooses a filter key from current CPU or pid/tgid, looks up `filter`, optionally deletes exited entries, reads leader delta key 0, and adds it to `accum_readings[accum_key]`. `on_newtask()` inherits PID/TGID filter membership from parent tasks into children. `on_exittask()` marks pid filter entries as exited so the fexit path can delete them after final accounting.

State and persistence: filter rows and accumulated readings live for the session. Mark-then-delete exit state avoids racing final counts. Inherited children share the parent's accumulator key.

Dependencies and integration: `bpf_counter.c` sets attach target to the leader's `on_switch`, reuses the leader diff map fd, sizes accumulators, populates filters, sets globals, and decides whether to attach only fexit or all programs for inheritance.

Risks: global mode bypasses filters and uses accumulator key zero. Non-inherited TGID uses pid as filter key to avoid counting new tasks, which can surprise readers expecting tgid matching. Hash map capacity is fixed at 102400. Correctness depends on fexit seeing leader deltas before user-space reads.

Test signals: run bperf global, CPU, PID, TGID, inherited and non-inherited workloads; fork/exit tasks during measurement; and compare accumulator rows with ordinary perf counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_follower.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_leader.bpf.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_leader.bpf.c

Purpose: this BPF program is the shared bperf leader. It reads one perf-event counter per CPU on scheduler switches or explicit test-run triggers and writes the latest delta into a per-CPU map for followers.

Important maps and programs: `events` is the perf-event array populated by user space with `BPF_F_PRESERVE_ELEMS`; `prev_readings` stores previous per-CPU readings; `diff_readings` stores current deltas. `on_switch` is a raw tracepoint program.

Control flow: on each invocation, `on_switch` uses the current CPU as the perf-event array key, reads the event value, subtracts the previous reading stored at key zero in per-CPU storage, writes counter/enabled/running deltas, and updates the previous reading.

State and persistence: previous and diff readings are per-CPU arrays and persist as long as the leader link exists. The leader program and maps can be shared through a pinned attr map and a bpf_link id held by user-space sessions.

Dependencies and integration: `bpf_counter.c` sizes `events`, attaches this program, stores link and diff-map ids, and opens perf-event fds. `bperf_follower.bpf.c` reuses `diff_readings`.

Risks: only one metric is handled by this skeleton instance; user space creates separate leaders by perf_event_attr. If `bpf_perf_event_read_value()` fails, no delta is produced. Initial deltas depend on zeroed previous readings and enable/follower semantics.

Test signals: verify leader reload, preserved perf-event array entries, per-CPU delta values, and explicit test-run refresh before reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_leader.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_u.h -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_u.h

Purpose: this shared header defines the filter contract between user-space bperf and the follower BPF program.

Important types: `enum bperf_filter_type` enumerates global, CPU, PID, and TGID filtering. `struct bperf_filter_value` stores the accumulator row and an exit marker for filter-map entries.

Control flow and state: there is no executable logic; user space writes `bperf_filter_value` rows into the follower `filter` map, and BPF reads/mutates the `exited` byte.

Dependencies and integration: included by `bpf_counter.c` and `bperf_follower.bpf.c`; enum values are part of the ABI between them.

Risks: changing enum values or struct layout breaks map interpretation. The `exited` flag is only one byte and must remain compatible with BPF C layout assumptions.

Test signals: compile both user-space and BPF sides after layout changes and run PID/TGID exit/inheritance cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_u.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bpf_prog_profiler.bpf.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bpf_prog_profiler.bpf.c

Purpose: this BPF skeleton profiles a target BPF program by attaching fentry/fexit programs and measuring perf-event deltas during the target program's execution.

Important maps and programs: `events` is a perf-event array keyed by CPU; `fentry_readings` stores readings captured at entry; `accum_readings` stores accumulated deltas. `fentry_XXX()` reads the event value at entry, and `fexit_XXX()` reads after return and calls `fexit_update_maps()`.

Control flow: user space retargets both programs to a target BPF function name. Entry reads the current CPU's perf event into per-CPU storage. Exit reads the after value, subtracts the entry value if it looks valid, and atomically accumulates counter/enabled/running deltas.

State and persistence: all readings are per-CPU arrays. `num_cpu` rodata is set by user space but this program uses the current CPU as the event key. Accumulated readings persist until user-space reads/destroys the skeleton.

Dependencies and integration: `bpf_counter.c` opens the target BPF prog fd by id, discovers BTF function name, attaches this skeleton, installs event fds into `events`, and folds `accum_readings` into perf counts.

Risks: target BPF program must have BTF and attachable fentry/fexit points. Nested calls on the same CPU can overwrite `fentry_readings`. The "before counter nonzero" guard can skip valid measurements if a counter legitimately reads zero at entry.

Test signals: profile a known BPF program under load, verify BTF-missing failure, compare event deltas with manual instrumentation, and exercise nested/reentrant target behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bpf_prog_profiler.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/func_latency.bpf.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/func_latency.bpf.c

Purpose: this BPF program records latency between begin/end probes for a function or raw tracepoint pair and stores both a histogram and summary stats.

Important maps and globals: `functime` maps tid to start timestamp; `cpu_filter` and `task_filter` gate collection; `latency` is a per-CPU array histogram. BSS globals hold `enabled`, `total`, `count`, `max`, and `min`; rodata configures filters, nanosecond mode, bucket range, min/max latency fields, and bucket count.

Control flow: begin programs check `enabled` and `can_record()`, then store `bpf_ktime_get_ns()` by current pid/tgid. End programs find the timestamp, call `update_latency()`, and delete the timestamp. `update_latency()` ignores negative deltas, chooses either fixed-range or log2-style bucket indexes, increments the per-CPU bucket, updates aggregate totals, and adjusts min/max.

State and persistence: timestamps persist per current pid/tgid between begin and end events. Histogram rows and aggregate globals persist until skeleton destruction. Nested begin events for the same key overwrite previous timestamps.

Dependencies and integration: user space in `bpf_ftrace.c` attaches kprobe/kretprobe or raw tracepoint programs, sizes maps, populates filters, and reads buckets/stats.

Risks: aggregate `max` and `min` updates are not atomic, so high concurrency can race. Nested or missing end events can distort results. `max_latency` rodata is present but not used in the visible code, which may be intentional future plumbing or a stale option.

Test signals: validate bucket assignment for range and power-of-two modes, CPU/task filters, nsec/usec conversions, nested function calls, and concurrent updates on many CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/func_latency.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/kwork_top.bpf.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/kwork_top.bpf.c

Purpose: this BPF program backs `perf kwork top` by accumulating runtime for scheduler tasks, IRQ handlers, and softirqs in per-CPU work maps.

Important maps and globals: `kwork_top_task_time` is task local storage for scheduler timestamps; `kwork_top_irq_time` stores IRQ/softirq entry timestamps; `kwork_top_tasks` stores pid/cpu task metadata; `kwork_top_works` stores runtime totals; `kwork_top_cpu_filter` gates CPUs. BSS globals include `enabled`, `from_timestamp`, and `to_timestamp`.

Control flow: `on_switch` records runtime for the previous task and timestamp for the next task. IRQ and softirq entry programs store a timestamp keyed by current task and class; exit programs compute delta and call `update_work()`. `update_task_info()` captures tgid, kernel-thread flag, and comm once per pid/cpu.

State and persistence: task-local scheduler timestamps survive across switches. Per-CPU hash maps accumulate runtimes by work key. Missing timestamps fall back to `from_timestamp`, trading continuity for possible overcounting.

Dependencies and integration: user space in `bpf_kwork_top.c` selects which programs autoload, sets CPU filter flags, reads maps, and translates class enum values. The program depends on tp_btf context layout and CO-RE reads of `task_struct`.

Risks: work key includes task pointer for disambiguation, so task lifetime/reuse affects cardinality. Max entries are finite. Runtime updates are not atomic across per-CPU rows but are isolated by per-CPU map semantics. Missing entry timestamps can inflate runtime.

Test signals: run scheduler/IRQ/softirq top modes, CPU-filtered sessions, high interrupt rates, task churn workloads, and verify user-space task metadata matches map rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/kwork_top.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/kwork_trace.bpf.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/kwork_trace.bpf.c

Purpose: this BPF program backs `perf kwork report` by measuring IRQ, softirq, and workqueue runtime or latency using tracepoints.

Important maps and helpers: `perf_kwork_names` stores display names, `perf_kwork_time` stores start timestamps, `perf_kwork_report` stores count/total/max rows, `perf_kwork_cpu_filter` and `perf_kwork_name_filter` gate collection. Helpers `trace_event_match()`, `do_update_time()`, `do_update_timestart()`, `do_update_timeend()`, and `do_update_name()` implement shared filtering and aggregation.

Control flow: runtime programs pair entry/exit events for IRQ, softirq, and workqueue execution. Latency programs pair softirq raise to entry and workqueue activate to execute start. Each begin stores a timestamp, each end deletes it and updates report totals, and names are stored when available from tracepoint data or `%ps` formatting.

State and persistence: BPF maps hold up to `KWORK_COUNT` keys for names, timestamps, and reports. `enabled` gates all updates; rodata flags enable CPU/name filters.

Dependencies and integration: user space controls autoload based on class/report mode and reads reports via matching C structs in `bpf_kwork.c`. The file depends on tracepoint struct definitions in `vmlinux.h` and softirq constants.

Risks: the fixed `KWORK_COUNT` of 100 is small for high-cardinality workqueues. Name filtering is exact string comparison and only applied when a name is known. Missing exit events leave timestamp rows. `bpf_snprintf("%ps")` availability and symbol formatting can vary by kernel.

Test signals: exercise runtime and latency modes for each class, CPU/name filters, workqueue functions with many unique work pointers, and tracepoint loss/missing-pair scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/kwork_trace.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/lock_contention.bpf.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/lock_contention.bpf.c

Purpose: this BPF program records kernel lock contention begin/end events, filters them, optionally captures call stacks and owner stacks, aggregates wait-time stats, identifies special lock classes, and exposes maps for user-space reporting.

Important maps and globals: maps include `stacks`, `stack_buf`, `owner_stacks`, `owner_data`, `owner_stat`, `tstamp`, `tstamp_cpu`, `lock_stat`, `task_data`, `lock_syms`, filter maps, `slab_filter`, `slab_caches`, and `lock_delays`. Ro/BSS globals configure filters, call stacks, owner tracing, cgroup mode, aggregation mode, stack skip/depth, delay injection, NUMA symbol addresses, and error counters.

Control flow: `contention_begin` checks filters, allocates a timestamp slot (per-CPU for spin-like locks, per-task otherwise), stores lock/timestamp/flags, captures waiter stack if requested, records task comms for task aggregation, and tracks owner stack state when owner tracing is enabled. `contention_end` finds the timestamp, computes duration, updates owner stats, builds a key based on caller/task/address/cgroup aggregation, creates or updates `lock_stat`, annotates special address locks, optionally delays, and clears/deletes timestamp state. Test-run programs collect runqueue/zone lock symbols and end timestamps. The slab iterator maps kmem_cache addresses to compact ids.

State and persistence: active contention state lives in `tstamp`/`tstamp_cpu`; aggregate stats in `lock_stat` and `owner_stat`; metadata in `task_data`, `lock_syms`, and `slab_caches`. Error counters persist for user-space diagnostics. `perf_subsys_id` is lazily initialized for cgroup v1.

Dependencies and integration: `bpf_lock_contention.c` sizes maps, populates filters, attaches programs, invokes test-run programs, reads stats, and decodes names. This BPF code depends heavily on CO-RE for mutex/rwsem/mm/rq/zone/cgroup layouts and optional kfuncs `bpf_get_kmem_cache`, `bpf_task_from_pid`, and `bpf_task_release`.

Risks: non-atomic max/min updates can race. Nested locks are intentionally skipped when a timestamp slot is already active. Owner stack tracing has many fallback paths and can lose attribution. `lock_delay` intentionally spins inside BPF and can perturb the system. Special lock identification depends on kernel symbols/layouts and may fail silently.

Test signals: run with callstack on/off, owner on/off, aggregation modes, filters, slab filters, and delay rules; inspect fail counters; validate special names (`mmap_lock`, `siglock`, `rq_lock`, `zone_lock`, slab names); and test kernels with missing optional BPF features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/lock_contention.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/lock_data.h -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/lock_data.h

Purpose: this header defines the shared data layout for lock contention BPF maps and user-space readers.

Important types and constants: `owner_tracing_data`, `tstamp_data`, `contention_key`, `contention_task_data`, `contention_data`, `slab_cache_data`, `enum lock_aggr_mode`, and `enum lock_class_sym` form the map ABI. Constants encode task comm length, max entries, high-bit pseudo-lock flags (`LCD_F_MMAP_LOCK`, `LCD_F_SIGHAND_LOCK`), slab id bit ranges, and type masks.

Control flow and state: there is no executable logic. BPF writes these structures into maps, and user space reads the same layouts to build reports.

Dependencies and integration: included by `lock_contention.bpf.c` and `bpf_lock_contention.c`; enum values must match perf lock-contention aggregation expectations.

Risks: any field reorder, size change, or flag-mask change breaks persisted map interpretation between skeleton and user-space code. The slab id range allows a finite number of cache ids and shares the `flags` field with lock type bits.

Test signals: compile BPF and user space together, run BTF/map layout checks where available, and test all aggregation modes and special-flag name decoding after changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/lock_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/off_cpu.bpf.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/off_cpu.bpf.c

Purpose: this BPF program measures how long user tasks stay off-CPU after scheduler switch-out, keyed by pid/tgid/state/callchain/cgroup, and either aggregates short waits in a map or emits thresholded raw samples directly.

Important maps and globals: `stacks` stores user stack traces; `offcpu_output` is a perf-event array; `offcpu_payload` is per-CPU scratch; task-local `tstamp` stores timestamp/state/stack data; `off_cpu` stores aggregated durations; CPU/task/cgroup filter maps gate collection. Ro/BSS globals configure filters, tgid mode, sched_switch signature, cgroup mode, and threshold.

Control flow: `on_switch` extracts previous and next tasks and previous state from either ctx or task struct, then calls `off_cpu_stat()`. The helper records a timestamp and user stack for eligible previous tasks in interruptible/uninterruptible sleep, then when a next task has a stored timestamp it computes delta, emits direct output if over threshold, otherwise aggregates into `off_cpu`, and clears the timestamp. `on_newtask` expands tgid filters for forked processes when tracking process targets.

State and persistence: task-local storage associates off-CPU start data with task structs. Aggregated map rows persist until user space writes them. Thresholded direct output is emitted immediately to perf ring buffers.

Dependencies and integration: user space in `bpf_off_cpu.c` fills filters, detects `prev_state` ABI, populates `offcpu_output`, and converts map rows to perf samples. The program uses CO-RE for task state/cgroup fields and stack helpers for user callchains.

Risks: kernel threads are skipped because user stacks are unavailable. Stack helper failures can create ambiguous stack ids. The code stores full stack data only when `stack_id > 0`, so stack id zero is treated as not copied. Task-local storage requires kernel support. Direct output and aggregate paths differ based on threshold, so parsers must handle both.

Test signals: test sleeping user workloads, cgroup recording/filtering, pid/tgid filters with forks, threshold zero and nonzero paths, kernels with old/new `task_struct` state field, and stack collection failure cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/off_cpu.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/perf_version.h -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/perf_version.h

Purpose: this header embeds the perf build version string into BPF `.rodata` metadata for tests and tooling.

Important API: `bpf_metadata_perf_version[] SEC(".rodata") = PERF_VERSION` is the only exported object.

Control flow and state: there is no runtime control flow. The build rule defines `PERF_VERSION`, and the value becomes part of the BPF object's read-only data.

Dependencies and integration: included by BPF metadata builds and verified by `tests/shell/record_bpf_metadata.sh`. It includes `vmlinux.h` and BPF helper definitions for section attributes.

Risks: builds that do not define `PERF_VERSION` will fail. Tests depend on section naming and symbol retention.

Test signals: run the BPF metadata shell test and inspect generated BPF object rodata for the version symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/perf_version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/sample-filter.h -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/sample-filter.h

Purpose: this shared header defines the BPF sample-filter bytecode-like ABI used to filter perf samples in kernel context.

Important types and constants: `MAX_FILTERS`, `MAX_IDX_HASH`, and `MAX_EVT_HASH` size filter machinery. `enum perf_bpf_filter_op` defines comparison, bitwise-and, grouping, and done operations. `enum perf_bpf_filter_term` maps supported sample fields and helper-derived UID/GID terms. `struct perf_bpf_filter_entry` holds one operation term/value. `struct idx_hash_key` keys per-event/per-tgid filter selection.

Control flow and state: there is no executable logic; user space fills arrays of entries, and `sample_filter.bpf.c` interprets them sequentially.

Dependencies and integration: included by BPF and user-space code that compile/load sample filters. Term numbering intentionally corresponds to `PERF_SAMPLE_*` bit positions for many sample fields.

Risks: enum value changes break filter interpretation and static assertions in the BPF program. `MAX_FILTERS` bounds expression complexity; unsupported sample terms return zero in the BPF interpreter.

Test signals: compile-time sample-bit assertions, filters using every supported operation/term, grouped OR-like expressions, and event/tgid indexed filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/sample-filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/sample_filter.bpf.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/sample_filter.bpf.c

Purpose: this BPF perf-event program interprets filter entries and decides whether a perf sample should be kept or dropped before user-space delivery.

Important maps and helpers: `filters` stores arrays of `perf_bpf_filter_entry`; `event_hash` maps event instance ids to representative ids; `idx_hash` maps event/tgid to filter index; `dropped` counts rejected samples. `perf_get_sample()` reads requested sample fields from `struct bpf_perf_event_data_kern`; `perf_sample_filter()` is the `SEC("perf_event")` entrypoint.

Control flow: the program casts the perf-event context to kernel context using `bpf_cast_to_kern_ctx`. If `use_idx_hash` is set, it resolves parent event id and current tgid to a filter index; otherwise it uses index zero. It then loops over up to `MAX_FILTERS`, evaluates each operation, supports grouped conditions by recording whether any grouped condition matched, returns 1 on `PBF_OP_DONE` or natural loop completion, and jumps to `drop` on failed non-group conditions.

State and persistence: filter maps are configured by user space and read-only from the program's perspective except for `dropped`, which is atomically incremented. No per-sample state persists.

Dependencies and integration: relies on perf's internal kernel sample structures, CO-RE field existence for `sample_flags` and data-source `mem_hops`, `sample-filter.h` enum layout, and a ksym `bpf_cast_to_kern_ctx`.

Risks: if `sample_flags` is unavailable, sample terms return zero, possibly dropping valid samples. Max/min comparisons are unsigned. Group semantics are simple "any condition in group true" and must match user-space expression generation. Kernel internal structure changes require CO-RE coverage.

Test signals: run filters on IP, TID pid/tid parts, CPU, time, period, weight, data_src parts, cgroup, page sizes, UID/GID, grouped expressions, missing idx_hash rows, and dropped-count accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/sample_filter.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/syscall_summary.bpf.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/syscall_summary.bpf.c

Purpose: this BPF program records syscall latency and error statistics, aggregated by thread, CPU, or cgroup.

Important maps and globals: `syscall_trace_map` maps tid to syscall number and enter timestamp. `syscall_stats_map` maps `struct syscall_key` to `struct syscall_stats`. BSS `enabled` gates collection; rodata `aggr_mode` and `use_cgroup_v2` select aggregation and cgroup id lookup.

Control flow: `sys_enter` stores syscall number and timestamp by tid. `sys_exit` calls `do_exit(ret)`, which looks up the enter record, chooses key fields according to aggregation mode, computes duration, updates stats, and deletes the trace record. `sched_process_exit` also calls `do_exit(0)` to account in-flight syscalls for exiting tasks.

State and persistence: enter records persist only while a syscall is active. Stats persist in a hash map and maintain total time, squared sum, min/max, count, and error count.

Dependencies and integration: includes `syscall_summary.h`; user space must set aggregation rodata and read the stats map. Cgroup v1 lookup uses perf_event cgroup subsystem via CO-RE.

Risks: squared sum can overflow for long durations or high counts. Max/min updates are not atomic. If an enter event is missed, exit is ignored; if exit is missed, process-exit may account with ret zero. Cgroup lookup depends on kernel cgroup layout and perf subsystem id.

Test signals: run syscall summary by thread, CPU, and cgroup; generate failing syscalls; verify min/max/mean/stddev inputs; and test task exit during a blocking syscall.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/syscall_summary.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/syscall_summary.h -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/syscall_summary.h

Purpose: this header defines the map ABI for syscall summary BPF collection.

Important types: `enum syscall_aggr_mode` selects thread, CPU, or cgroup aggregation. `struct syscall_key` combines cgroup id, cpu-or-tid, and syscall number. `struct syscall_stats` stores total time, squared sum, max/min, count, and error count.

Control flow and state: no executable logic. BPF writes `syscall_stats` rows keyed by `syscall_key`; user space reads and formats them.

Dependencies and integration: included by `syscall_summary.bpf.c` and the corresponding user-space summary reader.

Risks: struct layout changes break map compatibility. `cpu_or_tid` has mode-dependent meaning, so user-space readers must use the same aggregation mode used at collection time.

Test signals: map layout compile checks and functional runs for all aggregation modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/syscall_summary.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/vmlinux/vmlinux.h -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/vmlinux/vmlinux.h

Purpose: this hand-maintained minimal `vmlinux.h` supplies non-UAPI kernel types and fields needed by perf's BPF skeletons when building without a generated full vmlinux header.

Important definitions: it defines fixed-width aliases, `timespec64`, cgroup subsystem id, softirq enum, atomic/spinlock/mutex/rwsem/task/cgroup/css structs, tracepoint raw structs for IRQ/softirq/workqueue, `perf_sample_data`, `perf_event`, `bpf_perf_event_data_kern`, `rq`, `kmem_cache`, `bpf_iter__kmem_cache`, `zone`, and `pglist_data`. Most structs use `preserve_access_index` for CO-RE relocation.

Control flow and state: no executable logic. The header is a build-time type contract for BPF C files.

Dependencies and integration: included by nearly all files under `bpf_skel`. It must provide just enough fields for BPF programs while allowing libbpf CO-RE relocation against real kernel BTF.

Risks: missing fields break compilation; incorrect approximations can break CO-RE relocation or verifier behavior. The fake `perf_event_cgrp_id = 8` is relocated when enum preservation is available but remains a fallback otherwise. `pglist_data.node_zones[6]` is a placeholder and user space supplies actual zone size for lock contention.

Test signals: build all skeletons with and without generated vmlinux support; load on kernels with varied struct layouts; and run skeleton-specific CO-RE tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/vmlinux/vmlinux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_trace_augment.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/bpf_trace_augment.c

Purpose: this file is the user-space loader and control surface for `perf trace` raw syscall augmentation BPF.

Important APIs and functions: `augmented_syscalls__prepare()` opens, adjusts autoattach, loads, and attaches the augmented raw syscall skeleton. `augmented_syscalls__create_bpf_output()` adds a `bpf-output` evsel named `__augmented_syscalls__`. `augmented_syscalls__setup_bpf_output()` populates the BPF perf-event array with output fds per CPU. `augmented_syscalls__set_filter_pids()` fills the pid filter map. `augmented_syscalls__get_map_fds()` returns program-array and beauty-map fds. `augmented_syscalls__unaugmented()` and `augmented_syscalls__find_by_title()` expose BPF programs for map population. `augmented_syscalls__cleanup()` destroys the skeleton.

Control flow: prepare disables autoattach for all syscall-specific programs so only root `sys_enter` and `sys_exit` attach directly; those root programs later tail-call into configured maps. Output setup is separated from prepare because perf must first create/open the bpf-output evsel and have per-CPU fds.

State and persistence: static `skel` and `bpf_output` store session state. BPF maps retain tail-call and pid-filter configuration until cleanup.

Dependencies and integration: depends on libbpf skeleton `augmented_raw_syscalls`, perf evlist parsing/opening, CPU fd arrays, and trace augment code that populates tail-call maps and beauty maps.

Risks: `augmented_syscalls__prepare()` returns load errors without destroying an opened skeleton. `augmented_syscalls__setup_bpf_output()` assumes `bpf_output->core.fd` is indexed by CPU id, matching existing perf fd array conventions. Failure to populate program arrays means root programs filter/drop rather than augment many syscalls.

Test signals: run perf trace with syscall augmentation enabled, verify bpf-output map fds per CPU, set pid filters, populate tail calls for known syscalls, and unload/reload repeatedly to detect leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/bpf_trace_augment.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/branch.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/branch.c

Purpose: this file provides branch-stack classification and formatting helpers for perf reports.

Important APIs and functions: `branch_type_count()` updates `struct branch_type_stat` counters from branch flags and source/target addresses. `branch_new_type_name()`, `branch_type_name()`, `get_branch_type()`, and `branch_spec_desc()` translate enum values to strings. `branch_type_stat_display()` prints percentage summaries, and `branch_type_str()` builds a compact parenthesized branch-type descriptor string.

Control flow: counting ignores unknown branch types and zero `from` addresses, handles extended ABI branch types separately, splits conditional branches into forward/backward based on target address, and records whether branches cross 4K or 2M aligned regions. Formatting first computes totals, then emits only nonzero classes.

State and persistence: all state is caller-owned in `struct branch_type_stat`; this file is stateless.

Dependencies and integration: depends on perf branch flag definitions from `linux/perf_event.h`, `branch.h`, and `map_symbol.h`. It integrates with report/stat display paths that consume branch stacks.

Risks: `branch_new_type_name()` has architecture-specific names selected by build host `__aarch64__`, with a TODO noting cross-analysis on another architecture can mislabel recordings. `branch_type_str()` uses caller-provided buffers and accumulates `scnprintf` lengths; truncation must be acceptable. Unknown enum values return null.

Test signals: feed synthetic branch entries for every branch type, extended ABI type, conditional forward/backward, cross-4K/2M transitions, unknown values, and cross-architecture perf data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/branch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/branch.h -->
## sources/distributed-fs/ceph-client/tools/perf/util/branch.h

Purpose: this header defines perf branch-stack data structures and declares branch classification helpers.

Important types: `struct branch_flags` overlays the raw 64-bit branch flags with bitfields for prediction, transaction, cycle count, type, speculation, extended type, privilege, and not-taken state. `struct branch_info` stores resolved map symbols and source lines. `struct branch_entry`/`branch_stack` mirror sampled branch stack records. `struct branch_type_stat` accumulates counts.

Control flow: the inline `perf_sample__branch_entries()` handles the two possible branch stack layouts depending on whether `PERF_SAMPLE_BRANCH_HW_INDEX` is present; it skips `nr` and optionally `hw_idx` before returning entries.

State and persistence: data is embedded in perf samples or caller-owned stats; the header itself owns no state.

Dependencies and integration: includes perf event UAPI, sample definitions, and map-symbol types. Used by branch reporting, scripting, and statistics code.

Risks: bitfield layout assumes the platform/compiler representation matches perf's little-endian UAPI expectations. `perf_sample__branch_entries()` relies on `sample->no_hw_idx` being set correctly by sample parsing.

Test signals: parse samples with and without hardware branch index, validate bitfield decoding against raw flag values, and verify branch stats on recordings with extended ABI types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/branch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/btf.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/btf.c

Purpose: this file provides a small BTF utility for finding a struct member by name.

Important API: `__btf_type__find_member_by_name(struct btf *btf, int type_id, const char *member_name)` returns a pointer to the matching `struct btf_member` or null.

Control flow: it retrieves the BTF type by id, iterates `btf_members(t)` for `btf_vlen(t)` entries, resolves each member name offset with `btf__name_by_offset()`, and compares with `strcmp()`.

State and persistence: stateless; it returns a pointer into libbpf-owned BTF data.

Dependencies and integration: depends on libbpf BTF APIs and is declared in `util/btf.h`. Callers must ensure `type_id` names a type with members.

Risks: there is no null check for `btf__type_by_id()` before calling `btf_members(t)`, so invalid ids or non-aggregate types can crash. Member-name lookup assumes strings are non-null.

Test signals: test valid structs, missing members, invalid type ids, and non-struct type ids; consider adding defensive checks if wider callers are introduced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/btf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/btf.h -->
## sources/distributed-fs/ceph-client/tools/perf/util/btf.h

Purpose: this header declares the BTF member lookup helper implemented in `btf.c`.

Important API: `__btf_type__find_member_by_name()` is declared with forward-declared `struct btf` and `struct btf_member`.

Control flow and state: no executable logic; it keeps users from including heavier BTF details in their headers.

Dependencies and integration: included by perf utilities that need member lookup against loaded BTF data.

Risks: the double-underscore name signals an internal helper; callers should treat returned pointers as borrowed from the BTF object lifetime.

Test signals: compile callers with only the forward declaration and run lookup tests through `btf.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/btf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/build-id.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/build-id.c

Purpose: this file implements perf build-id handling: discovering build ids, writing build-id tables to perf data, maintaining the build-id cache, resolving cached filenames, listing/completing cached ids, and caching DSOs after a session.

Important APIs and functions: discovery/formatting includes `build_id__snprintf()`, `sysfs__snprintf_build_id()`, `filename__snprintf_build_id()`, `build_id__init()`, and `build_id__is_defined()`. Session integration includes `build_id__mark_dso_hit()`, `perf_session__write_buildid_table()`, `perf_session__read_build_ids()`, `perf_session__cache_build_ids()`, and `__perf_session__cache_build_ids()`. Cache APIs include `build_id_cache__linkname()`, `build_id_cache__origname()`, `build_id_cache__kallsyms_path()`, `build_id_cache__list_all()`, `build_id_cache__complement()`, `build_id_cache__cachedir()`, `build_id_cache__list_build_ids()`, `build_id_cache__add()`, `__build_id_cache__add_s()`, `build_id_cache__cached()`, and `build_id_cache__remove_s()`.

Control flow: sample processing marks DSOs as hit from IP and callchain maps. Writing a build-id table walks host and guest machines, skips unhit non-vdso DSOs, selects kernel/user misc flags, and writes padded `PERF_RECORD_HEADER_BUILD_ID` records. Caching creates a source-shaped directory under `buildid_dir`, stores `elf`, `debug`, `kallsyms`, or `vdso` files, updates `.build-id/xx/yyyy` symlinks, scans SDT probes when enabled, and optionally fetches debuginfo through debuginfod. Listing/completion walks `.build-id` two-level directories and can validate ids against current files.

State and persistence: `no_buildid_cache` disables cache writes process-wide. The build-id cache persists on disk under `buildid_dir`, with both source-path directories and `.build-id` symlinks. DSO hit flags and build ids live in perf machine/session state.

Dependencies and integration: depends on DSO, machine, map, symbol, session, namespace, probe cache, debuginfod, filesystem utility, and perf header code. It integrates with recording/reporting to make binaries and debug info available after collection.

Risks: many paths manipulate filesystem names and symlinks; namespace/root-dir handling must be correct for containers and guests. `build_id_cache__valid_id()` only validates absolute regular paths and kallsyms. Debug file detection uses a `.ko` suffix check that assumes name length is at least three. Cache removal follows relative symlink paths and then removes directories, so path correctness matters. Build ids larger than SHA-1 are truncated to `BUILD_ID_SIZE`.

Test signals: read build ids from files and sysfs; write/read session build-id tables for host/guest/vdso/kcore/modules; cache with namespaces, root dirs, stripped binaries with debug files, debuginfod enabled/disabled; list/complete ids; remove cache entries; and run with `disable_buildid_cache()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/build-id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/build-id.h -->
## sources/distributed-fs/ceph-client/tools/perf/util/build-id.h

Purpose: this header declares the build-id data type and cache/session APIs used throughout perf.

Important types and constants: `BUILD_ID_SIZE` is 20 bytes, `BUILD_ID_MIN_SIZE` is 16, and string sizes are hex plus NUL. `struct build_id` stores byte data plus actual size. The header declares DSO filename resolution, hit marking, build-id table read/write/cache operations, cache path/list/add/remove helpers, and the global `buildid_dir`.

Control flow and state: inline `build_id_cache__add_s()` supplies default `proper_name` and `root_dir` arguments to `__build_id_cache__add_s()`. Otherwise this is declarations only.

Dependencies and integration: includes machine/tool types and Linux integer types, and forward declares DSO, feature fd, namespace, and strlist types. It is a central interface for record, report, symbol, and cache tooling.

Risks: API callers must respect ownership of returned strings. `struct build_id` fixed maximum truncates longer future ids unless constants are changed throughout perf.

Test signals: compile all users after signature changes and run build-id cache/session tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/build-id.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cache.h -->
## sources/distributed-fs/ceph-client/tools/perf/util/cache.h

Purpose: this header centralizes small perf utility definitions related to command environment paths, allocation growth, command-line splitting, and formatted path construction.

Important APIs and macros: `CMD_EXEC_PATH`, `CMD_DEBUGFS_DIR`, `EXEC_PATH_ENVIRONMENT`, `PERF_DEBUGFS_ENVIRONMENT`, `PERF_TRACEFS_ENVIRONMENT`, and `PERF_PAGER_ENVIRONMENT` define option/env names. `split_cmdline()` parses command strings. `alloc_nr(x)` computes a growth size. `is_absolute_path()` tests for leading slash. `mkpath()` formats into a provided buffer.

Control flow and state: only `is_absolute_path()` is inline; other functions are implemented elsewhere. No persistent state is owned here.

Dependencies and integration: includes strbuf, pager, UI, compiler attributes, and Linux string helpers. Used broadly by perf utility code.

Risks: `is_absolute_path()` is POSIX-only and treats empty strings as reading `path[0]`, so callers need valid strings. `alloc_nr` can overflow if used with very large sizes.

Test signals: command-line splitting tests, path construction tests, and callers passing empty/null paths through defensive checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cacheline.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/cacheline.c

Purpose: this file determines and caches the system data-cache line size for perf's memory/cacheline analysis helpers.

Important API: `cacheline_size()` returns a cached integer. On systems with `_SC_LEVEL1_DCACHE_LINESIZE`, it uses `sysconf`; otherwise it reads `devices/system/cpu/cpu0/cache/index0/coherency_line_size` from sysfs and logs debug failure.

Control flow: the first call initializes a static `size`; subsequent calls return the cached value.

State and persistence: static process-local `size` persists for the program lifetime. No filesystem writes occur.

Dependencies and integration: used by `cacheline.h` inline address/offset helpers and memory analysis code. Depends on unistd/sysconf or perf sysfs helpers.

Risks: if discovery fails, `size` can remain zero, and callers doing bit operations with `size - 1` would behave incorrectly. Systems with heterogeneous cacheline sizes are represented by one value from CPU0/sysconf.

Test signals: run on platforms with and without `_SC_LEVEL1_DCACHE_LINESIZE`, mock sysfs read failure, and verify consumers handle zero or add fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cacheline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cacheline.h -->
## sources/distributed-fs/ceph-client/tools/perf/util/cacheline.h

Purpose: this header declares cacheline-size discovery and provides helpers to normalize addresses to cacheline boundaries.

Important APIs: `cacheline_size()` returns the system size. `cl_address(address, double_cl)` returns the base address of the containing cacheline or adjacent-prefetch doubled line. `cl_offset(address, double_cl)` returns the offset within that line.

Control flow and state: helpers call `cacheline_size()`, optionally double it, then mask the address. State is held by `cacheline_size()` implementation.

Dependencies and integration: used by perf c2c/memory reporting code to bucket addresses. Includes Linux compiler attributes.

Risks: helpers assume `cacheline_size()` returns a power-of-two positive value. A zero or non-power-of-two size produces invalid masks. `double_cl` models adjacent cacheline prefetch but may not match every architecture.

Test signals: unit-test address/offset outputs for 64-byte and doubled 128-byte lines, and behavior when discovery fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/cacheline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/call-path.c -->
## sources/distributed-fs/ceph-client/tools/perf/util/call-path.c

Purpose: this file implements an arena-backed tree of context-sensitive call paths for perf call-return/db-export style analysis.

Important APIs and functions: `call_path_root__new()` allocates and initializes a root. `call_path_root__free()` releases all arena blocks. `call_path__findnew()` finds or creates a child path under a parent keyed by symbol pointer or raw ip. Internal `call_path__new()` allocates nodes from fixed-size blocks, and `call_path__init()` initializes node fields.

Control flow: root allocation initializes an empty root call path and block list. New nodes are allocated from the last block until full, then a new block of `CALL_PATH_BLOCK_SIZE` nodes is appended. For non-root parents, `call_path__findnew()` searches the parent's red-black tree by `(sym, ip)` and inserts a new node if absent. If `sym` is non-null, `ip` is normalized to zero; `in_kernel` is computed by comparing ip to the kernel-start threshold.

State and persistence: all nodes live in blocks attached to `call_path_root`. Individual nodes are not freed; the whole root is freed at once. Each node owns its child RB tree.

Dependencies and integration: depends on Linux rbtree/list utilities and perf symbol pointers. Used where perf needs stable call path ids and parent-child context.

Risks: ordering by raw `struct symbol *` pointer is process-local and not persistent across runs; this is fine for in-memory lookup but not serialization. Allocation failure returns null and callers must handle it. `call_path__findnew()` with null parent always creates a new node instead of deduplicating root-like paths.

Test signals: create repeated paths with same symbol/ip and parent, different parents, null symbols, kernel/user thresholds, block-boundary allocations, and allocation failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/call-path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/call-path.h -->
## sources/distributed-fs/ceph-client/tools/perf/util/call-path.h

Purpose: this header defines the call-path tree data structures and public allocation/lookup API.

Important types and constants: `struct call_path` stores parent, symbol or ip, db-export id, kernel flag, RB node, and child tree. `CALL_PATH_BLOCK_SHIFT`, `CALL_PATH_BLOCK_SIZE`, and `CALL_PATH_BLOCK_MASK` define arena block size. `struct call_path_block` contains a block of nodes and list link. `struct call_path_root` contains the root path, block list, next index, and capacity.

Control flow and state: declarations expose `call_path_root__new()`, `call_path_root__free()`, and `call_path__findnew()`. State is root-owned and freed in bulk.

Dependencies and integration: includes Linux types and rbtree definitions; forward use of `struct symbol` is implicit through pointers. Used by call-return and export code that tracks context-sensitive call graphs.

Risks: callers must not free individual call paths or use nodes after root free. `db_id` is mutable caller/export state and initialized to zero.

Test signals: compile all call-path users, build and free deep trees, and verify exported db ids remain attached to stable nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/call-path.h -->
