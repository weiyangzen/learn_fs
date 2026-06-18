# subset-b-006767

Grouped research for perf utility metric parsing, event parsing, mmap/namespace helpers, hook/probe support, and architecture register mappings.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/metricgroup.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/metricgroup.c

Purpose: implements perf's metric-group expansion layer, translating PMU metric table rows into parsed `evsel` event lists and attaching `metric_expr` records to display-triggering events. It is the bridge between generated `pmu-events` metric metadata, expression parsing, event parsing, and `perf stat` shadow metric output.

Important APIs/types/functions: public entry points are `metricgroup__lookup`, `metricgroup__rblist_init`, `metricgroup__rblist_exit`, `metricgroup__for_each_metric`, `metricgroup__parse_groups`, `metricgroup__parse_groups_test`, `metricgroup__has_metric_or_groups`, `metricgroups__topdown_max_level`, weak `arch_get_runtimeparam`, and `metricgroup__copy_metric_events`. Internal `struct metric` tracks one metric under construction, including expression context, PMU, modifier, threshold, unit, referenced metrics, grouping policy, and parsed evlist. The rblist node type is `struct metric_event`; each node owns a list of heap `struct metric_expr` objects that stat output later evaluates.

Control flow: metric lookup is keyed by `evsel`, normalized through `metric_leader` for duplicated uncore aliases. `metricgroup__parse_groups` finds the current PMU metric table, then `parse_groups` expands a comma list like `IPC,TopdownL1` through `metricgroup__add_metric_list`. `add_metric` handles runtime-expanded metrics containing `?`; `__add_metric` parses expression IDs, detects recursive metric references through a stack of `visited_metric`, resolves nested metric names, and appends root metrics to a temporary list. Metrics are sorted by event-count to maximize sharing. If merge is allowed, non-grouped metrics without modifiers are folded into a combined expression context and parsed once. Each metric then either reuses a previous superset evlist, uses the combined evlist, or calls `parse_ids` to synthesize an event string and invoke `__parse_events`. Finally `setup_metric_events` maps expression IDs back to `evsel`s, `pick_display_evsel` chooses a non-tool, least-shared display event, and a `metric_expr` is attached to the destination `metric_event`.

State and persistence: all state is in memory. `metricgroup__rblist_init` installs rblist callbacks and `metric_event_delete` frees metric names, refs, event arrays, and expressions. `decode_all_metric_ids` mutates parsed evsel `metric_id` strings back from parser-safe encoding and may replace display names. `metricgroup__copy_metric_events` deep-copies metric-expression metadata across cloned evlists, especially for cgroup stat runs. No state is persisted outside the evlist/rblist lifetime.

Dependencies: depends on `expr` for metric expression ID discovery, `pmu-events` tables, PMU scanning/matching, `parse-events` for final event-string parsing, `tool_pmu` for synthetic tool events such as `duration_time`, `rblist`, `strbuf`, `smt`, sysctl NMI watchdog checks, cgroup-aware evlist cloning, and architecture weak hooks for runtime parameter expansion and grouping constraints.

Integration points: called by perf stat metric options, tests, and cgroup stat paths. It consumes generated metric metadata from architecture and system PMU tables, supports default metric grouping names, respects metric modifiers, handles hybrid PMU filtering, and marks evsels with `collect_stat`, `metric_leader`, `default_show_events`, and display metric expressions used by later stat output.

Risks: event-string construction encodes characters that `parse-events` cannot parse; changes to `code_characters`, PMU alias syntax, or `metric-id` decoding can break metric/event association. Recursive metric references must be caught or expansion loops. Merging improves multiplexing behavior but is sensitive to modifiers, PMU names, tool events, and duplicate uncore aliases. NMI-watchdog and SMT grouping rules can silently change group layout. Error paths allocate many small arrays; missing cleanup creates leaks or dangling refs in long-running tests. Test signals include metric parser tests via `metricgroup__parse_groups_test`, `perf stat -M` smoke tests for named/default/topdown metrics, hybrid PMU metric runs, cgroup metric copies, and negative tests for unknown/recursive metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/metricgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/metricgroup.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/metricgroup.h

Purpose: declares the public metric-group interface and the in-memory data structures that connect parsed `evsel`s to metric expressions for perf stat output.

Important APIs/types/functions: `struct metric_event` is an rbtree node keyed by `evsel`, with `is_default` and a `head` list of `metric_expr`. `struct metric_ref` stores referenced metric name/expression pairs for recursive expression evaluation. `struct metric_expr` stores the expression string, display name, optional threshold, scale/unit, default group name, null-terminated event pointer array, null-terminated referenced metric array, and runtime value substituted for `?`. Declared functions cover metric lookup, parsing metric groups into an evlist, test parsing, iteration over metrics, presence checks, topdown max-level discovery, runtime parameter hook, rblist lifecycle, and cgroup/copy support.

Control flow: this header has no executable flow, but its ownership rules drive `metricgroup.c`: the evlist owns a metric-events rblist, each rblist node owns its expression list, and each expression points at evsels that must remain valid for the evlist lifetime.

State and persistence: all types describe transient in-memory state. String fields often point to generated PMU metric table storage, while `metric_name`, `metric_refs`, and `metric_events` may be heap-owned by the metricgroup layer. No on-disk state is defined.

Dependencies: includes Linux list/rbtree primitives, booleans, and generated `pmu-events.h`. It forward-declares perf core types (`evlist`, `evsel`, `rblist`, `cgroup`) to keep callers decoupled from implementation headers.

Integration points: used by evlist/stat code that initializes metric rblists, looks up metric expressions by evsel, parses user metric requests, and clones metric metadata across cgroup evlists.

Risks: the structures expose ownership-sensitive pointers rather than opaque handles, so callers must preserve evsel lifetime and use the rblist lifecycle helpers. Typo risk exists in user-visible comments (`meric`). Test signals are compile coverage, metricgroup unit tests, and memory/leak checks around metric parse/free/copy cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/metricgroup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/mmap.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/mmap.c

Purpose: wraps libperf ring-buffer mmap handling with perf tool features: CPU affinity masks, optional compression staging buffers, optional AIO write buffers, auxtrace mmap hooks, and buffer draining.

Important APIs/types/functions: `mmap__mmap_len` delegates ring length calculation to libperf. Weak auxtrace hooks (`auxtrace_mmap__mmap`, `auxtrace_mmap__munmap`, parameter init/set-idx) allow auxtrace-enabled builds to override behavior. AIO helpers allocate per-control-block data buffers, optionally bind them to NUMA nodes, assign AIO priorities, and release them. Public `mmap__mmap` creates the perf ring buffer, affinity mask, zstd state, compression staging mmap, auxtrace mmap, and AIO buffers. `mmap__munmap` tears them down. `perf_mmap__push` drains ring data in one or two chunks across wraparound and calls a caller-supplied push callback.

