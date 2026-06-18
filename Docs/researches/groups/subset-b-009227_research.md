# subset-b-009227 research

Grouped research report for fio graphing, helper-thread, idle-profiler, initialization, I/O unit, queue, and I/O engine source files. Each section preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/graph.c -->
# sources/test-tools/fio/graph.c

## Purpose
Implements gfio's Cairo/GTK graph model and drawing routines. It supports bar graphs, line graphs, labels, colors, tick labels, unit-scaling callbacks, bounded history for live line graphs, and tooltip lookup for XY samples.

## Important APIs, Types, and Functions
Private state is held in `struct graph`, `struct graph_label`, `struct graph_value`, and `struct xyvalue`. Public functions from `graph.h` are implemented here: `graph_new`, `graph_set_size`, `graph_set_position`, `graph_set_font`, title setters, `graph_add_label`, `graph_add_data`, `graph_add_xy_data`, `graph_set_color`, `bar_graph_draw`, `line_graph_draw`, `graph_add_extra_space`, `line_graph_set_data_count_limit`, tooltip helpers, `graph_clear_values`, and `graph_free`. Important internal helpers include `graph_draw_common`, tick drawing, min/max scanners, `graph_label_add_value`, `graph_value_drop`, and priority-tree tooltip search.

## Control Flow
Callers create a graph, add labels, append values, optionally assign colors and axis callbacks, then draw into a Cairo context. Bar drawing computes one group per label and one bar per value. Line drawing scans all XY values for ranges, applies extra margins, records tick transforms, draws ticks and grid lines, then strokes each visible label's polyline. Tooltip insertion stores an X interval in a priority tree; lookup converts screen coordinates back into graph-space values using tick transform fields captured during the last draw and then chooses the closest Y match.

## State and Persistence Behavior
All state is in memory. Labels and values are heap-allocated and linked in fio `flist` lists. Tooltip-capable XY values are additionally indexed by `prio_tree_root`; duplicate X ranges become aliases on the existing priority-tree node. `per_label_limit` drops oldest samples when live graphs exceed the configured count. `graph_clear_values` drops values but retains labels, while `graph_free` frees titles and labels but does not free the `struct graph` object itself.

## Dependencies and Integration Points
Depends on Cairo, GTK, `tickmarks`, `cairo_text_helpers`, fio `flist`, and `lib/prio_tree`. It is used by gfio UI components to render bandwidth, latency, and other runtime charts.

## Risks
Several drawing paths divide by data ranges and assume non-empty labels or values; degenerate data is partly guarded with "No good data" fallbacks, but empty bar graphs can still produce unsafe label-width math. Tooltip correctness depends on a prior draw call to populate tick transform fields. `setstring()` assumes non-null strings. `graph_free()` omits `free(bg)`, so ownership expectations must stay clear. The code is not synchronized and is intended for UI-thread use.

## Test Signals
There are no direct unit tests in this subset. Useful coverage would render empty, single-valued, negative, all-zero, and bounded-history graphs; assert that tooltip lookup survives duplicate X ranges; run under ASan or Valgrind for add/drop/free cycles; and visually compare gfio charts.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/graph.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/graph.h -->
# sources/test-tools/fio/graph.h

## Purpose
Declares the public graphing API used by gfio to create, populate, draw, and query bar and line graphs.

## Important APIs, Types, and Functions
The header forward-declares `struct graph` and `struct graph_label`, exposes `graph_label_t`, defines `GRAPH_DEFAULT_FONT`, and declares lifecycle, sizing, position, title, label, data, color, axis callback, extra spacing, tooltip, base-offset, all-zero, and clear/free functions. `graph_axis_unit_change_callback` lets callers adjust axis titles when tick labels are scaled by powers of ten. `INVISIBLE_COLOR` marks a line as scale-affecting but not drawn.

## Control Flow
Typical use is `graph_new`, optional graph and title configuration, `graph_add_label`, repeated `graph_add_data` or `graph_add_xy_data`, drawing via `bar_graph_draw` or `line_graph_draw`, optional tooltip probing, and cleanup. Line graphs can also set a per-label data cap so append operations behave like a rolling window.

## State and Persistence Behavior
The API is purely in-memory and uses opaque structs to keep allocation and indexing details in `graph.c`. Callers retain label handles returned by `graph_add_label`, and those handles are invalid after label/free operations.

