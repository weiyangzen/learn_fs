# Research: subset-b-006601

Grouped research for perf x86 utility and perf bench files. Each section is source-tree-aligned and bracketed for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/intel-bts.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/intel-bts.c

Purpose: implements perf record-side Intel Branch Trace Store AUX trace setup for the `intel_bts` PMU. It creates an `auxtrace_record` provider, configures record options, fills `PERF_RECORD_AUXTRACE_INFO`, and handles snapshot-mode head/old adjustment for BTS circular buffers.

Important APIs/types/functions: `struct intel_bts_recording` wraps `struct auxtrace_record` with PMU, evlist, snapshot mode, and per-mmap snapshot reference state. `intel_bts_recording_init()` is the exported initializer. `intel_bts_recording_options()` validates user options, finds the single BTS evsel, sets `needs_auxtrace_mmap`, defaults mmap sizes, and injects a dummy tracking event. `intel_bts_info_fill()` writes BTS PMU type and TSC conversion fields. `intel_bts_find_snapshot()` reconciles circular AUX buffer wrap semantics. `intel_bts_reference()` returns `rdtsc()` for JIT dump timestamp alignment.

Control flow: initialization finds `INTEL_BTS_PMU_NAME`, sets `JITDUMP_USE_ARCH_TIMESTAMP`, allocates the recorder, and installs callback pointers. During record setup, the BTS event is moved to the evlist front so its fd can back AUX mmaps; full tracing enables dummy tracking, and snapshot mode disables/enables the BTS evsel around snapshots. Snapshot finalization detects first wrap by scanning the tail of the buffer and then normalizes `old`/`head` to the full-trace monotonic model.

State and persistence: state is in process memory only: `snapshot_refs` grows by powers of two and stores per-mmap wrap booleans plus optional ref buffers. The output persisted to perf.data is the auxtrace info private array, including PMU type, TSC conversion, and snapshot flag. No standalone files are written by this file.

Dependencies and integration: depends on perf util evlist/evsel/session/mmap/record/auxtrace APIs, PMU discovery, `perf_read_tsc_conversion()`, `parse_event("dummy:u")`, page size, and x86 `rdtsc()`. It integrates with perf record's generic auxtrace lifecycle through the callback table returned as `struct auxtrace_record *`.

Risks: option validation is strict: more than one BTS event, per-CPU recording, sample mode, non-power-of-two AUX sizes, or snapshot size larger than AUX mmap all fail. Snapshot wrap detection is heuristic before explicit wrap has been observed, so small or all-zero buffers can be ambiguous. Allocation growth must be checked because snapshot callback failures abort recording.

Test signals: build with Intel BTS support, `perf record -e intel_bts// ...`, snapshot mode `perf record -S -e intel_bts// ...`, nonprivileged defaults, invalid AUX mmap sizes, duplicate BTS events, and perf.data decode checks for `PERF_AUXTRACE_INTEL_BTS` metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/intel-bts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/intel-pt.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/intel-pt.c

Purpose: implements record-side Intel Processor Trace support for perf. It selects sane PT default config, validates PT-specific config terms against sysfs caps, configures AUX trace collection modes, emits decoder metadata, and manages snapshot buffers.

Important APIs/types/functions: `struct intel_pt_recording` owns the auxtrace callback object and PT runtime state. `intel_pt_pmu_default_config()` caches generated default PMU config from `caps/*` and `format/*`. `intel_pt_recording_init()` returns the auxtrace provider. `intel_pt_recording_options()` is the main policy function for full trace, snapshot, and AUX sample modes. `intel_pt_info_priv_size()` and `intel_pt_info_fill()` size and populate `PERF_AUXTRACE_INTEL_PT` private metadata. Helpers include `intel_pt_validate_config()`, `intel_pt_val_config_term()`, `intel_pt_psb_period()`, `intel_pt_min_max_sample_sz()`, and snapshot comparison/copy helpers.

Control flow: init discovers `intel_pt`, reads `intel-pt.all-switch-events` config, and registers callbacks. Default config builds a term string such as `tsc,mtc,...,pt,branch` based on hardware caps and parses it through PMU term handling. Record option processing finds the sole PT evsel, sets fixed period sampling, excludes guest PT when KVM passthrough mode requires it, validates config, chooses AUX mmap sizes, warns when snapshot/sample sizes may not include a PSB, configures aux watermarks, adds switch/text-poke sideband where possible, moves PT to the evlist front, and adds an aux dummy tracking event. Info fill extracts TSC conversion, CPUID leaf 0x15 ratio, max non-turbo ratio, event-trace cap, filter string, and selected config-bit meanings for decoders.

State and persistence: persistent output is the auxtrace info record containing PMU type, timing conversion, PT config bit locations, sched-switch mode, per-CPU mmap flag, filter string, and event-trace support. Runtime-only state includes cached default config, snapshot ref buffers, snapshot wrap flags, and `have_sched_switch` mode. The file sets `JITDUMP_USE_ARCH_TIMESTAMP=1` so JIT dump timestamps align with TSC.

Dependencies and integration: depends on perf PMU/sysfs scanning, parse-events terms, evlist/evsel configuration, record target logic, perf API probes for switch/text-poke events, libtraceevent for fallback sched switch tracing, x86 CPUID, TSC conversion, and generic auxtrace read finish. It integrates with Intel PT decoding through metadata contracts in `util/intel-pt.h`.

Risks: PT has many hardware-dependent branches. Invalid caps, missing sysfs files, unsupported config values, too-small AUX sample buffers, multiple aux-output events, clockid use, or combining snapshot/sample modes are rejected or warned. Per-CPU tracing without switch sideband can make userspace decode impossible. Snapshot wrap detection relies either on reference-buffer comparison or tail non-zero probing, depending on snapshot size.

Test signals: run `perf record -e intel_pt//`, snapshot `-S`, AUX sample mode, event filters, per-CPU tracing with and without sched switch permissions, invalid `mtc_period`/`psb_period`/`cyc_thresh` terms, `intel-pt.all-switch-events` config, and decode-side validation that perf.data contains complete PT auxtrace metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/intel-pt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/iostat.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/iostat.c

Purpose: implements x86 perf stat `--iostat` support for Intel uncore IIO root-port bandwidth metrics. It discovers root ports from sysfs, optionally filters them, generates uncore event groups, and formats metric rows by root port.

Important APIs/types/functions: `struct iio_root_port` stores PCI domain, bus, die, PMU index, and list index. `struct iio_root_ports_list` owns discovered ports. `iostat_parse()` scans and filters root ports and sets `config->iostat_run`. `iostat_prepare()` replaces unsupported user events with generated IIO event groups. `iostat_print_metric()` converts raw event counts into MB-like values. `iostat_print_counters()`, `iostat_prefix()`, `iostat_list()`, and `iostat_release()` handle output and cleanup.

