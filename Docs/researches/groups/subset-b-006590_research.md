# subset-b-006590 Research

Grouped research report for the 39 source files assigned to `subset-b-006590`. Each section is source-tree-aligned and bounded by the reconciliation markers used to split this grouped report into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/tests.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/tests.h

## Purpose
This internal libperf test header provides the lightweight harness used by the C unit tests under `tools/lib/perf/tests`. It centralizes verbose option parsing, start/end status printing, assertion handling, and conditional verbose logging.

## Important APIs, Types, and Functions
- `extern int tests_failed` and `extern int tests_verbose` are shared test-run state defined by `tests/main.c`.
- `get_verbose(char **argv, int argc)` scans for `-v` with `getopt`, returns a boolean-style verbose flag, and resets `optind` so each test function can parse the same argv.
- `__T_START` initializes per-test output, verbosity, and failure count.
- `__T_END` emits `OK` or `FAILED (n)`.
- `__T(text, cond)` records a failure, emits file/line context, and returns `-1` from the caller.
- `__T_VERBOSE(...)` lazily prints verbose detail after inserting a first newline.

## Control Flow and State
Every test function calls `__T_START`, performs checks with `__T`, and closes with `__T_END`. The macros mutate global `tests_failed` and `tests_verbose`; failures short-circuit the current helper by returning `-1`.

## Dependencies and Integration Points
The header depends on libc `stdio.h`, `unistd.h`, and `getopt`. It is included by libperf test sources and is separate from installed public libperf headers.

## Risks and Test Signals
Because `__T` returns from the enclosing function, it is only safe in functions returning `int`. `get_verbose` resets global getopt state, which is deliberate for repeated test entry points but would be surprising outside this harness. The test signal is textual stdout/stderr status plus the final return code from each test function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/tests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/threadmap.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/threadmap.h

## Purpose
This internal header exposes the concrete allocation layout for `struct perf_thread_map`, which is opaque in the public `perf/threadmap.h` API. It supports libperf internals that need direct access to thread IDs, command strings, refcounts, and the flexible-array map.

## Important APIs, Types, and Functions
- `struct thread_map_data` stores a `pid_t pid` and dynamically owned `char *comm`.
- `struct perf_thread_map` stores a `refcount_t`, element count `nr`, `err_thread`, and `map[]` flexible array.
- `perf_thread_map__realloc(struct perf_thread_map *map, int nr)` grows or allocates maps and is implemented in `threadmap.c`.

## Control Flow and State
The header itself has no control flow. Its state contract is ownership-oriented: `comm` strings are freed by `perf_thread_map__delete`, and the map object is lifetime-managed through refcounts.

## Dependencies and Integration Points
It depends on Linux `refcount_t`, `sys/types.h`, and `unistd.h`. Public thread-map functions create and retain these objects; evsel/evlist code consumes them when opening perf events.

## Risks and Test Signals
The flexible-array allocation must match `threadmap.c`; any size or field-order change can break internal users. Tests in `test-threadmap.c` validate dummy and array maps, refcount get/put behavior, PID mutation, and default `-1` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/threadmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/xyarray.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/xyarray.h

## Purpose
This internal header defines a compact two-dimensional array allocator used by libperf internals for fixed-size entries addressed by `(x, y)` indices, commonly useful for CPU/thread matrices such as fd or mmap tables.

## Important APIs, Types, and Functions
- `struct xyarray` records row size, entry size, total entries, max x/y bounds, and an 8-byte-aligned `contents[]` payload.
- `xyarray__new(int xlen, int ylen, size_t entry_size)` allocates zeroed storage.
- `xyarray__delete` frees it; `xyarray__reset` zeroes the payload.
- `__xyarray__entry` computes the unchecked address.
- `xyarray__entry` adds bounds checks and returns `NULL` on invalid indices.
- `xyarray__max_x` and `xyarray__max_y` expose dimensions.

## Control Flow and State
The allocator stores all entries contiguously. Addressing is `x * row_size + y * entry_size`; callers own any object semantics inside the raw memory.

## Dependencies and Integration Points
It depends on Linux compiler alignment helpers and is implemented by `xyarray.c`. It integrates with libperf internals that need rectangular, zero-initialized data without per-cell allocation overhead.

## Risks and Test Signals
There is no overflow guard for `xlen * ylen * entry_size`, so callers must pass sane sizes. `__xyarray__entry` is intentionally unchecked; public internal callers should prefer `xyarray__entry` unless they already proved bounds. Coverage is indirect through libperf tests that allocate fd/count matrices in evsel/evlist paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/xyarray.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/bpf_perf.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/bpf_perf.h

## Purpose
This public libperf header describes the bpffs-pinned attribute map contract used by BPF-assisted perf-stat sessions. It provides a small shared struct and default map-name constant for coordinating leader BPF programs.

## Important APIs, Types, and Functions
- `struct perf_event_attr_map_entry` contains two kernel object IDs: `link_id` for the leader program's BPF link and `diff_map_id` for the associated diff map.
- `BPF_PERF_DEFAULT_ATTR_MAP_PATH` names the default pinned attr-map file as `perf_attr_map`.

## Control Flow and State
The header has no executable control flow. Its comment defines the state model: a bpffs hash map is keyed by `struct perf_event_attr`, locked with `flock()` on the pinned file, and stores IDs rather than references. Perf-stat sessions hold their own BPF link references so leader programs and maps are released after all sessions exit.

## Dependencies and Integration Points
It includes Linux integer types and integrates with BPF perf-stat code that is outside this file. It is part of libperf's installed public API surface.

## Risks and Test Signals
The main risk is semantic drift between this shared layout and the BPF-side map value. Because it stores IDs only, consumers must correctly reacquire objects and hold references. No direct unit test appears in this subset; validation is expected from BPF perf-stat integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/bpf_perf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/core.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/core.h

## Purpose
This public header defines libperf's core symbol-export macro, print levels, logging callback type, and initialization entry point.

## Important APIs, Types, and Functions
- `LIBPERF_API` defaults to `extern __attribute__((visibility("default")))`, marking installed library symbols for export.
- `enum libperf_print_level` defines `ERR`, `WARN`, `INFO`, `DEBUG`, `DEBUG2`, and `DEBUG3`.
- `libperf_print_fn_t` is a printf-style callback taking a level, format string, and `va_list`.
- `libperf_init(libperf_print_fn_t fn)` installs the caller's print function.

## Control Flow and State
This header only declares the public setup contract. Runtime state lives in libperf implementation files: the installed callback is used by `libperf_print` and `pr_*` wrappers from `internal.h`.

## Dependencies and Integration Points
It depends on `<stdarg.h>` and is included by almost every public libperf header. Tests install local callbacks with `libperf_init` before exercising maps, evsels, and evlists.

## Risks and Test Signals
Changing enum ordering or callback signature is ABI-visible. Consumers that pass `NULL` or callbacks with incompatible formatting behavior can lose diagnostics. Tests validate initialization implicitly by routing libperf messages through local `vfprintf` callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/cpumap.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/cpumap.h

## Purpose
This public header declares libperf's CPU-map API. It abstracts sets of CPUs, including the special `any CPU` dummy value `-1`, and provides constructors, lifetime management, set operations, queries, and iteration macros.