Control flow: mapping starts with `perf_mmap__mmap`; affinity setup is skipped for system affinity and otherwise builds CPU or NUMA-node masks. zstd is initialized before optional compression staging allocation. Auxtrace mapping is attempted before AIO setup. Unmapping frees the bitmap, compression state, AIO resources, main data buffer, and auxtrace state. `perf_mmap__push` reads the head, initializes a read transaction, handles `-EAGAIN` as "try later", pushes wrapped and linear portions, advances `start`, records `prev`, and consumes the buffer.

State and persistence: state lives in `struct mmap`: `core` libperf mmap state, optional `aio` arrays, `affinity_mask`, `data` compression buffer, `file`, and zstd data. It reflects live kernel mmap buffers and anonymous user buffers only; nothing is persisted.

Dependencies: depends on libperf `perf_mmap`, Linux bitmap helpers, `page_size`, zstd compression helpers, CPU/NUMA topology utilities, optional `HAVE_AIO_SUPPORT`, optional `HAVE_LIBNUMA_SUPPORT`, auxtrace, and debug logging.

Integration points: used by record/top/report-like paths that read perf ring buffers. Compression and AIO fields are consumed by perf data writing code, while auxtrace hooks connect Intel PT/ARM SPE style auxiliary buffers.

Risks: partial setup failures can leave resources allocated unless callers follow cleanup paths. NUMA binding uses `node_index + 1 + 1`, so mask sizing changes need care. `perf_mmap__push` assumes callbacks can handle exact buffer fragments and must not consume after errors. Test signals include perf record smoke tests with and without compression/AIO/auxtrace, ring wraparound reads, NUMA affinity debug output at `verbose == 2`, and leak checks on failed setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/mmap.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/mmap.h

Purpose: declares perf's higher-level mmap wrapper around libperf ring buffers, including optional AIO, auxtrace, compression, and affinity metadata.

Important APIs/types/functions: `struct mmap_cpu_mask` stores a bitmap and bit count. `MMAP_CPU_MASK_BYTES` computes its byte size. `struct mmap` embeds `struct perf_mmap core`, `struct auxtrace_mmap`, optional AIO control/data arrays, affinity mask, compression buffer pointer, perf data file pointer, and zstd state. `struct mmap_params` wraps libperf params plus AIO count, affinity mode, flush mode, compression level, and auxtrace mmap params. Public functions are `mmap__mmap`, `mmap__munmap`, `perf_mmap__read_forward` declaration, `perf_mmap__push`, `mmap__mmap_len`, and `mmap_cpu_mask__scnprintf`.

Control flow: no local execution; callers allocate/initialize `struct mmap`, pass params into `mmap__mmap`, read/push data, then call `mmap__munmap`.

State and persistence: describes live process memory mappings and buffers tied to active perf events. The caller owns the struct storage; helpers own the dynamic subfields after successful setup.

Dependencies: includes internal libperf mmap, Linux bitops/types, perf cpumap, optional `<aio.h>`, auxtrace, and compression helpers.

Integration points: included by evlist/recording code and data writers that coordinate mmap buffers. It is also the stable boundary for auxtrace and compression support.

Risks: ABI is internal but broad; changing field layout affects many perf utility users. Callers must respect ownership and zero/cleanup expectations. Test signals are build coverage across AIO/non-AIO and auxtrace/non-auxtrace configurations plus record-mode runtime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/mmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/mutex.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/mutex.c

Purpose: provides perf-local wrappers for `pthread_mutex_t` and `pthread_cond_t` that centralize attribute setup and error reporting.

Important APIs/types/functions: `mutex_init`, `mutex_init_pshared`, and `mutex_init_recursive` share `__mutex_init`, which creates attributes, uses error-checking mutexes in non-`NDEBUG` builds, optionally sets recursive or process-shared type, initializes the mutex, and destroys attributes. `mutex_destroy`, `mutex_lock`, `mutex_unlock`, and `mutex_trylock` wrap pthread calls. `cond_init`, `cond_init_pshared`, `cond_destroy`, `cond_wait`, `cond_signal`, and `cond_broadcast` wrap condition variables. `check_err` prints pthread error strings through perf debug logging.

Control flow: initialization constructs and tears down pthread attribute objects around the pthread primitive. Runtime lock/unlock/wait/signal calls only forward and log nonzero errors. `mutex_trylock` returns true on success, false on `EBUSY`, and false after logging other errors.

State and persistence: only initializes/destroys caller-owned synchronization objects. No global state is kept.

Dependencies: depends on pthreads, `debug.h`, Linux string helpers, and errno constants. The header's thread-safety annotations are suppressed for lock/unlock bodies with `NO_THREAD_SAFETY_ANALYSIS`.

Integration points: used by perf code that wants consistent debug diagnostics and optional static thread-safety annotations without using pthread APIs directly.

Risks: errors are logged but not fatal, so caller logic must not assume initialization succeeded after severe pthread failures. Recursive initialization overrides error-checking type. Process-shared primitives require shared storage and platform support. Test signals include build coverage with/without `NDEBUG`, simple lock/trylock/cond smoke tests, and process-shared usage tests where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/mutex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/mutex.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/mutex.h

Purpose: defines perf synchronization wrapper types and optional Clang/GCC thread-safety annotation macros.

Important APIs/types/functions: feature-detects attributes such as `guarded_by`, `lockable`, `exclusive_lock_function`, `unlock_function`, and `no_thread_safety_analysis`, falling back to empty macros when unavailable. `struct mutex` wraps `pthread_mutex_t` and is marked `LOCKABLE` when supported. `struct cond` wraps `pthread_cond_t`. Function declarations cover normal, process-shared, and recursive mutex initialization; destroy/lock/unlock/trylock; normal and process-shared condition initialization; destroy/wait/signal/broadcast.

Control flow: no executable flow. The annotations document lock requirements to static analyzers while leaving compiled behavior to `mutex.c`.

State and persistence: caller-owned pthread objects only. No persistent state.

Dependencies: pthreads and booleans. It intentionally keeps the wrapper thin so existing pthread semantics remain recognizable.

Integration points: included by shared perf utilities needing annotated locking contracts. `cond_wait` is annotated as requiring the associated mutex.

Risks: annotation support differs by compiler; code must compile correctly when all macros are empty. Passing uninitialized wrappers or mixing raw pthread operations with wrapper annotations can defeat diagnostics. Test signals are compilation on GCC/Clang versions and runtime synchronization smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/mutex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/namespaces.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/namespaces.c

Purpose: handles perf namespace metadata and process namespace information, especially mount-namespace switching for resolving paths as seen by profiled processes.

Important APIs/types/functions: `perf_ns__name` maps namespace indexes to names. `namespaces__new`/`namespaces__free` allocate a variable-length `struct namespaces` from `PERF_RECORD_NAMESPACES`. `nsinfo__new`, `nsinfo__copy`, `nsinfo__get`, and `nsinfo__put` manage refcounted `struct nsinfo`. Accessors expose pid, tgid, nstgid, need-setns, and pid-namespace status. `nsinfo__mountns_enter` opens current and target mount namespaces, calls `setns`, and records old cwd; `nsinfo__mountns_exit` restores namespace and cwd. `nsinfo__realpath`, `nsinfo__stat`, and `nsinfo__is_in_root_namespace` provide namespace-aware helpers.