Control flow: `iio_pmu_count()` counts `uncore_iio_N` PMUs. `iio_mapping()` reads per-die mapping files such as `uncore_iio_%d/die%d` and builds root-port objects. Optional filter parsing accepts comma-separated `domain:bus` tokens. `iostat_event_group()` builds four events per root port for inbound/outbound read/write, parses them into the evlist, and attaches root-port pointers to each evsel. Printing walks selected counters, emits a new prefix when the root port changes, and scales counts by enabled/running ratio.

State and persistence: global `root_ports` is built during option parsing and consumed by prepare. Ownership transfers to evsel `priv` pointers; `iostat_release()` frees unique root-port objects. No persistent files are written; state comes from live sysfs and perf counter values.

Dependencies and integration: depends on perf stat config/output APIs, sysfs mountpoint and `sysfs__read_str()`, parse-events, evlist/evsel, perf counts, CPU/node topology, regex parsing, and Intel uncore IIO PMU naming. It integrates as an x86-specific perf stat mode.

Risks: this is platform-specific and fails on missing/changed IIO sysfs layout. `iostat_prepare()` assigns a new local evlist after `evlist__delete()` without returning it, so callers must already match this expected perf stat flow. Filtering transfers pointers by nulling old list entries; release logic depends on grouped evsel order and unique pointer changes. JSON prefix formatting is explicitly marked incorrect.

Test signals: `perf stat --iostat=list`, filtered `--iostat=0000:3d`, unsupported systems, interval/csv output, repeated runs under leak checking, and validation that four events per root port appear with expected metric labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/iostat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/machine.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/machine.c

Purpose: adds x86_64-specific extra kernel maps for entry trampoline symbols so perf can resolve trampoline addresses that live outside normal kernel text mappings.

Important APIs/types/functions: `struct extra_kernel_map_info` accumulates candidate maps and `_entry_trampoline`. `add_extra_kernel_map()` grows the map array. `find_extra_kernel_maps()` is a kallsyms parser callback that records `_entry_trampoline` and `is_entry_trampoline()` symbols. `machine__create_extra_kernel_maps()` is the integration entry point.

Control flow: the machine chooses a kallsyms filename, skips restricted `/proc/kallsyms`, parses symbols, requires `_entry_trampoline`, patches every collected trampoline map's `pgoff` to the entry trampoline base, and calls `machine__create_extra_kernel_map()` for each.

State and persistence: temporary symbol-derived map data is heap-allocated and freed before return. The durable effect is mutation of the perf `machine` object: extra maps are installed and `machine->trampolines_mapped` records the count.

Dependencies and integration: compiled only for `__x86_64__`. Depends on perf machine/map/symbol APIs, kallsyms parser, ELF binding translation, page size, and `is_entry_trampoline()`.

Risks: if kallsyms is restricted or `_entry_trampoline` is absent, the function silently does nothing. Map end is assumed to be one page after symbol start. Allocation or map creation failure aborts the pass.

Test signals: symbol resolution tests on x86_64 kernels with KPTI trampolines, restricted kallsyms behavior, and perf report annotation of entry trampoline samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/machine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/mem-events.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/mem-events.c

Purpose: defines x86 architecture-specific perf memory event templates for Intel and AMD PMUs.

Important APIs/types/functions: exports four `struct perf_mem_event` arrays: `perf_mem_events_intel`, `perf_mem_events_intel_aux`, `perf_mem_events_amd`, and `perf_mem_events_amd_ldlat`. Macro `E()` fills tag, printable name template, event name, load-latency support, and auxiliary event config. `MEM_LOADS_AUX` identifies Intel's auxiliary mem-loads event.

Control flow: there is no runtime control flow. The arrays are selected by `perf_pmu__arch_init()` in `pmu.c` depending on CPU vendor, PMU kind, and caps.

State and persistence: static global arrays define immutable event templates used in process memory. No persistence or dynamic allocation occurs.

Dependencies and integration: depends on `util/mem-events.h` for `struct perf_mem_event` and `PERF_MEM_EVENTS__MAX`. The local `mem-events.h` header exposes the arrays to x86 PMU initialization.

Risks: template strings are parse-events contracts; drift from PMU event names such as `mem-loads-aux`, `mem-loads`, `mem-stores`, or AMD `ibs_op` syntax breaks `perf mem`. Array order must match the generic `PERF_MEM_EVENTS__MAX` enum.

Test signals: `perf mem record` and `perf mem report` on Intel and AMD, Intel systems with and without `mem-loads-aux`, AMD IBS ldlat-capable PMUs, and parse-events validation of every template.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/mem-events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/mem-events.h -->
# Research: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/mem-events.h

Purpose: declares x86 memory event template arrays for PMU initialization.

Important APIs/types/functions: exports `perf_mem_events_intel`, `perf_mem_events_intel_aux`, `perf_mem_events_amd`, and `perf_mem_events_amd_ldlat`, all sized by `PERF_MEM_EVENTS__MAX`.

Control flow: header-only declarations guarded by `_X86_MEM_EVENTS_H`.

State and persistence: no state; provides external linkage contracts for arrays defined in `mem-events.c`.

Dependencies and integration: requires `struct perf_mem_event` and `PERF_MEM_EVENTS__MAX` to be visible through includers. Used by x86 `pmu.c`.

Risks: declarations must stay in sync with definitions; missing includes in a translation unit could make this header fragile.

Test signals: compile x86 perf with memory event support and verify `pmu.c` links against all four arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/mem-events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/pmu.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/pmu.c

Purpose: performs x86-specific PMU initialization. It marks Intel PT/BTS PMUs as AUX trace capable, attaches x86 memory event template tables, and adjusts Granite Rapids uncore CHA/IMC CPU masks for sub-NUMA clustering.

Important APIs/types/functions: `perf_pmu__arch_init()` is the exported hook. `x86__is_intel_graniterapids()` caches CPUID matching. `snc_nodes_per_l3_cache()`, `num_chas()`, `uncore_cha_snc()`, `uncore_imc_snc()`, and `uncore_cha_imc_compute_cpu_adjust()` derive SNC mapping. `gnr_uncore_cha_imc_adjust_cpumask_for_snc()` rewrites PMU cpumaps. `read_sysfs_cpu_map()` parses sysfs CPU lists.

Control flow: arch init first recognizes `intel_pt` and `intel_bts`. On AMD, it only handles `ibs_op`, selecting basic or ldlat-capable memory events after cap parsing. On non-AMD Intel, core PMUs receive Intel memory events, with `mem-loads-aux` preferred if available. For Granite Rapids uncore CHA/IMC PMUs, cpumasks are adjusted from socket-level first CPUs to SNC-node first CPUs.

