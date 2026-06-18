# subset-b-009226 research

Grouped research report for selected fio core setup, timing, semaphore, flow-control, and gfio GUI/client sources. Each section preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/filesetup.c -->
# sources/test-tools/fio/filesetup.c

Purpose: implements fio's generic file lifecycle for jobs: file discovery and allocation, size probing, layout/prepopulation, cache invalidation, open/close reference handling, per-file locking, random-offset map initialization, directory recursion, and cleanup. It is the bridge between parsed `thread_options`, `thread_data`, `fio_file`, and ioengine hooks.

Important APIs/types/functions: exported entry points include `setup_files`, `pre_read_files`, `generic_open_file`, `generic_close_file`, `generic_get_file_size`, `generic_prepopulate_file`, `file_invalidate_cache`, `add_file`, `add_file_exclusive`, `add_dir_files`, `dup_files`, `get_file`, `put_file`, `lock_file`, `unlock_file`, `close_files`, `close_and_free_files`, `fio_file_reset`, `fio_files_done`, `filesetup_mem_free`, `fio_set_directio`, and syncfs helpers `fio_open_fs`/`fio_close_fs`. Internal helpers cover fallocate modes, file extension, file/block/char sizing, mount discovery, offset calculation, work-directory creation, duplicate-name tracking, and random-map setup.

Control flow: `setup_files` bumps the job runstate to `TD_SETTING_UP`, creates missing parent directories, validates `end_syncfs` engine support, invokes ioengine `setup` or generic size probing, initializes zoned block-device metadata, computes per-file offsets and `io_size`, extends or prepopulates files when needed, invalidates cache after layout writes, initializes SPRandom/dedupe preparation, sets total I/O size, and restores runstate. `generic_open_file` derives POSIX flags from workload direction and options, handles stdin/stdout, retries without `FIO_O_NOATIME` on permission failure, closes shadow fds on `EMFILE`, shares locks through the file hash, and stores duplicate write descriptors as shadow fds. `put_file` decrements file references, unlocks, optionally fsyncs on close, invokes engine close, updates open counters, and clears open/closing flags.

State and persistence behavior: durable effects include creating directories, creating/extending/unlinking regular files, fallocating/truncating file space, prewriting file contents, flushing/fsyncing, and invalidating caches. In-memory state spans `thread_data.files`, `thread_data.file_locks`, `fio_file` offsets/sizes/type/open/reference flags, file hash entries, mount lists, `filename_list` duplicate-name tracking, axmaps/LFSR/zipf/pareto/gauss state, and optional ZBD/FDP/SPRandom metadata. Cleanup must release both normal heap and fio shared-memory allocations depending on `fio_file_smalloc`.

Dependencies/integration: depends on `fio.h`, `filehash`, `ioengine_ops`, `os/os.h`, `options`, `smalloc`, `axmap`, `rwlock`, `zbd`, `sprandom`, POSIX `open/stat/lstat/dirent/ftruncate/fsync/posix_fadvise`, block/char-device helpers, and platform fallocate/direct-I/O macros. It integrates deeply with option parsing (`allow_create`, `fill_device`, `file_size_*`, `offset*`, `random_generator`, `file_lock_mode`, `unlink`, `create_on_open`, `create_only`, `end_syncfs`) and job runstate/status reporting.

Risks and test signals: highest-risk paths are size/offset arithmetic around `-1ULL`, percentages, append mode, random file-size ranges, and min-block alignment; descriptor sharing and shadow-fd cleanup; duplicate file allocation across `numjobs`; block-device cache invalidation permissions; partial layout writes on ENOSPC/EDQUOT; and platform-specific direct-I/O/fallocate behavior. Test signals should cover missing files with and without `allow_create`, existing small files requiring extension, `fill_device`, directories with nested files, stdin/stdout, block/char devices, ZBD jobs, random-map allocation failure with and without `softrandommap`, file locks under shared filenames, `unlink=1`, `create_only`, and `end_syncfs`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/filesetup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/fio.c -->
# sources/test-tools/fio/fio.c

Purpose: command-line fio entry point. It initializes global fio state, parses arguments, starts either remote-client orchestration or local backend execution, and performs final key/global cleanup.

Important APIs/types/functions: the only function is `main(int argc, char *argv[], char *envp[])`. It calls `initialize_fio`, `fio_server_create_sk_key`, `parse_options`, `fio_time_init`, `set_genesis_time`, `fio_start_all_clients`, `fio_handle_clients`, `fio_backend`, `fio_server_destroy_sk_key`, and `deinitialize_fio`.

Control flow: startup returns immediately on failed `initialize_fio`. It creates the server shared-key material before option parsing, then parses CLI/job options. Standard output is switched to line buffering so multi-threaded status output is less interleaved. After time initialization, `nr_clients` selects remote-client mode: set genesis time, start all clients, and handle client callbacks through `fio_client_ops`. With no clients, it runs the normal backend with no socket-output object. Both success and failure paths destroy the server key before deinitializing fio.

State and persistence behavior: persistent external effects are whatever option parsing and backend/client execution perform; this file itself only mutates process-global initialization state, stdout buffering, timing baseline, and server-key lifecycle. Return value starts as failure and is overwritten by client/backend execution result.

Dependencies/integration: includes `fio.h`, so it relies on the full fio core. It is the top-level integration point among initialization, option parsing, time setup, network client mode, and local job execution.