## Dependencies and Integration Points
The declarations reference `cairo_t` but do not include Cairo themselves in this file, so includers must have the relevant Cairo type visible. The API integrates with gfio UI code and fio's graph drawing support.

## Risks
Opaque pointer ownership is implicit: `graph_free()` frees internals but implementation does not free the graph object. `graph_set_font()` stores a pointer rather than duplicating it. Tooltip APIs depend on coordinates and tick state established by drawing.

## Test Signals
Compile-time coverage is the main signal. Runtime tests should exercise the API sequence from graph allocation through drawing and cleanup, plus rolling-window and tooltip functions.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/graph.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/hash.h -->
# sources/test-tools/fio/hash.h

## Purpose
Provides small inline hashing utilities copied from Linux-style helpers: multiplicative hashing for integers and pointers plus Bob Jenkins `jhash` for byte buffers.

## Important APIs, Types, and Functions
Defines `GOLDEN_RATIO_32`, `GOLDEN_RATIO_64`, `JHASH_INITVAL`, `__hash_long`, `hash_long`, `__hash_u64`, `hash_ptr`, `rol32`, `__jhash_mix`, `__jhash_final`, and `jhash`. `hash_long()` returns high bits of a multiplicative hash sized by `BITS_PER_LONG`; `hash_ptr()` casts through `uintptr_t`; `jhash()` mixes arbitrary byte keys with a caller-supplied initial value.

## Control Flow
`jhash()` initializes three 32-bit accumulators from length and seed, processes full 12-byte chunks through `__jhash_mix`, then folds the final 0 to 12 bytes through a fallthrough switch and `__jhash_final`. The multiplicative helpers perform constant multiplication and right shifts for hash-table indexing.

## State and Persistence Behavior
No state is stored. Outputs are deterministic for the same input, architecture width, and seed.

## Dependencies and Integration Points
Depends on `arch/arch.h` for `BITS_PER_LONG` and `compiler/compiler.h` for `fio_fallthrough`. Used anywhere fio needs compact hash-table distribution without pulling in a separate library.

## Risks
The 32-bit fallback in `__hash_long()` is intentionally hand-expanded and architecture-sensitive. `jhash()` adds `*k`, `*(k + 4)`, and `*(k + 8)` as single bytes in the full-block loop rather than assembling 32-bit little-endian words, so behavior must be treated as fio's local contract rather than assumed identical to every Jenkins hash variant. These hashes are not cryptographic.

## Test Signals
Good tests pin known hash outputs on 32-bit and 64-bit builds, compare bucket distribution for common keys, and compile with warnings enabled to verify fallthrough annotations.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/helper_thread.c -->
# sources/test-tools/fio/helper_thread.c

## Purpose
Implements fio's background helper thread. The helper performs periodic runtime work such as disk utilization sampling, status output, steadystate checks, ramp-period checks, log sample scheduling, and final log flushing, while receiving explicit actions from the main thread.

## Important APIs, Types, and Functions
Public entry points are `helper_thread_create`, `helper_thread_exit`, `helper_thread_destroy`, `helper_reset`, `helper_do_stat`, and `helper_should_exit`. Internal state is `struct helper_data` with an exit flag, action pipe, `sk_out`, thread id, and startup semaphore. `struct interval_timer` describes recurring callbacks. Key helpers include pipe/socket compatibility wrappers, `submit_action`, `wait_for_action`, `reset_timers`, `eval_timer`, `helper_thread_main`, and Windows `pipe_over_loopback`.

## Control Flow
Creation allocates helper data, sets up disk and steadystate support, creates a nonblocking pipe or loopback socket pair, starts `helper_thread_main`, and waits on a startup semaphore. The helper blocks signals, initializes timer precision, assigns socket output, resets interval timers, then loops until an exit flag, timer callback error, or `A_EXIT`. Each iteration waits for a pipe action or timeout, evaluates periodic timers, handles forced stat output, calculates the next log deadline, and prints thread status for non-backend runs. Exit closes timerfd if present, writes logs, and drops socket output.

## State and Persistence Behavior
Persistent user-visible effects are periodic status output, disk-util sampling state, steadystate results, and final log files. In-memory state is global `helper_data`, `sleep_accuracy_ms`, and optional `timerfd`. `helper_do_stat()` is documented as callable from signal-handler context and routes work through the pipe action.