State and persistence: caches CPUID result, SNC counts, CHA count, per-SNC CPU adjustments, and adjusted cpumaps in static variables. The persistent runtime effect is mutation of `struct perf_pmu` fields: `auxtrace`, `selectable`, default attr init callback, `mem_events`, and `cpus`.

Dependencies and integration: depends on PMU/sysfs APIs, internal cpumap refcounted maps, CPUID helper, x86 vendor detection, Intel PT/BTS names, memory event arrays, and sysfs topology paths for NUMA nodes and L3 cache sharing.

Risks: Granite Rapids SNC logic assumes naming/order of `uncore_cha_N` and lookup tables for IMC SNC2/SNC3 only. `snc_nodes_per_l3_cache()` divides map sizes and assumes both sysfs reads succeed. CPU adjust path has assertions and bounds assumptions. Static adjusted cpumaps are retained for process lifetime.

Test signals: perf list/record for Intel PT/BTS, `perf mem` on Intel and AMD IBS, Granite Rapids per-node uncore stat output under SNC2/SNC3, and sysfs-failure tests for missing node/cache paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/topdown.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/topdown.c

Purpose: implements x86 support for Intel topdown metric events and synthesized slots insertion.

Important APIs/types/functions: `topdown_sys_has_perf_metrics()` detects core PMU support for `slots`. `arch_is_topdown_slots()` recognizes the raw slots encoding. `arch_is_topdown_metrics()` recognizes PMU type `PERF_TYPE_RAW` with `PERF_SAMPLE_READ` sampling. `arch_topdown_sample_read()` sets grouped read format for sampled metric leaders. `topdown_insert_slots_event()` creates and inserts the `slots` event before a metric event.

Control flow: capability detection is cached after the first raw PMU lookup. Slots recognition compares event type and config to `TOPDOWN_SLOTS`. Inserting slots allocates an evsel from the string `"slots"`, assigns index, inserts before the metric event, and increments the metric event index to preserve ordering.

State and persistence: two static booleans cache feature detection. The evlist is mutated by inserting an evsel. No files are written.

Dependencies and integration: depends on perf PMU discovery, evlist/evsel list management, parse-events through `evsel__newtp_idx("slots", idx)`, and generic topdown interfaces in `util/topdown.h`.

Risks: assumes raw PMU type represents the core PMU and `slots` event availability implies perf metrics. Failure to allocate/parse slots returns `-ENOMEM`. Index mutation must match caller expectations for metric grouping.

Test signals: `perf stat` topdown metrics on Intel systems, missing `slots` event behavior, sampled topdown metrics requiring `PERF_FORMAT_GROUP`, and event list ordering tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/topdown.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/topdown.h -->
# Research: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/topdown.h

Purpose: provides the x86 topdown helper prototype needed by generic perf topdown/stat code.

Important APIs/types/functions: declares `topdown_sys_has_perf_metrics()`.

Control flow: no runtime control flow; guarded by `_X86_TOPDOWN_H`.

State and persistence: no state.

Dependencies and integration: paired with `topdown.c` and generic `util/topdown.h` consumers.

Risks: minimal; declaration must match implementation signature.

Test signals: x86 perf build and link of topdown code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/topdown.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/tsc.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/tsc.c

Purpose: provides x86 TSC reading and frequency discovery for perf utilities.

Important APIs/types/functions: `rdtsc()` emits the `rdtsc` instruction and returns a 64-bit cycle value. `arch_get_tsc_freq()` is the exported frequency helper. `cpuinfo_tsc_freq()` parses `/proc/cpuinfo` for `cpu MHz`.

Control flow: `arch_get_tsc_freq()` first uses CPUID leaf 0x15 denominator/numerator/crystal frequency to compute TSC frequency. If unavailable or incomplete, it falls back to `/proc/cpuinfo`, parsing MHz into kHz/Hz scale. It returns zero on failure.

State and persistence: no cached state and no persistent writes. Reads CPUID and `/proc/cpuinfo` at call time.

Dependencies and integration: depends on x86 inline asm, `cpuid()` helper, libc stdio/string parsing, and perf's `u64` type. Used by AUX trace timestamp/reference paths and other perf timing code.

Risks: CPUID 0x15 is not universally populated. `/proc/cpuinfo` parsing is locale/string-format sensitive and uses integer/fraction handling limited by the expected `cpu MHz` line. Virtualized systems may expose unstable or synthetic values.

Test signals: unit or manual checks on systems with CPUID 0x15, systems requiring cpuinfo fallback, and comparison against kernel-reported TSC conversion in AUX trace metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/tsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/unwind-libunwind.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/unwind-libunwind.c

Purpose: maps perf DWARF register numbers to libunwind register identifiers for x86 and x86_64.

Important APIs/types/functions: exports `LIBUNWIND__ARCH_REG_ID(int regnum)` with architecture-specific implementations. x86_64 maps DWARF registers 0-16 plus RIP to `UNW_X86_64_*`; i386 maps common general registers and EIP to `UNW_X86_*`.

Control flow: switch statements translate known register numbers and return `-EINVAL` for unsupported registers.

State and persistence: no state.

Dependencies and integration: depends on libunwind architecture constants and perf unwind glue macro naming. Used by perf callchain/unwind code when libunwind is enabled.

Risks: register maps must match the DWARF ABI and libunwind constants. Unsupported SIMD/FPU/system registers return errors; callers must tolerate missing registers.

Test signals: build with libunwind on 32-bit and 64-bit x86, unwind user stacks from samples, and validate instruction pointer/register recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/unwind-libunwind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/xtensa/include/dwarf-regs-table.h -->
# Research: sources/distributed-fs/ceph-client/tools/perf/arch/xtensa/include/dwarf-regs-table.h

Purpose: supplies the Xtensa perf DWARF register name table.

Important APIs/types/functions: defines `REG_DWARFNUM_NAME(r, num)` entries for `a0` through `a15` mapped to DWARF register numbers 0 through 15.

Control flow: header data only; consumed by generic register table generation logic.

State and persistence: no runtime state.

Dependencies and integration: depends on the includer defining `REG_DWARFNUM_NAME`. Integrated into perf's architecture-specific DWARF register lookup.

Risks: minimal but ABI-sensitive; missing special registers means only the listed general address registers are named.

Test signals: Xtensa perf build and `perf probe`/DWARF register name lookup tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/xtensa/include/dwarf-regs-table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/bench.h -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/bench.h

Purpose: central declaration header for `perf bench` benchmark entry points, shared timing globals, output formats, and portability shims.