Risks and test signals: cleanup labels must preserve `fio_server_destroy_sk_key` when key creation succeeded and `deinitialize_fio` for all initialized exits. Tests should cover option-parse failure, key-create failure, local backend success/failure, client mode with failed `fio_start_all_clients`, and line-buffered output behavior under multiple jobs.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/fio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/fio.h -->
# sources/test-tools/fio/fio.h

Purpose: central public/internal fio header that aggregates core dependencies and defines the main job execution contract. Most fio modules consume `struct thread_data`, option/runstate/output enums, global runtime declarations, thread/file iteration macros, error macros, and small policy helpers from this header.

Important APIs/types/functions: key types are `struct thread_data`, `struct thread_segment`, `struct trim_range`, and `struct zone_split_index`. Important enums define thread flags, random seed offsets, I/O mode/rate process types, fadvise modes, ETA policy, runstates, termination scope, output formats, random distributions/generators, and CPU allocation policy. Important macros include `td_verror`, `td_vmsg`, `td_clear_error`, `for_each_td`, `for_each_file`, `REAL_MAX_JOBS`, `JOBS_PER_SEG`, `FIO_GETOPT_JOB`, and `FIO_NR_OPTIONS`. Inline helpers include `tnumber_to_td`, `is_running_backend`, `fio_ro_check`, `multi_range_trim`, `should_fsync`, `td_set_ioengine_flags`, `td_ioengine_flagged`, `fio_offset_overlap_risk`, rate/block-size helpers, async/offload helpers, thread-safe flag setters, and `fio_memalign`/`fio_memfree`.

Control flow: this header does not run a control flow by itself, but it shapes almost every fio flow. Runstate constants define the lifecycle from not-created through setup, running, verifying, finishing, exited, and reaped. Function declarations expose initialization, parsing, backend execution, runstate transitions, termination, memory management, stats reset, I/O queue events, latency target handling, inflight logging, and trigger handling.

State and persistence behavior: `struct thread_data` is the durable in-memory state for a fio job/thread/process. It stores parsed options, ioengine hooks/private data, file arrays and locks, stats/log handles, random generator states, verification state, rate/latency accounting, timing baselines, I/O queues, workqueues, flow-control state, memory pins, steady-state state, error message state, and optional CUDA fields. Global externs expose process-level state such as `segments`, `thread_number`, output format, time source, backend/client mode, trigger configuration, page geometry, and read-only mode.

Dependencies/integration: pulls in fio's broad core: compiler/arch/os shims, options, file/ioengine/iolog/stat/server/client modules, timing, random/rbtree/memalign helpers, workqueue, steady-state, dedupe, CUDA/NUMA platform headers, and OS getopt. Because it includes many module headers, changes here have repository-wide compile impact.

Risks and test signals: `thread_data` layout and flags are high blast-radius ABI-like internals, especially when shared memory, client protocol packing, or ioengine modules assume fields. Bit-shifted ioengine flags must not collide with thread flags. Iteration macros depend on `thread_number`, segmented storage, and `files_index`/`nr_files` consistency. Test signals are full builds across enabled platforms/features, server/client runs, verify/rate/latency tests, ioengine modules, and static analysis around packed/shared structures and atomic flag paths.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/fio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/fio_sem.c -->
# sources/test-tools/fio/fio_sem.c

Purpose: implements fio's small counting semaphore abstraction on top of a process-shared pthread mutex and condition variable. It supports mmap-backed semaphores, inline initialization for embedded/shared objects, blocking waits, timed waits, trylock, wakeups, and removal.

Important APIs/types/functions: exports `__fio_sem_init`, `fio_sem_init`, `__fio_sem_remove`, `fio_sem_remove`, `fio_sem_down_timeout`, `fio_sem_down_trylock`, `fio_sem_down`, and `fio_sem_up`. Internal `sem_timed_out` compensates for platforms whose timed condition wait may return timeout early.

Control flow: `fio_sem_init` allocates `struct fio_sem` with anonymous shared mmap and calls `__fio_sem_init`; failure removes/unmaps. `fio_sem_down` locks the mutex, waits while `value` is zero, tracks waiters around each `pthread_cond_wait`, decrements value, and unlocks. The timeout variant computes an absolute timeout using monotonic clock when supported, loops on `pthread_cond_timedwait`, double-checks elapsed wall time after `ETIMEDOUT`, and decrements only on success. `fio_sem_up` increments value and signals one waiter if the semaphore was previously unavailable and waiters exist.

State and persistence behavior: semaphore state is in `value`, `waiters`, `magic`, `pthread_mutex_t`, and `pthread_cond_t`. `__fio_sem_remove` destroys pthread objects and clears memory outside Valgrind so use-after-remove tends to assert on magic rather than hang. `fio_sem_remove` additionally unmaps mmap storage.

Dependencies/integration: depends on `fio_sem.h`, `pshared.h` for `mutex_cond_init_pshared`, `os/os.h` for mmap flags, `fio_time.h`/`gettime.h` for timeout math, pthreads, mmap, and Valgrind detection. Used by flow control, gettimeofday thread startup, job synchronization, and file locks.

Risks and test signals: `fio_sem_down_trylock` returns `false` on successful acquisition and `true` when unavailable, which is easy to misuse. Timed waits rely on correct condition-variable clock attributes from `pshared`. Test signals should cover interprocess use, embedded `__fio_sem_init`/`__fio_sem_remove`, timeout accuracy, trylock semantics, wake-one behavior, removal while unused, and Valgrind/non-Valgrind behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/fio_sem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/fio_sem.h -->
# sources/test-tools/fio/fio_sem.h

Purpose: declares fio's process-capable counting semaphore structure and API.