## Important APIs, Types, and Functions
- `struct perf_cpu` wraps a signed 16-bit CPU number to reduce confusion between CPU IDs and map indices.
- `struct perf_cache` names cache level/index pairs.
- Constructors include `perf_cpu_map__new_any_cpu`, `perf_cpu_map__new_online_cpus`, `perf_cpu_map__new(const char *cpu_list)`, and `perf_cpu_map__new_int`.
- Refcount functions are `perf_cpu_map__get` and `perf_cpu_map__put`.
- Set and query APIs include `merge`, `intersect`, `has`, `equal`, `min`, `max`, `nr`, and several `any CPU`/empty predicates.
- Iteration macros expose all CPUs, skip dummy CPUs, or iterate indices.

## Control Flow and State
The header is declarative; the implementation stores map contents elsewhere. The public contract treats empty maps specially: `perf_cpu_map__nr` returns one so invalid-index reads can behave like the dummy `-1` CPU.

## Dependencies and Integration Points
It depends on `perf/core.h`, `stdbool.h`, and `stdint.h`. Evsel and evlist use CPU maps to decide which perf_event file descriptors to open and which mmaps to allocate.

## Risks and Test Signals
The `-1` dummy value is subtle: APIs distinguish empty, has-any, and is-any-or-empty. Callers must not treat iteration length as a count of real CPUs without checking for `-1`. `test-cpumap.c`, `test-evsel.c`, and `test-evlist.c` exercise online CPU construction, refcounting, iteration, and perf-event reads across mapped CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/cpumap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/event.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/event.h

## Purpose
This public header defines libperf's user-space representation of perf event records and perf.data-style metadata records. It is primarily an ABI/schema header for parsing ring-buffer events, generated perf records, CPU/thread maps, stat records, BPF metadata, compression records, and schedstat records.

## Important APIs, Types, and Functions
- `event_contains(obj, mem)` tests whether a record's `header.size` reaches a member.
- Record structs mirror kernel perf records: `mmap`, `mmap2`, `comm`, `namespaces`, `fork`, `lost`, `lost_samples`, `read`, `throttle`, `ksymbol`, `bpf_event`, `cgroup`, `text_poke`, `sample`, `switch`, and deferred callchains.
- Header/metadata records include attr, event type, tracing data, build ID, ID index, auxtrace info/data/error, aux output hardware ID, thread map, CPU map, stat config/stat/stat round, time conversion, feature, compression, BPF metadata, and schedstat CPU/domain records.
- CPU-map encodings support array, 32-bit mask, 64-bit mask, and compact range formats. `perf_record_cpu_map_data` is explicitly packed for file-format compatibility.
- Schedstat record payloads are generated by including `schedstat-v15.h`, `schedstat-v16.h`, or `schedstat-v17.h` under field-defining macros.
- `enum perf_user_event_type` reserves user-space record IDs beginning at 64.
- `union perf_event` overlays all supported record types for ring-buffer/event-file parsing.

## Control Flow and State
There is no executable control flow, but this file defines how variable-sized records are traversed: many structs end with flexible arrays, zero-length arrays, or payloads whose true length comes from `header.size`. `perf_record_header_attr_id(evt)` computes the ID array address using the recorded `attr.size` rather than the current compile-time struct layout.

## Dependencies and Integration Points
It includes Linux perf, BPF, limits, and type headers. It is consumed by `mmap.c` when returning `union perf_event *` from ring buffers and by higher-level perf tooling when reading/writing perf.data metadata.

## Risks and Test Signals
This is ABI-sensitive. Packing, padding, flexible-array handling, enum IDs, and schedstat-version field ordering must remain compatible with kernel and perf.data expectations. Tests in this subset exercise event pointers indirectly through `test-evlist.c` tracepoint mmap reads, but broad validation depends on perf record parsing and perf.data compatibility tests outside this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/evlist.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/evlist.h

## Purpose
This public header declares the libperf event-list API. An evlist owns an ordered collection of event selectors, shared CPU/thread maps, poll descriptors, and optional mmap buffers.

## Important APIs, Types, and Functions
- List management: `perf_evlist__new`, `delete`, `add`, `remove`, and `next`.
- Runtime operations: `open`, `close`, `enable`, `disable`, `poll`, and `filter_pollfd`.
- Map binding: `perf_evlist__set_maps(cpus, threads)`.
- Mmap lifecycle: `perf_evlist__mmap`, `munmap`, `next_mmap`, and the mmap iteration macro.
- Group helpers: `perf_evlist__set_leader` and `perf_evlist__nr_groups`.
- `perf_evlist__for_each_evsel` and `perf_evlist__for_each_mmap` provide public iteration syntax.

## Control Flow and State
The implementation iterates over evsels, opens each event against configured maps, controls all fds together, and exposes poll/mmap traversal. Group leadership ties later evsels to the first selector unless grouping rules create more groups.

## Dependencies and Integration Points
It depends on `perf/core.h` and forward-declared evsel, CPU-map, thread-map, and mmap types. Tests build evlists with software counters and tracepoints, set maps, open, enable, read, mmap, and delete them.

## Risks and Test Signals
Evlist correctness depends on coordinated ownership of maps, evsels, fds, poll descriptors, and mmaps. Tracepoint mmap tests require debugfs/sysfs event IDs and can fail on restricted hosts. `test-evlist.c` is the main signal for group leadership, CPU/thread stat reads, enable/disable, mmap event consumption, and multiplex scaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/evlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/evsel.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/evsel.h

## Purpose
This public header declares the libperf event-selector API. An evsel wraps a `struct perf_event_attr`, the fd matrix produced by opening that event over CPU/thread maps, optional mmaps, and read/enable/disable operations.

## Important APIs, Types, and Functions
- `struct perf_counts_values` stores up to five read outputs: value, enabled time, running time, ID, and lost count.
- Lifecycle: `perf_evsel__new`, `delete`, `open`, `close`, `close_cpu`.
- Mmap access: `perf_evsel__mmap`, `munmap`, `mmap_base`.
- Runtime operations: `read`, `enable`, `enable_cpu`, `enable_thread`, `disable`, `disable_cpu`.
- Accessors expose bound `cpus`, `threads`, and mutable `attr`.
- `perf_counts_values__scale` scales multiplexed counts and reports scaling status through `pscaled`.

## Control Flow and State
The evsel is opened against CPU and/or thread maps, then read by CPU-map index and thread index. Group reads may involve leader/member relationships, and mmap reads expose kernel perf ring-buffer pages.

## Dependencies and Integration Points
It depends on `perf/core.h`, Linux types, and `struct perf_event_attr`. Evlist is a collection wrapper around evsels. Tests reach internal leader fields through `internal/evsel.h` to validate grouping behavior.

## Risks and Test Signals
Read-format handling must match kernel `read_format` combinations, including group reads and `PERF_FORMAT_LOST`. User-space counter reads depend on architecture support and kernel permissions. `test-evsel.c` validates CPU/thread stat reads, disabled/enabled behavior, mmap base access, hardware RDPMC/user reads on supported architectures, and read-format combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/evsel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/mmap.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/mmap.h

## Purpose
This public header exposes the minimal API for consuming events from libperf mmap ring buffers.