Important APIs/types/functions: declares `bench__start`, `bench__end`, `bench__runtime`, all `bench_*` command functions, `bench_format`, `bench_repeat`, and format constants. It also defines missing `MADV_HUGEPAGE`/`MADV_NOHUGEPAGE` constants and a no-op `pthread_attr_setaffinity_np()` fallback when unavailable.

Control flow: no runtime control flow; provides compile-time declarations and compatibility definitions.

State and persistence: declares external process-global benchmark state owned elsewhere.

Dependencies and integration: included by almost every perf bench implementation and by bench command dispatch code.

Risks: function declarations must remain synchronized with implemented benchmarks and command tables. The affinity fallback silently disables requested affinity on platforms without `pthread_attr_setaffinity_np`.

Test signals: full perf bench build across libc/platform variants and command dispatch for every declared benchmark.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/bench.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/breakpoint.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/breakpoint.c

Purpose: benchmarks hardware breakpoint overhead in two scenarios: inheritable breakpoint impact on thread create/join, and repeated breakpoint disable/enable while passive or active threads exist.

Important APIs/types/functions: `breakpoint_setup()` opens a `PERF_TYPE_BREAKPOINT` event with RW one-byte watchpoint attributes. `bench_breakpoint_thread()` creates `nbreakpoints`, then `nparallel` workers repeatedly create/join `nthreads` passive futex waiters. `bench_breakpoint_enable()` creates one breakpoint, starts passive futex waiters and active spinners, then loops `PERF_EVENT_IOC_DISABLE/ENABLE`.

Control flow: options are parsed with subcmd parse-options. Missing hardware breakpoint support (`-ENODEV`) skips cleanly. Timing uses `gettimeofday()` and `timersub()`. Passive threads block on futex until a shared atomic `done`; active threads spin until `done`.

State and persistence: benchmark state is process-local static option structs and allocated arrays of threads/breakpoints. No files persist. The kernel perf_event breakpoint fd is opened and closed per run.

Dependencies and integration: depends on `perf_event_open`, Linux hardware breakpoint ABI, futex helpers, pthreads, ioctl perf event enable/disable, and global bench output format.

Risks: `repeat` is shared by parallel workers with relaxed atomic fetch-sub and may overshoot semantics under unusual values. Hardware watchpoint availability and permissions vary. Active spinner mode can burn CPU and skew system-wide measurements.

Test signals: run both breakpoint subcommands with default/simple formats, no-breakpoint hardware path, multiple breakpoints, passive/active mix, and perf_event permission failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/breakpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/epoll-ctl.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/epoll-ctl.c

Purpose: benchmarks concurrent `epoll_ctl(2)` ADD/MOD/DEL operations against one shared epoll instance, optionally with nested epoll and randomized operations.

Important APIs/types/functions: `bench_epoll_ctl()` is the entry point. `do_threads()` creates workers, eventfds, optional CPU affinity, and initial random-mode fd registration. `workerfn()` performs deterministic or random `epoll_ctl` loops. `nest_epollfd()` builds nested epoll chains. `print_summary()` reports average operation counts with stats.

Control flow: only compiled under `HAVE_EVENTFD_SUPPORT`. The entry point parses options, installs SIGINT handler, creates the shared epoll fd, raises `RLIMIT_NOFILE`, starts workers behind a mutex/cond barrier, sleeps for runtime seconds, toggles `done`, joins workers, aggregates per-op stats, and frees fd maps.

State and persistence: static process globals track options, `done`, shared epoll fd, nesting fds, startup barrier state, and stats. No persistent files. File descriptors and worker arrays are runtime resources.

Dependencies and integration: depends on eventfd, epoll, pthreads, perf CPU map affinity, perf mutex/cond wrappers, stat helpers, and bench timing globals.

Risks: shared `done` is a plain bool written from a signal handler and read by threads. Nested epoll allocation has limited cleanup. Resource-limit changes affect the process. Random mode intentionally permits failed operations and counts only successes, so interpretation differs from deterministic mode.

Test signals: build with/without eventfd support, default CPU-count threads, `--randomize`, `--nested`, `--noaffinity`, high `--nfds`, SIGINT early stop, and leak/fd exhaustion checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/epoll-ctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/epoll-wait.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/epoll-wait.c

Purpose: benchmarks `epoll_wait(2)` throughput with eventfd producers under single shared queue or one-queue-per-worker models, with optional edge-triggered, one-shot, nonblocking, nested, and randomized behavior.

Important APIs/types/functions: `bench_epoll_wait()` orchestrates the run. `do_threads()` creates worker epoll registrations and optional CPU affinity. `workerfn()` performs one-event `epoll_wait`, reads eventfd data, and re-adds or rearms for EPOLLET/EPOLLONESHOT. `writerfn()` continuously writes to workers' fd maps. `shuffle()` supports random order. `print_summary()` aggregates throughput.

Control flow: under `HAVE_EVENTFD_SUPPORT`, setup parses options, configures SIGINT, creates epoll fd(s), defaults workers to online CPUs minus one, raises `RLIMIT_NOFILE`, starts workers behind a barrier, starts a writer thread, sleeps runtime seconds, toggles `done`, stops writer after a delay, joins, sorts randomized workers for output, and reports ops/sec.

State and persistence: process-global booleans configure mode and termination; per-worker state holds epoll fd, eventfds, thread id, and op count. No persistent files. Runtime uses many fds and threads.

Dependencies and integration: depends on eventfd/epoll/pthreads, perf cpumap, mutex/cond wrappers, stats, signal handling, and bench globals.

Risks: plain bool termination flags are shared with signal/thread contexts. Nonblocking mode can count iterations with no event if `epoll_wait` returns zero and `ev` is stale; default mode avoids that. Writer pressure and eventfd saturation can skew results. Nested epoll arrays are global even in multiq mode.

Test signals: single vs multiq, edge-triggered and one-shot rearm paths, nonblocking mode, nested epolls, random writer order, large fd counts, and build without eventfd support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/epoll-wait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/evlist-open-close.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/evlist-open-close.c

Purpose: benchmarks perf evlist creation, opening, mmaping, enabling/disabling, unmapping, and closing for a configurable event expression and target.

Important APIs/types/functions: `bench_evlist_open_close()` parses options. `bench__repeat_event_string()` clones event selectors. `bench__create_evlist()` parses events, applies UID filtering, creates maps, and configures evlist. `bench__do_evlist_open_close()` exercises open/mmap/enable/disable/munmap/close. `bench_evlist_open_close__run()` runs iterations and reports average/stddev.

Control flow: parse target/event options, validate target, enable missing-thread tolerance for pid targets, expand event string, print event/cpu/thread/fd counts from a first evlist, then create and destroy a new evlist for each timed iteration.

State and persistence: static `record_opts` mirrors perf record defaults used for evlist config. Runtime evlists are allocated per iteration and deleted. No files persist.