Important APIs/types/functions: defines `FIO_SEM_MAGIC`, `struct fio_sem` with `pthread_mutex_t lock`, `pthread_cond_t cond`, `int value`, `int waiters`, and `uint32_t magic`; lock-state constants `FIO_SEM_LOCKED` and `FIO_SEM_UNLOCKED`; and prototypes for normal mmap semaphores, shared-memory semaphores, blocking/timeout/trylock down operations, and up/removal operations.

Control flow: consumers use `fio_sem_init` or `fio_shared_sem_init`, then pair `fio_sem_down`/`fio_sem_up` or use timeout/trylock variants. `__fio_sem_init` and `__fio_sem_remove` are exposed for callers embedding a semaphore in another allocation.

State and persistence behavior: the header fixes the in-memory layout used by both mmap-backed and fio shared-memory-backed semaphores. There is no file persistence; state must be valid across pthreads and, when process-shared attributes are available, forked workers.

Dependencies/integration: includes pthreads and fio integer types. It is consumed by synchronization-heavy fio modules including file locking, flow control, gettime offload startup, and other job coordination code.

Risks and test signals: any layout or magic-value change affects users that allocate semaphores in shared memory. Tests should include compilation on platforms with and without process-shared condattr support, embedded semaphore lifecycle, and misuse detection via magic assertions.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/fio_sem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/fio_shared_sem.c -->
# sources/test-tools/fio/fio_shared_sem.c

Purpose: provides shared-memory allocation wrappers for `fio_sem`, separated from `fio_sem.c` to avoid a circular dependency between semaphore code and fio's shared allocator.

Important APIs/types/functions: exports `fio_shared_sem_init(int value)` and `fio_shared_sem_remove(struct fio_sem *sem)`.

Control flow: initialization allocates semaphore storage with `smalloc`, calls `__fio_sem_init`, and returns the semaphore on success. On initialization failure it calls `fio_shared_sem_remove`, which destroys pthread state with `__fio_sem_remove` and returns storage with `sfree`.

State and persistence behavior: semaphore state is held in fio shared memory rather than anonymous mmap. This allows a parent process to free semaphores allocated by child processes as part of fio's shared memory lifetime. There is no durable persistence beyond process/shared-memory lifetime.

Dependencies/integration: depends on `fio_sem.h` for the common semaphore implementation and `smalloc.h` for fio shared allocations. It is the right constructor for locks stored in structures shared across fio worker processes.

Risks and test signals: correct behavior depends on `smalloc` lifetime and process-shared pthread initialization. Test signals should cover child-created locks, parent cleanup, failed allocation, failed `__fio_sem_init`, and mixed use with ordinary `fio_sem_remove` avoided.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/fio_shared_sem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/fio_time.h -->
# sources/test-tools/fio/fio_time.h

Purpose: declares fio's wall-clock, monotonic-clock, ramp-period, sleep/spin, and job epoch timing helpers.

Important APIs/types/functions: declares `ramp_period_enabled`, `RAMP_PERIOD_CHECK_MSEC`, `ntime_since`, `utime_since`, `mtime_since`, `rel_time_since`, `time_since_now`, genesis-time helpers, `cycles_spin`, `usec_spin`, `usec_sleep`, `fill_start_time`, `fio_time_init`, ramp-period helpers, `timespec_add_msec`, and `set_epoch_time`.

Control flow: consumers call initialization and epoch helpers during fio startup/job start, then use elapsed-time helpers throughout rate control, ETA, latency accounting, ramp transitions, and timeouts. Ramp helpers indicate whether stats should still be suppressed or reset.

State and persistence behavior: the header exposes timing API over process-global genesis/ramp state and per-job `thread_data` timing fields. It does not define storage itself except the external ramp-period flag declaration.

Dependencies/integration: includes standard time headers and fio types. It is paired with `gettime.h`/`gettime.c` and used by backend, rate, stats, and synchronization code.

Risks and test signals: mixed nanosecond/microsecond/millisecond units are easy to confuse, and signed versus clamped elapsed functions have different semantics. Test signals should cover negative/warped time, ramp completion, alternate clocks, sleep precision, and arithmetic overflow near large intervals.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/fio_time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/flist.h -->
# sources/test-tools/fio/flist.h

Purpose: fio's Linux-kernel-style intrusive doubly linked list helper. It provides compact list-head manipulation used by many fio structures without separate list node allocations.

Important APIs/types/functions: defines `container_of`, `struct flist_head`, `FLIST_HEAD_INIT`, `FLIST_HEAD`, `INIT_FLIST_HEAD`, add/delete/splice helpers, `flist_empty`, entry accessors, iteration macros `flist_for_each` and `flist_for_each_safe`, and external `flist_sort`.

Control flow: callers embed `struct flist_head` in their own object, initialize a list head or node, add nodes at head/tail, remove or remove-and-reinitialize nodes, splice lists, and iterate with either ordinary or safe traversal depending on whether deletion can occur during iteration.

State and persistence behavior: list state is purely pointer links in caller-owned memory. Deleting with `flist_del` poisons the entry's next/prev to `NULL`; `flist_del_init` makes it an empty singleton. There is no synchronization or persistence; locking is the caller's responsibility.

Dependencies/integration: depends only on stdlib/stddef. It is used by file lists, flow lists, GUI option lists, debug timing hash buckets, and many other fio modules.