## Important APIs, Types, and Functions
- `perf_mmap__read_init(struct perf_mmap *map)` prepares an iteration over currently available records.
- `perf_mmap__read_event(struct perf_mmap *map)` returns the next `union perf_event *` or `NULL`.
- `perf_mmap__consume(struct perf_mmap *map)` advances tail/consumption state after a record is processed.
- `perf_mmap__read_done(struct perf_mmap *map)` closes a read pass, especially important for overwrite mode.

## Control Flow and State
The intended loop is `read_init`, repeated `read_event` plus `consume`, then `read_done`. The hidden `struct perf_mmap` tracks start/end offsets, previous tail/head, overwrite mode, refcount, and copied straddling events.

## Dependencies and Integration Points
It depends on `perf/core.h` and forward-declares `struct perf_mmap` and `union perf_event`. Evsel and evlist mmap APIs create the maps consumed here. `mmap.c` implements the ring-buffer logic.

## Risks and Test Signals
Callers must consume after processing records in non-overwrite mode, otherwise tail updates are delayed. The pointer returned by `read_event` may refer to an internal copy buffer for wraparound records and should not be persisted after later reads. `test-evlist.c` exercises this API with tracepoint events generated by `prctl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/mmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/schedstat-v15.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/schedstat-v15.h

## Purpose
This header is an X-macro field list for scheduler statistics version 15. It is included multiple times under macros such as `CPU_FIELD`, `DOMAIN_FIELD`, `DERIVED_CNT_FIELD`, `DERIVED_AVG_FIELD`, and `DOMAIN_CATEGORY` to generate record layouts, formatting tables, or derived metric logic.

## Important APIs, Types, and Functions
- CPU fields include yield count, legacy array expiration, schedule count, go-idle count, wakeup count/local wakeups, runqueue CPU time, run delay, and timeslice count.
- Domain fields cover idle, busy, and newly idle load-balancing counters; active load balance counters; legacy sched-balance exec/fork counters; and wakeup movement counters.
- Derived macros define success counts and average pulled-task metrics when enabled by the includer.

## Control Flow and State
There is no standalone control flow. The includer decides whether the entries generate struct fields, output descriptors, or calculations.

## Dependencies and Integration Points
`event.h` includes this file to build `perf_record_schedstat_cpu_v15` and `perf_record_schedstat_domain_v15`. Other perf schedstat renderers can include it with formatting-oriented macro definitions.

## Risks and Test Signals
Ordering and type widths are ABI-relevant for versioned schedstat records. Version 15 uses aggregate imbalance fields such as `*_lb_imbalance`, unlike v17's split load/util/task/misfit counters. Tests are likely in schedstat/perf record tooling outside this subset; no direct unit test here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/schedstat-v15.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/schedstat-v16.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/schedstat-v16.h

## Purpose
This header is the X-macro field list for scheduler statistics version 16. It represents the same broad CPU/domain counter categories as v15 while preserving v16-specific field ordering and derived metric names.

## Important APIs, Types, and Functions
- CPU fields mirror v15: yield, legacy, schedule, go-idle, wakeup, runtime, delay, and timeslice counters.
- Domain categories are busy, idle, newly idle, active load balance, legacy exec/fork balancing, and wakeup information.
- Optional derived macros define load-balance success counts and average pulled-task metrics. In v16 the newly-idle derived average macro is named `newidle_lb_avg_count`.

## Control Flow and State
This file is inert unless included with field macros. It is a schema source for generated structs or display metadata.

## Dependencies and Integration Points
`event.h` uses it to generate `perf_record_schedstat_cpu_v16` and `perf_record_schedstat_domain_v16`. It must remain aligned with any parser/renderer that interprets schedstat version 16 payloads.

## Risks and Test Signals
The most important risk is accidental normalization across versions. Even small ordering or name changes would corrupt record interpretation or output. There is no direct test in this subset; consumers should compare generated layouts and parsed scheduler-stat output for v16 kernels or fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/schedstat-v16.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/schedstat-v17.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/schedstat-v17.h

## Purpose
This header is the X-macro field list for scheduler statistics version 17. It updates domain imbalance accounting by splitting prior aggregate imbalance counters into load, utilization, task-count, and misfit-task fields.

## Important APIs, Types, and Functions
- CPU fields match v15/v16 categories for scheduling, wakeups, runtime, delay, and timeslices.
- Domain fields include busy/idle/newidle load-balance counts, balanced/failed counts, split imbalance counters, gained/hot-gained counters, no-busy-queue/group counters, active load-balance counters, legacy exec/fork fields, and wakeup movement counters.
- Optional derived count and average macros expose success and average-pull metrics.

## Control Flow and State
Like the other schedstat headers, it has no standalone execution. The including macro definitions determine generated code or data.

## Dependencies and Integration Points
`event.h` uses it for `perf_record_schedstat_cpu_v17` and `perf_record_schedstat_domain_v17`. Version dispatch in schedstat readers must select this schema only for v17 records.

## Risks and Test Signals
The split imbalance fields make v17 structurally different from v15/v16. Reusing earlier parsers would misread subsequent fields. There is no direct unit test here; reliable coverage requires schedstat record fixtures or perf schedstat integration tests across versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/schedstat-v17.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/threadmap.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/threadmap.h

## Purpose
This public header declares libperf's thread-map API. Thread maps identify target PIDs/TIDs for per-thread perf_event opens and hide the concrete map/refcount layout from callers.

## Important APIs, Types, and Functions
- Constructors are `perf_thread_map__new_dummy()` for a single dummy `-1` entry and `perf_thread_map__new_array(int nr_threads, pid_t *array)`.
- Mutation/query APIs include `set_pid`, `pid`, `comm`, `nr`, and `idx`.
- Refcount APIs are `perf_thread_map__get` and `perf_thread_map__put`.

## Control Flow and State
The public contract treats `NULL` maps similarly to a single dummy thread in some implementation paths. A dummy map initially contains PID `-1`; tests often change it to `0` to target the current thread/process.

## Dependencies and Integration Points
It depends on `perf/core.h` and `sys/types.h`. Evsel and evlist use thread maps to open perf events for selected threads and to index reads by thread slot.

## Risks and Test Signals
Callers must keep indices within `nr`; public accessors do not advertise bounds checking. The returned `comm` pointer is owned by the map. `test-threadmap.c`, `test-evsel.c`, and `test-evlist.c` validate allocation, mutation, lookup, refcounting, and current-thread perf reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/threadmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/internal.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/internal.h

## Purpose
This private libperf header declares the internal logging function and convenience macros used by implementation files.

## Important APIs, Types, and Functions
- `libperf_print(enum libperf_print_level level, const char *format, ...)` is printf-annotated for compile-time format checking.
- `__pr(level, fmt, ...)` prefixes messages with `libperf: `.
- `pr_err`, `pr_warning`, `pr_info`, `pr_debug`, `pr_debug2`, and `pr_debug3` map to the corresponding libperf print levels.

## Control Flow and State
The macros evaluate to calls into the configured libperf print path. The effective sink is controlled by `libperf_init` from the public core API.

## Dependencies and Integration Points
It includes `perf/core.h`. `mmap.c` uses debug macros for ring-buffer diagnostics and warnings. Other libperf implementation files can use the same private logging surface.

## Risks and Test Signals
Logging macros must not evaluate side effects unexpectedly beyond normal printf argument evaluation. Since they always prefix messages, callers should avoid duplicating prefixes. Tests install a `vfprintf` callback and therefore exercise the print path whenever warnings/debug output is emitted, though most tests do not assert log text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/lib.c -->
# sources/distributed-fs/ceph-client/tools/lib/perf/lib.c

## Purpose
This libperf implementation file provides exact-size read/write helpers used by internal code and defines the global `page_size` variable.

## Important APIs, Types, and Functions
- `unsigned int page_size` is shared state used by mmap sizing.
- Static `ion(bool is_read, int fd, void *buf, size_t n)` loops until exactly `n` bytes are read/written or an error/EOF occurs, retrying `EINTR`.
- `readn(int fd, void *buf, size_t n)` reads exactly `n` bytes.
- `preadn(int fd, void *buf, size_t n, off_t offs)` does positioned exact reads while advancing the offset.
- `writen(int fd, const void *buf, size_t n)` writes exactly `n` bytes.

## Control Flow and State
The helpers repeatedly call `read`, `write`, or `pread`, adjust the remaining byte count and buffer pointer, and return `n` only on full completion. `ion` asserts the final pointer delta with `BUG_ON`.

## Dependencies and Integration Points
It includes libc unistd/errno, Linux `kernel.h`, and `internal/lib.h`. Mmap code depends on `page_size` for mapping length and ring-buffer data offset.

## Risks and Test Signals
Returning `0` or negative values on short/EOF paths means callers must distinguish partial failure from full success. Pointer arithmetic on `void *` relies on compiler extensions used in kernel tooling. There are no direct tests in this subset; coverage is indirect through libperf file and mmap operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/mmap.c -->
# sources/distributed-fs/ceph-client/tools/lib/perf/mmap.c

## Purpose
This file implements libperf mmap ring-buffer setup, teardown, event iteration, overwrite-buffer handling, refcounted unmapping, and user-space counter reads from perf mmap pages.

## Important APIs, Types, and Functions
- `perf_mmap__init` initializes fd, overwrite flag, optional unmap callback, refcount, and linked-list `next`.
- `perf_mmap__mmap_len` returns `mask + 1 + page_size`.
- `perf_mmap__mmap` maps the perf fd with `mmap`, stores fd/cpu/mask, and resets `prev`.
- `perf_mmap__munmap`, `get`, and `put` handle event-copy storage, `munmap`, fd reset, refcount reset, and callback dispatch.
- `perf_mmap__consume` writes the ring tail for non-overwrite mode and auto-puts the last reference when empty.
- `perf_mmap__read_init`, `read_event`, and `read_done` implement public event traversal.
- `overwrite_rb_find_range` recovers readable ranges in full backward overwrite buffers.
- Architecture-specific `read_perf_counter` and `read_timestamp` support x86, arm64, riscv64, and fallback paths.
- `perf_mmap__read_self` reads counts directly from the mmap page using seq-lock style validation, rdpmc/PMU registers, and time scaling.

## Control Flow and State
The ring state is `prev`, `start`, `end`, `mask`, `flush`, `overwrite`, `base`, and a temporary `event_copy` for records that wrap across the buffer end. Non-overwrite mode advances `prev` as events are read and writes it to kernel tail on consume. Overwrite mode snapshots head/start/end and requires `read_done` to reset `prev` to the latest head. Refcount zero indicates an unmapped/hung-up event.

## Dependencies and Integration Points
It depends on perf mmap public/internal headers, Linux ring-buffer helpers, perf_event mmap-page layout, kernel math/barrier helpers, and `page_size` from `lib.c`. Evsel/evlist mmap APIs create `struct perf_mmap` instances and tests consume them through `perf/mmap.h`.

## Risks and Test Signals
The highest-risk areas are wraparound copy logic, overwrite full-buffer recovery, memory-ordering around mmap-page lock/head fields, architecture-specific counter register mapping, and lifecycle interactions between poll hangups and refcounts. `test-evlist.c` validates tracepoint ring-buffer consumption by generating `prctl` events; `test-evsel.c` validates mmap base access and user counter reads on supported architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/main.c -->
# sources/distributed-fs/ceph-client/tools/lib/perf/tests/main.c

## Purpose
This is the libperf test executable entry point. It defines the global harness state and invokes the individual test suites.

## Important APIs, Types, and Functions
- Defines `int tests_failed` and `int tests_verbose` declared by `internal/tests.h`.
- `main(int argc, char **argv)` runs `test_cpumap`, `test_threadmap`, `test_evlist`, and `test_evsel` with `__T` assertions.

## Control Flow and State
Each suite returns zero on success. `__T` records and prints failures, but `main` returns `0` unconditionally after the checks, so failure signaling is primarily via harness output and `tests_failed` increments inside the macro execution.

## Dependencies and Integration Points
It includes the internal test harness and local `tests.h`. It links with all test source files and libperf.

## Risks and Test Signals
The unconditional `return 0` can hide suite failures from process exit status if the outer `__T` does not return early in `main`; in practice a failing `__T` returns `-1` from `main` immediately. Test output indicates which suite failed. This file is the integration point for adding new libperf tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-cpumap.c -->
# sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-cpumap.c

## Purpose
This test suite validates basic public CPU-map behavior and libperf logging initialization.

## Important APIs, Types, and Functions
- Local `libperf_print` forwards libperf diagnostics to `stderr` with `vfprintf`.
- `test_cpumap(int argc, char **argv)` initializes the harness and libperf, creates maps, exercises refcounting, iterates online CPUs, and reports status.

## Control Flow and State
The test creates an any-CPU map, increments/decrements its refcount, then creates an online-CPU map and verifies each iterated CPU is not the dummy `-1`. It releases maps through `perf_cpu_map__put`.

## Dependencies and Integration Points
It depends on `perf/cpumap.h`, `perf/core.h` via the callback type, and `internal/tests.h`. It calls `perf_cpu_map__new_online_cpus`, which may read sysfs or fall back to processor counts.

## Risks and Test Signals
The test is small and does not cover parsing CPU-list strings, set operations, or empty-map edge cases. It does catch basic allocation, refcount, online-map iteration, and dummy-value regressions. Host CPU topology and sysfs availability affect the online map implementation path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-cpumap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-evlist.c -->
# sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-evlist.c

## Purpose
This suite validates libperf evlist behavior across CPU and thread stat events, event grouping, enable/disable, tracepoint mmap consumption, CPU-affinity event routing, and multiplexed count scaling.

## Important APIs, Types, and Functions
- `test_stat_cpu`, `test_stat_thread`, and `test_stat_thread_enable` create two software evsels in an evlist, set leaders/maps, open, read, enable/disable, and close.
- `test_mmap_thread` opens a `sys_enter_prctl` tracepoint for a forked child, mmaps the evlist, generates 100 `prctl` calls, consumes events, and checks the count.
- `test_mmap_cpus` opens a system-wide tracepoint, iterates online CPUs with `sched_setaffinity`, generates events, and expects at least one per CPU.
- `test_stat_multiplexing` compares a single hardware instruction event against 15 multiplexed events and validates scaled count error within 1%.
- `test_evlist` orchestrates all subtests.

## Control Flow and State
The tests build evlists, add evsels, bind maps, open kernel perf_event fds, enable workloads, read counts or mmap records, then close/delete. Mmap tests use `perf_mmap__read_init`, repeated `read_event`/`consume`, and `read_done`.

## Dependencies and Integration Points
The suite depends on debugfs/sysfs tracepoint IDs, `sched_getaffinity`, `sched_setaffinity`, `fork`, `pipe`, `waitpid`, `prctl`, public libperf headers, and `internal/evsel.h` for leader assertions.

## Risks and Test Signals
These are high-value integration tests but environment-sensitive: perf permissions, tracefs/debugfs mount state, CPU affinity restrictions, hardware event availability, and virtualization can cause failures unrelated to libperf logic. They cover evlist map ownership, grouping, polling/mmap consumption, and scaling behavior more thoroughly than isolated unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-evlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-evsel.c -->
# sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-evsel.c

## Purpose
This suite validates individual evsel behavior: opening events over CPU/thread maps, reading counts, enabling disabled events, user-space mmap counter reads, and multiple `read_format` combinations.

## Important APIs, Types, and Functions
- `test_stat_cpu` opens CPU-clock counters for online CPUs and reads each CPU slot.
- `test_stat_thread` opens task-clock for the current thread.
- `test_stat_thread_enable` verifies disabled events read zero until `perf_evsel__enable`.
- `test_stat_user_read(event)` opens hardware events, mmaps page 0, checks user rdpmc/PMU metadata on supported architectures, and verifies monotonically increasing work-loop counts.
- `test_stat_read_format_single` and `test_stat_read_format_group` verify `PERF_FORMAT_TOTAL_TIME_ENABLED`, `RUNNING`, `ID`, and `LOST` for single and group reads.
- `test_stat_read_format` drives all format combinations.

## Control Flow and State
Each helper creates maps and an evsel, opens kernel fds, optionally mmaps, performs workload loops, reads into `struct perf_counts_values`, then closes/deletes and drops maps. Group tests manually set internal leader/member relationships.

## Dependencies and Integration Points
It depends on Linux perf_event hardware/software events, public libperf APIs, and `internal/evsel.h`. User counter validation is architecture-gated for x86 and arm64.

## Risks and Test Signals
Hardware counter availability, perf_event permissions, kernel support for `PERF_FORMAT_LOST`, and user rdpmc access can affect results. Some helpers skip old-kernel read-format failures by returning success when open fails. The suite is a strong regression signal for evsel read layout and enable/disable semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-evsel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-threadmap.c -->
# sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-threadmap.c

## Purpose
This suite validates public thread-map allocation, default values, PID mutation, and refcount behavior.

## Important APIs, Types, and Functions
- Local `libperf_print` routes diagnostics to stderr.
- `test_threadmap_array(int nr, pid_t *array)` creates a map, verifies size and initial values, mutates entries 1..nr-1, verifies values, and releases the map.
- `test_threadmap` tests dummy map refcounting, a NULL-array map initialized with `-1`, and an explicit PID array.

## Control Flow and State
The dummy map is retained and released twice to validate get/put. Array tests preserve the first element's initial value while changing later slots to `i * 100`.

## Dependencies and Integration Points
It uses `perf/threadmap.h` and the shared test harness. It supports evsel/evlist test coverage because thread maps are required for per-thread perf events.

## Risks and Test Signals
The test does not check `perf_thread_map__idx`, `comm` ownership, invalid indices, or reallocation growth. It does catch allocation, count reporting, default dummy PID behavior, explicit initialization, mutation, and refcount deletion regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-threadmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/tests.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/tests/tests.h

## Purpose
This local test header declares the test-suite entry points used by `tests/main.c`.

## Important APIs, Types, and Functions
- `test_cpumap(int argc, char **argv)`
- `test_threadmap(int argc, char **argv)`
- `test_evlist(int argc, char **argv)`
- `test_evsel(int argc, char **argv)`

## Control Flow and State
The header has no logic. It standardizes all suite signatures so the main test runner can pass through command-line arguments, especially `-v` for the shared harness.

## Dependencies and Integration Points
It is included by each test implementation and by `main.c`. It works with `internal/tests.h`, where the common macros and globals are declared.

## Risks and Test Signals
Any signature mismatch between this header and implementation files would be caught at compile time. Adding new suites requires updating this header and `main.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/tests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/threadmap.c -->
# sources/distributed-fs/ceph-client/tools/lib/perf/threadmap.c

