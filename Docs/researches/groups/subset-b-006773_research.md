# subset-b-006773 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/target.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/target.h

## Purpose

`target.h` defines the common target-selection contract used by perf commands. It represents whether a command is operating on explicit PIDs, TIDs, CPUs, system-wide mode, BPF-selected tasks, inherited children, mmap usage, per-thread collection, and delayed start behavior.

## Important APIs, Types, and Functions

The central type is `struct target`, with string selectors (`pid`, `tid`, `cpu_list`, `bpf_str`, `attr_map`) and booleans that describe target mode. `enum target_errno` reserves perf-specific negative validation errors for mutually exclusive target combinations. The public declarations are `target__validate()`, `parse_uid()`, and `target__strerror()`. Inline helpers include `target__has_task()`, `target__has_cpu()`, `target__none()`, `target__enable_on_exec()`, `target__has_per_thread()`, and `target__uses_dummy_map()`.

## Control Flow and State

The header itself has no runtime control flow, but its inline predicates encode decisions used by record/stat/top setup. `target__enable_on_exec()` returns true for a command-spawned workload with no initial delay. `target__uses_dummy_map()` chooses dummy mmap events for task-oriented or per-thread modes so perf can bootstrap event delivery even without explicit CPU mmap rings.

## Dependencies and Integration Points

It depends only on standard types and integrates with record options, evlist creation, validation diagnostics, and target-to-thread/CPU map construction. It is consumed wherever perf translates CLI selectors into kernel perf_event attributes.

## Risks and Test Signals

Risks are mostly semantic: invalid combinations such as PID plus CPU or BPF plus TID must be rejected consistently by the implementation. Tests should cover each target mode, dummy-map decisions, delayed start behavior, and formatted validation errors for all `target_errno` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/target.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/term.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/term.c

## Purpose

`term.c` provides small terminal helpers for interactive perf UIs. It discovers terminal dimensions and switches stdin into quiet noncanonical mode for key polling.

## Important APIs, Types, and Functions

`get_term_dimensions(struct winsize *ws)` prefers `LINES` and `COLUMNS`, falls back to `ioctl(1, TIOCGWINSZ)`, then defaults to 25x80. `set_term_quiet_input(struct termios *old)` saves current stdin settings, clears `ICANON` and `ECHO`, sets `VMIN`/`VTIME` to zero, and applies the modified settings.

## Control Flow and State

The only persistent effect is terminal state changed by `tcsetattr`; callers must restore the saved `old` termios. The dimension helper mutates only the passed `winsize`.

## Dependencies and Integration Points

It depends on libc termios, environment variables, and optional `TIOCGWINSZ`. It is used by terminal and TUI-oriented commands such as `perf top`.

## Risks and Test Signals

Risks include leaving stdin noncanonical if callers fail to restore settings, environment variables with invalid zero values, and non-tty stdout. Tests can set `LINES`/`COLUMNS`, run under a pseudo-terminal, and verify fallback dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/term.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/term.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/term.h

## Purpose

`term.h` declares the terminal helper API used by perf interactive display code.

## Important APIs, Types, and Functions

It forward-declares `struct termios` and `struct winsize`, then exports `get_term_dimensions()` and `set_term_quiet_input()`.

## Control Flow and State

There is no local state. The declarations expose functions that mutate caller-owned terminal structures and process terminal mode.

## Dependencies and Integration Points

The header intentionally avoids including termios headers, keeping include cost low for users in UI code.

## Risks and Test Signals

The API relies on callers passing valid storage and restoring terminal state after quiet mode. Build tests should ensure users include the platform headers that define the concrete structs where needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/term.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/thread-stack.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/thread-stack.c

## Purpose

`thread-stack.c` reconstructs per-thread call stacks and branch stacks from branch samples. It supports two related modes: lightweight callchain synthesis for samples, and full call/return pairing for call-path export through a `call_return_processor`.

## Important APIs, Types, and Functions

Internal `struct thread_stack_entry` stores a return address, timing/count snapshots, export IDs, a `call_path`, and flags for no-call, trace-end, and non-call synthetic edges. Internal `struct thread_stack` stores the dynamic entry array, trace number, running branch/instruction/cycle counts, kernel boundary, current comm, optional branch-stack ring, and retpoline detection state. Public functions include `thread_stack__event()`, `thread_stack__sample()`, `thread_stack__sample_late()`, `thread_stack__br_sample()`, `thread_stack__br_sample_late()`, `thread_stack__flush()`, `thread_stack__free()`, `thread_stack__depth()`, `thread_stack__set_trace_nr()`, `thread_stack__process()`, `call_return_processor__new()`, and `call_return_processor__free()`.

## Control Flow and State

Stacks grow in blocks of 2048 entries. Idle thread `pid == tid == 0` uses one stack per CPU; other threads use one stack. `thread_stack__event()` lazily allocates state, flushes when `trace_nr` changes, updates the optional branch ring, and then pushes calls or pops returns for callchain synthesis. `thread_stack__sample()` converts the current synthesized stack into an `ip_callchain`, inserting user/kernel context markers. Late sample helpers drop entries that happened after delayed hardware sample capture. `thread_stack__process()` is the richer export path: it tracks current comm, initializes the bottom frame, updates branch/insn/cycle counters, handles calls, returns, trace begin/end, missing calls/returns, optimized jumps to symbol starts, kernel-to-user returns, and x86 retpoline cleanup before invoking the processor callback.

## Dependencies and Integration Points

It integrates with `thread`, `machine`, `env`, `symbol`, `comm`, `event`, and `call-path` code. It consumes `PERF_IP_FLAG_*` branch metadata and `perf_sample` counts. Export users receive `struct call_return` records with parent db-id wiring for database output. Branch-stack output feeds sample synthesis, scripting, and report views.

## State and Persistence Behavior

State lives in `thread->ts` until flushed or freed. Trace discontinuities intentionally discard or export unfinished state to avoid misleading callchains. Call/return export stores per-entry db IDs and parent references but does not persist itself; persistence happens in the callback consumer. Branch ring buffers persist only up to the configured depth.

## Risks and Test Signals

Risks include stack corruption across trace gaps, missing return handling for longjmp-like flows, kernel/user boundary mistakes, retpoline over-filtering, branch-ring wrap errors, and memory pressure on deep stacks. Tests should exercise call/return pairs, unmatched calls, unmatched returns, trace begin/end, idle per-CPU stacks, late samples, retpoline thunks, branch stack wrapping, comm changes on exec, and callback error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/thread-stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/thread-stack.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/thread-stack.h

## Purpose

`thread-stack.h` defines the public interface for synthesized thread stacks and call/return export.

## Important APIs, Types, and Functions

The call-return flag bits are `CALL_RETURN_NO_CALL`, `CALL_RETURN_NO_RETURN`, and `CALL_RETURN_NON_CALL`. `struct call_return` carries paired call and return metadata: thread, comm, call path, call/return times, branch/instruction/cycle deltas, sample references, database IDs, parent ID, and flags. `struct call_return_processor` owns a `call_path_root`, callback, and opaque data. The header exports stack event, sample, branch sample, flush/free/depth, processor allocation, and `thread_stack__process()`.

## Control Flow and State

Callers feed branch samples into this API. Simple users ask for synthesized callchains later; export users provide a processor callback that receives completed call-return records.

## Dependencies and Integration Points

The API references perf sample, address-location, call-path, symbol, dso, comm, and thread structures without forcing all definitions into the header. It is used by callchain and branch-history consumers.

## Risks and Test Signals

Consumers must keep callback data valid and respect that flush may emit incomplete calls. Compile tests should catch signature drift; behavior tests should verify flag combinations and parent db-id assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/thread-stack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/thread.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/thread.c

## Purpose

`thread.c` implements perf's per-thread runtime object. A thread owns process/thread IDs, maps, comm history, namespace history, source-code state, unwind state hooks, optional synthesized stack state, architecture identity, filters, and LBR stitch state.

## Important APIs, Types, and Functions

Creation and lifetime functions are `thread__new()`, `thread__delete()`, `thread__get()`, `thread__put()`, and `thread__set_priv_destructor()`. Mapping functions include `thread__init_maps()`, `thread__insert_map()`, `thread__fork()`, `thread__find_map()`, `thread__find_symbol()`, `thread__find_cpumode_addr_location()`, and `thread__memcpy()`. Metadata functions include `thread__set_namespaces()`, `thread__set_comm()`, `thread__set_comm_from_proc()`, `thread__comm()`, `thread__exec_comm()`, `thread__comm_str()`, `thread__comm_len()`, `thread__e_machine()`, `thread__main_thread()`, and `thread__free_stitch_list()`.