## Dependencies and Integration Points
Depends on fio core timing, logging, diskutil, status/stat output, steadystate, semaphores, `sk_out`, platform pipe/socket APIs, timerfd when available, and Valgrind DRD annotations. The main runtime creates the helper around job execution and uses reset/stat/exit APIs to coordinate it.

## Risks
`submit_action()` asserts on short writes, which is deliberate but harsh if the action pipe is full or closed. `helper_thread_create()` leaks the allocated helper data on some pipe/thread creation failures. Timer callbacks share a single return path, so any nonzero callback return stops the helper. `helper_data->exit` is volatile but not an atomic synchronization primitive. The Windows pipe emulation has several socket setup failure paths.

## Test Signals
Tests should create and destroy the helper repeatedly, inject `A_RESET` and `A_DO_STAT`, cover timerfd and non-timerfd builds, validate no blocked signals are handled in the helper, and run under sanitizers for failure paths. Integration signals are stable status intervals, disk-util updates, and log flushes at run end.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/helper_thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/helper_thread.h -->
# sources/test-tools/fio/helper_thread.h

## Purpose
Declares the helper-thread lifecycle and action API used by fio runtime code.

## Important APIs, Types, and Functions
Forward-declares `struct fio_sem` and `struct sk_out`. Exposes `helper_thread_create`, `helper_thread_exit`, `helper_thread_destroy`, `helper_reset`, `helper_do_stat`, and `helper_should_exit`.

## Control Flow
Callers create the helper with a startup semaphore and socket output context, use reset/stat functions while jobs run, ask whether exit is requested, then call exit and destroy during shutdown.

## State and Persistence Behavior
The header exposes no state. The implementation owns the single global helper instance and its action pipe.

## Dependencies and Integration Points
Included by fio runtime setup, signal/status paths, and shutdown code that need to coordinate periodic background maintenance.

## Risks
The API is singleton-oriented; creating multiple helpers is not supported. `helper_do_stat()` has signal-handler constraints that callers must preserve.

## Test Signals
Compile-time API coverage plus integration tests that start fio jobs with status intervals and verify clean helper startup/shutdown are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/helper_thread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/helpers.c -->
# sources/test-tools/fio/helpers.c

## Purpose
Provides portability stubs for optional platform syscalls that fio can call even when the host libc or OS lacks support.

## Important APIs, Types, and Functions
Conditionally defines `fallocate`, `posix_fallocate`, `sync_file_range`, `syncfs`, and `posix_fadvise` when the corresponding `CONFIG_*` feature macro is absent.

## Control Flow
Unsupported operations either set `errno = ENOSYS` and return `-1` (`fallocate`, `sync_file_range`, `syncfs`) or become successful no-ops (`posix_fallocate`, `posix_fadvise`) depending on fio's expected fallback behavior.

## State and Persistence Behavior
No state is persisted. The only side effect is setting `errno` for explicit unsupported errors.

## Dependencies and Integration Points
Includes `helpers.h` and `errno.h`. Used by file setup, cache advice, allocation, and sync paths so call sites can compile across platforms without sprinkling feature guards everywhere.

## Risks
No-op `posix_fallocate()` and `posix_fadvise()` can make a build appear to support behavior that the OS does not actually perform. Callers must treat these as compatibility shims rather than guarantees of preallocation or advisory cache behavior.

## Test Signals
Build matrix coverage with feature macros enabled and disabled is most important. Runtime tests should verify unsupported sync/allocation operations surface `ENOSYS` where callers expect fallback behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/helpers.h -->
# sources/test-tools/fio/helpers.h

## Purpose
Declares portability wrappers or fallback definitions for file allocation, sync, and advisory APIs.

## Important APIs, Types, and Functions
Declares `fallocate`, `posix_fallocate`, `sync_file_range`, `syncfs`, and `posix_fadvise` depending on platform feature macros. Includes `sys/types.h` and fio `os/os.h` for `off_t` and `uint64_t` support.

## Control Flow
There is no executable control flow in the header. It ensures callers can reference these functions regardless of platform configuration.

## State and Persistence Behavior
No state is defined.

## Dependencies and Integration Points
Used by helpers implementation and any fio file or I/O path that needs these APIs without direct platform conditionals.

## Risks
Declaring libc-like symbols locally can conflict if feature macros are wrong. The contract depends on configure-time detection being accurate.