Risks and test signals: intrusive lists fail hard when entries are not initialized, are double-deleted, or are removed during unsafe iteration. `container_of` relies on compiler `__typeof__`. Test signals should cover add/tail ordering, safe deletion while iterating, splice-and-init semantics, empty-list behavior, and sanitizer runs for double delete or uninitialized nodes.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/flist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/flow.c -->
# sources/test-tools/fio/flow.c

Purpose: implements fio's `flow` option support, which throttles jobs sharing a `flow_id` so their issued I/O proportions track configured flow weights.

Important APIs/types/functions: internal `struct fio_flow` stores refs, id, intrusive list node, shared `flow_counter`, and `total_weight`. Exported functions are `flow_threshold_exceeded`, `flow_init_job`, `flow_exit_job`, `flow_init`, and `flow_exit`; internal helpers are `flow_get` and `flow_put`.

Control flow: `flow_init` allocates a shared flow list and a semaphore lock. `flow_init_job` obtains or creates a `fio_flow` for the job's `flow_id`, resets the job-local counter, and adds its weight to the group's total weight. During I/O selection, `flow_threshold_exceeded` compares the job's counter ratio against its weight ratio; if the job is ahead, it optionally quiesces and sleeps or quiesces for ZBD mode, then asks the caller to stall. Otherwise it atomically increments the shared and job-local counters. `flow_exit_job` subtracts the job's contribution, drops refs, and frees the flow when last user leaves.

State and persistence behavior: state is in fio shared allocations and atomic counters for the process lifetime. `flow_counter` starts at 1 to avoid division by zero and is expected to return to 1 when the last reference exits. There is no durable persistence.

Dependencies/integration: depends on `fio.h`, `fio_sem`, `smalloc`, `flist`, atomic helpers, `io_u_quiesce`, job options `flow`, `flow_id`, `flow_sleep`, and ZBD mode. It is called from job setup/teardown and I/O issue loops.

Risks and test signals: ratio math divides by atomically loaded counters and can be skewed by concurrent updates, but it is intended as proportional throttling rather than exact scheduling. Risks include missing `flow_init`, leaked refs, counter underflow in `flow_put`, and excessive stalls when flow weights or sleep settings are wrong. Tests should run mixed jobs with different weights, same/different `flow_id`, ZBD and non-ZBD modes, and teardown while counters are nonzero.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/flow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/flow.h -->
# sources/test-tools/fio/flow.h

Purpose: public declaration for fio flow-control support.

Important APIs/types/functions: defines `FLOW_MAX_WEIGHT` as 1000 and declares `flow_threshold_exceeded`, `flow_init_job`, `flow_exit_job`, `flow_init`, and `flow_exit`.

Control flow: fio core initializes the subsystem once, initializes per-job flow state for jobs with `flow` weight, checks `flow_threshold_exceeded` during issue decisions, and tears down job/subsystem state at exit.

State and persistence behavior: the header exposes no state, but callers should treat flow state as process-lifetime shared scheduler state managed by `flow.c`.

Dependencies/integration: it requires `struct thread_data` from including context, normally through `fio.h`. It is included by `fio.h`, making flow checks available broadly.

Risks and test signals: changing `FLOW_MAX_WEIGHT` or function semantics affects option validation and runtime throttling. Test signals are compile coverage plus proportional throughput tests for weighted jobs.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/flow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/gclient.c -->
# sources/test-tools/fio/gclient.c

Purpose: gfio network-client callback and result-rendering implementation. It translates fio client protocol events into GTK UI updates, ETA graphs, log rows, disk-utilization panels, and detailed end-result pages.

Important APIs/types/functions: exports `gfio_client_ops` and `gfio_display_end_results`. Important callbacks include `gfio_text_op`, `gfio_disk_util_op`, `gfio_thread_status_op`, `gfio_update_client_eta`, `gfio_update_all_eta`, `gfio_probe_op`, `gfio_quit_op`, `gfio_add_job_op`, `gfio_update_job_op`, timeout/start/stop/job-start/removed handlers. Result helpers build windows, menus, disk-util pages, latency bucket/percentile graphs, I/O depth tables, CPU/resource summaries, and per-direction read/write/trim status.

Control flow: fio client networking invokes `gfio_client_ops` callbacks as PDUs arrive. Text PDUs append rows to the global log and open the log view for errors. Probe and add-job replies populate host/job metadata and advance `gui_entry` state. ETA callbacks format rates/IOPS with `num2str`, update progress bars, and append graph samples. Thread-status callbacks store end results and immediately render them if the results window is open; otherwise rendering is triggered lazily. Disk-util PDUs are accumulated and displayed in the results notebook. Update-job replies set status fields used by the options dialog.

State and persistence behavior: state is in GTK widgets/models, `gfio_client` fields (`du`, `nr_du`, `results`, `nr_results`, option list, update-job status), graph objects, and per-entry result windows. Nothing is written to disk by this file. UI updates are wrapped with `gdk_threads_enter`/`leave` because callbacks can run off the GTK main thread.

Dependencies/integration: depends on fio protocol types from `client.h`/`server` via `fio.h`, stats helpers (`sum_thread_stats`, latency distributions, percentiles), graph/printing helpers, GTK/GDK/Cairo, gfio shared structs, and helper widgets. It is wired into `gfio.c` connection management through `gfio_client_ops`.

Risks and test signals: memory ownership of accumulated PDUs/results and generated strings is manual; repeated result rendering can duplicate pages; GTK thread locking must match the networking thread model; graph drawing depends on GTK2/GTK3 draw-event compatibility; and protocol endian conversion must be applied before use. Test signals should include simulated probe/add-job/ETA/text/disk-util/thread-status PDUs, multi-client aggregate ETA, results printing, closing/reopening results windows, update-job apply replies, and timeout/removal cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/gclient.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/gclient.h -->
# sources/test-tools/fio/gclient.h