## Control Flow and State

`thread__new()` initializes defaults, creates a placeholder `":tid"` comm, initializes locks and lists, sets refcount to one, and allocates namespace info. `thread__delete()` flushes stack state, drops maps, frees namespace/comm histories under write locks, clears source-code state, frees stitch lists, runs the private destructor, and frees the refcounted object. Comm and namespace updates append new history entries and timestamp old entries when appropriate. Fork handling copies or shares maps according to process/thread relationship and optionally clones maps for new processes. Architecture detection first consults cached thread fields, then leader thread, then mapped DSOs, and finally `/proc/<pid>/exe` for live sessions before falling back to host identity.

## Dependencies and Integration Points

It depends on machine/thread registries, maps, DSOs, symbols, namespaces, comm records, unwind access preparation, DWARF registers, callchain, and procfs helpers. It is a core integration point for perf record/report/top/script because most events are resolved through a `thread`.

## State and Persistence Behavior

State is in-memory and refcounted. Map groups may be shared with the process leader. Comm and namespace lists retain historical names/namespaces with timestamps for event-time resolution. Cached `e_machine` and `e_flags` avoid repeated ELF inspection. LBR stitch state and thread stacks are released on deletion.

## Risks and Test Signals

Risks include refcount leaks, stale map sharing after fork/exec, missing comm locks, incorrect architecture detection for mixed 32/64-bit workloads, and failed unwind preparation on new maps. Tests should cover thread creation/deletion, forked thread vs new process behavior, comm updates with exec flushing unwind state, namespace history, symbol/map lookup across CPU modes, `/proc` comm reads, and `thread__memcpy()` against mapped DSOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/thread.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/thread.h

## Purpose

`thread.h` defines the refcounted `struct thread` and its accessor API. It is the central type for associating perf events with a task, maps, comm history, namespace state, filters, source-code state, unwind data, and branch-stack stitching.

## Important APIs, Types, and Functions

`DECLARE_RC_STRUCT(thread)` contains `maps`, `pid_`, `tid`, `ppid`, current CPU/guest CPU, `refcnt`, exit/filter flags, comm and namespace lists with rwsems, database ID, private data, `thread_stack`, namespace info, source-code state, ELF flags/machine, and `struct lbr_stitch`. The header exports lifecycle, comm, namespace, fork, map/symbol lookup, memory copy, architecture, filtering, stitch cleanup, and resolve functions. Inline accessors wrap fields through `RC_CHK_ACCESS`.

## Control Flow and State

The header's inline helpers provide controlled field mutation and filtering checks against global `symbol_conf` comm/PID/TID lists. Reference helpers ensure callers explicitly own thread references.

## Dependencies and Integration Points

It depends on refcount/rwsem/list infrastructure, callchain, source-code state, symbol configuration, and rc-check instrumentation. It is included across machine, event processing, unwinding, hist, and scripting code.

## Risks and Test Signals

Risks include direct field access bypassing rc-check wrappers, lock ordering issues around comm/namespace lists, and stale filter criteria. Tests should verify accessor behavior, filtering by comm/pid/tid lists, and proper cleanup of LBR stitch resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/thread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/thread_map.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/thread_map.c

## Purpose

`thread_map.c` builds and manipulates `perf_thread_map` objects from PIDs, TIDs, procfs scans, or recorded thread-map events. These maps drive perf event opening and aggregation over selected threads.

## Important APIs, Types, and Functions

Constructors include `thread_map__new_by_pid()`, `thread_map__new_by_tid()`, `thread_map__new()`, `thread_map__new_str()`, `thread_map__new_by_tid_str()`, and `thread_map__new_event()`. Utility functions are `thread_map__fprintf()`, `thread_map__read_comms()`, `thread_map__has()`, and `thread_map__remove()`. Internal helpers scan `/proc/<pid>/task`, all `/proc` task directories, and `/proc/<tid>/comm`.

## Control Flow and State

PID-based creation expands each process to its task list. TID-based creation creates explicit entries or a dummy map when no TID string is supplied. All-thread mode scans all numeric `/proc` directories and grows the map as needed. Event-based creation reconstructs pids and comm strings from `PERF_RECORD_THREAD_MAP`. `thread_map__remove()` frees the removed comm and shifts later entries.

## Dependencies and Integration Points

It depends on procfs, `strlist`, `perf_thread_map__realloc`, internal thread-map accessors, and perf event record formats. It integrates with target parsing, evlist open paths, stat output, and perf.data replay.

## State and Persistence Behavior

Maps are heap objects with refcounts initialized to one. Comm strings are optional and best-effort; failing to read a comm emits a warning but still leaves a usable thread map. Recorded thread maps preserve 16-byte comm strings from perf.data.

## Risks and Test Signals

Risks include races with exiting tasks, duplicate input IDs, unbounded all-thread scans, and partial allocation failures. Tests should cover PID expansion, TID lists, null TID dummy behavior, all-thread scans under disappearing tasks, comm loading, event round-trip, and removal edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/thread_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/thread_map.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/thread_map.h

## Purpose

`thread_map.h` declares perf's thread-map constructors and helpers.

## Important APIs, Types, and Functions

It exports constructors from PID, TID, PID/TID strings, recorded thread-map events, and the dummy map path through `thread_map__new_dummy()` from another implementation. It also exports formatting, comm reading, membership, and removal helpers.

## Control Flow and State

The header has no implementation state. It establishes that callers work with `struct perf_thread_map` from libperf and perf record thread-map events.

## Dependencies and Integration Points

It includes `<perf/threadmap.h>` and is consumed by event opening, stat, record, and replay paths.

## Risks and Test Signals

Compile tests should catch ABI changes to `perf_thread_map`. Behavioral tests belong in the implementation and should verify ownership of returned maps and comm strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/thread_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/threads.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/threads.c

## Purpose

`threads.c` implements a sharded in-memory registry of `struct thread` objects keyed by TID. It gives machine code fast lookup, creation, deletion, and iteration for active and retained threads.

## Important APIs, Types, and Functions

The public functions are `threads__init()`, `threads__exit()`, `threads__nr()`, `threads__find()`, `threads__findnew()`, `threads__remove_all_threads()`, `threads__remove()`, and `threads__for_each_thread()`. Internal helpers choose a shard by `tid % THREADS__TABLE_SIZE`, hash long keys, compare keys, and maintain a per-shard `last_match` cache.

## Control Flow and State

Initialization creates eight hashmap shards and rwsems. Find first checks `last_match` under read lock, then falls back to the hashmap and refreshes the cache. Find-new allocates a thread under write lock and handles add races by dropping the new object and returning the existing one. Remove paths clear `last_match`, delete from the shard, and drop references.

## Dependencies and Integration Points

It depends on the perf hashmap, rwsem, machine, and thread reference API. It is embedded in `struct machine` and used by event processing for fork, exit, mmap, comm, samples, and synthetic event replay.

## State and Persistence Behavior

All state is in memory. The registry owns a reference to each stored thread; callers receive additional references from find functions and must put them. The `last_match` cache also owns a reference.

## Risks and Test Signals

Risks include reference leaks in cache replacement, shard races, deleting absent keys, and callback iteration holding read locks too long. Tests should cover find/findnew races, cache hits, negative TIDs, removal, remove-all cleanup, and early-stop iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/threads.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/threads.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/threads.h

## Purpose

`threads.h` defines the sharded thread-registry container used by perf machines.

## Important APIs, Types, and Functions

`THREADS__TABLE_BITS` is 3, giving `THREADS__TABLE_SIZE` of 8. `struct threads_table_entry` contains a hashmap shard, rwsem, and cached `last_match`. `struct threads` is the array of shards. The header exports init, exit, count, find, findnew, remove-all, remove-one, and foreach APIs.

## Control Flow and State

The state model is per-shard locking with refcounted thread ownership. Callers must respect reference ownership from find APIs.

## Dependencies and Integration Points

It depends on hashmap and rwsem utilities and is used by `machine` thread tables.

## Risks and Test Signals

The main risks are misuse of returned references and changing the shard count without validating lookup distribution. Tests should validate lookup and removal under repeated TID patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/threads.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/time-utils.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/time-utils.c

## Purpose

`time-utils.c` parses, formats, and applies time ranges for perf data filtering. It supports absolute seconds.nanoseconds ranges, multiple ranges, percentage slices of recorded sample time, and relative ranges from the first sample.