## Purpose
This file implements libperf thread-map allocation, mutation, lookup, and refcounted lifetime management.

## Important APIs, Types, and Functions
- `perf_thread_map__reset` zeroes newly allocated slots and sets `err_thread = -1`.
- `perf_thread_map__realloc` resizes the flexible-array object and resets only newly added entries.
- `perf_thread_map__new_array` allocates `nr_threads` entries, initializes PIDs from the supplied array or `-1`, sets `nr`, and initializes refcount to 1.
- `perf_thread_map__new_dummy` creates a one-entry dummy map.
- `perf_thread_map__delete` warns on unbalanced refcount, frees each `comm`, and frees the map.
- Public accessors/mutators implement get/put, `nr`, `pid`, `comm`, `set_pid`, and linear `idx` lookup.

## Control Flow and State
Maps are contiguous allocations containing header plus flexible array. Ownership is reference-counted. `NULL` maps are treated in accessors as one dummy PID slot for compatibility with callers that omit explicit thread maps.

## Dependencies and Integration Points
It includes public and internal thread-map headers, Linux refcount and bug/assert helpers, libc allocation/string headers, and is consumed by evsel/evlist open/read logic.

## Risks and Test Signals
`perf_thread_map__realloc` assumes growth rather than shrink and can leave callers responsible for preserving old pointers after failed realloc. Accessors do not perform general bounds checks. `comm` strings are freed but not assigned in this file. `test-threadmap.c` validates the primary allocation/refcount/mutation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/threadmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/xyarray.c -->
# sources/distributed-fs/ceph-client/tools/lib/perf/xyarray.c