Dependencies and integration: depends on parse-events, evlist/evsel APIs, record options, target validation, UID parsing, perf cpumap/threadmap, mmap handling, stats, and debug/error utilities.

Risks: failures after `evlist__mmap()` in `bench__do_evlist_open_close()` return without local cleanup, relying on caller deletion. Event repetition can build large selector strings. Results are sensitive to permissions, target lifetimes, and CPU/thread map size.

Test signals: dummy event defaults, repeated events, system-wide and CPU-list modes, pid/tid/uid/per-thread targets, invalid event strings, and low permission `perf_event_open` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/evlist-open-close.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/find-bit-bench.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/find-bit-bench.c

Purpose: benchmarks bitmap set-bit iteration against direct `test_bit` probing for several bitmap sizes.

Important APIs/types/functions: `bench_mem_find_bit()` is the entry point. `do_for_each_set_bit()` allocates a bitmap, sets bits with varying sparsity, times `for_each_set_bit` and direct test-bit loops, and reports stats. `asm_test_bit()` uses x86 `bt` when available, otherwise falls back to `test_bit`. `workload()` prevents optimization of found values.

Control flow: parses outer/inner iteration counts, then for each bitmap size and sparsity pattern repeatedly times both approaches with `gettimeofday()`, updating stats and printing averages/stddevs.

State and persistence: static counters `accumulator` and `use_of_val` create observable side effects. Bitmaps are heap-allocated per test and freed. No persistence.

Dependencies and integration: depends on Linux bitmap/bitops helpers, perf stats, parse-options, bench format, and optional x86 inline asm.

Risks: microbenchmark results depend heavily on compiler optimization, CPU branch prediction, bit density, and timer granularity. The x86 asm path differs from generic `test_bit`, so cross-arch comparisons are not apples-to-apples.

Test signals: run with varied `-i/-j`, check bitmap sizes and sparse/dense cases, compare x86 and non-x86 builds, and ensure no optimizer removes workload side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/find-bit-bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/futex-hash.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/futex-hash.c

Purpose: stresses Linux futex user-address hashing by issuing many failing `FUTEX_WAIT` calls across per-thread futex arrays.

Important APIs/types/functions: `bench_futex_hash()` is the entry point. `workerfn()` loops over `params.nfutexes` and calls `futex_wait()` with an unmatched expected value. `toggle_done()` stops workers and records runtime. `print_summary()` reports average ops/sec and futex hash bucket setting.

Control flow: options configure buckets, threads, runtime, futexes per thread, shared/private mode, silent mode, and `mlockall`. The benchmark defaults threads to online CPUs, pins each worker, starts them behind a condition barrier, sleeps for runtime seconds, toggles `done`, joins, aggregates per-thread throughput, and frees futex arrays.

State and persistence: global bench timing variables are defined here. Static `params`, `done`, `futex_flag`, startup barrier state, and stats hold runtime state. No files persist.

Dependencies and integration: depends on futex wrappers, perf CPU maps, pthread affinity, mutex/cond wrappers, stats, `mlockall`, and futex bucket sysctl helper in `futex.c`.

Risks: expected failures check `errno` after futex wrapper return; wrapper semantics must match. Plain `done` is shared across threads and signal path. High thread/futex counts can consume memory and alter scheduler behavior.

Test signals: private/shared modes, custom buckets, mlockall, silent output, high CPU-count scaling, and expected EAGAIN/EWOULDBLOCK failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/futex-hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/futex-lock-pi.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/futex-lock-pi.c

Purpose: benchmarks priority-inheritance futex lock/unlock throughput, either contending on one global PI futex or using one futex per worker.

Important APIs/types/functions: `bench_futex_lock_pi()` sets up the run. `create_threads()` allocates/pins workers and chooses shared versus per-worker futex. `workerfn()` loops `futex_lock_pi()`, sleeps briefly while holding the lock, and `futex_unlock_pi()`. `print_summary()` reports ops/sec and bucket state.

Control flow: options configure buckets, threads, runtime, multi-futex mode, shared/private futex, mlockall, and silent mode. The run defaults threads to online CPUs, initializes stats/barriers, starts workers, sleeps runtime, toggles done, joins, frees per-worker futexes in multi mode, and reports.

State and persistence: global static `global_futex`, worker array, params, barrier state, and stats. No persistent files; optional futex hash bucket sysctl write is performed through helper if requested.

Dependencies and integration: depends on PI futex syscalls, perf CPU map affinity, pthreads, mutex/cond wrappers, stats, and futex helper declarations.

Risks: PI futex support and permissions vary by kernel. Shared `done` is unsynchronized. The 1 microsecond sleep intentionally changes lock hold time and may dominate on some systems. Multi mode changes benchmark from contention to mostly syscall cost.

Test signals: single and multi futex modes, shared/private flags, custom bucket setting, no-PI-support behavior, and throughput under varying thread counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/futex-lock-pi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/futex-requeue.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/futex-requeue.c

Purpose: benchmarks `futex_cmp_requeue()` latency by blocking threads on one futex and requeueing them to another.

Important APIs/types/functions: `bench_futex_requeue()` orchestrates repeated runs. `block_threads()` creates CPU-pinned waiters. `workerfn()` waits on the first futex. `print_summary()` aggregates requeue latency and number of requeued tasks.

Control flow: parses threads, wake/requeue counts, shared/private, mlockall, silent, and bucket options. For each repeat, it starts waiters behind a barrier, sleeps to let them block, times `futex_cmp_requeue()`, joins workers, records stats, and resets for the next repeat.

State and persistence: uses static futex words, thread array, condition state, stats, and params. No persistent files except optional kernel futex bucket sysctl adjustment via helper.

Dependencies and integration: futex wrappers including cmp-requeue, perf CPU maps, pthreads, mutex/cond, stats, and bench repeat.

Risks: correctness depends on waiters actually being queued before requeue; the fixed sleep is a heuristic. Requested wake/requeue values are adjusted for thread count. Shared `done` only affects signal interruption. Kernel futex semantics differ for private/shared flags.

Test signals: varied `--nwakes`/`--nrequeues`, repeat counts, private/shared, divisible and boundary thread counts, and verifying all waiters exit after requeue/wake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/futex-requeue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/futex-wake-parallel.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/futex-wake-parallel.c

Purpose: measures latency when multiple waker threads concurrently call `futex_wake()` on a shared futex to wake a blocked population.

Important APIs/types/functions: if `HAVE_PTHREAD_BARRIER` is absent, `bench_futex_wake_parallel()` reports the benchmark disabled. Otherwise, `block_threads()` creates pinned waiters, `wakeup_threads()` starts waker threads behind a barrier, `waking_workerfn()` times each `futex_wake()`, and `do_run_stats()`/`print_summary()` aggregate latency and wake counts.