## Test Signals
Compile fio on Linux, Windows, and minimal POSIX-like environments with combinations of `CONFIG_SYNC_FILE_RANGE`, `CONFIG_SYNCFS`, and allocation/advice support.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/idletime.c -->
# sources/test-tools/fio/idletime.c

## Purpose
Implements fio's CPU idle profiler. It calibrates a small CPU-bound memory-touch workload on each CPU, optionally runs low-priority per-CPU profiler threads during a job, then reports inferred CPU idleness as normal or JSON output.

## Important APIs, Types, and Functions
Public functions are `fio_idle_prof_parse_opt`, `fio_idle_prof_init`, `fio_idle_prof_start`, `fio_idle_prof_stop`, `show_idle_prof_stats`, and `fio_idle_prof_cleanup`. Global profiler state lives in volatile `ipc` (`struct idle_prof_common`). Worker state is `struct idle_prof_thread`. Internal helpers include `calibrate_unit`, CPU affinity setup/free, `idle_prof_thread_fn`, `calibration_stats`, and `fio_idle_prof_cpu_stat`.

## Control Flow
Option parsing accepts `calibrate`, `system`, or `percpu` only when CPU affinity and idle scheduling support exist. Initialization allocates one thread record and one page-sized buffer per CPU, initializes locks/condition variables, locks per-thread gates, creates detached worker threads, releases the initialization gates, waits for calibration, and computes mean/stddev. Start unlocks the profiling gates. Stop sets `IDLE_PROF_STATUS_PROF_STOP`, waits for worker exit, and computes idleness from loop count, calibrated unit time, and elapsed runtime. Stats are then printed or added to JSON.

## State and Persistence Behavior
No persistent files are written. `ipc` stores selected option, CPU count, calibration stats, buffers, thread records, and status. Threads are detached, so cleanup only frees the arrays after stop/stat collection. Calibration-only mode runs init/start/stop immediately and returns a command-line early-exit signal.

## Dependencies and Integration Points
Depends on fio timing, logging, JSON output, CPU affinity wrappers, scheduler idle support, `page_size`, and thread state constants. It is wired through `parse_cmd_line()` via `--idle-prof` and through normal output generation.

## Risks
The code aborts profiling if any CPU thread fails, which is accurate but fragile on constrained systems. `calibration_stats()` divides by `nr_cpus - 1`; single-CPU systems risk invalid standard-deviation math. Detached worker threads plus mutex-gated lifecycle require careful ordering. `ipc.status` is volatile shared state, not a full atomic protocol. CPU affinity or idle scheduling failures disable profiling on otherwise valid runs.

## Test Signals
Tests should cover unsupported-platform option errors, calibration-only output, system/percpu JSON fields, single-CPU behavior, thread creation failure paths, and start/stop cleanup under sanitizers. Integration signals are stable `CPU idleness` output and no lingering profiler threads after fio exits.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/idletime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/idletime.h -->
# sources/test-tools/fio/idletime.h

## Purpose
Defines idle-profiler options, status codes, shared data structures, and public API declarations.

## Important APIs, Types, and Functions
Constants include `CALIBRATE_RUNS`, `CALIBRATE_SCALE`, and `MAX_CPU_STR_LEN`. Option values distinguish none, calibration-only, system, and per-CPU profiling. Status values distinguish OK, calibration stop, profiling stop, and abort. `struct idle_prof_thread` stores thread id, CPU id, state, timestamps, calibration time, loop count, idleness, data buffer, synchronization primitives, and CPU mask. `struct idle_prof_common` aggregates all threads and global stats. Declared functions parse options, initialize/start/stop/cleanup profiling, and show stats.

## Control Flow
Runtime code sets an option through `fio_idle_prof_parse_opt()`, calls init/start/stop around job execution, emits stats after completion, and finally cleans up allocations.

## State and Persistence Behavior
The header describes in-memory profiler state only. No persistence contract is exposed.

## Dependencies and Integration Points
Includes fio `os/os.h`, pthread-visible types through platform headers, and JSON/buffer output forward usage in function declarations. Used by initialization and output paths.

## Risks
The structs expose implementation details, so changes affect every includer. Fields such as `state` rely on thread-state constants defined elsewhere.

## Test Signals
Compile-time coverage across CPU-affinity and non-affinity platforms plus runtime idle-prof option tests are the useful signals.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/idletime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/init.c -->
# sources/test-tools/fio/init.c