## Purpose
This file implements the internal `xyarray` rectangular storage helper.

## Important APIs, Types, and Functions
- `xyarray__new(int xlen, int ylen, size_t entry_size)` calculates row size, allocates zeroed storage with `zalloc`, and stores dimensions and entry counts.
- `xyarray__reset(struct xyarray *xy)` zeroes the payload contents.
- `xyarray__delete(struct xyarray *xy)` frees the allocation.

## Control Flow and State
Allocation is a single block containing metadata plus `xlen * ylen * entry_size` bytes. Reset operates only on the payload, preserving dimensions. The header inline accessors compute individual entry addresses.

## Dependencies and Integration Points
It depends on `internal/xyarray.h`, Linux `zalloc`, libc allocation, and string functions. Libperf internals use it where a two-dimensional CPU/thread index space needs compact storage.

## Risks and Test Signals
The allocation math has no explicit overflow checking and uses signed integer dimensions converted into `size_t`. Negative or very large dimensions would be unsafe if not filtered by callers. There is no direct unit test in this subset; coverage is indirect through evsel/evlist internals that allocate matrices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/xyarray.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/__init__.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/__init__.py

## Purpose
This package marker makes `tools/lib/python` importable as a Python package root for helper modules such as `abi`, `feat`, `jobserver`, and `kdoc`.

## Important APIs, Types, and Functions
The file is intentionally empty and exports no names.

## Control Flow and State
There is no runtime logic, state, persistence, or side effect.