Control flow: parse thread/waker counts, validate divisibility, set `nwakes = nthreads / nwakers`, create blocked waiters for each repeat, broadcast them into `futex_wait()`, sleep briefly, launch synchronized wakers, join all waiters, record per-run stats, and print summary.

State and persistence: static shared futex, blocked worker array, pthread barrier, condition variables, stats, and params. Runtime only; no persistent files except optional futex bucket sysctl adjustment.

Dependencies and integration: depends on pthread barriers, futex wrappers, perf CPU maps, mutex/cond wrappers, stats, and bench repeat.

Risks: fixed sleeps and scheduling can affect whether all waiters are blocked. The benchmark requires thread count divisible by waker count. Plain `done` only stops repeats on signal. Barrier availability gates the whole file.

Test signals: builds with/without pthread barrier, `--threads` divisible/nondivisible by `--nwakers`, shared/private futexes, bucket changes, repeat count, and wake-count warning paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/futex-wake-parallel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/futex-wake.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/futex-wake.c

Purpose: measures latency for waking blocked futex waiters in batches from one main thread.

Important APIs/types/functions: `bench_futex_wake()` is the entry point. `block_threads()` creates CPU-pinned waiters. `workerfn()` waits on the shared futex. `print_summary()` reports average wake latency and average wake count.

Control flow: parse thread count, `nwakes`, private/shared, buckets, mlockall, and silent options. For each repeat, create and release waiters into `futex_wait()`, sleep to allow queueing, time repeated `futex_wake()` calls until all requested threads are woken, join workers, update stats, and print per-run/summary output.

State and persistence: static shared futex, worker thread array, condition variables, stats, and params. No files are persisted; optional futex bucket helper may alter kernel sysctl for the run.

Dependencies and integration: futex wrappers, perf CPU map affinity, pthreads, mutex/cond, stats, bench repeat, and optional `mlockall`.

Risks: queueing readiness uses a fixed sleep after condition broadcast. Wake counts can differ from requested counts due to races or signals. Shared `done` is signal-set and read in loops.

Test signals: varied `--threads` and `--nwakes`, shared/private modes, repeat counts, mlockall, bucket setting, and warning when fewer waiters wake than expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/futex-wake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/futex.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/futex.c

Purpose: shared futex benchmark helper for configuring and reporting the kernel futex hash bucket count.

Important APIs/types/functions: `futex_set_nbuckets_param()` writes requested bucket count to `/proc/sys/kernel/futex_hash_buckets` when `params->nbuckets > 0`. `futex_print_nbuckets()` reads and prints the current bucket count.

Control flow: both helpers early-return when no bucket override/reporting is requested. They use `sysctl__write_int()` and `sysctl__read_int()` and print warnings on failure.

State and persistence: unlike most bench files, this can persistently change the kernel sysctl futex hash bucket setting for the running system. It stores no internal state.

Dependencies and integration: depends on `bench_futex_parameters` from `futex.h`, sysctl helpers, and warning output. Used by futex hash/wake/requeue/PI benchmarks.

Risks: changing a global kernel sysctl affects the whole system and may require privileges. The helper does not restore the old value. Tests should isolate or avoid bucket writes unless intentional.

Test signals: run futex benchmarks with default `-1`, explicit valid bucket count, permission-denied sysctl, and readback reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/futex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/futex.h -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/futex.h

Purpose: provides futex syscall wrappers and shared option state for perf futex benchmarks.

Important APIs/types/functions: `struct bench_futex_parameters` carries common options: threads, futex count, runtime, wake/requeue counts, shared/private, mlockall, multi, silent, and bucket count. Inline wrappers cover `futex_wait`, `futex_wake`, `futex_lock_pi`, `futex_unlock_pi`, and `futex_cmp_requeue`. It declares bucket helper functions from `futex.c`.

Control flow: wrappers call `syscall(SYS_futex, ...)` directly with operation plus private/shared flag, then return syscall result.

State and persistence: no internal state. The parameter struct is embedded as static state in benchmark files.

Dependencies and integration: depends on Linux futex ABI, syscall numbers, time types, and common bench users. It is the contract between futex benchmarks and raw kernel futex operations.

Risks: wrappers expose raw syscall return conventions; callers must inspect return and `errno` correctly. Operation flags are caller-composed, so misuse of `FUTEX_PRIVATE_FLAG` changes semantics.

Test signals: compile on supported Linux targets and exercise each futex benchmark path, especially PI and cmp-requeue operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/inject-buildid.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/inject-buildid.c

Purpose: benchmarks `perf inject -b` and `perf inject -b --buildid-all` by synthesizing perf.data streams with MMAP2 and SAMPLE events referencing real DSOs with build IDs.

Important APIs/types/functions: `bench_inject_build_id()` runs the benchmark. `collect_dso()` walks `/usr/lib` via `nftw()` and `add_dso()` to collect DSOs with build IDs. `setup_injection()` forks a child that runs perf's `main()` as `perf inject`. `synthesize_attr()`, `synthesize_fork()`, `synthesize_mmap()`, `synthesize_sample()`, and `synthesize_flush()` write input records. `inject_build_id()` feeds one iteration and collects child `ru_maxrss`.

Control flow: after option parsing, symbol support initializes, sample type/header size are fixed, DSOs are collected, then two loops run: build-id injection and build-id-all injection. Each iteration creates pipes, forks perf inject, writes a perf pipe header, attr/fork records, randomized mmap/sample records, periodic finished-round records, closes input, waits for child, joins output drain thread, and updates timing/memory stats.

State and persistence: process-local arrays store DSO paths and inode ids; pipes connect parent and child. No benchmark output files are persisted, but it reads real filesystem DSOs and executes an in-process child perf command.

Dependencies and integration: depends on perf data/header/session/sample/synthetic event APIs, build-id reading, symbol init, pthreads, fork/pipe/wait4, `/usr/lib` contents, and perf's top-level `main()`.

Risks: assumes enough DSOs with build IDs under `/usr/lib`; otherwise benchmark cannot run. Forking and calling `main()` recursively is unusual and sensitive to global state. Large path names require split writes around sample id headers. Child stderr is redirected to `/dev/null`, hiding diagnostics.

Test signals: systems with/without build-id DSOs, varied mmap/sample/iteration counts, verbose DSO collection, child exit status, memory usage stability, and comparison of `-b` versus `--buildid-all`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/inject-buildid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/kallsyms-parse.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/kallsyms-parse.c

Purpose: benchmarks parsing `/proc/kallsyms` through perf's kallsyms parser.

Important APIs/types/functions: `bench_kallsyms_parse()` parses options and loops. `do_kallsyms_parse()` invokes `kallsyms__parse()` with a no-op callback and measures elapsed time.