Control flow: `nsinfo__new(pid)` initializes default pid/tgid/nstgid, then `nsinfo__init` compares `/proc/self/ns/mnt` with `/proc/<pid>/ns/mnt`; differing inodes cause `need_setns` and store the target namespace path. It also parses `/proc/<pid>/status` for `Tgid:` and `NStgid:` to identify innermost tgid and pid namespace membership. Path operations wrap `realpath` or `stat` between mount namespace enter/exit calls when required.

State and persistence: `nsinfo` stores pid-derived namespace state, a heap `mntns_path`, and a refcount. `namespaces` stores copied namespace link info and an `end_time`. State is process memory only and may become stale if the target process exits or changes namespaces.

Dependencies: `/proc`, `stat`, `open`, `setns`, `getcwd`, `chdir`, Linux refcount/rc-check helpers, perf event namespace record structures, and zalloc utilities.

Integration points: symbol, DSO, map, build-id, and path resolution code use `nsinfo` to inspect files in the target process's mount namespace. Event processing uses `namespaces` records to track namespace lifetime.

Risks: target processes can exit while `/proc` is being read; the code tolerates init failure by clearing `need_setns`. `setns` and cwd restoration failures can affect subsequent path lookups. `nsinfo__get_nspid` depends on `/proc/<pid>/status` formatting and tab positions. Test signals include namespace unit tests, perf record/report against containers, mount namespace path resolution, root namespace detection, and leak/refcount checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/namespaces.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/namespaces.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/namespaces.h

Purpose: declares namespace metadata and refcounted process namespace information for perf utilities.

Important APIs/types/functions: `struct namespaces` contains a list node, `end_time`, and flexible `perf_ns_link_info` array. `DECLARE_RC_STRUCT(nsinfo)` defines pid, tgid, nstgid, `need_setns`, `in_pidns`, mount namespace path, and refcount. `struct nscookie` stores old/new namespace fds and old cwd for restoration. Public functions allocate/free/copy/get/put namespace objects, inspect and mutate flags, enter/exit mount namespaces, perform namespace-aware `realpath`/`stat`, check root namespace status, and map namespace index to name. If libc lacks setns support, it declares a fallback `setns`.

Control flow: no local execution; it defines the lifecycle contract for `namespaces.c`.

State and persistence: structs represent transient snapshots of `/proc` namespace data and live namespace-switch cookies. Callers must balance `nsinfo__get`/`put` and `mountns_enter`/`exit`.

Dependencies: sys/types/stat, Linux perf event namespace link info, refcount, internal rc-check helpers, and list support.

Integration points: included by map/symbol/session code that needs namespace-aware filesystem resolution and by event code handling namespace records.

Risks: flexible array allocation must size by namespace count. `nsinfo__zput` macro assumes an lvalue variable. Namespace switching is process-wide, so callers must avoid concurrent path operations without coordination. Test signals include compile coverage without `HAVE_SETNS_SUPPORT`, refcount checks, and namespace path lookup tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/namespaces.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/off_cpu.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/off_cpu.h

Purpose: defines the public off-CPU profiling interface and constants used when BPF skeleton support is available.

Important APIs/types/functions: `OFFCPU_EVENT` is the synthetic event name `"offcpu-time"`. `OFFCPU_SAMPLE_TYPES` declares required sample fields: identifier, IP, TID, time, ID, CPU, period, raw data, and cgroup. `OFFCPU_THRESH` is a 500,000,000 ns threshold. When `HAVE_BPF_SKEL` is set, `off_cpu_prepare` and `off_cpu_write` are declared; otherwise inline stubs return `-1`.

Control flow: no runtime logic in supported builds beyond declarations. Unsupported builds fail fast through stubs so callers can disable or reject off-CPU mode.

State and persistence: no state is stored here. The eventual implementation prepares evlists/record options and writes data into a perf session.

Dependencies: Linux perf event sample flags and forward-declared perf `evlist`, `target`, `perf_session`, and `record_opts`.

Integration points: included by perf record/session code for off-CPU sampling. The event name and sample type constants are shared contracts between command-line setup, BPF collection, and data writing.

Risks: stale sample-type bits would break decoder expectations for raw off-CPU records. Stubs returning `-1` require callers to present useful diagnostics. Test signals include build coverage with and without `HAVE_BPF_SKEL`, off-CPU record smoke tests, and perf data decode checks for expected sample fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/off_cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/ordered-events.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/ordered-events.c

Purpose: maintains a timestamp-ordered queue of perf events so session processing can tolerate moderately out-of-order input and deliver records in time order.

Important APIs/types/functions: `ordered_events__queue` queues a record with timestamp, file offset, and file path. `ordered_events__flush` and `ordered_events__flush_time` deliver queued records according to final, round, half, top, or explicit time policies. `ordered_events__delete` moves delivered nodes to a cache. `ordered_events__init`, `ordered_events__free`, `ordered_events__reinit`, and `ordered_events__first_time` manage lifecycle. Internal allocation uses 64 KiB buffers of `struct ordered_event` plus optional duplicated perf records when `copy_on_queue` is enabled.

Control flow: `queue_event` inserts new nodes near `oe->last`, optimizing for nearly sorted input while preserving ascending timestamps. `alloc_event` reuses cached nodes, then current buffer slots, then allocates a new buffer under `max_alloc_size`; it also duplicates input records when requested. `ordered_events__queue` rejects zero or all-ones timestamps, increments unordered counters for timestamps older than `last_flush`, flushes half the queue on allocation failure, and retries. Flushing computes `next_flush`, iterates until timestamps exceed the limit, calls the client deliver callback, deletes delivered nodes, updates progress and last-flush state, then repairs `oe->last`.

State and persistence: `struct ordered_events` holds the ordered event list, cache list, allocation buffers, allocation accounting, flush timestamps, counters, callback, copy mode, and caller data. State is entirely in memory and freed through `ordered_events__free`.

Dependencies: Linux lists, perf session abort checks, debug ordered-event logging, `ui_progress`, `memdup`, and caller-supplied delivery logic.

Integration points: used by perf session processing for ordered sample delivery, especially `perf report/script` paths consuming perf.data records. File offset/path fields support diagnostics and data provenance during processing.

Risks: allocation accounting is shared between duplicated records and buffers; incorrect accounting can defeat limits or underflow. `ordered_events__free` must free only allocated slots in the current buffer. Delivery callbacks returning errors stop flushing and leave remaining records queued. Test signals include ordered-events unit tests, final/half/time flush scenarios, `copy_on_queue` memory tests, unordered-event counters, allocation-limit retry behavior, and report/script runs on out-of-order perf.data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/ordered-events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/ordered-events.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/ordered-events.h

Purpose: declares timestamp-ordered perf event queue types and lifecycle/flush APIs.