## Dependencies and Integration Points
Its integration role is packaging: scripts can import modules beneath this directory when the path is added to `PYTHONPATH` or executed in a context that includes the tools library.

## Risks and Test Signals
The main risk is accidental removal, which can affect package-style imports on Python setups or tooling that still expects explicit package markers. There are no direct tests in this subset; import smoke tests for `abi.*`, `feat.parse_features`, `jobserver`, and `kdoc.*` would validate its packaging role.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/abi/__init__.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/abi/__init__.py

## Purpose
This empty package marker makes the ABI documentation tooling directory importable as `abi`.

## Important APIs, Types, and Functions
The file exports no symbols directly. Functional code lives in `abi_parser.py`, `abi_regex.py`, `helpers.py`, and `system_symbols.py`.

## Control Flow and State
There is no runtime control flow or stored state.

## Dependencies and Integration Points
Modules in this package use absolute imports such as `from abi.helpers import AbiDebug`, so the package marker supports those import paths when `tools/lib/python` is on `PYTHONPATH`.

## Risks and Test Signals
Removing or populating this file incorrectly could break imports or introduce unintended import-time side effects. Basic import tests for `abi.abi_parser`, `abi.abi_regex`, and `abi.system_symbols` cover this marker indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/abi/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/abi/abi_parser.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/abi/abi_parser.py

## Purpose
`AbiParser` parses Linux `Documentation/ABI` files into structured symbol/file records and can emit text or ReST documentation, cross-reference ABI paths, check duplicates, and search symbols.

## Important APIs, Types, and Functions
- Class constants `TAGS` and `XREF` define valid ABI tags and path-like references.
- `__init__` prepares regexes, logger, output options, and mutable indexes: `data`, `what_symbols`, `file_refs`, and `what_refs`.
- `warn` emits line-aware parser warnings.
- `add_symbol` tracks where each `What:` symbol is defined and optional xrefs.
- `_parse_line` is the main tag/state parser for `What`, `Date`, `KernelVersion`, `Contact`, `Description`, and `Users`.
- `parse_readme`, `parse_file`, `_parse_abi`, and `parse_abi` traverse files and populate the database.
- `desc_txt`, `desc_rst`, `xref`, and `doc` emit plain text or ReST with generated cross references.
- `check_issues` warns on duplicate ABI entries.
- `search_symbols` prints matching ABI symbols and metadata.

## Control Flow and State
Parsing is stateful per file through a `Namespace` object (`fdata`) tracking current tag, key, label, indentation, line number, file reference, and active `what` list. New `What:` tags create stable-ish keys from sanitized content; duplicate keys append deterministic pseudo-random letters after seeding with 42. Descriptions preserve indentation and are post-processed for ReST links.

## Dependencies and Integration Points
It depends on `abi.helpers.AbiDebug` and `ABI_DIR`, `argparse.Namespace`, logging, regex, filesystem traversal, and pprint/random helpers. `AbiRegex` subclasses it to add regex generation for sysfs symbol matching. Documentation scripts use `doc()` output.

## Risks and Test Signals
Parsing relies on permissive regular expressions and a mutable class-level `Namespace` pattern, so malformed ABI files can lead to warnings or surprising state carryover if fields are missed. Key generation for duplicates is deterministic only relative to current parsed data order. ReST enrichment must avoid code-block false positives. Tests should cover malformed tags, multi-`What` entries, README handling, duplicate symbols, xref generation, and search output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/abi/abi_parser.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/abi/abi_regex.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/abi/abi_regex.py

## Purpose
`AbiRegex` extends `AbiParser` by converting ABI `What:` sysfs paths into grouped regular expressions for fast matching against live system symbols.

## Important APIs, Types, and Functions
- `escape_symbols`, `leave_others`, and `re_whats` define the transformation pipeline from ABI wildcard syntax to Python regex syntax.
- `regex_append(what, new)` selects a search subgroup from path components and stores a compiled regex.
- `get_regexes(what)` returns candidate regexes for a live sysfs path by checking reversed path components plus the `others` bucket.
- `__init__` accepts optional `search_string`, validates it, and delegates parser initialization.
- `parse_abi` first parses ABI files, then builds `regex_group` from `/sys` `What:` entries and optionally emits debug/subgroup diagnostics.

## Control Flow and State
After base parsing, each ABI symbol is transformed through ordered regex substitutions. The transformed regex is stored in the symbol record and inserted into a subgroup chosen from the most specific usable path component. This reduces live symbol checking from a full scan to a smaller candidate set.

## Dependencies and Integration Points
It imports `AbiParser` and `AbiDebug`. `SystemSymbols` calls `get_regexes` while scanning sysfs. Debug flags from helpers control conversion and subgroup reporting.

## Risks and Test Signals
The substitution order is fragile: temporary marker bytes are used to protect dots, numeric ranges, and wildcard forms before final escaping. Incorrect transforms can overmatch, undermatch, or produce invalid regexes. Group selection skips common names like `devices` and `hwmon`, which improves performance but can affect candidate size. Tests should feed representative ABI wildcards, numeric ranges, alternatives, and invalid patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/abi/abi_regex.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/abi/helpers.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/abi/helpers.py

## Purpose
This helper module defines shared constants and debug bit flags for the ABI documentation parser and live-system symbol checker.

## Important APIs, Types, and Functions
- `ABI_DIR = "Documentation/ABI/"` centralizes the path fragment used by parsers to recognize ABI documentation roots.
- `class AbiDebug` defines integer bit flags for parser state, file opens, structure dumps, undefined-symbol diagnostics, regex conversion, subgroup maps/dicts/sizes, and graph output.
- `DEBUG_HELP` documents the flags for CLI help or diagnostics.

## Control Flow and State
The module has no dynamic control flow beyond class and constant definition.

## Dependencies and Integration Points
It is imported by `abi_parser.py`, `abi_regex.py`, and `system_symbols.py`. The flags are used as bitmasks, so callers can combine debug categories.

## Risks and Test Signals
Flag values are part of the CLI/debug contract; changing values can break saved invocations or documentation. The help string has a typo in "reference", but it does not affect behavior. Import tests and CLI debug-option tests cover this file indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/abi/helpers.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/abi/system_symbols.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/abi/system_symbols.py

## Purpose
`SystemSymbols` scans a live or alternate sysfs tree, builds a path/alias graph, and compares discovered nodes against ABI documentation regexes to report undocumented system symbols.

## Important APIs, Types, and Functions
- `graph_add_file(path, link=None)` inserts real paths and optional symlink aliases into a nested graph.
- `print_graph` emits a bounded tree visualization.
- `_walk(root)` recursively scans files, directories, and symlinks while applying ignore rules.
- `__init__(abi, sysfs="/sys", hints=False)` stores parser references, ignore regexes, graph state, aliases, and discovered files, then walks sysfs.
- `check_file(refs, found)` checks a chunk of sysfs names against candidate ABI regexes.
- `_ref_interactor` traverses graph leaf references and honors optional ABI search filtering.
- `get_fileref` chunks references.
- `check_undefined_symbols(max_workers=None, chunk_size=50, found=None, dry_run=None)` parses ABI regexes, optionally prints graph/dry-run data, dispatches chunk checks through process or thread executors, prints progress, and reports missing symbols.