Control flow: for each iteration, open/parse kallsyms, time the parse, update stats, and print average/stddev at the end.

State and persistence: only runtime stats; no persistent output. Reads `/proc/kallsyms`.

Dependencies and integration: depends on perf kallsyms parser, stats, parse-options, and access to kernel symbol file.

Risks: restricted kallsyms, kernel symbol count, and I/O cache state heavily affect results. A no-op callback measures parser overhead but not downstream symbol processing.

Test signals: normal and restricted `/proc/kallsyms`, repeated iterations, cold vs warm cache, and parser error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/kallsyms-parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/mem-functions.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/mem-functions.c

Purpose: implements perf bench memory benchmarks for `memcpy`, `memset`, and `mmap` demand/populate behavior.

Important APIs/types/functions: `bench_mem_memcpy()`, `bench_mem_memset()`, and `bench_mem_mmap()` are entry points. `bench_mem_common()` parses common options, validates sizes/page sizes, selects a function, and calls `__bench_mem_function()`. `do_memcpy()`, `do_memset()`, and `do_mmap()` perform timed operations. `bench_mmap()` maps 4KB/2MB/1GB pages with optional huge pages and populate. `init_cycles()`/`get_cycles()` optionally measure CPU cycles.

Control flow: common setup parses buffer size, chunk size, page size, loops, selected implementation, and cycle timing. Copy/set benchmarks allocate prefaulted mmap buffers, run nested loop over loops and chunks, then report bandwidth or cycles/byte. Mmap benchmark starts configurable threads, each repeatedly maps, touches pages either sequentially or random-offset, unmaps, and accumulates timing.

State and persistence: static option globals and a static stats object hold process state. Memory is anonymous mmap and freed after each function. Optional cycle counter fd is opened for the process. No files persist.

Dependencies and integration: depends on perf syscall wrapper for `perf_event_open`, perf size parser, stats, x86 asm implementation tables when enabled, pthreads, mmap/hugetlb flags, and bench output format.

Risks: uses `void *` pointer arithmetic as a compiler extension. Huge-page modes require kernel support and available huge pages. `print_bps()` has a formatting typo for KB (`%lfd`). Cycle measurement requires perf permissions. Multi-thread mmap results use shared global options and aggregate per-thread stats.

Test signals: `mem memcpy`, `mem memset`, and `mem mmap` with default/all/help functions, x86 asm functions, chunked operations, cycle mode, 4KB/2MB/1GB pages, random mmap touch, multiple threads, and allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/mem-functions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memcpy-arch.h -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memcpy-arch.h

Purpose: declares architecture-specific memcpy benchmark implementations for x86_64 builds.

Important APIs/types/functions: under `HAVE_ARCH_X86_64_SUPPORT`, temporarily defines `MEMCPY_FN()` to emit prototypes and includes `mem-memcpy-x86-64-asm-def.h`.

Control flow: preprocessor-only expansion.

State and persistence: no state.

Dependencies and integration: consumed by `mem-functions.c`; declarations must match assembly symbols supplied by `mem-memcpy-x86-64-asm.S`.

Risks: macro contract must stay synchronized with definition header and assembly symbol names.

Test signals: x86_64 perf bench build and selecting `x86-64-unrolled` / `x86-64-movsq` memcpy functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memcpy-arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memcpy-x86-64-asm-def.h -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memcpy-x86-64-asm-def.h

Purpose: defines the x86_64 memcpy benchmark implementation table through `MEMCPY_FN()` macro invocations.

Important APIs/types/functions: lists `memcpy_orig` as `x86-64-unrolled` and `__memcpy` as `x86-64-movsq`, both using `mem_alloc` and `mem_free`.

Control flow: preprocessor data only; behavior depends on how the includer defines `MEMCPY_FN`.

State and persistence: no runtime state.

Dependencies and integration: included once for prototypes and once for `struct function` table entries in `mem-functions.c`.

Risks: symbol names come from the included kernel assembly and must remain exported by the wrapper assembly file.

Test signals: function-help output lists both names, and both selected functions link and run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memcpy-x86-64-asm-def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memcpy-x86-64-asm.S -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memcpy-x86-64-asm.S

Purpose: wraps the kernel x86_64 `memcpy_64.S` implementation so it can be built into user-space perf bench.

Important APIs/types/functions: redefines `SYM_FUNC_START_LOCAL()` to export local kernel symbols globally, renames `memcpy` to `MEMCPY` to avoid hiding glibc, stubs exception-table macros, remaps `altinstr_replacement`, and includes `../../arch/x86/lib/memcpy_64.S`.

Control flow: assembly inclusion supplies actual memcpy implementations; this file only adapts build macros.

State and persistence: no state. Adds `.note.GNU-stack` to request a non-executable stack.

Dependencies and integration: depends on kernel x86 assembly source and Linux assembly macro conventions. Provides symbols referenced by `mem-memcpy-x86-64-asm-def.h`.

Risks: fragile against changes in kernel assembly macro names or required sections. User-space build stubs exception handling, so only benchmark-safe paths are expected.

Test signals: x86_64 assembly build/link, non-executable stack note in object, and successful execution of both x86 memcpy variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memcpy-x86-64-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memset-arch.h -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memset-arch.h

Purpose: declares architecture-specific memset benchmark implementations for x86_64 builds.

Important APIs/types/functions: under `HAVE_ARCH_X86_64_SUPPORT`, defines `MEMSET_FN()` to emit prototypes and includes `mem-memset-x86-64-asm-def.h`.

Control flow: preprocessor-only expansion.

State and persistence: no state.

Dependencies and integration: consumed by `mem-functions.c`; declarations correspond to symbols from `mem-memset-x86-64-asm.S`.

Risks: macro signature and symbol names must remain synchronized with table and assembly files.

Test signals: x86_64 perf bench build and explicit selection of x86 memset variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memset-arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memset-x86-64-asm-def.h -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memset-x86-64-asm-def.h

Purpose: defines the x86_64 memset benchmark implementation table through `MEMSET_FN()` macro invocations.

Important APIs/types/functions: lists `memset_orig` as `x86-64-unrolled` and `__memset` as `x86-64-stosq`, both using `mem_alloc` and `mem_free`.

Control flow: preprocessor data only; expansion depends on includer macro.

State and persistence: no state.

Dependencies and integration: included for prototypes and function table construction in `mem-functions.c`.

Risks: description says movsq for a memset `stosq` variant; labels should remain clear for users. Symbol names must match wrapper assembly exports.

Test signals: function-help output and selected execution of both x86 memset implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memset-x86-64-asm-def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memset-x86-64-asm.S -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memset-x86-64-asm.S