Purpose: gfio client header exposing the GUI client operation table, end-result renderer, and color constants used for read/write/trim graphs and labels.

Important APIs/types/functions: declares `extern struct client_ops gfio_client_ops`, `gfio_display_end_results(struct gfio_client *)`, and RGB constants `GFIO_READ_*`, `GFIO_WRITE_*`, and `GFIO_TRIM_*`.

Control flow: `gfio.c` passes `gfio_client_ops` to fio client connection/handler APIs and calls `gfio_display_end_results` from the Results menu path. The color constants are consumed when graph labels and colored ETA entries are created.

State and persistence behavior: no state is defined here, but the extern operation table is a process-global callback contract.

Dependencies/integration: requires `struct client_ops` and `struct gfio_client` from surrounding includes. It couples the GUI shell to `gclient.c`.

Risks and test signals: callback-table signature drift will break networking integration at compile time. Visual tests should confirm read/write/trim colors match between live ETA and result views.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/gclient.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/gcompat.c -->
# sources/test-tools/fio/gcompat.c

Purpose: compatibility implementations for GTK APIs that differ across older GTK2/GTK3 versions.

Important APIs/types/functions: conditionally defines `gtk_combo_box_text_new`, append/insert/prepend/get-active-text wrappers for older GTK before 2.24, `gtk_widget_get_allocated_width`, `gtk_widget_get_allocated_height` for GTK before 3, and `gtk_widget_set_can_focus` for GTK before 2.18.

Control flow: compilation selects only the shims needed for the GTK version. Wrappers delegate to older GTK APIs or direct struct fields/macros.

State and persistence behavior: no persistent state. Functions return widgets or read/modify widget flags/allocation fields.

Dependencies/integration: includes GTK and `gcompat.h`. Used by gfio helpers and drawing code so the rest of the GUI can call newer API names unconditionally.

Risks and test signals: these shims rely on GTK2 struct internals such as `allocation` and `GTK_WIDGET_SET_FLAGS`. Test signals are builds against supported GTK2 minor versions and GTK3, combo-box text behavior, drawing-area size handling, and focus flag behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/gcompat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/gcompat.h -->
# sources/test-tools/fio/gcompat.h

Purpose: declares and maps GTK compatibility APIs for gfio across GTK2 and GTK3.

Important APIs/types/functions: for older GTK2, aliases `GtkComboBoxText` to `GtkComboBox`, declares text-combo helpers, and defines `GTK_COMBO_BOX_TEXT`. For GTK before 2.14 it defines inline `gtk_dialog_get_content_area` and `gtk_widget_get_window`. For GTK before 3 it declares allocated-size helpers. It defines `GFIO_DRAW_EVENT` as `"draw"` for GTK3 and `"expose_event"` for GTK2, and declares `gtk_widget_set_can_focus` for GTK before 2.18.

Control flow: preprocessor version checks select declarations/inlines at compile time, letting GUI sources use a mostly uniform API surface.

State and persistence behavior: no state beyond widget access performed by the declared functions.

Dependencies/integration: included by `gfio.h`, which spreads the compatibility layer throughout gfio. It must match implementations in `gcompat.c`.

Risks and test signals: incorrect version guards cause duplicate symbol definitions on newer GTK or missing APIs on older GTK. Build-matrix tests across GTK2.12/2.18/2.24-era headers and GTK3 are the primary signal, along with draw-event runtime smoke tests.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/gcompat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/gerror.c -->
# sources/test-tools/fio/gerror.c

Purpose: centralizes gfio error and informational message presentation using GTK info bars and modal dialogs.

Important APIs/types/functions: exports `gfio_report_error(struct gui_entry *ge, const char *format, ...)` and `gfio_report_info(struct gui *ui, const char *title, const char *message)`. Internal `report_error` builds or updates the main-window error info bar, and `on_info_bar_response` destroys it on OK.

Control flow: `gfio_report_error` formats a `GError` from varargs, passes it to `report_error`, and frees it. `report_error` creates a `GTK_MESSAGE_ERROR` info bar with an OK button when none exists, adds a label to the main UI vbox, and shows the window. If an info bar already exists, it updates the label with a fixed failure message. `gfio_report_info` creates a modal dialog, adds a label, runs it, and destroys it.

State and persistence behavior: UI state is stored in `ui->error_info_bar` and `ui->error_label`; dismissal resets only the info-bar pointer. No disk persistence.

Dependencies/integration: depends on GTK, GLib `GError`, `gfio.h` structs, and is called from connection, file, option, and state error paths.

Risks and test signals: existing-error updates discard the specific new error message and replace it with a generic string. Dialogs are synchronous and block the GTK main loop until dismissed. Tests should trigger first and repeated errors, OK dismissal, info dialog display, and errors from worker/network callbacks with GTK thread locking already held.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/gerror.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/gerror.h -->
# sources/test-tools/fio/gerror.h

Purpose: small gfio error-reporting API header.

Important APIs/types/functions: declares `gfio_report_error` for formatted entry-scoped errors and `gfio_report_info` for modal informational dialogs.

Control flow: callers route user-visible failures through these functions instead of directly constructing GTK info bars/dialogs.

State and persistence behavior: no state is declared here; implementations mutate GUI widget fields.

Dependencies/integration: requires `struct gui_entry` and `struct gui` declarations from `gfio.h` inclusion context.