## Control Flow and State
Initialization is eager: scanning happens in `__init__`. The graph stores `__name` arrays at leaves, with the first entry as canonical path and later entries as symlink aliases. Undefined checks parse ABI data, collect refs, choose process workers unless limited to one, shuffle work for load balance, poll futures with progress output, and accumulate `not_found`.

## Dependencies and Integration Points
It depends on `AbiRegex`-style parser methods (`parse_abi`, `get_regexes`, `re_string`, debug flags), filesystem APIs, `concurrent.futures`, datetime, random shuffle, and stderr/stdout output. It intentionally skips debugfs, tracing, pstore, bpf, cgroup, firmware, modules, and parameter paths.

## Risks and Test Signals
Scanning `/sys` can be expensive and host-specific. `_walk` uses `return` when an ignored path matches, which stops the current directory traversal branch immediately. Multiprocessing serializes parser state and chunks, so memory/performance can regress with large ABI sets. Tests should use a small fixture sysfs tree with files, symlinks, ignored paths, aliases, filtering, dry-run, and hint output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/abi/system_symbols.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/feat/parse_features.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/feat/parse_features.py

## Purpose
`ParseFeature` parses Linux `Documentation/features/**/arch-support.txt` files and generates ReST feature matrices, per-architecture summaries, per-feature summaries, or plain list output.

## Important APIs, Types, and Functions
- Header constants define table labels such as `Feature`, `Kconfig`, `Description`, `Subsystem`, `Status`, and `Architecture`.
- `status_map` orders `ok`, `TODO`, `N/A`, and other statuses.
- `__init__` initializes output width tracking, parse data, debug flags, and message buffer.
- `emit` appends to the output buffer.
- `parse_error` prints warning messages with file/line context.
- `parse_feat_file(fname)` parses one `arch-support.txt`, extracting feature metadata and architecture status rows.
- `parse()` recursively finds feature files under a prefix and populates `data`.
- `output_arch_table`, `output_feature`, `output_matrix`, and `list_arch_features` render different views.
- `matrix_lines` helps render grid-style ReST tables.

## Control Flow and State
Parsing iterates all files under the prefix, ignores anything not named `arch-support.txt`, derives subsystem from the parent directory, updates maximum column widths, and stores records keyed by feature name. Rendering functions reuse `self.msg`; callers should use fresh instances or manage accumulated output carefully.

## Dependencies and Integration Points
It depends on `os`, `re`, `sys`, and recursive `glob.iglob`. Kernel documentation build scripts can use it to turn feature support text files into generated ReST.

## Risks and Test Signals
The parser is strict about expected comment headers and table row syntax. It normalizes `..` status to `---` to avoid special ReST cell meaning. `re.search(r"^\\s*$", line)` appears to match a literal backslash-s rather than whitespace, so blank-line handling mostly relies on other paths. Tests should cover valid files, missing headers, status sorting, long descriptions, list/matrix rendering, and filename-emission mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/feat/parse_features.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/jobserver.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/jobserver.py

## Purpose
This module integrates Python tooling with GNU Make's POSIX jobserver. It claims currently available job tokens, exposes the available parallelism through `PARALLELISM`, runs a child command, and returns tokens afterward.

## Important APIs, Types, and Functions
- `warn(text, *args)` prints warnings to stderr.
- `class JobserverExec` tracks claimed token bytes, reader/writer fds, open state, and computed `claim`.
- `open()` parses `MAKEFLAGS` for `--jobserver*`, supports GNU Make 4.4 `fifo:path` and older `R,W` fd forms, opens a nonblocking reader, drains available tokens, and sets `claim = len(jobs) + 1`.
- `close()` writes claimed tokens back.
- Context manager methods call `open`/`close`.
- `run(cmd, *args, **pwargs)` sets `PARALLELISM` when a claim exists and runs the command with `subprocess.call`.

## Control Flow and State
The object only tries to open once per lifecycle. Token bytes are retained in `self.jobs` until `close`. If setup or reads fail, it warns, clears/returns tokens as needed, and leaves `claim` falsey so children choose their own parallelism.

## Dependencies and Integration Points
It depends on `MAKEFLAGS`, `/proc/self/fd` for fd duplication, POSIX nonblocking pipe semantics, and subprocess execution. It is designed for kernel build scripts that need nested parallelism without oversubscribing the parent make.

## Risks and Test Signals
Correct token return is critical; lost or extra writes can stall or corrupt the jobserver. The code handles `EWOULDBLOCK` as completion but only warns on other pipe anomalies. It mutates global `os.environ["PARALLELISM"]`. Tests should mock `MAKEFLAGS`, fd pipes, fifo paths, malformed options, read errors, context manager cleanup, and child environment propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/jobserver.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/__init__.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/__init__.py

## Purpose
This empty marker makes the kernel-doc helper directory importable as the `kdoc` Python package.

## Important APIs, Types, and Functions
The file defines no names. Functional modules include tokenization, parser support, file orchestration, output formatting, YAML fixtures, and list transforms.

## Control Flow and State
There is no runtime logic, mutable state, or persistence behavior.

## Dependencies and Integration Points
Several modules use package imports such as `from kdoc.kdoc_parser import KernelDoc` and `from kdoc.kdoc_output import OutputFormat`, so this marker supports package-style imports.

## Risks and Test Signals
Adding import-time work here would slow or alter all kdoc CLI invocations. Removing it can break package imports depending on Python execution context. Basic import smoke tests for `kdoc.c_lex`, `kdoc.kdoc_files`, and `kdoc.kdoc_output` cover it indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/c_lex.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/c_lex.py

## Purpose
This module provides C tokenization and delimiter-aware matching/substitution helpers for the Python kernel-doc implementation. It supports macro transforms, visibility filtering, nested argument extraction, and replacements that are difficult with Python's regular expressions alone.

## Important APIs, Types, and Functions
- `tokenizer_set_log(logger, prefix="")` installs a prefixed logger adapter.
- `CToken` defines enum-like token kinds and stores token value, source position, and bracket/paren/brace nesting levels.
- `RE_SCANNER_LIST`, `fill_re_scanner`, `RE_CONT`, `RE_COMMENT_START`, and `RE_SCANNER` define tokenization regexes.
- `CTokenizer` converts source strings or token lists to token streams; `__str__` reconstructs visible code while honoring `/* private: */` and `/* public: */` comments.
- `CTokenArgs` parses replacement backrefs like `\0`, `\1`, and greedy `\4+`, extracts grouped macro arguments, and generates replacement tokens.
- `CMatch` finds balanced nested delimiter blocks after a name regex and supports `search` and `sub` operations over strings or tokenizers.

## Control Flow and State
Tokenization strips line continuations, emits tokens while tracking nesting levels, and logs mismatches. Reconstruction keeps a stack of visibility booleans by nesting depth. `CMatch` scans tokens until a target name is found, waits for the expected opening delimiter, then yields only balanced ranges; substitutions splice token slices and replacement tokens into a new tokenizer.

## Dependencies and Integration Points
It depends on logging, regex, copy, and `KernRe`. It is consumed by kdoc parser/transform modules that need to normalize complex C declarations and macros before documentation extraction.

## Risks and Test Signals
Regex tokenization is intentionally approximate and can mis-handle unusual C extensions. Visibility filtering depends on comment text and nesting. `CTokenArgs.groups` references `sub_str` in one error path where only `self.sub_str` is in scope, which could mask an intended diagnostic. Tests should cover strings/chars/comments, nested macro arguments, greedy replacements, private/public sections, unmatched delimiters, and token-level substitution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/c_lex.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/enrich_formatter.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/enrich_formatter.py