Important APIs/types/functions: `struct ordered_event` stores timestamp, file offset/path, perf event pointer, and list node. `enum oe_flush` defines none, final, round, half, top, and time flush modes. `ordered_events__deliver_t` is the callback signature. `struct ordered_events_buffer` owns flexible arrays of event nodes. `struct ordered_events` stores flush timestamps, allocation limits/accounting, event/cache/free lists, current buffer, last node, deliver callback, counters, copy mode, and caller data. Inline setters configure allocation size and copy-on-queue; an inline getter exposes `last_flush`.

Control flow: callers initialize with a delivery callback, queue events, flush by policy, and free/reinit when done.

State and persistence: queue state is mutable and in memory only. If `copy_on_queue` is false, queued `event` pointers must remain valid until delivery; if true, this layer owns duplicates.

Dependencies: Linux types and list support through included headers in users. `union perf_event` is forward-used.

Integration points: session processing and perf.data readers include this header to buffer samples before ordered delivery.

Risks: wrong copy-on-queue mode causes dangling event pointers or unnecessary memory pressure. `max_alloc_size` defaults to unlimited until explicitly set. Test signals are compile coverage, queue/flush unit tests, and session processing regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/ordered-events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/parse-branch-options.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/parse-branch-options.c

Purpose: parses branch stack sampling option strings used by perf record/report options into `PERF_SAMPLE_BRANCH_*` mode bits.

Important APIs/types/functions: `branch_modes` maps names such as `u`, `k`, `hv`, `any`, `any_call`, `any_ret`, `ind_call`, transaction filters, `cond`, `ind_jmp`, `call`, `no_flags`, `no_cycles`, `save_type`, `stack`, `hw_index`, `priv`, and `counter` to kernel branch-sample flags. `parse_branch_str` parses a comma-separated string into a mode bitmask. `parse_branch_stack` is the `parse-options` callback for `--branch-filter`/related options.

Control flow: null strings default to `PERF_SAMPLE_BRANCH_ANY`. Non-null strings are duplicated, split on commas, looked up case-insensitively, ORed into `*mode`, and freed. If only privilege-level mode bits were supplied, it adds default `ANY`. The option callback rejects double-setting to avoid mixing `-b` and `-j`.

State and persistence: only mutates the caller-provided `__u64` mode. No global state.

Dependencies: kernel branch sample constants, perf debug logging, perf event definitions, and subcmd parse-options.

Integration points: used by perf record branch sampling options and by parse-events config term `branch_type`, which delegates to `parse_branch_str`.

Risks: mode names are user-facing and must match documentation. New kernel flags require table updates. Empty elements are not specially ignored. Test signals include option parser tests for each branch filter, duplicate option rejection, default privilege-only behavior, and invalid-name diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/parse-branch-options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/parse-branch-options.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/parse-branch-options.h

Purpose: declares branch-stack option parsing helpers.

Important APIs/types/functions: exposes `parse_branch_stack` for subcmd option callbacks and `parse_branch_str` for direct conversion of comma-separated branch filter strings into kernel branch sample masks.

Control flow: none. Callers pass storage through `struct option` or an explicit `__u64 *`.

State and persistence: no state; functions mutate caller-owned masks.

Dependencies: stdint for integer types and `struct option` through including users.

Integration points: perf record options and parse-events term handling.

Risks: the header uses `__u64` without directly including its defining Linux type header, relying on include order. Test signals are compile coverage in all users and branch option parser tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/parse-branch-options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/parse-events.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/parse-events.c

Purpose: implements perf's event parser runtime: turning parsed lexer/grammar structures into `evsel`s, configuring `perf_event_attr`, resolving PMUs and aliases, applying modifiers and filters, sorting/regrouping events by PMU constraints, and reporting syntax/configuration errors.

Important APIs/types/functions: public APIs include `event_type`, `parse_events__decode_legacy_cache`, `parse_events__filter_pmu`, `parse_events_add_tracepoint`, `parse_events_add_numeric`, `parse_events_add_breakpoint`, `parse_events_multi_pmu_add`, `parse_events_multi_pmu_add_or_add_pmu`, modifier helpers, `__parse_events`, `parse_event`, option callbacks, filter callbacks, parse term constructors/destructors, and error APIs. Internal `__add_event` centralizes evsel creation, CPU map selection, PMU discovery, metric id/name copying, config-term transfer, and wildcard linkage.

Control flow: lexer/parser build event/term lists, then semantic actions call helpers here. Numeric and raw events initialize `perf_event_attr` directly; PMU events copy terms, fix raw terms late against the chosen PMU, apply hardcoded config terms, resolve aliases through `perf_pmu__check_alias`, record user-changed config bits, call `perf_pmu__config`, apply CPU terms, and create evsels. Tracepoints support exact and globbed system/event names. Breakpoints parse `mem:` syntax, type bits, and default lengths. After parsing, `parse_events__sort_events_and_fix_groups` calls arch-required event injection, computes group PMU names, sorts by group/user/PMU constraints, splits groups that span PMUs, forces architecture-required groups, and warns on regrouping when requested.

State and persistence: state is transient in `struct parse_events_state`, `parse_events_terms`, temporary lists, and the destination evlist. `config_term_shrinked` is a module-global mode that restricts terms usable in `perf stat`. Error entries own heap strings until `parse_events_error__exit`. Created evsels persist in the evlist until caller deletion.

Dependencies: generated flex/bison headers, evlist/evsel, PMU registry and alias/config helpers, cpumaps, tracepoint PMU enumeration, branch parser, BPF filter parser, stat config, UI warnings, tracing-path diagnostics, architecture weak hooks (`arch_evlist__cmp`, `arch_evlist__add_required_events`, and external must-be-in-group checks), kernel perf constants, and subcmd parse-options.

Integration points: the central event parser for `-e`, metricgroup-generated event strings, tracepoint filters, UID filters, `--exclude-perf`, breakpoint events, PMU aliases, hybrid PMU wildcards, and test fake-PMU/fake-tracepoint modes. It also supplies helper term parsing for sysfs and PMU alias logic.

Risks: parser semantics are broad and user-facing. PMU wildcard expansion, hybrid extended types, CPU term validation, metric-id handling, alias rewriting, and regrouping can all change command behavior. Error paths intentionally splice partial lists for cleanup; callers must delete evlists on failure. `parse_events__shrink_config_terms` is global. Tracepoint and BPF filtering choose paths heuristically, with UID filters forced to BPF. Test signals include `perf test` event parser cases, PMU alias tests, tracepoint glob tests, hybrid PMU parsing, breakpoint syntax, config-term validation, regroup warning checks, filter/UID/exclude-perf tests, and fake-PMU metric parser tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/parse-events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/parse-events.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/parse-events.h

Purpose: declares perf event parser types, term enums, state structs, modifiers, error handling, and APIs used by CLI option handling, PMU alias code, metric parsing, and tests.