Risks and test signals: signature changes affect most GUI error paths. Compile coverage and UI smoke tests for failure dialogs are sufficient for this header.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/gerror.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/gettime-thread.c -->
# sources/test-tools/fio/gettime-thread.c

Purpose: implements fio's optional gettimeofday offload thread, which continuously updates a shared timestamp so worker threads can read time through a seqlock without making system calls.

Important APIs/types/functions: defines global `struct fio_ts *fio_ts`, global `int fio_gtod_offload`, static `gtod_thread` and CPU mask, and exports `fio_gtod_init`, `fio_start_gtod_thread`, and `fio_gtod_set_cpu`. Internal functions are `fio_gtod_update` and `gtod_thread_main`.

Control flow: `fio_gtod_init` allocates shared timestamp storage once. `fio_start_gtod_thread` creates a locked startup semaphore, starts a small-stack detached thread, waits until the thread has attempted affinity setup, removes the semaphore, and returns creation/affinity status. The thread sets CPU affinity, signals startup, then loops while `nr_segments` is nonzero, calling `gettimeofday`, publishing the `timespec` under a seqlock, and executing `nop` to keep precision high. `fio_gtod_set_cpu` updates the target mask when CPU affinity is available.

State and persistence behavior: shared state is `fio_ts->ts` protected by `fio_ts->seqlock`, the offload flag, thread id, CPU mask, and the global `nr_segments` lifetime condition. No disk persistence.

Dependencies/integration: depends on `fio.h`, `lib/seqlock.h`, `smalloc`, `fio_sem`, CPU affinity OS helpers, and `gettimeofday`. `gettime.h` reads this state through `fio_gettime_offload`.

Risks and test signals: the update loop intentionally busy-spins and can consume a CPU; affinity failure aborts the thread; lifetime depends on `nr_segments`; and seqlock initialization must be valid in the `smalloc` allocation. Test signals should cover offload enabled/disabled, CPU pinning, startup synchronization, timestamp monotonicity enough for fio's use, and shutdown when segments drain.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/gettime-thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/gettime.c -->
# sources/test-tools/fio/gettime.c

Purpose: fio's timing implementation. It selects and initializes clock sources, reads timestamps directly or through the offload cache, converts CPU clocks to nanoseconds, computes elapsed intervals in ns/us/ms/sec, and validates CPU-clock monotonicity across CPUs.

Important APIs/types/functions: exports `fio_get_mono_time`, `fio_gettime`, `fio_local_clock_init`, `fio_clock_init`, `ntime_since`, `ntime_since_now`, `utime_since`, `utime_since_now`, `mtime_since_tv`, `mtime_since_now`, `rel_time_since`, `mtime_since`, `time_since_now`, and `fio_monotonic_clocktest`. CPU-clock builds include calibration globals (`cycles_per_msec`, `clock_mult`, masks/shifts), TLS warning state, and clock-test structs.

Control flow: `fio_gettime` optionally logs caller sites in debug builds, returns the offloaded timestamp if `fio_ts` exists, otherwise dispatches by `fio_clock_source` to `gettimeofday`, monotonic `clock_gettime`, or CPU-clock conversion. `fio_clock_init` creates TLS keys when needed, calibrates CPU clock conversion, and may select `CS_CPUCLOCK` if TSC is marked reliable and the monotonic test passes. Calibration samples cycles per millisecond, trims outliers, computes multiplier/shift parameters, and records `cycles_start`. Elapsed helpers normalize signed sec/nsec or sec/usec differences and clamp unsigned variants to zero on time warp. The CPU monotonic test pins threads to CPUs, records ordered TSC samples using an atomic sequence, sorts them, and reports failures if TSC order goes backward.

State and persistence behavior: process-global timing state includes selected/inited clock source, CPU-clock calibration parameters, `tsc_reliable`, optional wrap warning state, debug caller hashes, and TLS data. No durable persistence.

Dependencies/integration: depends on fio architecture clock hooks, OS affinity helpers, `fio_sem`, `flist`, `hash`, math library, pthreads, and `gettime-thread` offload state. Timing APIs feed rate limiting, ETA, latency accounting, ramp period, sem timeout validation, and setup progress.

Risks and test signals: CPU-clock calibration and wrap handling are architecture-sensitive; offload timestamps use wall-clock `gettimeofday` while monotonic paths may use `CLOCK_MONOTONIC`; elapsed helpers silently clamp negative time for unsigned variants; and monotonic clock tests can be affected by CPU affinity masks. Tests should cover each clock source, forced unreliable TSC, CPU affinity masks, wrap-prone architectures, debug time logging, negative time deltas, and high-frequency `fio_gettime` overhead.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/gettime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/gettime.h -->
# sources/test-tools/fio/gettime.h

Purpose: declares fio clock-source selection, timestamp retrieval, gettimeofday offload state, and local clock initialization APIs.

Important APIs/types/functions: defines `enum fio_cs` values `CS_GTOD`, `CS_CGETTIME`, `CS_CPUCLOCK`, and `CS_INVAL`; declares `fio_get_mono_time`, `fio_gettime`, `fio_gtod_init`, `fio_clock_init`, `fio_start_gtod_thread`, `fio_monotonic_clocktest`, `fio_local_clock_init`, `fio_gtod_set_cpu`; defines `struct fio_ts` with a `seqlock` and `timespec`; and provides inline `fio_gettime_offload`.

Control flow: callers normally call `fio_gettime`; the inline first checks `fio_ts`, reads a seqlock-protected timestamp until stable, and returns whether offload satisfied the request. Initialization functions are called during fio startup and per-thread setup.