## Important APIs, Types, and Functions

Key functions are `parse_nsec_time()`, `perf_time__parse_str()`, `perf_time__percent_parse_str()`, `perf_time__range_alloc()`, `perf_time__skip_sample()`, `perf_time__ranges_skip_sample()`, `perf_time__parse_for_ranges_reltime()`, `perf_time__parse_for_ranges()`, `timestamp__scnprintf_usec()`, `timestamp__scnprintf_nsec()`, and `fetch_current_timestamp()`. Internal helpers split `start,end`, parse `N%/slice`, parse `start%-end%`, convert percentages to nanosecond windows, and reject overlapping intervals.

## Control Flow and State

Parsing copies input strings before inserting terminators. Absolute ranges default missing start/end to zero. Multiple absolute ranges are comma separated and checked for non-overlap. Percentage ranges require session first/last sample timestamps; relative mode offsets parsed ranges by the first sample time. Skip helpers return false for missing timestamps and true only when a sample falls outside all selected intervals.

## Dependencies and Integration Points

It depends on `perf_session`, `evlist` first/last sample times, `debug` diagnostics, libc time functions, and Linux nanosecond constants. It integrates with report/script time filters and timestamp display.

## State and Persistence Behavior

The module keeps no global state. It allocates caller-owned interval arrays and writes formatted timestamps into caller buffers.

## Risks and Test Signals

Risks include off-by-one endpoints in percentage conversion, overlapping range rejection, invalid fractional nanoseconds over 9 digits, missing sample-boundary metadata, and relative ranges with zero endpoints. Tests should cover `1.2`, `1,2`, multiple intervals, invalid overlaps, `10%/2`, `0%-10%`, single `50%`, relative mode, formatting, and empty timestamp behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/time-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/time-utils.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/time-utils.h

## Purpose

`time-utils.h` declares time interval parsing, filtering, formatting, and monotonic clock helpers.

## Important APIs, Types, and Functions

It defines `struct perf_time_interval { u64 start, end; }`, declares all parser/filter/formatter functions from `time-utils.c`, and provides inline `rdclock()` using `clock_gettime(CLOCK_MONOTONIC)`.

## Control Flow and State

The header has no persistent state. `rdclock()` returns nanoseconds since the monotonic clock epoch and is used by synthetic duration events.

## Dependencies and Integration Points

It depends on Linux integer types and libc time. It is used by tool PMU duration counting and perf data time filtering.

## Risks and Test Signals