Important APIs/types/functions: `parse_events_option_args` carries evlist pointer and optional PMU filter. `parse_events_term` models config terms with config name, numeric/string value, predefined term type, parse columns, weak/used/no-value flags. `parse_events_terms` wraps a list. `parse_events_state` carries destination list, next index, error list, term result, start token, fake modes, PMU filter, legacy-cache matching, and wildcard-PMU status. `parse_events_modifier` stores parsed modifier letters. The header exposes parser entry points, filters, term constructors/destructors, term parsing, modifier application, event creation helpers, multi-PMU expansion, leader setup, error APIs, SDT event detection, and breakpoint length helper.

Control flow: no executable flow besides inline `parse_events`, which calls `__parse_events` with default PMU filter and real PMU/tracepoint modes. The `is_sdt_event` inline detects SDT/cached probe syntax only when ELF support is enabled.

State and persistence: defines transient parser and error state. Terms own strings and must be freed with `parse_events_terms__exit/delete`; errors own message/help strings until exit.

Dependencies: Linux list/types/perf_event, booleans, string/sys types, and forward declarations for perf PMU/evsel/evlist/option/strbuf.

Integration points: included by `parse-events.c`, flex/bison generated code, PMU code, metricgroup, CLI option files, and tests.

Risks: enum values must stay synchronized with lexer term names and `parse_events__term_type_str`. Adding modifiers requires updates in lexer, struct fields, and semantic handling. Inline SDT detection is build-feature dependent. Test signals are full event parser build/test coverage and static checks that term-name tables and enums remain aligned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/parse-events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/parse-events.l -->
# sources/distributed-fs/ceph-client/tools/perf/util/parse-events.l

Purpose: flex lexer for perf event syntax. It tokenizes full event lists and standalone config term lists for the bison grammar in `parse-events.y`.

Important APIs/types/functions: lexer options make it reentrant, bison-bridge/location-aware, prefixed with `parse_events_`, and no-yywrap. Helper functions parse numeric values, duplicate names and quoted names, strip `@` driver-config strings, rewind matched event text, emit static term tokens, and parse event modifiers into `struct parse_events_modifier`. Start conditions separate `event`, `config`, and `mem` modes.

Control flow: the first token is controlled by `parse_events_state->stoken`, switching to event or config mode and returning `PE_START_EVENTS` or `PE_START_TERMS`. In event mode, grouped or PMU-style text is rewound for grammar-level parsing, while commas are emitted directly. In config mode, known term names become `PE_TERM`, raw encodings become `PE_RAW`, driver terms become `PE_DRV_CFG_TERM`, and slash exits config mode. In `mem` mode, breakpoint modifiers and length separators are disambiguated from event modifiers and PMU config slashes. Global rules tokenize `mem:`, raw hex, numbers, modifiers, names, quoted names, braces, colon, equals, and commas.

State and persistence: uses scanner-local yylval/yylloc and parse-state extra data. Allocated strings are owned by bison semantic values and released by destructors/actions.

Dependencies: generated bison header, `parse-events.h`, errno/stdlib/stdio, and flex location/column support.

Integration points: generated into `parse-events-flex.*` and used by `parse_events__scanner`. It defines the accepted CLI syntax for event names, groups, modifiers, PMU config terms, raw events, and memory breakpoint syntax.

Risks: token regex changes directly alter user-visible event parsing. Modifier letters must stay disjoint from breakpoint modifiers where assumed and synchronized with semantic handling. Quoted-name support is intentionally narrow. Bad numeric conversion emits parser errors. Test signals include event parser tests for each syntax family, config-term parsing, quoted names, driver-config terms, duplicate modifiers, memory breakpoints, and raw event encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/parse-events.l -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/parse-events.y -->
# sources/distributed-fs/ceph-client/tools/perf/util/parse-events.y

Purpose: bison grammar for perf event lists and config term lists. It assembles lexer tokens into evsel lists and config-term objects by invoking semantic helpers in `parse-events.c`.

Important APIs/types/functions: grammar values include strings, numbers, `parse_events_modifier`, term types, evsel lists, term lists, term objects, and tracepoint name pairs. It defines destructors for strings, terms, term lists, evsel lists, and tracepoint names. Helper `alloc_list` creates list heads and `free_list_evsel` deletes evsels on grammar cleanup.

Control flow: entry `start` switches between `start_events` and `start_terms`. `groups` combines groups and events separated by commas. `group_def` sets the first event as leader and optional group name. `event_mod` applies event modifiers; `group` can apply group modifiers. `event_pmu` handles PMU names, PMU configs, or event-name multi-PMU expansion. Legacy forms cover `mem:` breakpoints, `sys:event` tracepoints, numeric `type:config`, and raw `rNNN` events. `event_config` builds term lists from assignments, no-value terms, built-in terms, and driver-config terms.

State and persistence: successful event parsing splices owned evsels into `parse_state->list`; successful term parsing stores a term list in `parse_state->terms`. Destructors clean up on parse abort.

Dependencies: PMU/PMU registry headers, evsel deletion, parse-events semantic API, Linux types, and generated lexer token declarations.

Integration points: generated parser is called by `parse_events__scanner` for both CLI event strings and sysfs/alias term parsing. It is the formal syntax contract for groups, modifiers, PMU config, tracepoint, raw, numeric, and memory breakpoint event forms.

Risks: grammar ambiguity around slashes/colons is coordinated with lexer states; changes can break legacy syntax. Ownership transfer between grammar actions and destructors is delicate. Errors use `PE_ABORT` to distinguish OOM from semantic invalidity. Test signals are parser regression tests across all event syntaxes, OOM/error cleanup checks, group leader/name behavior, and term-list parsing tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/parse-events.y -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/parse-regs-options.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/parse-regs-options.c

Purpose: parses `perf record` register sampling option strings for user registers and interrupt registers.

Important APIs/types/functions: `list_perf_regs` prints available register names for a mask. `name_to_perf_reg_mask` resolves a case-insensitive register name to one or more mask bits by calling architecture `perf_reg_name`. `__parse_regs` implements shared parsing for user and interrupt modes. Public callbacks are `parse_user_regs` and `parse_intr_regs`.

Control flow: the parser rejects unset/double-set cases, obtains the architecture mask through `perf_user_reg_mask` or `perf_intr_reg_mask`, defaults to the whole mask when the option has no argument, splits comma-separated names, prints available names for `?`, and ORs matched register bits into the caller mask. Unknown names produce a UI warning suggesting the relevant option with `?`.

State and persistence: only mutates the caller-provided `uint64_t` mask. No global state.

Dependencies: DWARF/ELF machine constants, perf register abstraction, UI warnings/debug, subcmd parse-options, and architecture register-name tables.

Integration points: perf record option handling for sampled user/interrupt register sets. It depends on files under `perf-regs-arch` for architecture masks/names.

Risks: duplicate architecture names are suppressed only in listing; name lookup can return multiple bits when aliases exist. Header/mask consistency is architecture-sensitive. Test signals include `perf record --user-regs=?`, valid/invalid register lists per architecture, no-argument defaults, and double-set rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/parse-regs-options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/parse-regs-options.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/parse-regs-options.h