State and persistence behavior: exposes the global `fio_ts` pointer. Timestamp state is process/shared-memory state, not durable persistence.

Dependencies/integration: includes architecture definitions and fio's seqlock. It is included by `fio.h` and timing users throughout fio.

Risks and test signals: all users depend on `fio_gettime_offload` being lock-free and returning consistent `timespec` pairs. Test signals include seqlock retry behavior under concurrent updates, null `fio_ts` fallback, and build coverage for architectures with/without CPU clocks.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/gettime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/gfio.c -->
# sources/test-tools/fio/gfio.c

Purpose: gfio application shell and main entry point. It builds the GTK UI, manages job tabs, file open/recent handling, connection dialogs, local backend startup, button/menu state, live graphs, preferences, log/results windows, drag-and-drop, and application lifetime.

Important APIs/types/functions: exports global `struct gui main_ui`, color/font globals, `gfio_view_log`, `gfio_set_state`, `clear_ge_ui_info`, and `main`. Major internal groups include graph setup/drawing, button state updates, `gui_entry` allocation/destruction, server/client job threads, connection details dialog, file open/new/close/recent handling, job menu callbacks, preferences/about dialogs, main and per-client page construction, recent-file menu synthesis, drag-and-drop, and `init_ui`.

Control flow: `main` initializes fio and options, initializes the goptions dependency tree, creates the main UI/hash table, enters GTK, then destroys the hash and exits goptions. `init_ui` initializes GTK threading, colors, window, menu, recent manager, notebook, main page, drag target, and log model. Opening a job file creates or reuses a tab, gathers connection details, adds a fio client, records recent-file metadata, and optionally starts a local backend thread. Connect sends the selected job through fio client APIs and starts a client handler thread if needed. Incoming callbacks from `gclient.c` advance `gui_entry` state, which drives menu and button sensitivity.

State and persistence behavior: process state includes `main_ui`, per-tab `gui_entry` objects stored in a `GHashTable` keyed by notebook page number, `gfio_server_running`, graph font/limit preferences for the current process, recent-file entries in GTK's recent manager, open result/log windows, client references, and job file/host strings. It starts backend and client-handler pthreads but performs no job-file saving yet; `file_save` is a placeholder.

Dependencies/integration: integrates fio core initialization, client/server APIs, gfio client callbacks, goptions, graph rendering, GTK/GDK/Cairo/GLib, recent-file APIs, and helper widgets. It shares UI structures defined in `gfio.h`.

Risks and test signals: page-number keys store addresses of `ge->page_num`, which are removed on destroy but can be fragile if notebook pages reorder; `send_clicked` appears to enable Start when `send_job_file` returns nonzero, which is suspicious because nonzero indicates failure; server thread toggles backend globals; GTK threading APIs are deprecated in newer GTK; `file_save` is incomplete; and graph refresh manually emits draw/expose events. Test signals should cover open/connect/send/start/disconnect, local auto-spawn, failed connections, tab close while connected, recent-file menu, drag-and-drop, preferences changing graphs/ETA interval, log window detach/reattach, and main-tab menu sensitivity.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/gfio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/gfio.h -->
# sources/test-tools/fio/gfio.h

Purpose: shared gfio data-model header for the GTK frontend. It defines main-window, per-job-tab, graph, ETA/probe, client, and result structures used across `gfio.c`, `gclient.c`, `goptions.c`, and helper modules.

Important APIs/types/functions: defines `struct probe_widget`, `struct eta_widget`, `struct gfio_graphs` and drawing dimensions, `struct gui`, `enum GE_STATE_*`, `enum GFIO_BUTTON_*`, `struct gui_entry`, `struct end_results`, `struct gfio_client_options`, and `struct gfio_client`. Declares `main_ui`, `gfio_view_log`, `gfio_set_state`, `clear_ge_ui_info`, graph font/color globals, and `GFIO_MIME`.

Control flow: the state enums drive button/menu sensitivity and represent the GUI client's lifecycle from new to connected, job sent/started/running/done. The structs are populated by UI construction in `gfio.c` and mutated by network callbacks in `gclient.c`.

State and persistence behavior: this header defines the in-memory state layout for gfio: GTK widget pointers, graph objects/labels, log/result models, pthread ids, client pointers, job file/host connection fields, option lists, accumulated disk-util and result data, and update-job status flags. Persistent effects are indirect, through GTK recent-manager metadata and fio server/client actions.

Dependencies/integration: includes GTK, compatibility shims, fio stat/thread option types, helper widgets, and graph types. It is the main coupling point among the gfio compilation units.

Risks and test signals: changes to these structs can break callback assumptions and memory ownership. The volatile update-job fields are used for cross-thread signaling but not a full synchronization primitive. Test signals include full gfio builds, state-transition UI tests, option-dialog update flows, and valgrind/sanitizer checks for result/client cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/gfio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/ghelpers.c -->
# sources/test-tools/fio/ghelpers.c

Purpose: reusable GTK widget helpers for gfio: framed read-only entries/labels, colored entries, spin buttons, tree-view columns, multitext rotating entries, and scrolled windows.

Important APIs/types/functions: exports `new_combo_entry_in_frame`, `new_info_entry_in_frame`, `new_info_entry_in_frame_rgb`, `new_info_label_in_frame`, `create_spinbutton`, `label_set_int_value`, `entry_set_int_value`, `tree_view_column`, `multitext_add_entry`, `multitext_set_entry`, `multitext_update_entry`, `multitext_free`, and `get_scrolled_window`. Internal `fill_color_from_rgb` converts floating RGB to `GdkColor`.