Callers must free arrays from `perf_time__range_alloc()` and understand that zero means unbounded for intervals. Build tests should validate availability of `CLOCK_MONOTONIC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/time-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/tool.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/tool.c

## Purpose

`tool.c` initializes perf event-processing dispatch tables and implements default handlers and delegation wrappers. It lets each perf command override only the event callbacks it cares about while preserving safe defaults for all perf record types.

## Important APIs, Types, and Functions

`perf_tool__init()` fills `struct perf_tool` callbacks and option flags. Default stubs include sample, generic event, finished-round, attr/event-update, tracing data, stat, time-conv, thread/cpu-map, compressed data, BPF metadata, and schedstat handlers. `perf_tool__compressed_is_stub()` detects missing zstd support. `delegate_tool__init()` builds a wrapper whose callbacks forward to another `perf_tool`. With zstd support, `perf_session__process_compressed_event()` streams `PERF_RECORD_COMPRESSED` and `PERF_RECORD_COMPRESSED2` payloads into session decompression buffers.

## Control Flow and State

Initialization sets defaults such as ordered-events mode, feature-header behavior, and deferred callchain merge. Ordered tools get real finished-round handling; unordered tools get a stub. The auxtrace stub consumes auxtrace bytes from pipes so stream alignment remains valid even when a command ignores auxtrace. Compressed handling mmaps a decompression node, preserves leftovers from the previous node, appends to the active decompression chain, and records source file offset/path metadata.

## Dependencies and Integration Points

It depends on session, data, event, stat, header, TSC, zstd helpers when enabled, and ordered-events. Every perf command that processes perf.data or live events relies on this callback table.

## State and Persistence Behavior

`struct perf_tool` is caller-owned state. Delegates store a pointer to an existing tool and do not own it. Decompression nodes are attached to `session->active_decomp` for later event replay.

## Risks and Test Signals

Risks include callback signature mismatch, missing default consumption of variable-length pipe payloads, decompression buffer sizing bugs, and incomplete delegate forwarding when new callbacks are added. Tests should initialize tools with ordered and unordered modes, process ignored auxtrace from a pipe, inspect dump output for stubs, read compressed perf.data with and without zstd support, and verify delegate callbacks forward all event classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/tool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/tool.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/tool.h

## Purpose

`tool.h` defines the `struct perf_tool` event-processing callback interface shared by perf commands.

## Important APIs, Types, and Functions

It declares callback typedefs for sample events, generic events, attr events, session events, auxtrace events, compressed events, and ordered-event rounds. `struct perf_tool` contains callbacks for samples, mmap, comm, namespaces, cgroup, fork/exit, lost data, aux/itrace, context switch, ksymbol, BPF, text poke, attr/update, tracing data, build-id/id-index, auxtrace, maps, stat, time conversion, features, compressed records, schedstat, and behavior flags. `struct delegate_tool` embeds a `perf_tool` plus a delegate pointer.

## Control Flow and State

The header defines the shape of the dispatch table but no implementation logic. Command code fills or overrides callbacks after `perf_tool__init()`.

## Dependencies and Integration Points

It is the ABI between `perf_session` event readers and command-specific processors such as report, script, top, record, inject, and stat.

## Risks and Test Signals

Adding a perf event type requires updating this struct, initialization, delegation, and session dispatch together. Compile tests and callback coverage tests should catch missing fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/tool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/tool_pmu.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/tool_pmu.c

## Purpose

`tool_pmu.c` implements perf's synthetic `tool` PMU. These events are computed by userspace rather than programmed in the kernel and expose elapsed time, user/system CPU time, topology counts, PMEM presence, SMT status, TSC frequency, and target-mode indicators.

## Important APIs, Types, and Functions

Event mapping functions are `tool_pmu__event_to_str()`, `tool_pmu__str_to_event()`, `tool_pmu__skip_event()`, `tool_pmu__num_skip_events()`, `perf_pmu__is_tool()`, `evsel__is_tool()`, `evsel__tool_event()`, and `evsel__tool_pmu_event_name()`. Open/read functions are `evsel__tool_pmu_prepare_open()`, `evsel__tool_pmu_open()`, `tool_pmu__read_event()`, `evsel__tool_pmu_read()`, and `tool_pmu__new()`. Internal parsers read fields from `/proc/stat` and `/proc/<pid>/stat`.

## Control Flow and State

Architecture filters hide `slots` off arm64 and `system_tsc_freq` off x86. Duration events record `rdclock()` at open and emit elapsed nanoseconds only for CPU 0/thread 0. User/system time events open procfs files for each relevant CPU/thread and store starting ticks in `evsel->start_times`; reads seek back to offset zero, read current fields, convert clock ticks to nanoseconds, and report deltas. Static topology events compute values only on CPU 0/thread 0 and write zero elsewhere to avoid aggregation multiplication.

## Dependencies and Integration Points

It depends on evsel counts, xyarray, thread maps, CPU maps, topology, SMT, cgroup fd state, stat configuration, sysfs/procfs, TSC helpers, and the common PMU event table. It integrates with `perf stat` and event parsing under the `tool/` PMU.

## State and Persistence Behavior

State lives in evsel fields: `start_time`, `start_times`, fd array, `pid_stat`, counts, and previous raw counts. PMEM detection is cached statically after checking ACPI NFIT.

## Risks and Test Signals

Risks include fragile procfs field parsing, incorrect CPU/thread aggregation, stale fd ownership on partial open failure, clock tick conversion precision, and platform-specific event visibility. Tests should cover all event names, skipped events per architecture, duration no-sampling validation, per-process and per-CPU user/system deltas, topology events with CPU filters, cgroup pid handling, and lost-count behavior when a synthetic read fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/tool_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/tool_pmu.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/tool_pmu.h

## Purpose

`tool_pmu.h` declares the synthetic userspace PMU interface.

## Important APIs, Types, and Functions

`enum tool_pmu_event` lists `duration_time`, `user_time`, `system_time`, topology and target indicator events, `slots`, and `system_tsc_freq`. `tool_pmu__for_each_event` iterates all real events. The header declares name conversion, skip logic, direct read, PMU/evsel classification, prepare/open/read hooks, CPU slots helper, and PMU construction.

## Control Flow and State

The enum values are stored in `perf_event_attr.config` for tool evsels, so ordering is part of the internal contract.

## Dependencies and Integration Points

It depends on `pmu.h`, evsel, thread maps, and CPU maps. Event parsing and stat reading use this header to identify synthetic events.

## Risks and Test Signals

Risks include enum/name table drift and architecture-specific skip mismatches. Tests should iterate the enum and validate names, reverse lookup, and PMU type classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/tool_pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/top.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/top.c

## Purpose

`top.c` contains shared helpers for `perf top`, primarily construction of the dynamic header line and periodic counter reset.

## Important APIs, Types, and Functions

`perf_top__header_snprintf()` formats sample rate, kernel/user/guest percentages, exact sample percentage, lost/drop counts, selected event, target identity, and CPU coverage. `perf_top__reset_sample_counters()` clears interval counters after a header is emitted.

## Control Flow and State

The formatter derives rates by dividing interval counters by `delay_secs`. It has separate non-guest and guest display paths. If only one event is active, it prints the sample period or frequency. It chooses target text from PID, TID, UID, or all-target mode and includes CPU list or count. It resets interval counters before returning.

## Dependencies and Integration Points

It depends on evlist/evsel, parse-events, symbol globals such as `perf_guest`, target settings in record options, and CPU maps. It is used by stdio and TUI refresh loops.

## Risks and Test Signals

Risks include divide-by-zero when no samples exist, header truncation, lost/drop counters resetting at the wrong time, and incorrect guest percentage math. Tests should format headers for PID/TID/UID/all targets, single and multi-event evlists, explicit CPU lists, guest mode, zero samples, and lost/drop counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/top.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/top.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/top.h

## Purpose

`top.h` defines the shared state structure for `perf top`.

## Important APIs, Types, and Functions

`struct perf_top` embeds a `perf_tool`, evlists, record options, event switch state, interval and total counters, display/filter settings, session pointer, terminal size, symbol filters, LBR stitching toggle, and a two-buffer ordered-event queue with mutex and condition variable. It declares header formatting and counter reset functions. It also defines `CONSOLE_CLEAR`.

## Control Flow and State

The struct is mutable live UI state. Sample processing updates counters and histograms; display code reads and resets interval counters; queue state coordinates event ingestion and rendering.

## Dependencies and Integration Points

It depends on the perf tool dispatch table, evswitch, annotate, ordered-events, record options, mutex/cond wrappers, and terminal ioctls. It is consumed by the `perf top` builtin.

## Risks and Test Signals

Risks include concurrent queue access, counter reset races, and platform differences in terminal clear behavior. Tests should focus on header rendering and queue rotation under event load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/top.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/topdown.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/topdown.c

## Purpose

`topdown.c` provides the weak generic implementation of architecture-specific top-down sample reading.

## Important APIs, Types, and Functions

`arch_topdown_sample_read(struct evsel *leader)` is defined weakly and returns false.

## Control Flow and State

There is no state. Architectures can override the weak symbol to indicate and perform top-down sample reading for event groups.

## Dependencies and Integration Points

It depends on `topdown.h` and is linked into perf unless an architecture implementation replaces it.

## Risks and Test Signals

The default must remain conservative. Tests should verify non-supporting builds return false and architecture builds override as intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/topdown.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/topdown.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/topdown.h

## Purpose

`topdown.h` declares the architecture hook for top-down sample reading.

## Important APIs, Types, and Functions

It forward-declares `struct evsel` and exports `arch_topdown_sample_read()`.

## Control Flow and State

The header has no state. Runtime behavior depends on whether an architecture overrides the weak implementation.

## Dependencies and Integration Points

It is included by common code that wants top-down analysis without depending on a specific PMU backend.

## Risks and Test Signals

The key risk is an architecture override with incompatible semantics. Build tests should verify the declaration matches overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/topdown.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/tp_pmu.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/tp_pmu.c

## Purpose

`tp_pmu.c` exposes tracepoints through the generic PMU event-enumeration interface. It discovers tracepoint systems/events under tracefs, reads event IDs and format files, and reports them as PMU events.

## Important APIs, Types, and Functions

Public functions are `tp_pmu__id()`, `tp_pmu__for_each_tp_event()`, `tp_pmu__for_each_tp_sys()`, `perf_pmu__is_tracepoint()`, `tp_pmu__for_each_event()`, `tp_pmu__num_events()`, and `tp_pmu__have_event()`. Internal callbacks skip non-event directory entries and assemble `struct pmu_event_info` with name, encoding description, long format text, PMU name, and tracepoint descriptor.

## Control Flow and State

System iteration opens tracefs `events`, skips control/header directories, and invokes a system callback. Event iteration opens one system directory, skips `enable` and `filter`, and invokes an event callback. Full PMU enumeration reads `id` for encoding and `format` for the long description, replacing tabs with spaces for rendering. Existence checks split `system:event` and verify the ID can be read.

## Dependencies and Integration Points

It depends on tracefs path helpers, `io_dir`, filename read helpers, PMU definitions, and print-events callbacks. It backs `perf list` and tracepoint PMU lookup.

## State and Persistence Behavior

There is no module-owned persistent state. All data is discovered live from tracefs and returned through callbacks.

## Risks and Test Signals

Risks include disappearing tracepoints during iteration, permission failures, long format allocations, malformed names without colons, and tracefs not mounted. Tests should run with tracefs present and absent, enumerate at least one known tracepoint, verify `system:event` encoding, count events, and handle callback early termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/tp_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/tp_pmu.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/tp_pmu.h

## Purpose

`tp_pmu.h` declares tracepoint PMU discovery and enumeration helpers.

## Important APIs, Types, and Functions

It defines callback typedefs `tp_sys_callback` and `tp_event_callback`, declares tracepoint ID lookup, per-system and per-event iteration, PMU classification, PMU event enumeration, event counting, and existence checking.

## Control Flow and State

The API is callback-driven and has no header-level state.

## Dependencies and Integration Points

It includes `pmu.h` for `struct perf_pmu` and PMU event callback types. It is used by PMU enumeration and tracepoint event parsing paths.

## Risks and Test Signals

Callback users must tolerate negative errno returns and live tracefs changes. Compile tests should cover callback signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/tp_pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/trace-event-info.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/trace-event-info.c

## Purpose

`trace-event-info.c` records the tracefs metadata needed to decode tracepoint raw data later. It serializes trace headers, selected event formats, ftrace formats, printk formats, saved command lines, and a compatibility kallsyms marker into perf.data.

## Important APIs, Types, and Functions

Public functions are `tracing_data_get()`, `tracing_data_put()`, `read_tracing_data()`, `have_tracepoints()`, and `tracepoint_id_to_name()`. Internal helpers include `record_file()`, `record_header_files()`, `copy_event_system()`, `record_ftrace_files()`, `record_event_files()`, `record_proc_kallsyms()`, `record_ftrace_printk()`, `record_saved_cmdline()`, `tracepoint_id_to_path()`, `tracepoint_name_to_path()`, `get_tracepoints_path()`, and `tracing_data_header()`. `struct tracepoint_path` links selected subsystem/event pairs.

## Control Flow and State

`get_tracepoints_path()` walks evsels and builds a selected tracepoint list from names or config IDs. `tracing_data_get()` sets a file-scope `output_fd`, optionally writes to a temporary file, emits the magic/version/endian/long/page header, then records header files, ftrace event formats, selected event-system formats, a zero-sized kallsyms placeholder, printk formats, and saved cmdlines. `tracing_data_put()` copies the temp file into the final output if temp mode was used and unlinks it.

## Dependencies and Integration Points

It depends on tracefs path helpers, tracepoint iteration macros, evsel attributes, libtraceevent-compatible format text, host endianness helpers, page size, and perf debug output. It integrates with `perf record` tracing data feature generation and with `trace-event-read.c` replay.

## State and Persistence Behavior

The serialized stream becomes persistent perf.data metadata. Temporary mode stores the stream under `/tmp/perf-XXXXXX` until copied. `output_fd` is global module state during recording, so calls are not reentrant.

## Risks and Test Signals

Risks include tracefs files changing during recording, endian-size backpatch errors, temp-file leaks, missing tracepoint IDs, and format counts that do not match payloads. Tests should record a tracepoint workload, replay with `perf script`, compare event names from config IDs, validate temp and direct modes, handle absent `printk_formats` and `saved_cmdlines`, and verify old-parser compatibility for zero kallsyms payload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/trace-event-info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/trace-event-parse.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/trace-event-parse.c

## Purpose

`trace-event-parse.c` provides libtraceevent parsing helpers for tracepoint raw data, common fields, ftrace format files, event format files, saved command lines, printk format strings, task state strings, and symbolic flag values.

## Important APIs, Types, and Functions

Public helpers include `common_lock_depth()`, `common_flags()`, `common_pc()`, `raw_field_value()`, `read_size()`, `event_format__fprintf()`, `parse_task_states()`, `parse_ftrace_printk()`, `parse_saved_cmdline()`, `parse_ftrace_file()`, `parse_event_file()`, and `eval_flag()`. Internal recursive helpers search libtraceevent print arguments to find task-state flag mappings.

## Control Flow and State

Common-field helpers lazily cache offsets and sizes in static variables using the first event in the `tep_handle`. Raw field helpers locate fields by name and use libtraceevent number readers. Print helpers wrap raw bytes in a `tep_record` and ask libtraceevent to render `TEP_PRINT_INFO`. `parse_ftrace_printk()` registers address-to-format strings, `parse_saved_cmdline()` registers PID-to-comm mappings, and event parsers pass format text to `tep_parse_event()`.

## Dependencies and Integration Points

It depends on libtraceevent types, scripting context, debug logging, and trace-event declarations. It is used by `perf script`, trace-event readback, and scripting language bindings.

## State and Persistence Behavior

The module mutates the caller's `tep_handle` by registering events, comms, and printk strings. The static common-field caches are process-global and assume a stable field layout.

## Risks and Test Signals

Risks include the common-field helper argument order bug potential because offset/size pointers must be correct, stale static caches across different trace handles, malformed printk/cmdline input, and missing symbolic flags. Tests should parse recorded tracing data, render raw events, read common fields, decode sched task states, register printk formats, register saved cmdlines, and evaluate known softirq/hrtimer symbolic constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/trace-event-parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/trace-event-read.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/trace-event-read.c

## Purpose

`trace-event-read.c` reads the tracing metadata stream produced by `trace-event-info.c` and reconstructs a `struct trace_event`/libtraceevent handle for perf.data replay.

## Important APIs, Types, and Functions

The public function is `trace_report(int fd, struct trace_event *tevent, bool repipe)`. Internal helpers read exact byte counts, optionally repipe bytes to stdout, read strings, skip legacy kallsyms, read and parse header files, ftrace files, event files, printk formats, and saved command lines.

## Control Flow and State

`trace_report()` validates the magic bytes and `"tracing"` tag, reads the version string, endian flag, long size, and page size, initializes a trace-event handle, sets libtraceevent endian/size configuration, then parses headers, ftrace formats, event formats, kallsyms placeholder, printk data, and saved cmdlines for version 0.6 and newer. It returns the number of bytes consumed or -1 on failure.

## Dependencies and Integration Points

It depends on libtraceevent, trace-event parsing helpers, host endian detection, and debug logging. It is used when reading perf.data trace metadata before decoding tracepoint raw samples.

## State and Persistence Behavior

Module-level `input_fd`, `trace_data_size`, and `repipe` hold current read state, making parsing non-reentrant. Successful parsing leaves `tevent->pevent` initialized for later event formatting.

## Risks and Test Signals

Risks include corrupt size fields causing large allocations, non-reentrant globals, repipe write failures, version-gated saved-cmdline parsing, and endian/long-size mismatches. Tests should round-trip metadata from `trace-event-info.c`, parse older streams without saved cmdlines, reject bad magic/tag, exercise repipe mode, and run with big-endian fixture data when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/trace-event-read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/trace-event-scripting.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/trace-event-scripting.c

## Purpose

`trace-event-scripting.c` manages scripting-engine registration and common scripting context updates, and it formats branch/sample flags for script output.

## Important APIs, Types, and Functions

Public globals/functions include `scripting_max_stack`, `scripting_context`, `script_spec__lookup()`, `script_spec__for_each()`, `setup_python_scripting()`, `setup_perl_scripting()`, `scripting_context__update()`, and `perf_sample__sprintf_flags()`. Internal `struct script_spec` links a spec string such as `Python`, `py`, `Perl`, or `pl` to `struct scripting_ops`. Unsupported Python/Perl ops print rebuild guidance and return errors for start/generate.

## Control Flow and State

Setup allocates the global scripting context and registers language aliases to either real ops or unsupported stubs based on build flags. Context update copies the current event, sample, evsel, address locations, raw data, and trace-event parser handle into the global context. Flag formatting first tries named branch types and events, including trace begin/end and transaction/additional-state annotations; if no named format matches, it falls back to raw bit characters.

## Dependencies and Integration Points

It depends on libtraceevent when available, perf samples, evsels, address locations, and optional Python/Perl support. It is used by `perf script` and generated scripts.

## State and Persistence Behavior

Script specs and scripting context are process-global. Registered ops persist for the process lifetime. Context fields are overwritten for each processed event.

## Risks and Test Signals

Risks include duplicate spec registration disabling scripting, missing context allocation, unsupported builds returning confusing errors, and flag string truncation/alignment mistakes. Tests should verify Python/Perl alias lookup, unsupported messages, context update for tracepoint and non-tracepoint evsels, callback iteration, and formatting for calls, returns, trace boundaries, branch misses, not-taken branches, transactions, and unknown bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/trace-event-scripting.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/trace-event.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/trace-event.c

## Purpose

`trace-event.c` owns the common libtraceevent handle used for live tracepoint format lookup and function resolution.

## Important APIs, Types, and Functions

Public functions are `trace_event__init()`, `trace_event__cleanup()`, `trace_event__register_resolver()`, `trace_event__tp_format()`, and `trace_event__tp_format_id()`. Internal `tp_format()` reads a tracefs `format` file and parses it into a `tep_event`.

## Control Flow and State

`trace_event__init()` allocates a `tep_handle` and loads plugins. A file-scope `tevent` and `tevent_initialized` are lazily initialized by `trace_event__init2()`, which sets nanosecond output and endian flags. Format lookup by name reads `events/<sys>/<name>/format`; lookup by ID asks libtraceevent for an already parsed event. Cleanup unloads plugins and frees the handle.

## Dependencies and Integration Points

It depends on libtraceevent, tracefs path helpers, machine resolver callbacks, and filename read helpers. It supports event parsing, scripting, and tracepoint formatting.

## State and Persistence Behavior

The global trace-event object has no registered cleanup hook according to the local TODO, so process lifetime owns it. Parsed events persist in the `tep_handle`.

## Risks and Test Signals

Risks include global lifetime leaks, stale tracefs formats after initialization, error-pointer handling, and plugin load/unload mismatches. Tests should initialize and cleanup explicit handles, lazily fetch a known tracepoint format, lookup by ID after parsing, and register a symbol resolver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/trace-event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/trace-event.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/trace-event.h

## Purpose

`trace-event.h` is the shared declaration point for trace-event metadata, parsing, scripting, and formatting utilities.

## Important APIs, Types, and Functions

It defines `struct trace_event`, `MAKE_LIBTRACEEVENT_VERSION`, `tep_func_resolver_t`, `struct tracing_data`, `struct scripting_ops`, and `struct scripting_context`. It declares trace initialization/cleanup, tracepoint format lookup, event-format printing/parsing, raw field access, task-state parsing, trace metadata reading/writing, scripting registration, context update, common field helpers, and sample flag formatting. It also defines `SAMPLE_FLAGS_BUF_SIZE`, `SAMPLE_FLAGS_STR_ALIGNED_SIZE`, and a compatibility `tep_field_is_relative()` helper.

## Control Flow and State

The header ties several subsystems together: metadata capture/replay, live tracefs format lookup, and script engine event callbacks. `struct scripting_ops` is a vtable for language-specific script engines.

## Dependencies and Integration Points

It depends on libtraceevent types, perf events, sessions, samples, evsels, machines, and address locations. It is included by trace readers, script engines, and tracepoint users.

## Risks and Test Signals

Risks include version compatibility with libtraceevent, callback ABI drift, and build configurations without libtraceevent/Python/Perl. Compile matrix tests should cover feature combinations and verify compatibility helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/trace-event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/trace.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/trace.h

## Purpose

`trace.h` declares optional BPF-backed syscall/trace summary support for perf trace.

## Important APIs, Types, and Functions

`enum trace_summary_mode` selects no summary, total summary, per-thread summary, or per-cgroup summary. With `HAVE_BPF_SKEL`, the header declares prepare/start/end/print/cleanup functions. Without BPF skeleton support, inline stubs return failure or no-op.

## Control Flow and State

The header provides build-time feature gating. Runtime code can call the same API and receive `-1`/no-op behavior on unsupported builds.

## Dependencies and Integration Points

It depends only on `FILE` and is consumed by `perf trace` code that wants optional BPF aggregation.

## Risks and Test Signals

Risks include callers assuming BPF support unconditionally or ignoring `trace_prepare_bpf_summary()` failure. Tests should build with and without BPF skeleton support and verify graceful fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/trace_augment.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/trace_augment.h

## Purpose

`trace_augment.h` declares optional BPF augmentation helpers for syscall tracing.

## Important APIs, Types, and Functions

With `HAVE_BPF_SKEL`, it declares preparation, BPF output creation/setup, PID filtering, map fd retrieval, BPF program lookup by title, unaugmented program lookup, and cleanup. Without BPF skeleton support, inline stubs return `-1`, `0`, or `NULL` as appropriate.

## Control Flow and State

The header is a feature gate; implementation state exists only in BPF-enabled builds.

## Dependencies and Integration Points

It references `struct bpf_program` and `struct evlist`. `perf trace` uses it to attach augmentation programs that enrich syscall enter/exit data.

## Risks and Test Signals

Risks include callers failing to handle disabled support, PID filter no-op semantics in stub builds, and map fd lifetime in real builds. Build tests should cover both feature configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/trace_augment.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/tracepoint.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/tracepoint.c

## Purpose

`tracepoint.c` provides low-level helpers for validating tracepoint event directories and `system:event` strings.

## Important APIs, Types, and Functions

`tp_event_has_id()` checks whether a tracepoint event directory has an `id` file. `is_valid_tracepoint()` converts `system:event` to `system/event/id`, resolves it under tracefs events, and checks file availability.

## Control Flow and State

Validation allocates a path buffer, replaces colon with slash, appends `/id`, calls `get_events_file()`, then checks the resulting file and frees both buffers. There is no persistent state.

## Dependencies and Integration Points

It depends on tracefs path helpers and `fncache` file availability. It backs tracepoint iteration macros in the header and CLI validation of tracepoint event names.

## Risks and Test Signals

Risks include malformed strings without colons, allocation failure, tracefs unavailability, and event directories racing away. Tests should validate known good and bad tracepoints and paths with missing `id` files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/tracepoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/tracepoint.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/tracepoint.h

## Purpose

`tracepoint.h` declares tracepoint validation helpers and directory iteration macros.

## Important APIs, Types, and Functions

It declares `tp_event_has_id()` and `is_valid_tracepoint()`. `for_each_event` iterates tracepoint event directories that are not `.`/`..` and have an `id` file. `for_each_subsystem` iterates tracepoint subsystem directories.

## Control Flow and State

The macros embed filtering logic around `readdir()` and call `tp_event_has_id()` for event validation.

## Dependencies and Integration Points

It depends on `dirent`, `string`, and bool support. It is used by trace metadata capture and tracepoint discovery.

## Risks and Test Signals

Macros can be surprising because they expand to `while` plus `if` blocks. Tests should exercise iteration with fake tracefs directories and ensure non-events are skipped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/tracepoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/trigger.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/trigger.h

## Purpose

`trigger.h` implements a tiny state machine for operations that wait for an observed event, such as signal-driven transitions.

## Important APIs, Types, and Functions

`struct trigger` contains a volatile enum state and name. States are `TRIGGER_ERROR`, `TRIGGER_OFF`, `TRIGGER_ON`, `TRIGGER_READY`, and `TRIGGER_HIT`. Inline operations are `trigger_is_available()`, `trigger_is_error()`, `trigger_on()`, `trigger_ready()`, `trigger_hit()`, `trigger_off()`, `trigger_error()`, `trigger_is_ready()`, and `trigger_is_hit()`. `DEFINE_TRIGGER(name)` creates an off trigger.

## Control Flow and State

The intended transition is OFF to ON to READY to HIT, with HIT able to return to READY. Invalid transitions warn once. Error/off states make ready/hit/off operations no-op except explicit error.

## Dependencies and Integration Points

It depends on perf's `WARN_ONCE` support. It is used by command code that needs lightweight trigger coordination without a full synchronization primitive.

## Risks and Test Signals

The state is volatile but not atomic, so this is not a complete thread-safety primitive. Tests should check transition warnings, no-op behavior for off/error states, and `DEFINE_TRIGGER` initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/trigger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/tsc.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/tsc.c

## Purpose

`tsc.c` converts between perf nanosecond timestamps and hardware time-stamp-counter cycles, reads conversion parameters from the perf mmap page, and synthesizes `PERF_RECORD_TIME_CONV` events.

## Important APIs, Types, and Functions

Public functions are `perf_time_to_tsc()`, `tsc_to_perf_time()`, `perf_read_tsc_conversion()`, `perf_event__synth_time_conv()`, weak `rdtsc()`, and `perf_event__fprintf_time_conv()`.

## Control Flow and State

Conversion uses `time_zero`, `time_mult`, and `time_shift`; short-time support masks cycles relative to `time_cycles`. `perf_read_tsc_conversion()` loops on the mmap page seqlock, uses read barriers, retries up to 10000 times, and requires `cap_user_time_zero`. Synthesis fills a perf event and invokes a supplied process callback unless conversion is unsupported. Formatting prints base fields and extended short-time fields only when the record contains them.

## Dependencies and Integration Points

It depends on perf event mmap page ABI, event synthesis, machine/tool callbacks, barrier primitives, and debug output. It integrates with record headers and readers that need timestamp conversion.

## State and Persistence Behavior

There is no global state. Conversion data can be persisted into perf.data as `PERF_RECORD_TIME_CONV`.

## Risks and Test Signals

Risks include seqlock races, unsupported `cap_user_time_zero`, overflow in conversion arithmetic, and backward compatibility with shorter records. Tests should read a live mmap page, synthesize and process time-conv events, round-trip ns/cycles for known conversion values, and format old/new record sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/tsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/tsc.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/tsc.h

## Purpose

`tsc.h` declares perf timestamp/TSC conversion support.

## Important APIs, Types, and Functions

`struct perf_tsc_conversion` stores `time_shift`, `time_mult`, `time_zero`, `time_cycles`, `time_mask`, and capability bits. The header declares conversion, mmap-page reading, `rdtsc()`, `arch_get_tsc_freq()`, and time-conv event formatting.

## Control Flow and State

The header has no state. Architecture code may provide `rdtsc()` and `arch_get_tsc_freq()` implementations.

## Dependencies and Integration Points

It includes `event.h` for perf event types and is used by TSC conversion records, tool PMU frequency reporting, and timestamp-sensitive code.

## Risks and Test Signals

Risks are ABI drift with `perf_event_mmap_page` and missing architecture hooks. Build tests should cover x86 and non-x86 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/tsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/units.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/units.c

## Purpose

`units.c` provides simple unit parsing and scaling helpers for perf output and option parsing.

## Important APIs, Types, and Functions

`parse_tag_value()` parses a decimal number followed by a recognized single-character tag multiplier. `convert_unit_double()` scales values by 1000 into K/M/G and returns the scaled double plus unit char. `convert_unit()` wraps that for unsigned long. `unit_number__scnprintf()` formats byte-like numbers using 1024 steps and units B/K/M/G.

## Control Flow and State

The module has no state. Parsing walks the provided tag table and returns `(unsigned long)-1` on no match, overflow, or malformed input.

## Dependencies and Integration Points

It depends on Linux `scnprintf`, time/integer constants, and caller-provided tag tables. It is used by command-line parsers and display code.

## Risks and Test Signals

Risks include confusing 1000 vs 1024 scaling, overflow in multiplier application, and accepting embedded tag positions only when the numeric parse stops at the tag. Tests should cover valid suffixes, unknown suffixes, overflow, boundary values around 1000/1024, and formatting buffer sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/units.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/units.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/units.h

## Purpose

`units.h` declares unit parsing and scaling helpers.

## Important APIs, Types, and Functions

It defines `struct parse_tag { char tag; int mult; }` and declares `parse_tag_value()`, `convert_unit_double()`, `convert_unit()`, and `unit_number__scnprintf()`.

## Control Flow and State

No header-level state exists. Callers provide null-terminated tag arrays.

## Dependencies and Integration Points

It depends on Linux `u64` and standard `size_t`. It is included by option parsing and output formatting code.

## Risks and Test Signals

Callers must ensure the tag table ends with `tag == 0`. Compile tests should check declaration consistency with the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/units.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/unwind-libdw.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/unwind-libdw.c

## Purpose

`unwind-libdw.c` implements DWARF callchain unwinding using elfutils libdwfl. It unwinds post-mortem samples from captured user registers and user stack dumps.

## Important APIs, Types, and Functions

Public functions are `unwind__get_entries()` for libdw builds and `libdw__invalidate_dwfl()`. Internal types include `struct dwfl_ui_thread_info`, which stores a cached `Dwfl` and current `unwind_info`. Key helpers report modules to DWFL, read memory from sample stack or DSOs, map perf registers to DWARF registers, process frames, and store `unwind_entry` records.

## Control Flow and State

`unwind__get_entries()` validates user regs, allocates an `unwind_info` with entry storage, obtains or creates a per-maps DWFL, sets it as busy, reads the initial IP, reports the module, attaches thread state callbacks, and calls `dwfl_getthread_frames()`. Frame callbacks adjust non-activation PCs, report modules, store entries, and stop at max depth. After unwind, entries are emitted in caller or callee order according to `callchain_param.order`, map symbols are released, and the cached DWFL is marked idle.

## Dependencies and Integration Points

It depends on libdw/libdwfl, DSOs, maps, symbols, threads, machine/env, perf regs, callchain ordering, sample user stack/regs, and build-id or symfs paths. It integrates with DWARF callchain sampling and map invalidation.

## State and Persistence Behavior

The DWFL object is cached on `struct maps` and invalidated by `libdw__invalidate_dwfl()`. During one unwind, `dwfl_ui_thread_info->ui` points to current state and asserts only one unwind per DWFL. Entries are transient and passed to the caller callback.

## Risks and Test Signals

Risks include stale cached DWFL after map changes, missing user regs/stack, unsafe unaligned stack reads, DSO module base mismatches, JIT mapping base handling, and silent best-effort failures. Tests should capture DWARF callchains, unwind through shared libraries and JIT-like maps, invalidate maps, test caller/callee ordering, handle truncated stacks, and run with and without debuginfo/build-id paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/unwind-libdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/unwind-libdw.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/unwind-libdw.h

## Purpose

`unwind-libdw.h` declares libdw-specific unwind state when libdw support is enabled.

## Important APIs, Types, and Functions

Under `HAVE_LIBDW_SUPPORT`, `struct unwind_info` stores DWFL pointer, sample, machine, thread, callback, callback data, max stack, entry index, ELF flags/machine, best-effort flag, and a flexible array of `unwind_entry`. It declares `libdw__invalidate_dwfl()`.

## Control Flow and State

The state object is per-unwind invocation, while the DWFL pointer may come from maps-level cache.

## Dependencies and Integration Points

It includes `unwind.h` and references maps, machine, sample, and thread structures. It is consumed by libdw unwinding and map cleanup code.

## Risks and Test Signals

Risks include conditional compilation drift between libdw-enabled and disabled builds. Build tests should cover both configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/unwind-libdw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/unwind-libunwind-local.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/unwind-libunwind-local.c

## Purpose

`unwind-libunwind-local.c` implements local post-mortem DWARF unwinding using libunwind over perf's captured register and stack dumps.

## Important APIs, Types, and Functions

The file defines libunwind accessors for procedure info, memory, registers, unsupported fpregs/resume/name lookups, and cache cleanup. It includes ELF helpers for `.eh_frame_hdr`, `.debug_frame`, executable detection, and base address calculation. Publicly, it publishes `local_unwind_libunwind_ops` with `prepare_access`, `flush_access`, `finish_access`, and `get_entries`.

## Control Flow and State

`_unwind__prepare_access()` creates a libunwind address space with custom accessors and stores it on maps. `find_proc_info()` locates the map/DSO for an IP, tries `.eh_frame_hdr` first using libunwind's remote table search, then `.debug_frame` when enabled. `access_mem()` reads from the captured stack if an address falls in the sampled stack range, otherwise reads from mapped DSO data. `access_reg()` maps libunwind registers to perf regs and reads from sample user regs. `_unwind__get_entries()` builds initial state and `get_entries()` records the sampled IP, initializes a remote cursor, steps frames up to max depth, adjusts non-signal-frame return IPs, and emits entries in configured order.

## Dependencies and Integration Points

It depends on libunwind, libelf/gelf, maps, DSOs, symbols, machine/session, perf regs, callchain configuration, and sample user stack/regs. `unwind-libunwind.c` selects these ops for supported target architectures.

## State and Persistence Behavior

The libunwind address space is stored in maps and uses global caching policy. DSO data caches `.eh_frame_hdr`, `.debug_frame`, and ELF base offsets. Unwind entries are transient callback outputs.

## Risks and Test Signals

Risks include unsupported pointer encodings, stale address-space caches, missing CFI sections, debuglink path failures, stack range boundary mistakes, register mapping gaps, and architecture mismatch for 32-bit or arm targets. Tests should cover unwinding through binaries with `.eh_frame_hdr`, `.debug_frame`, debuglink debuginfo, missing stack/register data, cache flush/finish, caller/callee ordering, and mixed-architecture perf.data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/unwind-libunwind-local.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/unwind-libunwind.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/unwind-libunwind.c

## Purpose

`unwind-libunwind.c` selects and dispatches libunwind operations for a thread's maps based on build support, target architecture, and DSO bitness.

## Important APIs, Types, and Functions

It defines weak operation pointers `local_unwind_libunwind_ops`, `x86_32_unwind_libunwind_ops`, and `arm64_unwind_libunwind_ops`. Public functions are `unwind__prepare_access()`, `unwind__flush_access()`, `unwind__finish_access()`, and `unwind__get_entries()`.

## Control Flow and State

Preparation is skipped if no DWARF callchain users exist or an address space is already initialized. Otherwise it inspects machine environment architecture and DSO type to choose local, x86-32, or arm64 ops, stores selected ops on maps, and invokes `prepare_access()`. Flush/finish/get delegate through maps-stored ops when present.

## Dependencies and Integration Points

It depends on DSO type detection, maps state, thread maps, machine env architecture, session callchain globals, and architecture-specific libunwind backends. It is called from map insertion and thread preparation paths.

## State and Persistence Behavior

Selected ops and address space are stored in maps. Preparation can report `initialized` to indicate whether a new address space was created.

## Risks and Test Signals

Risks include unsupported arch warnings, wrong backend for mixed-bit DSOs, live mode with missing env arch, and no-op behavior when ops are unavailable. Tests should cover live mode, x86 32-bit perf.data on 64-bit host, arm/arm64 selection, unsupported arch, repeated prepare, flush, finish, and get without ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/unwind-libunwind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/unwind.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/unwind.h

## Purpose

`unwind.h` declares the generic DWARF unwind abstraction used by perf callchain code.

## Important APIs, Types, and Functions

`struct unwind_entry` carries a `map_symbol` and IP. `unwind_entry_cb_t` is the callback type. `struct unwind_libunwind_ops` is the backend vtable for prepare, flush, finish, and entry extraction. Depending on build flags, the header declares real `unwind__get_entries()`, libunwind register and access functions, or inline no-op stubs.

## Control Flow and State

The header gates unwind functionality by `HAVE_DWARF_UNWIND_SUPPORT` and `HAVE_LIBUNWIND_SUPPORT`. Unsupported builds compile callers but return no entries.

## Dependencies and Integration Points

It depends on map-symbol state and is used by callchain sampling, thread map insertion, and report/script unwinding.

## Risks and Test Signals

Risks include callers not distinguishing no-op stubs from successful empty unwinds, and build matrix drift. Tests should cover DWARF-enabled and disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/unwind.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/usage.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/usage.c

## Purpose

`usage.c` provides perf's generic usage strings and a basic usage reporting hook.

## Important APIs, Types, and Functions

It defines `perf_usage_string`, `perf_more_info_string`, static `usage_builtin()`, a static `usage_routine` pointer initialized to that builtin, and public `usage(const char *err)`.

## Control Flow and State

`usage()` calls the current usage routine, which prints `Usage: <err>` to stderr and exits with status 129. The routine pointer is kept static to avoid writes through globals in dlopened shared objects.

## Dependencies and Integration Points

It depends on stdio/stdlib and is included through `util.h`. CLI command parsing calls `usage()` on fatal syntax errors.

## Risks and Test Signals

Risks are limited: `usage()` is noreturn and unsuitable for recoverable errors. Tests should verify output and exit status for invalid command invocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/usage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/util.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/util.c

## Purpose

`util.c` collects general perf utility functions for global mode flags, sysctl reads, perf attributes, directory creation/removal, CPU mask conversion, permissions, random tips, executable path discovery, debuginfod setup, chroot path expansion, dynamic array growth, and portability shims.

## Important APIs, Types, and Functions

Global state includes `input_name`, `perf_singlethreaded`, `sysctl_perf_event_max_stack`, `sysctl_perf_event_max_contexts_per_stack`, `exclude_GH_default`, `perf_host`, and `perf_guest`. Public functions include `perf_set_singlethreaded()`, `perf_set_multithreaded()`, `sysctl__max_stack()`, `sysctl__nmi_watchdog_enabled()`, `event_attr_init()`, `mkdir_p()`, `rm_rf_perf_data()`, `rm_rf()`, `lsdir_no_dot_filter()`, `lsdir()`, `cpumask_to_cpulist()`, `print_separator2()`, `hex_width()`, `perf_event_paranoid()`, `perf_event_paranoid_check()`, `perf_tip()`, `perf_exe()`, `perf_debuginfod_setup()`, `filename_with_chroot()`, `do_realloc_array_as_needed()`, compatibility `sched_getcpu()`, compatibility `scandirat()`, and `perf_basename()`.

## Control Flow and State

Sysctl helpers cache max stack/context settings and NMI watchdog status. `event_attr_init()` sets attr size and optional host/guest exclusion defaults. Recursive removal uses `lstat`, pattern matching, and depth limits; perf-data removal specially removes kcore directories only if their contents match expected names. CPU mask conversion parses hex blocks into a bitmap and formats a CPU list. Permission checks accept CAP_SYS_ADMIN, CAP_PERFMON, or a low enough `perf_event_paranoid`. Debuginfod setup clears or sets `DEBUGINFOD_URLS` based on CLI configuration and warns when support is not compiled in. Array growth doubles capacity with overflow checks and initializes new slots.

## Dependencies and Integration Points

It depends on procfs/sysctl helpers, capabilities, strlist/string helpers, bitmap formatting, Linux constants, perf debug logging, and libc filesystem APIs. It is widely used by command setup, cleanup, permission diagnostics, perf.data management, and UI output.

## State and Persistence Behavior

Some global booleans affect future event attribute initialization. Environment variable changes for debuginfod persist in the process. Filesystem helpers create or delete real paths; callers must ensure paths are safe.

## Risks and Test Signals

Risks include dangerous recursive deletion if callers pass wrong paths, pattern-removal partial failures, cpumask buffer assumptions, stale sysctl cache, environment side effects, lost old array pointer in `do_realloc_array_as_needed()` because it does not free the old array after copying, and portability syscall behavior. Tests should cover mkdir recursion, safe rm patterns, kcore cleanup constraints, cpumask conversions, permission checks under mocked sysctls/caps, debuginfod env modes, chroot filename generation, array growth initialization, and basename behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/util.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/util.h

## Purpose

`util.h` declares shared utility APIs and global settings used throughout perf.

## Important APIs, Types, and Functions

It declares usage strings, `input_name`, host/guest exclusion globals, filesystem helpers, sysctl helpers, tips, CPU mask conversion, threading mode flags, executable path, debuginfod configuration, basename/chroot helpers, dynamic array growth, endian detection, and compatibility declarations for `sched_getcpu()` and `scandirat()`. It defines `struct perf_debuginfod`, `realloc_array_as_needed()`, and inline `host_is_bigendian()`.

## Control Flow and State

Most declarations reference process-global state. The `realloc_array_as_needed()` macro evaluates the requested index once and calls the implementation only when growth is needed.

## Dependencies and Integration Points

It pulls in common POSIX and Linux headers and is one of perf's broad utility include points.

## Risks and Test Signals

Risks include macro side effects, buffer-size assumptions for `perf_exe()`, and byte-order detection portability. Compile and unit tests should exercise the macro with side-effecting expressions and both compiler/endian paths where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/values.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/values.c

## Purpose

`values.c` accumulates read-format counter values by PID/TID and evsel, then prints them in pretty or raw tabular form.

## Important APIs, Types, and Functions

Public functions are `perf_read_values_init()`, `perf_read_values_destroy()`, `perf_read_values_add_value()`, and `perf_read_values_display()`. Internal helpers grow thread arrays, find or create thread rows, grow counter arrays, find or create counter columns, and render pretty/raw output.

## Control Flow and State

Initialization allocates arrays for 16 threads and 16 counters. Adding a value creates a row for `(pid, tid)` if needed, creates a counter column for the evsel if needed, and accumulates into `value[row][column]`. Pretty display computes dynamic column widths for PID/TID and event names/counts. Raw display prints PID, TID, event name, raw evsel index, and count for each row/column pair.

## Dependencies and Integration Points

It depends on evsel names and indices, debug logging, and zalloc helpers. It is used by perf read/stat style reporting paths that need per-thread counter summaries.

## State and Persistence Behavior

All state is in caller-owned `struct perf_read_values`. Destroy frees per-thread value arrays and all top-level arrays. Values are accumulated in memory only.

## Risks and Test Signals

Risks include partial realloc leaks in enlarge paths, raw display missing line terminators, large table memory growth, and evsel pointer identity being the counter key. Tests should initialize/destroy, add repeated values, force thread/counter growth, print pretty/raw output, and handle allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/values.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/values.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/values.h

## Purpose

`values.h` declares the per-thread/per-counter read-values table.

## Important APIs, Types, and Functions

`struct perf_read_values` stores row count/capacity, PID/TID arrays, counter count/capacity, evsel pointer array, and a 2D value array. It declares init, destroy, add-value, and display functions.

## Control Flow and State

The table is mutable caller-owned state. Rows are keyed by PID/TID and columns by evsel pointer.

## Dependencies and Integration Points

It depends on Linux integer types and `FILE`; evsel is forward-declared. It is used by code that accumulates `PERF_RECORD_READ` results.

## Risks and Test Signals

Callers must initialize before use and destroy once. Tests should verify zeroed state and repeated accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/values.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/vdso.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/vdso.c

## Purpose

`vdso.c` materializes the process vDSO image as temporary files and registers matching DSOs in a machine. This lets perf symbolize vDSO samples, including compat 32-bit and x32 vDSOs on 64-bit builds when helper programs are available.

## Important APIs, Types, and Functions

Internal `struct vdso_file` tracks whether a temp file was found or errored, the temp filename template, DSO name, and optional helper program. `struct vdso_info` contains native and compat vDSO slots. Public functions are `machine__exit_vdso()`, `machine__findnew_vdso()`, and `dso__is_vdso()`. Internal helpers copy the in-memory native vDSO via `find_map()`, create DSOs, determine a thread's DSO type from maps, run compat helper programs, and find existing vDSO DSOs.

## Control Flow and State

`machine__findnew_vdso()` lazily allocates `machine->vdso_info`, checks for an existing type-appropriate vDSO DSO, tries compat vDSO creation for 32-bit/x32 threads on 64-bit hosts, otherwise copies the current process `[vdso]` mapping to `/tmp/perf-vdso.so-XXXXXX` and adds a DSO with that long name. `machine__exit_vdso()` unlinks any created temp files and frees the info. `dso__is_vdso()` checks short names against native and compat constants.

## Dependencies and Integration Points

It depends on DSOs, maps, symbols, machine, thread maps, temporary-file APIs, helper binaries `perf-read-vdso32` and `perf-read-vdsox32`, and `find-map.c`. It integrates with symbol resolution for user samples in vDSO regions.

## State and Persistence Behavior

Temporary files persist until `machine__exit_vdso()` unlinks them. `vdso_file` caches success or failure to avoid repeated work. The DSO list stores references to the temp file paths.

## Risks and Test Signals

Risks include temp-file leaks, helper program failures, wrong DSO type selection for mixed 32/64-bit workloads, copying the current process vDSO when analyzing a different environment, and stale error caching. Tests should symbolize native vDSO samples, exercise compat helper availability and absence, verify cleanup unlinks temp files, detect `dso__is_vdso()` names, and analyze workloads with mixed bitness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/vdso.c -->