## Purpose
Owns fio process and job initialization: global CLI options, job-file parsing, default option setup, thread-data allocation, shared-memory segment management, I/O engine loading, option fixups, random seed setup, log initialization, client/server command handling, and top-level option parsing.

## Important APIs, Types, and Functions
Externally visible functions include `free_threads_shm`, `init_rand_offset_seed`, `td_fill_rand_seeds`, `ioengine_load`, `parse_dryrun`, `add_job_opts`, `parse_jobs_ini`, `parse_cmd_line`, `fio_init_options`, `parse_options`, `options_default_fill`, and `get_global_options`. Major internal functions include `free_shm`, `add_thread_segment`, `expand_thread_area`, `get_new_job`, `put_job`, `fixup_options`, `setup_random_seeds`, `init_flags`, `make_filename`, `add_job`, `__parse_jobs_ini`, debug/usage helpers, and output-format parsing.

## Control Flow
`parse_options()` initializes global defaults, parses command-line switches, dispatches job files or client/server mode, frees temporary default resources, and verifies that jobs exist unless the invocation was help, dry-run, profile, backend, or client-only. CLI job options create or update a `thread_data`; job files create sections with `global` inheritance and optional includes. `add_job()` turns parsed options into runnable jobs: initializes flags, loads the engine, creates implicit files, seeds random generators, normalizes options, initializes flow/rate/ramp/steadystate/log state, prints job summaries, handles blktrace merging, and recursively expands `numjobs`.

## State and Persistence Behavior
Global process state includes output files, CLI mode flags, ETA/status settings, trigger paths, debug masks, backend/client status, job-section filters, default thread options, shared thread segments, and job counters. Thread data may live in SysV shared memory unless configured otherwise. `atexit(free_shm)` tears down engines, files, shared memory, triggers, options, locks, and global cleanup. Runtime persistence includes configured output files and per-job logs initialized by `setup_log()`.

## Dependencies and Integration Points
This file integrates most of fio: parser/options, `smalloc`, file hash, verify, profiles, server/client, idle profiling, file locks, steadystate, blktrace, I/O engines, logs, flow, random distributions, dedupe, zoned block device options, and OS helpers. `ioengine_load()` bridges parsed options to `load_ioengine()` and engine-specific option storage.

## Risks
`fixup_options()` is broad and order-sensitive; changes can silently alter legacy job semantics. Shared-memory segment allocation and cleanup must match process/thread execution modes. Recursive `numjobs` cloning duplicates files and engine option memory, so ownership bugs are possible. Command-line parsing has many early-exit paths that call `exit()` directly. Include-file parsing uses mutable buffers and relative path logic that can be fragile. Global variables make repeated parser invocations sensitive to stale state.

## Test Signals
Strong signals come from fio parser tests, command-line help/enghelp/cmdhelp tests, job-file include tests, client/server parsing tests, option compatibility matrices, random seed reproducibility tests, `numjobs` cloning tests, log naming tests, and sanitizer runs over parse-only and failing-parse cases.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/io_ddir.h -->
# sources/test-tools/fio/io_ddir.h

## Purpose
Defines fio's I/O direction enums, job direction bitmasks, and helper macros used throughout scheduling, accounting, logging, and option validation.

## Important APIs, Types, and Functions
`enum fio_ddir` defines read, write, trim, sync variants, wait, invalid, timeout, and direction counts. `for_each_rw_ddir` iterates read/write/trim. `io_ddir_name`, `ddir_sync`, `ddir_rw`, `ddir_str`, and `ddir_rw_sum` provide name and classification helpers. `enum td_ddir` defines job direction combinations such as `TD_DDIR_RANDRW` and `TD_DDIR_RANDTRIMWRITE`. Macros such as `td_read`, `td_write`, `td_trim`, `td_rw`, `td_random`, `td_trimwrite`, and `td_randtrimwrite` inspect `thread_data` options.

## Control Flow
There is no standalone execution. The helpers are inline decision points used by I/O generation, engine dispatch, initialization fixups, and statistics.

## State and Persistence Behavior
No state is stored. The macros read `td->o.td_ddir` and file random-map state.

## Dependencies and Integration Points
Used by `io_u.c`, `init.c`, `ioengines.c`, stats, verify, trim, and file setup paths. It relies on `fio_file_axmap()` being visible where `file_randommap()` is used.