## Purpose
This module defines an argparse help formatter that preserves raw description line breaks and optionally enriches marked-up help text for terminals.

## Important APIs, Types, and Functions
- `class EnrichFormatter(argparse.HelpFormatter)` is the only public class.
- `__init__` records whether stdout is a TTY.
- `enrich_text(text)` converts ReST inline literals ``text`` to ANSI bold only on TTY output.
- `_fill_text` preserves existing description line breaks while applying enrichment.
- `_format_usage` constructs usage text with positional arguments uppercased and enriched.
- `_format_action_invocation` enriches positional argument names and returns option strings for flags.

## Control Flow and State
Formatting is synchronous and stateless except for `_tty` and argparse's inherited formatter state. Terminal enrichment is disabled for non-TTY output to keep generated help plain.

## Dependencies and Integration Points
It depends on `argparse`, `re`, and `sys`. Kernel-doc command-line tools can use it as `formatter_class` to make positional arguments and inline literals easier to read.

## Risks and Test Signals
The custom `_format_usage` is simpler than argparse's default and may omit some advanced grouping/nargs formatting. ANSI insertion depends on stdout, not necessarily the destination argparse writes to. Tests should cover TTY/non-TTY behavior, options with arguments, positionals, descriptions with multiple lines, and literal markup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/enrich_formatter.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_files.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_files.py

## Purpose
This module orchestrates kernel-doc parsing across files and directories. It finds C sources, configures parser/output behavior, parses documentation and exported symbols, and yields formatted messages.

## Important APIs, Types, and Functions
- `GlobSourceFiles` recursively yields files with configured extensions from explicit files or directories, optionally under `srctree`.
- `KdocConfig` stores verbosity, warning policy, warning categories, logger, and a replaceable `warning` callback.
- `KernelFiles` is the main controller.
- `KernelFiles.parse_file` runs `KernelDoc.parse_kdoc`, caches entries and export tables, and optionally stores source for YAML tests.
- `process_export_file` parses only `EXPORT_SYMBOL*` macros.
- `file_not_found_cb`, `warning`, and `error` count diagnostics.
- `__init__` resolves verbosity from `KBUILD_VERBOSE`, warning mode from arguments/env, output style, transforms, YAML test output, `SRCTREE`, and internal caches.
- `parse(file_list, export_file=None)` processes input docs and export-only files.
- `msg(...)` applies filters and yields `(fname, msg)` output tuples or writes YAML test files.

## Control Flow and State
The controller caches parsed files in `files`, export-parsed files in `export_files`, per-file parser results in `results`, and export symbol sets in `export_table`. Output filtering combines explicit symbols, exported/internal mode, no-symbol exclusions, line-number mode, and doc-section suppression.

## Dependencies and Integration Points
It depends on `KernelDoc`, `CTransforms`, `OutputFormat`, and `KDocTestFile` modules. It also reads build environment variables and is the primary bridge between CLI arguments and parser/output modules.

## Risks and Test Signals
The `KCFLAGS` `-Werror` regex includes a trailing slash in the pattern, likely preventing intended matches. `export_file` defaults can cause current file exports to be parsed repeatedly unless caches work correctly. Directory traversal follows real directories but not symlink directories. Tests should cover file discovery, missing files, caching, export/internal filters, env-driven verbosity/werror, YAML mode, and no-doc-section filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_files.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_item.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_item.py

## Purpose
`KdocItem` is the structured data container passed from the kernel-doc parser to output formatters.

## Important APIs, Types, and Functions
- `__init__(name, fname, type, start_line, **other_stuff)` initializes core metadata, section maps, parameter lists/descriptions/types, warning list, and stores unknown fields in `other_stuff`.
- `get` and `__getitem__` provide dictionary-like access to optional fields.
- `__repr__` returns a compact identifier.
- `from_dict` reconstructs an item from a plain dictionary, merging nested `other_stuff`.
- `set_sections` and `set_params` update section and parameter tracking data.

## Control Flow and State
Known parser fields become direct attributes; all other parser-specific data remains in `other_stuff` for backward compatibility. Output modules read both direct attributes and optional fields such as `purpose`, `definition`, `full_proto`, or `default_val`.

## Dependencies and Integration Points
It has no external imports. It integrates with `kdoc_parser` producers and `kdoc_output` consumers.

## Risks and Test Signals
Using the parameter name `type` shadows the built-in but is consistent with parser terminology. Unknown fields are intentionally loose, so misspelled keys can silently land in `other_stuff` and later appear missing. Tests should cover conversion from dictionaries, section/parameter updates, optional access, and formatter expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_item.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_output.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_output.py

## Purpose
This module formats parsed kernel-doc `KdocItem` objects into ReST or man/troff output. It defines a filtering base class and concrete output styles for Sphinx documentation and man pages.

## Important APIs, Types, and Functions
- Module-level `KernRe` regexes detect kernel-doc inline markup for constants, functions, parameters, environment variables, enum/struct/typedef/union references, members, and function pointers.
- `OutputFormat` defines output modes (`OUTPUT_ALL`, `OUTPUT_INCLUDE`, `OUTPUT_EXPORTED`, `OUTPUT_INTERNAL`), filter state, warning dispatch, `check_doc`, `check_declaration`, `msg`, and `output_symbols`. Virtual `out_*` methods are overridden by subclasses.
- `RestFormat` converts docs into ReST directives such as `.. c:function::`, `.. c:enum::`, `.. c:macro::`, `.. c:type::`, and `.. c:struct::`. It highlights inline references, preserves literal/code blocks, emits optional line markers, and formats parameters, members, sections, defaults, and definitions.
- `ManFormat` emits troff man pages with `.TH`, `.SH`, `.IP`, `.BI`, `.TS`, and formatting escapes. It handles dates from `KBUILD_BUILD_TIMESTAMP`, module names, SEE ALSO tails, grid/simple table conversion, code blocks, lists, functions, enums, vars, typedefs, structs, and doc sections.

## Control Flow and State
Formatting is item-driven. `set_filter` configures which symbols are eligible. `output_symbols` calls `set_symbols`, then dispatches each item through `msg`. `RestFormat` accumulates output in `self.data` with a mutable `lineprefix`. `ManFormat.msg` calls the base dispatch then appends a tail for every emitted page. Both subclasses transform inline markup through ordered regex substitutions before writing output.

## Dependencies and Integration Points
It depends on `KernelDoc` constants, `type_param`, and `KernRe`. `KernelFiles` instantiates an output style and calls `output_symbols`. The output is intended for kernel documentation builds and man-page generation.

## Risks and Test Signals
Filtering behavior is shared across both formats, so mode bugs affect all output. ReST highlighting must avoid mutating literal blocks; man highlighting must escape leading dots and translate tables/code/list constructs correctly. `ManFormat.msg` appends a SEE ALSO tail even if base dispatch produced empty data, which may need care for filtered items. Some local variables such as `module` are assigned but unused. Tests should cover every `KdocItem` type, filters, no-symbol exclusions, line numbers, literal/code blocks, table conversion, function-pointer signatures, missing descriptions, and timestamp formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_output.py -->