Purpose: wraps kernel x86_64 `memset_64.S` so perf bench can benchmark kernel-style memset implementations in user space.

Important APIs/types/functions: exports local symbols by redefining `SYM_FUNC_START_LOCAL()`, renames `memset` to `MEMSET`, remaps `altinstr_replacement`, defines `globl`, includes `../../arch/x86/lib/memset_64.S`, and emits `.note.GNU-stack`.

Control flow: actual memset control flow is in the included kernel assembly; this file supplies build adaptation.

State and persistence: no state. Non-executable stack note is emitted.

Dependencies and integration: depends on kernel x86 memset assembly and symbol names referenced by `mem-memset-x86-64-asm-def.h`.

Risks: user-space wrapper can break if kernel assembly gains new macro dependencies. It intentionally avoids glibc symbol collision by renaming.

Test signals: x86_64 assembly build/link, stack note check, and perf bench memset using `x86-64-unrolled` and `x86-64-stosq`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memset-x86-64-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/numa.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/numa.c

Purpose: implements `perf bench numa mem`, a NUMA-sensitive workload generator that measures bandwidth, runtime spread, and convergence behavior across processes, threads, CPU bindings, memory-node bindings, and memory access patterns.

Important APIs/types/functions: `bench_numa()` is the command entry. `struct params` holds all CLI-controlled workload settings. `struct global_info` is shared across processes and tracks shared data, synchronization, thread results, stop flags, and copied params. `init_params()`, `init()`, `__bench_numa()`, `worker_process()`, and `worker_thread()` form the main lifecycle. Binding/allocation helpers include `bind_to_cpu()`, `bind_to_node()`, `bind_to_memnode()`, `alloc_data()`, `parse_setup_cpu_list()`, and `parse_setup_node_list()`. Work and convergence helpers include `do_work()`, `calc_convergence()`, `count_process_nodes()`, and `count_node_processes()`.

Control flow: defaults are initialized, options parsed, then `init()` allocates shared global state, parses memory sizes, creates shared global data and shared thread metadata, and applies CPU/node binding lists. `__bench_numa()` forks `nr_proc` children. Each child allocates process data, creates `nr_threads`, and each thread binds CPU/memory policy, allocates thread-local memory, optionally waits for serialized startup, then loops over global/process/thread memory work until loops, seconds, convergence, or stop flag ends. Parent waits for children, aggregates shared thread runtimes and total bytes, prints result metrics, and deinitializes shared mappings.

State and persistence: most state lives in MAP_SHARED anonymous mappings so parent and children share `global_info`, thread result records, stop flags, mutexes, and condition variables. Process/thread private data is anonymous mmap. CPU affinity and memory policy are changed for tasks and restored in limited initialization cases. No output files persist.

Dependencies and integration: depends on libnuma (`numa.h`, `numaif.h`), sched affinity, `set_mempolicy`, pthreads, process-shared mutex/cond wrappers, mmap/madvise THP flags, sysfs CPU online checks, perf option parsing, and bench output globals.

Risks: uses many `BUG_ON()` assertions for runtime/environment errors, so invalid topology or allocation failures abort. Shared flags such as `stop_work` are not fully synchronized for all reads. `free_data()` munmaps the aligned pointer with the original byte count even though allocation added `HPSIZE`, which is a subtle mapping-management risk. Built-in `-a` tests assume large NUMA systems and memory. Binding parser is powerful but fragile around ranges, steps, masks, and multiplicators.

Test signals: default `perf bench numa mem`, explicit CPU and memnode bindings, THP on/off, `--serialize-startup`, read/write/backward/random/zero modes, convergence measurement, quiet/detail formats, offline CPU handling, one-node systems, and resource-heavy `--all` only on suitable hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/numa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/pmu-scan.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/pmu-scan.c

Purpose: benchmarks perf PMU sysfs scanning for core-only and all-PMU scans while verifying consistency of discovered PMU metadata.

Important APIs/types/functions: `bench_pmu_scan()` parses options. `save_result()` performs a baseline `perf_pmus__scan()` and stores PMU name, alias count, format count, caps count, and core flag. `check_result()` rescans and compares current data to baseline. `run_pmu_scan()` times repeated `perf_pmus__scan_core()` and `perf_pmus__scan()` calls.

Control flow: save baseline, then run two phases: core-only and all PMUs. Each iteration times scan, checks results, destroys PMU cache, and updates stats. Finally prints average scan time and frees baseline.

State and persistence: static `results` array and `nr_pmus` hold baseline metadata. No persistent files; reads sysfs PMU hierarchy.

Dependencies and integration: depends on perf PMU cache/scanning APIs, list traversal of PMU format entries, stats, parse-options, and debug output.

Risks: baseline can become stale if PMU sysfs changes during the run. The same stats object is reused across core/all phases without reinitialization between phases, so second reported average includes prior samples. Allocation failure in `strdup()` is not explicitly checked.

Test signals: systems with only core PMUs and with uncore/software PMUs, varied iteration counts, hotplug/sysfs changes, and intentional PMU cache destroy/rebuild correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/pmu-scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/sched-messaging.c -->
# Research: sources/distributed-fs/ceph-client/tools/perf/bench/sched-messaging.c

Purpose: implements a hackbench-derived scheduler/IPC benchmark using groups of senders and receivers communicating through pipes or Unix socketpairs, in process or thread mode.

Important APIs/types/functions: `bench_sched_messaging()` is the entry. `fdpair()` creates pipe/socketpair channels. `ready()` blocks workers until main releases them. `sender()` writes fixed-size messages to receiver fds. `receiver()` polls/reads until expected packets arrive. `group()` allocates sender/receiver contexts and starts workers. `reap_worker()` joins threads or waits processes. `sig_handler()` kills child processes on abnormal termination.

Control flow: options choose pipes, thread mode, group count, and loops. Main allocates a worker table, creates ready/wake fds, installs signal handlers for process mode, builds each group of 20 senders and 20 receivers, waits for every worker readiness byte, starts timing, writes one wake byte, reaps all workers, stops timing, prints default/simple output, and frees contexts.

State and persistence: global linked lists retain allocated sender/receiver contexts until cleanup; worker table holds pthread ids or pids. No files persist. IPC fds are inherited by forked workers or shared by threads.

Dependencies and integration: depends on pthreads, fork/wait, sockets/pipes, poll, Linux list helpers, parse-options, and bench output globals.

Risks: high group counts create many fds and processes/threads. Signal cleanup only handles process mode. Context/fd ownership is complex across fork/thread paths; fd leaks can skew long repeated use. The fixed group size of 20 is embedded in the benchmark.

Test signals: process and thread modes, pipe vs socketpair, varied group/loop counts, simple/default output, SIGINT cleanup, and fd/resource-limit stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/bench/sched-messaging.c -->