Control flow: widget factory functions create a frame, create the requested child, pack it into a caller-provided GTK box, and return the child widget. `tree_view_column` configures a text renderer, sorting, alignment, visibility, and appends the column. Multitext functions grow a string array, select/update text by index, and free all strings when the owning combo is destroyed.

State and persistence behavior: state is in GTK widget trees and `struct multitext_widget` arrays allocated with `realloc`/`strdup`. No disk persistence.

Dependencies/integration: depends on GTK, `gcompat.h`, and `ghelpers.h`. Used heavily by main gfio pages, result pages, ETA displays, and options dialogs.

Risks and test signals: `multitext_update_entry` assumes the index exists once `mt->text` is non-null; callers must allocate entries first. `multitext_free` sets unsigned `cur_text` to `-1`, producing a large value by design/accident. Tests should cover adding/updating/selecting entries, freeing empty and populated multitext widgets, column alignment/visibility flags, and GTK version compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/ghelpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/ghelpers.h -->
# sources/test-tools/fio/ghelpers.h

Purpose: header for gfio GTK helper widgets and small display utilities.

Important APIs/types/functions: declares framed widget factories, integer label/entry setters, scrolled-window creation, `struct multitext_widget`, multitext management functions, tree-view alignment/visibility/sort flags, and `tree_view_column`.

Control flow: callers include this header to build consistent gfio pages and result tables without duplicating GTK boilerplate.

State and persistence behavior: exposes the `multitext_widget` state layout: entry widget, dynamic text array, current index, and maximum index/count. Other functions operate on caller-owned GTK widgets.

Dependencies/integration: requires GTK types from including context or GTK headers included elsewhere. Included by `gfio.h` and GUI implementation files.

Risks and test signals: callers must initialize `multitext_widget` storage to zero before use and must not update out-of-range indexes. Compile and UI smoke tests cover this header.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/ghelpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/goptions.c -->
# sources/test-tools/fio/goptions.c

Purpose: gfio option editor. It builds a GTK dialog from the global fio option table, groups options by category, handles dependencies and inverse options, tracks modified controls, converts widget values back into `thread_options`, and sends live option updates to a connected fio client.

Important APIs/types/functions: exports `gopt_get_options_window`, `gopt_init`, and `gopt_exit`. Internal widget wrappers include `struct gopt`, `gopt_combo`, `gopt_int`, `gopt_bool`, `gopt_str`, `gopt_str_val`, `gopt_range`, `gopt_str_multi`, and `gopt_job_view`. Core helpers create controls for option types, set controls from `thread_options`, handle changed controls, maintain `changed_list`, update Apply sensitivity, build group tabs/frames, and build the dependency tree.

Control flow: `gopt_init` builds a `GNode` dependency tree from `fio_options` and each option's `parent`. `gopt_get_options_window` creates the modal dialog, fills a job combo from `gfio_client.o_list`, creates group tabs, adds every supported option widget, and runs an apply/OK/cancel loop. Widget change callbacks mark controls dirty unless a job switch is in progress, update dependent-child sensitivity, and handle inverse bool/int coupling. Apply walks changed controls, writes GTK values into the selected `thread_options`, calls `fio_client_update_options`, waits for the matching reply, and clears the changed list only on success. Job switching is blocked while modifications are pending and otherwise repopulates widgets from the selected job.

State and persistence behavior: transient dialog state is in `gopt_job_view`, per-widget `gopt` allocations, each option's `gui_data`, changed-list links, and `gopt_dep_tree`. Applying mutates the in-memory `thread_options` in the gfio client's option list and then remote client job options through fio's network protocol. No local job file is saved.

Dependencies/integration: depends on fio option metadata (`fio_options`, option groups/categories, `td_var`, parser helpers), gfio client structures, GTK/GLib, `flist`, and fio client update/wait APIs. It is invoked from the main GUI's Edit Job action.

Risks and test signals: several option types are incomplete or explicitly unhandled (`FIO_OPT_FLOAT_LIST`, partial `FIO_OPT_STR_MULTI` set-value, deprecated options). `gopt_set_options` assumes a `gopt` exists for every option and can dereference null for unsupported options. Combo handlers assume a valid active index. String handlers replace pointers with `strdup`, so ownership must match the rest of fio options. Apply blocks synchronously waiting for network reply. Test signals should include opening the dialog with representative option types, parent/child visibility, inverse bool/int options, range min/max adjustment, string-value unit wrapping, multi-job switching with dirty changes, failed update replies, and sanitizers for dialog destroy/changed-list lifetime.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/goptions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/goptions.h -->
# sources/test-tools/fio/goptions.h

Purpose: public header for gfio's option editor.

Important APIs/types/functions: declares `gopt_get_options_window(GtkWidget *window, struct gfio_client *gc)`, `gopt_init`, and `gopt_exit`.

Control flow: gfio initializes the option dependency tree at startup, opens an option window for the current client when the user selects Edit Job, and destroys option-editor global state at exit.

State and persistence behavior: no state is declared here; implementation maintains the dependency tree and mutates client option state during apply.

Dependencies/integration: includes GTK and relies on `struct gfio_client` from gfio context. It connects `gfio.c` menu actions to `goptions.c`.

Risks and test signals: initialization order matters: `gopt_init` must run after fio options are initialized and before any option window. Test signals include gfio startup/shutdown and opening/closing option dialogs repeatedly.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/goptions.h -->