## Risks
Array order must stay synchronized with `DDIR_*` values. `io_ddir_name()`'s static name list appears shorter/misaligned for later sync values, so any enum additions need careful review. `ddir_str()` indexes by bitmask value and only supports specific combinations.

## Test Signals
Compile-time and unit coverage should assert expected strings/classification for each direction and common `td_ddir` combinations. Full fio job tests indirectly validate direction macros.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/io_ddir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/io_u.c -->
# sources/test-tools/fio/io_u.c

## Purpose
Implements fio's I/O unit lifecycle: selecting files, generating offsets and block sizes, enforcing rate and latency targets, preparing `io_u` objects, handling verify/trim backlogs, completing sync and async I/O, updating accounting, filling write buffers, and issuing sync/trim helpers.

## Important APIs, Types, and Functions
Public functions include `__get_io_u`, `get_io_u`, `put_io_u`, `clear_io_u`, `requeue_io_u`, `io_u_quiesce`, `io_u_mark_submit`, `io_u_mark_complete`, `io_u_mark_depth`, `lat_target_init`, `lat_target_reset`, `lat_target_check`, `queue_full`, `io_u_log_error`, `io_u_sync_complete`, `io_u_queued_complete`, `io_u_queued`, `fill_io_buffer`, `io_u_fill_buffer`, `do_io_u_sync`, and `do_io_u_trim`. Internal clusters cover random offset distributions, sequential offsets, zoned modes, mixed read/write direction choice, file service selection, latency target ramping, completion accounting, dedupe/compression buffer generation, and short-I/O requeue.

## Control Flow
`get_io_u()` obtains a free or requeued unit, checks verify and trim backlogs, reads iolog input or selects a file, fills direction/offset/length, updates file positions, fills or scrambles write buffers, sets transfer pointers and priority, then calls `td_io_prep()`. Submission happens through `ioengines.c`. Completion returns through `io_u_sync_complete()` or `io_u_queued_complete()`, which call engine event methods, `io_completed()`, accounting, short-I/O requeue, verify bookkeeping, error handling, bytes-done updates, and `put_io_u()`.

## State and Persistence Behavior
Mutates `thread_data` counters, latency histograms, rate timing, queue-depth state, file positions, random maps, zoned state, verification lists, failed write numberio arrays, bytes done, and per-file write ranges used by sync-file-range. It writes no standalone files, but it drives logs and stats through accounting helpers and determines persistent device/file I/O patterns.

## Dependencies and Integration Points
Tightly integrates with `fio.h`, verify, trim, random generators, axmap, min/max helpers, zoned block devices, data placement, sprandom, ioengine wrappers, logging, stats, file lifetime, iolog replay, and OS trim/sync APIs.

## Risks
This is a high-risk concurrency and correctness file. Offset generation depends on many interacting options: random maps, nonuniform distributions, zone modes, trimwrite/randtrimwrite, time-based loops, and file-service policy. `lat_target_check()` divides by the number of I/Os in a window and assumes progress. Short-I/O requeue mutates buffer pointers and offsets. Parent/child thread accounting and async verify require careful locking. Error paths must avoid double file puts while preserving verification state. Dedupe/compression buffer state is intentionally stateful and can break reproducibility if seeds are changed incorrectly.

## Test Signals
Important signals include fio's random/sequential offset tests, verify and trim backlog jobs, async and sync engine jobs, zoned block device tests, rate limiting tests, latency target tests, short-I/O injection, dedupe/compression buffer reproducibility checks, iolog replay tests, and sanitizer runs under offload/async verify.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/io_u.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/io_u.h -->
# sources/test-tools/fio/io_u.h

## Purpose
Defines `struct io_u`, its flags, and the public API for fio I/O unit allocation, preparation, accounting, completion, and buffer filling.

## Important APIs, Types, and Functions
Flags include free/in-flight/current-depth markers, file-put suppression, trim/barrier/verify/pattern/device-error/zeroed/error state, and ZBD verification flags. `struct io_u` stores timing, file pointer, direction and accounting direction, write sequence number, priority, trim count, buffer and transfer state, random seed, verify offset, residual/error fields, engine private data, verify/workqueue union, ZBD callbacks, completion callback, data placement fields, and engine-specific unions for libaio, POSIX AIO, SGIO, Solaris AIO, RDMA, and mmap. Declared functions cover get/put/requeue, completion, queue state, error logging, depth maps, buffer filling, sync, trim, and queue fullness.