Purpose: declares parse-options callbacks for register sampling options.

Important APIs/types/functions: forward-declares `struct option` and exposes `parse_user_regs` plus `parse_intr_regs`.

Control flow: none; callbacks are implemented in `parse-regs-options.c`.

State and persistence: no state in the header.

Dependencies: parse-options users must include the actual `struct option` definition.

Integration points: perf record CLI option tables.

Risks: minimal; compile coverage verifies the callback signatures stay compatible with subcmd parse-options. Runtime tests should cover user and interrupt register options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/parse-regs-options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/parse-sublevel-options.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/parse-sublevel-options.c

Purpose: parses comma-separated sublevel option strings of the form `name` or `name=value` into integer fields supplied by the caller.

Important APIs/types/functions: `parse_one_sublevel_option` duplicates one token, splits optional `=`, finds the matching `struct sublevel_option` by exact name, defaults value to 1, converts explicit values with `atoi`, and writes `*value_ptr`. Public `perf_parse_sublevel_options` tokenizes the input with `strtok` and applies the helper.

Control flow: the top-level function duplicates the whole string, iterates comma tokens, aborts on unknown names or allocation failure, frees temporary storage, and returns 0 or -1.

State and persistence: mutates caller-owned integer targets. No global state.

Dependencies: libc string/stdlib/stdio and perf debug logging.

Integration points: used by perf options that have nested sub-options, such as feature-specific mode strings.

Risks: `atoi` provides no validation for malformed or overflowing values, so callers must validate resulting integers if needed. Empty tokens are skipped by `strtok`. Test signals include known option names with and without values, unknown-name diagnostics, and malformed numeric value behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/parse-sublevel-options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/parse-sublevel-options.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/parse-sublevel-options.h

Purpose: declares the small sublevel-option parser interface.

Important APIs/types/functions: `struct sublevel_option` maps an option `name` to an integer pointer. `perf_parse_sublevel_options` applies a comma-separated user string to an array terminated by `name == NULL`.

Control flow: none; caller provides the terminator and storage.

State and persistence: state is caller-owned integers only.

Dependencies: none beyond C declarations.

Integration points: perf CLI sub-option parsing.

Risks: missing terminator causes out-of-bounds scanning. Test signals are parser unit tests and option-table validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/parse-sublevel-options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/path.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/path.c

Purpose: provides small filesystem path helpers for perf utilities.

Important APIs/types/functions: `mkpath` formats into a caller buffer with `vsnprintf`, substitutes `"/bad-path/"` on truncation, and strips leading `./` through `cleanup_path`. `path__join` and `path__join3` concatenate path components with separators. `is_regular_file`, `is_directory`, and `is_directory_at` use `stat`/`fstatat` to test file types.

Control flow: formatting helpers are direct string operations. Directory helpers build or receive paths, stat them, return false on errors, and test mode bits.

State and persistence: no stored state. All outputs are caller buffers or boolean results from current filesystem state.

Dependencies: perf cache/kernel helpers for `scnprintf`, libc stdio/string/stat/dirent/unistd, and `PATH_MAX`.

Integration points: used by PMU/sysfs/file discovery code that needs safe joins and file-type checks, including filesystems where `dirent.d_type` may be `DT_UNKNOWN`.

Risks: `mkpath` is not declared in `path.h` in this slice, so callers may get it through another header. `path__join` does not normalize duplicate separators except empty first path. `strncpy` on truncation may not NUL-fill if size is unusual. Test signals include join edge cases, truncation behavior, DT_UNKNOWN directory scanning, and `fstatat` relative directory checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/path.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/path.h

Purpose: declares perf path join and file-type helper APIs.

Important APIs/types/functions: exposes `path__join`, `path__join3`, `is_regular_file`, `is_directory`, and `is_directory_at`; forward-declares `struct dirent`.

Control flow: no executable flow.

State and persistence: helpers operate on caller buffers or live filesystem metadata only.

Dependencies: `stddef.h` and `stdbool.h`.

Integration points: included by utilities doing source-tree/sysfs/procfs traversal.

Risks: no declaration for `mkpath` despite implementation in `path.c`, implying legacy declaration elsewhere or dead use. Test signals are compile coverage and path helper unit/smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/path.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-hooks-list.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/perf-hooks-list.h

Purpose: central X-macro list of supported perf hook names.

Important APIs/types/functions: expands `PERF_HOOK(record_start)`, `PERF_HOOK(record_end)`, and `PERF_HOOK(test)` wherever included.

Control flow: no direct execution; inclusion context decides whether declarations, definitions, inline invokers, or arrays are generated.

State and persistence: no state, but each hook name produces global hook descriptor/function pointer storage in `perf-hooks.c`.

Dependencies: requires the including file to define `PERF_HOOK`.

Integration points: used by `perf-hooks.h` and `perf-hooks.c` to keep declarations and implementation arrays synchronized.

Risks: adding a hook changes public API and global symbols; forgetting to include this list in all generation contexts would desynchronize hooks. Test signals include compile/link coverage and hook set/get/invoke tests for all names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-hooks-list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-hooks.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/perf-hooks.c

Purpose: implements a lightweight runtime hook registry for selected perf lifecycle points, with recovery from hook-triggered segmentation faults.

Important APIs/types/functions: `perf_hooks__invoke` calls a hook descriptor's function pointer with context if installed. `perf_hooks__recover` longjmps out of a crashing hook when signal handling routes there. X-macro expansion creates `__perf_hook_func_<name>` storage and `__perf_hook_desc_<name>` descriptors. `perf_hooks__set_hook` installs or overwrites a hook by name; `perf_hooks__get_hook` retrieves it or returns `ERR_PTR(-ENOENT)`.

Control flow: invoke uses `sigsetjmp`; normal path sets `current_perf_hook`, calls the function, then clears it. Recovery path logs a warning and disables the current hook by storing NULL. Set/get linearly scan the descriptor array generated from `perf-hooks-list.h`.

State and persistence: module globals are `jmpbuf`, `current_perf_hook`, per-hook function pointers, descriptor contexts, and the descriptor array. State persists for the process lifetime.

Dependencies: setjmp/signal recovery machinery, Linux `ERR_PTR`, array-size helpers, debug logging, and the hook list header.

Integration points: external scripts/plugins or tests can set hooks for `record_start`, `record_end`, and `test`; callers use inline `perf_hooks__invoke_<name>` wrappers from the header.

Risks: global state is not thread-safe; concurrent hook invocation/set could race. Recovery only helps when signal handling calls `perf_hooks__recover`. Longjmp from signal context is delicate. Test signals include hook install/get/invoke tests, overwrite warning checks, test hook coverage, and fault-injection recovery where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-hooks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-hooks.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/perf-hooks.h

Purpose: declares the perf hook descriptor API and generates inline invokers for every hook in `perf-hooks-list.h`.