## Control Flow
The header describes objects flowing from freelist to preparation to engine queue to completion and back to freelist, with optional requeue for partial transfers or verify/trim backlog reuse.

## State and Persistence Behavior
`io_u` is transient runtime state. Its fields drive persistent I/O effects on target files/devices and the stats/log records emitted by fio.

## Dependencies and Integration Points
Includes compiler, OS, direction, debug, file, workqueue, and optional engine headers. It is central to ioengine implementations and fio core scheduling.

## Risks
The struct is shared across many engines and feature macros, so layout and field semantics are compatibility-sensitive. Flag handling must be consistent between core and engines. `acct_ddir()` treats `-1` as unset in an enum field, matching initialization in `io_u.c`.

## Test Signals
Engine build coverage across optional backends, async/sync jobs, verify paths, trim paths, and debug builds with `dprint_io_u()` enabled provide coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/io_u.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/io_u_queue.c -->
# sources/test-tools/fio/io_u_queue.c

## Purpose
Implements allocation and cleanup for fio's simple `io_u` pointer stack queue and circular requeue ring.

## Important APIs, Types, and Functions
Defines `io_u_qinit`, `io_u_qexit`, `io_u_rinit`, and `io_u_rexit`. Inline push/pop operations live in `io_u_queue.h`.

## Control Flow
`io_u_qinit()` allocates a pointer array with `smalloc()` for shared allocations or `calloc()` for local allocations, then initializes count and max. `io_u_rinit()` rounds `nr + 1` up to a power of two, allocates the ring array, and initializes head/tail. Exit functions free the corresponding allocation.

## State and Persistence Behavior
State is in-memory queue arrays plus counters. There is no persistence.

## Dependencies and Integration Points
Depends on `io_u_queue.h` and `smalloc`. Used by thread-data initialization for freelists and requeue rings consumed by `io_u.c`.

## Risks
Ring capacity uses one empty slot to distinguish full from empty and requires power-of-two masking. The power-of-two rounding only shifts through 16 bits, so very large queue sizes would need review on 64-bit values. Exit functions do not null pointers or reset counts.

## Test Signals
Unit tests should cover shared and non-shared allocation, exact power-of-two and non-power-of-two ring sizes, push/pop ordering, full assertions in debug builds, and cleanup under sanitizers.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/io_u_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/io_u_queue.h -->
# sources/test-tools/fio/io_u_queue.h

## Purpose
Defines lightweight queue containers used to manage free and requeued `io_u` pointers.

## Important APIs, Types, and Functions
`struct io_u_queue` is a LIFO stack with `io_us`, `nr`, and `max`. Inline functions `io_u_qpop`, `io_u_qpush`, `io_u_qempty`, and `io_u_qiter` operate on it. `struct io_u_ring` is a circular FIFO with `head`, `tail`, `max`, and `ring`, operated by `io_u_rpush`, `io_u_rpop`, and `io_u_rempty`. Allocation functions are declared for both queue types.

## Control Flow
Free `io_u` objects are pushed/popped from the stack queue. Requeued partial or deferred units are pushed to and popped from the ring in FIFO order.

## State and Persistence Behavior
All state is in memory. The inline operations assert on overflow but otherwise do not allocate or persist anything.

## Dependencies and Integration Points
Includes `assert.h`, `stddef.h`, and fio `lib/types.h`. Used directly by `io_u.c` and thread-data setup.

## Risks
The queue is not internally synchronized; callers must use thread-data locks when needed. Overflow handling is an assertion, so release builds may not catch misuse cleanly depending on assert configuration.

## Test Signals
Focused queue tests for empty/full behavior, ordering, iterator behavior, and async-lock callers are useful. fio runtime depth tests indirectly exercise this code.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/io_u_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/ioengines.c -->
# sources/test-tools/fio/ioengines.c

## Purpose
Implements fio's I/O engine registry, dynamic engine loading, engine lifecycle cleanup, and wrapper functions that mediate between core `io_u` scheduling and engine callback implementations.