Important APIs/types/functions: `perf_hook_func_t` is a `void (*)(void *ctx)`. `struct perf_hook_desc` stores hook name, pointer to the installed function pointer, and context. Declares `perf_hooks__invoke`, `perf_hooks__recover`, `perf_hooks__set_hook`, and `perf_hooks__get_hook`. X-macro expansion declares external descriptors and defines `perf_hooks__invoke_record_start`, `perf_hooks__invoke_record_end`, and `perf_hooks__invoke_test`.

Control flow: inline invokers pass the generated descriptor to the generic invoke function.

State and persistence: descriptors/function storage are defined in `perf-hooks.c`; this header exposes references only.

Dependencies: C++ compatibility guards and the hook list header.

Integration points: included by code that invokes or registers hooks. It keeps hook declarations synchronized with the central list.

Risks: public inline functions change when the hook list changes. `perf_hooks__get_hook` can return `ERR_PTR`, so callers must not blindly call the result. Test signals are compile/link coverage and hook registration/invocation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-hooks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_aarch64.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_aarch64.c

Purpose: supplies Arm64 register sampling masks, register names, instruction-pointer/stack-pointer IDs, and SDT argument conversion.

Important APIs/types/functions: `__perf_sdt_arg_parse_op_arm64` supports SDT operands `x0`-`x31` and `[sp]`/`[sp, NUM]`, converting them to uprobe-style `%xN` or `+offset(%sp)`. `__perf_reg_mask_arm64` returns the base mask and conditionally includes `PERF_REG_ARM64_VG` when SVE is advertised and accepted by a probe `perf_event_open`. `__perf_reg_name_arm64` maps x0-x29, sp, lr, pc, and vg. `__perf_reg_ip_arm64` and `__perf_reg_sp_arm64` return PC/SP IDs.

Control flow: regexes are compiled once lazily. SDT parsing matches register or stack forms and skips unsupported operands. Register-mask probing builds a disabled cycles event with requested user regs and falls back when the kernel rejects extended registers.

State and persistence: static regex objects and an initialized flag persist. No other state.

Dependencies: regex, auxv `AT_HWCAP`, sys_perf_event_open, Arm64 perf register definitions, kernel perf constants, and debug logging.

Integration points: used by perf register option parsing, sample decoding, and SDT probe argument setup on Arm64.

Risks: SVE VG availability depends on both hardware and kernel attr support. Regex supports only a subset of possible SDT operand syntax. Test signals include register name/mask tests, SVE-capable kernel probing, and SDT conversion cases for x registers and stack offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_aarch64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_arm.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_arm.c

Purpose: maps 32-bit ARM perf register IDs to names and basic sampling masks.

Important APIs/types/functions: `__perf_reg_mask_arm` returns `PERF_REGS_MASK`. `__perf_reg_name_arm` maps r0-r10, fp, ip, sp, lr, and pc. `__perf_reg_ip_arm` returns PC and `__perf_reg_sp_arm` returns SP.

Control flow: direct switch-based mapping only.

State and persistence: no state.

Dependencies: generic perf regs abstraction and ARM arch register definitions.

Integration points: register sampling options and sample display on ARM builds.

Risks: names must match user-facing register option expectations and kernel register IDs. Test signals include `--user-regs=?` listing and sample register decoding on ARM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_arm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_csky.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_csky.c

Purpose: provides C-SKY register masks, names, and IP/SP register IDs.

Important APIs/types/functions: `__perf_reg_mask_csky` returns `PERF_REGS_MASK`. `__perf_reg_name_csky` maps ABI v2 register IDs to names including a0-a3, regs0-regs9, sp, lr, pc, exregs0-exregs14, tls, hi, and lo, while suppressing extended register names for ABI v2 when the ELF flags indicate they are not valid. `__perf_reg_ip_csky` returns PC and `__perf_reg_sp_csky` returns SP.

Control flow: direct mask return and switch mapping with an ABI/e_flags guard before the switch.

State and persistence: no state.

Dependencies: ELF C-SKY ABI flags, generic perf regs, and C-SKY arch register definitions with ABI v2 definitions forced.

Integration points: register option parsing and sample display for C-SKY perf.

Risks: ABI flag handling is easy to invert; names must reflect the sampled binary ABI. Test signals include ABI-specific register listing/decoding and compile coverage where EF_CSKY constants are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_csky.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_loongarch.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_loongarch.c

Purpose: maps LoongArch perf register IDs to user-facing names and basic masks.

Important APIs/types/functions: `__perf_reg_mask_loongarch` returns `PERF_REGS_MASK`. `__perf_reg_name_loongarch` maps PC and `%r1` through `%r31`. `__perf_reg_ip_loongarch` returns PC and `__perf_reg_sp_loongarch` returns R3.

Control flow: direct switch mapping only.

State and persistence: no state.

Dependencies: generic perf regs and LoongArch arch register definitions.

Integration points: register sampling option parsing and sample display on LoongArch.

Risks: `%rN` casing/prefix is user-visible; SP must stay aligned with the LoongArch ABI. Test signals include register list output and sample decoding tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_loongarch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_mips.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_mips.c

Purpose: maps MIPS perf register IDs to names and exposes IP/SP IDs.

Important APIs/types/functions: `__perf_reg_mask_mips` returns `PERF_REGS_MASK`. `__perf_reg_name_mips` maps PC and general registers `$1` through `$25`, `$28`, `$29`, `$30`, and `$31`. `__perf_reg_ip_mips` returns PC and `__perf_reg_sp_mips` returns R29.

Control flow: direct switch mapping.

State and persistence: no state.

Dependencies: generic perf regs and MIPS arch register definitions.

Integration points: perf register sampling and display on MIPS.

Risks: missing IDs intentionally reflect architecture definitions; adding kernel registers requires table updates. Test signals include register list output and decoded sampled register names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_mips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_powerpc.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_powerpc.c

Purpose: supplies PowerPC register names, IP/SP IDs, interrupt-register mask probing for recent POWER CPUs, and SDT operand conversion.

Important APIs/types/functions: `__perf_sdt_arg_parse_op_powerpc` converts register and displacement forms such as `18`, `%r18`, `48(18)`, and `-48(%r18)` into uprobe `%gprN` syntax, while skipping immediate `iNUM` constants. `__perf_reg_mask_powerpc` returns base mask for user regs; on PowerPC builds it probes PMU extended interrupt registers based on PVR for POWER9, POWER10, and POWER11. `__perf_reg_name_powerpc` maps r0-r31, NIP, MSR, orig_r3, CTR, LINK, XER, CCR, SOFTE, TRAP, DAR, DSISR, SIER/MMCR/PMC/SDAR/SIAR extended names. IP is NIP and SP is R1.

Control flow: SDT regexes are compiled once; operands are matched against register or displacement forms. Interrupt-mask probing reads PVR, chooses the extended mask, opens a disabled precise cycles event with `sample_regs_intr`, and includes the mask only if the kernel accepts it.

State and persistence: static regex objects/flag. No other persistent state.

Dependencies: regex, PowerPC PVR/mfspr utilities, sys_perf_event_open, arch register definitions, kernel perf constants, and debug logging.

Integration points: register sampling on PowerPC, SDT probe conversion, and sample display for extended PMU registers.

Risks: PVR handling is compiled only for native PowerPC; cross-build fallback returns base mask. New POWER generations require updated PVR/mask logic. SDT supports only a subset of operand forms. Test signals include SDT operand conversion tests, register list output, POWER9/10/11 extended interrupt register probe tests, and sample decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_powerpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_riscv.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_riscv.c

Purpose: maps RISC-V perf register IDs to ABI register names and exposes masks/IP/SP IDs.

Important APIs/types/functions: `__perf_reg_mask_riscv` returns `PERF_REGS_MASK`. `__perf_reg_name_riscv` maps pc, ra, sp, gp, tp, t0-t6, s0-s11, and a0-a7. `__perf_reg_ip_riscv` returns PC and `__perf_reg_sp_riscv` returns SP.

Control flow: direct switch mapping.

State and persistence: no state.

Dependencies: generic perf regs and RISC-V arch register definitions.

Integration points: perf register option parsing and sample register display on RISC-V.

Risks: ABI aliases are user-facing and should stay consistent with docs. Test signals include `--user-regs=?` and decoded register samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_riscv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_s390.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_s390.c

Purpose: provides s390 register names, masks, IP/SP IDs, and SDT operand validation/conversion.

Important APIs/types/functions: `__perf_reg_mask_s390` returns `PERF_REGS_MASK`. `__perf_reg_name_s390` maps R0-R15, FP0-FP15, MASK, and PC. `__perf_reg_ip_s390` returns PC and `__perf_reg_sp_s390` returns R15. `__perf_sdt_arg_parse_op_s390` accepts `%r0`-`%r15` and signed displacement forms like `+48(%r1)`, returning the same syntax when valid and skipping unsupported operands.

Control flow: regexes compile lazily with a two-step initialized state. SDT parsing matches either direct register or displacement form, duplicates the matched operand, and returns valid/skip/error.

State and persistence: static compiled regexes and initialized flag.

Dependencies: regex, s390 arch register definitions, zalloc, debug logging.

Integration points: s390 perf register sampling, sample display, and SDT probe argument setup.

Risks: regex initialized state must reset correctly on second-regex failure. Register names are uppercase for display while SDT syntax is lowercase `%rN`. Test signals include SDT operand cases, register list output, and sample decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_s390.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_x86.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_x86.c

Purpose: supplies x86 register names/masks/IP/SP IDs and converts x86 SDT marker operands into uprobe-compatible register syntax.

Important APIs/types/functions: `sdt_reg_tbl` maps many GAS register spellings (`%rax`, `%eax`, byte regs, `%r8d`, etc.) to uprobe register names. `__perf_sdt_arg_parse_op_x86` accepts optional signed displacement plus one register, rejects scaled/indexed, RIP-symbol, and immediate forms, adds `+0` for bare parenthesized registers, renames registers, and returns a new uprobe operand. `__perf_reg_mask_x86` probes extended interrupt register support with `PERF_REG_EXTENDED_MASK`, adjusting config for hybrid core PMU type. `__perf_reg_name_x86` maps general/segment/control names and XMM register pairs. IP is IP and SP is SP.

Control flow: regex is compiled lazily. SDT parsing rejects operands containing comma or `$`, validates register length, builds an optional prefix, renames the register, allocates the output, and formats it. Interrupt-mask probing opens a disabled precise cycles event and includes extended regs only on success.

State and persistence: static compiled regex and initialization flag. No other state.

Dependencies: regex, x86 arch register definitions, PMU scanning for hybrid type, sys_perf_event_open, kernel perf constants, zalloc, and debug logging.

Integration points: x86 register sampling options, interrupt sample decoding, SDT probe conversion, and hybrid PMU handling.

Risks: SDT conversion intentionally skips common unsupported forms; broadening regex could create invalid uprobe syntax. Hybrid PMU type probing assumes register support is uniform across core PMUs. XMM mapping returns the same display name for paired IDs. Test signals include SDT conversion tests, `--intr-regs=?`, extended register probe tests, hybrid systems, and sample register display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_x86.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf_api_probe.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/perf_api_probe.c

Purpose: probes whether the running kernel accepts newer `perf_event_attr` fields and CPU-wide recording modes before perf enables related features.

Important APIs/types/functions: `perf_do_probe_api` parses a safe event, opens it once, applies a setup callback that toggles one attr field, opens it again, and interprets `EINVAL` as unsupported. `perf_probe_api` tries `software/cpu-clock/u` first, then core PMU `cycles` or `instructions` events. Setup callbacks toggle sample identifier, comm exec, context switch, text poke, build-id, and cgroup bits. Public probes are `perf_can_sample_identifier`, `perf_can_comm_exec`, `perf_can_record_switch_events`, `perf_can_record_text_poke_events`, `perf_can_record_cpu_wide`, `perf_can_aux_sample`, `perf_can_record_build_id`, and `perf_can_record_cgroup`.

Control flow: probe opens use close-on-exec flags and the first online CPU. If cpu-wide `pid=-1` fails with `EACCES`, a static `pid` fallback switches subsequent probes to `pid=0`. `perf_can_record_cpu_wide` directly opens a software CPU-clock event for `pid=-1,cpu=first`. `perf_can_aux_sample` deliberately sets only `aux_sample_size=1` and relies on `E2BIG` to indicate an old kernel attr size.

State and persistence: only static `pid` inside `perf_do_probe_api` persists to remember permission fallback. Probes create transient evlists and file descriptors, closing/deleting them before return.

Dependencies: sys_perf_event_open, evlist/evsel, parse-events, PMU scanning, online CPU maps, close-on-exec flag helper, errno, and kernel perf attr semantics.

Integration points: used by record/stat/session setup to gate features like sample identifiers, comm exec, switch/text-poke/build-id/cgroup records, CPU-wide recording, and AUX sample size.

Risks: probing can be affected by permissions, perf_event_paranoid, unavailable PMUs, or container restrictions, causing false negatives. `perf_can_aux_sample` only checks kernel attr-size support, not hardware AUX sampling. Test signals include unit/smoke probes on old and new kernels, permission-restricted environments, and feature-specific record tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf_api_probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf_api_probe.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/perf_api_probe.h

Purpose: declares runtime kernel perf API capability probes.

Important APIs/types/functions: exposes boolean functions for AUX sample support, comm exec records, CPU-wide recording, context-switch records, text-poke records, sample identifiers, build-id records, and cgroup records.

Control flow: none in the header. Callers invoke probes before enabling optional perf_event_attr fields or modes.

State and persistence: no header state; implementation keeps only minimal process-local probe cache/fallback behavior.

Dependencies: booleans.

Integration points: included by recording/session setup code that needs feature gating across kernel versions and permission environments.

Risks: callers must treat false as "do not enable feature" rather than fatal unless the feature was explicitly required. Test signals are compile coverage and feature-gating tests on kernels with varied perf API support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/perf_api_probe.h -->