## Important APIs, Types, and Functions
Public functions include `register_ioengine`, `unregister_ioengine`, `load_ioengine`, `free_ioengine`, `close_ioengine`, `td_io_prep`, `td_io_getevents`, `td_io_queue`, `td_io_init`, `td_io_commit`, `td_io_open_file`, `td_io_close_file`, `td_io_unlink_file`, `td_io_get_file_size`, and `fio_show_ioengine_help`. Internal helpers include `check_engine_ops`, `find_ioengine`, dynamic `dlopen_*` helpers, `async_ioengine_sync_trim`, and `async_ioengine_sync_syncfs`.

## Control Flow
Static engines register on the global `engine_list`; dynamic engines are loaded with `dlopen()` and resolved by engine symbol or `get_ioengine()`. `load_ioengine()` resolves aliases such as `aio`/`linuxaio` to `libaio`, validates operation table version and required callbacks, and returns ops to initialization. Queueing marks an `io_u` in flight, logs it, updates issue counters, calls engine `queue`, handles ZBD callbacks, backs out counters on busy, optionally commits async batches, records issue time, and updates depth/completion maps. Completion wrappers call engine `commit`, `getevents`, and `event`. File wrappers handle open/close accounting, invalidation, fadvise, write hints, direct I/O setup, unlink, and size queries.

## State and Persistence Behavior
Global engine state is the `engine_list` and dynamic library handles stored in `ioengine_ops`. Per-thread state includes `td->io_ops`, engine options `td->eo`, open file counts, in-flight/queued counts, and file flags. Persistent effects are engine-driven I/O and file open/unlink operations.

## Dependencies and Integration Points
Depends on `fio.h`, diskutil, ZBD support, dynamic linker APIs, file locking, file logging, fadvise/write hints, and every engine's `struct ioengine_ops` contract. `init.c` loads engines and engine options, while `io_u.c` calls the wrapper APIs.

## Risks
Engine ABI compatibility hinges on `FIO_IOOPS_VERSION`. Dynamic loading has several symbol naming paths and must close handles correctly. `td_io_queue()` updates counters before calling the engine and must exactly reverse them on `FIO_Q_BUSY`. Offload overlap unlock ordering is subtle. File open error paths must balance disk-util counters, file refs, and engine close callbacks. `td_io_open_file()` sets `FIO_RAWIO` by mutating engine flags for direct I/O, which can matter if ops are shared.

## Test Signals
Useful signals include static and dynamic engine loading tests, `--enghelp`, sync and async engine jobs, busy queue injection, direct-I/O alignment failures, fadvise/write-hint jobs, openfiles limit tests, ZBD jobs, and sanitizer runs around engine load/unload.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/ioengines.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/ioengines.h -->
# sources/test-tools/fio/ioengines.h

## Purpose
Defines fio's I/O engine ABI: callback table, queue status values, engine flags, dynamic-engine entry type, and public wrapper declarations.

## Important APIs, Types, and Functions
`FIO_IOOPS_VERSION` is the ABI version. `enum fio_q_status` defines completed, queued, and busy queue outcomes. `struct ioengine_ops` includes lifecycle callbacks, queue/commit/event callbacks, file operations, memory hooks, `io_u` hooks, ZBD and FDP callbacks, engine-specific options, and dynamic-library handle storage. Flag enums define capabilities and constraints such as sync, raw, diskless, noextend, pipe, barrier, no stats, no offload, atomic writes, multi-range trim, and syncfs support. Public wrappers mirror the implementation in `ioengines.c`.

## Control Flow
Engines register or are dynamically loaded, then fio calls setup/init/post-init, per-I/O prep/queue/commit/getevents/event, file operations, and cleanup/free according to job lifecycle.

## State and Persistence Behavior
The header defines callback shape and capability flags only. Engine implementations own their private state through `td->io_ops_data`, `td->eo`, and `io_u->engine_data`.

## Dependencies and Integration Points
Includes compiler helpers, fio lists, `io_u.h`, ZBD types, and data placement types. Every ioengine implementation and core engine wrapper depends on this header.

## Risks
Any callback or flag changes require version coordination. Missing callbacks are only valid for sync engines or optional capabilities. Shared `ioengine_ops` structures can be mutated by core code and dynamic loading, so engines must respect fio's lifecycle.

## Test Signals
Build all configured engines, load dynamic engines, run `--enghelp`, and execute smoke jobs for sync, async, diskless, trim, syncfs, ZBD, and FDP-capable engines.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/ioengines.h -->
