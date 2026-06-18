# sources/distributed-fs/ceph-client/kernel/trace/trace.c

Work item: subset-b-006069

## Purpose

`trace.c` is the central implementation of the Linux ftrace/tracefs tracing core in this Ceph-client kernel source snapshot. It owns the global tracing instance, trace-array instance lifecycle, ring-buffer allocation and resizing, tracefs control files, trace output iteration, trace marker writes, panic/oops dumping, boot-time tracing parameters, and several exported helper APIs used by trace events, function tracers, snapshots, and other kernel subsystems.

The file is not Ceph-specific by itself. Its relevance to the distributed filesystem tree is as kernel infrastructure that Ceph client code and other kernel code can use indirectly through tracepoints, ftrace, tracefs instances, trace markers, and panic-time trace dumps.

## Important APIs, Types, and State

Key exported or externally visible APIs include:

- `register_tracer()` registers a tracer plugin, runs or postpones startup selftests, creates per-instance option files, and optionally starts a boot-selected tracer.
- `tracing_on()`, `tracing_off()`, `tracer_tracing_on()`, `tracer_tracing_off()`, `tracer_tracing_disable()`, and `tracer_tracing_enable()` control whether ring buffers accept records.
- `tracing_is_enabled()`, `tracing_is_on()`, and `tracer_tracing_is_on()` report tracing state, with `tracing_is_enabled()` explicitly optimized as a racy fast-path mirror.
- `trace_buffer_lock_reserve()`, `trace_event_buffer_lock_reserve()`, `trace_event_buffer_commit()`, `trace_buffer_unlock_commit_regs()`, and `trace_buffer_unlock_commit_nostack()` reserve and commit ring-buffer records for trace events.
- `trace_function()` writes function trace records, optionally including function arguments.
- `trace_dump_stack()` records kernel stack traces into the active trace buffer.
- `tracing_set_tracer()` switches the current tracer for a `struct trace_array`.
- `tracing_set_cpumask()`, `tracing_resize_ring_buffer()`, and `tracing_set_clock()` modify CPU selection, buffer sizing, and timestamp source.
- `trace_array_get_by_name()`, `trace_array_put()`, and `trace_array_destroy()` expose named trace-instance creation, lookup, refcount release, and teardown.
- `trace_parse_run_command()` is a generic newline/comment-aware command parser for tracefs command files.
- `ftrace_dump()` emits trace contents to the console during explicit dump, oops, panic, or configured instance dump paths.

Important local types/state include:

- `global_trace`: the top-level `struct trace_array`, initialized with `TRACE_DEFAULT_FLAGS`, used by default tracefs files and by `printk_trace`.
- `struct trace_array`: the central per-instance state object referenced throughout this file, including current tracer, trace flags, buffers, cpumasks, tracefs dentries, event lists, snapshot state, marker state, error log, persistent-buffer metadata, and refcounts.
- `struct array_buffer`: wraps a `struct trace_buffer` ring buffer plus per-CPU `struct trace_array_cpu` data and timing metadata.
- `struct trace_iterator`: read-side state for formatted trace output, raw pipe reading, panic dumping, CPU selection, sequence buffers, and current event.
- `struct tracers`: per-trace-array wrapper pairing a `struct tracer` with instance-specific `struct tracer_flags`.
- `struct trace_eval_map_*`: optional eval-map storage for enum-to-string data exposed through `eval_map`.
- `struct trace_scratch` and `struct trace_mod_entry`: persistent boot-buffer metadata used to translate previous-boot kernel/module addresses to current-boot addresses.
- `struct trace_user_buf_info` and `struct trace_user_buf`: per-CPU temporary user-copy buffers used by trace marker writes and other trace-user-fault reads.
- `struct tracing_log_err`: bounded per-instance error-log records for trace command failures.

Global control state includes `tracing_disabled`, `tracing_buffer_mask`, `trace_types`, `trace_types_lock`, `ftrace_trace_arrays`, `trace_buf_size`, `tracing_thresh`, `tracepoint_printk`, `ftrace_dump_on_oops`, `marker_copies`, `tracepoint_print_iter`, and several static keys for trace exports and tracepoint printk.

## Control Flow

Boot and initialization flow:

1. Kernel command line handlers collect settings for `ftrace=`, `trace_options=`, `trace_clock=`, `trace_buf_size=`, `tracing_thresh=`, `tp_printk`, `traceoff_after_boot`, `trace_instance=`, and `ftrace_dump_on_oops`.
2. `early_trace_init()` allocates the tracepoint printk iterator when requested, calls `tracer_alloc_buffers()`, and initializes events.
3. `tracer_alloc_buffers()` allocates cpumasks, saved-cmdline support, the temporary trigger buffer, the global ring buffers, snapshot support, ftrace ops, and the global trace array. It registers notifiers and the nop tracer, then initializes function tracing and boot options.
4. `trace_init()` initializes trace events and enables boot-requested instances.
5. `tracer_init_tracefs()` runs at `fs_initcall`, creates tracefs control files through `tracer_init_tracefs_work_func()`, initializes per-CPU tracefs directories, trace instances, event files, ftrace top-level files, and optional runtime-verification interfaces.
6. `late_trace_init()` handles `tp_printk_stop_on_boot`, `traceoff_after_boot`, unstable-clock defaulting, and cleanup of unresolved boot tracer names.

Trace event record flow:

1. Callers reserve space with `trace_event_buffer_lock_reserve()` or `trace_buffer_lock_reserve()`.
2. Filtered or soft-disabled events may first use per-CPU temporary buffered events to avoid expensive ring-buffer discard operations.
3. If the normal buffer is off but trigger conditions need event data, events may be reserved from `temp_buffer`.
4. `trace_event_buffer_commit()` runs event triggers, optional tracepoint-to-printk output, optional registered trace exports, then commits via `trace_buffer_unlock_commit_regs()`.
5. Commit can append kernel and user stack trace entries depending on trace options and build config.

Trace read flow:

- Static `trace` reads use seq-file operations `s_start()`, `s_next()`, `s_stop()`, and `s_show()`. Iteration merges per-CPU entries by timestamp unless reading a per-CPU file. Formatting is routed through tracer-specific `print_line`, binary/hex/raw modes, event printer functions, and standard context headers.
- Consuming `trace_pipe` reads use `tracing_open_pipe()`, `tracing_wait_pipe()`, `tracing_read_pipe()`, and `trace_consume()` so entries are removed after printing.
- Raw `trace_pipe_raw`/buffer reads use `tracing_buffers_open()`, `tracing_buffers_read()`, `tracing_buffers_splice_read()`, `tracing_buffers_ioctl()`, and `tracing_buffers_mmap()` to expose ring-buffer sub-buffers directly, including reader-page ioctl and mmap support.

Tracer selection flow:

1. Users write `current_tracer`; `tracing_set_trace_write()` copies and trims the requested name.
2. `tracing_set_tracer()` expands buffers on first real use, finds the tracer in the instance's tracer list, rejects invalid boot/instance/snapshot/active-pipe cases, disables branch tracing, resets the previous tracer, handles snapshot arming/disarming, runs the new tracer's `init`, updates current flags, increments `enabled`, and re-enables trace branches.

Tracefs instance flow:

- User-created directories under `instances/` call `instance_mkdir()`, which creates a `trace_array`, allocates buffers, ftrace ops, cpumasks, tracefs files, and event directories.
- Removals call `instance_rmdir()` and `__remove_instance()`, which enforce refcount and active-reader checks, restore global marker/printk ownership if needed, clear zeroed flags, reset tracer state, remove event/ftrace files, release buffers, cpumasks, error logs, persistent reserved memory, and the instance name.
- Kernel users can call `trace_array_get_by_name()` to create or lookup an instance and hold a reference until `trace_array_put()`.

## State and Persistence Behavior

Most trace state is in memory and exposed through tracefs. Ring buffers are per-instance and per-CPU; default allocation may start minimal and expand to `trace_buf_size` on first use unless the user or boot parameters already expanded or resized the buffer.

Persistent/boot-mapped buffers are supported by `trace_instance=` syntax that can map a physical range or reserved memory name into a trace array. For those instances, `TRACE_ARRAY_FL_BOOT` and `TRACE_ARRAY_FL_LAST_BOOT` distinguish previous-boot contents from current-boot tracing. `setup_trace_scratch()` validates and sorts saved module metadata, computes kernel text deltas, builds per-module address deltas, and restores the previous trace clock when possible. `trace_adjust_address()` translates previous-boot addresses for display. `update_last_data()` clears previous-boot state once current tracing starts or the buffer is observed empty, resets ring buffers, records current module bases, clears `text_delta`, and updates scratch metadata.

Backup instances can copy a boot-mapped instance into vmalloc memory and mark it read-only plus auto-removable. `trace_array_autoremove()` and the `autoremove_wq` remove such arrays after the last reference is released.

`ftrace_dump_on_oops` persists only as a runtime sysctl/boot parameter string. On panic/oops, notifiers call `ftrace_dump(DUMP_PARAM)` to dump the global or named instances, optionally only the original CPU.

The error log is bounded to eight entries per trace array and is kept in memory. Opening `error_log` with truncation clears it. Trace marker writes are in-memory ring-buffer events; the global trace marker can be copied to interested instances through `marker_copies`.

## Dependencies and Integration Points

Major dependencies:

- Ring buffer APIs from `linux/ring_buffer.h` for allocation, reserve/commit, resize, per-CPU reads, splice, mmap, timestamps, overwrite mode, wait queues, and stats.
- tracefs/debugfs APIs for user ABI file creation and optional deprecated debugfs automount.
- ftrace internals for function tracing, tracer plugins, dynamic ftrace stats, ftrace ops, branch control, PID filters, graph options, and function filter files.
- trace event infrastructure for event registration, filtering, triggers, print functions, eval maps, system directories, saved cmdlines/tgids, synthetic/dynamic event command surfaces, and module event updates.
- snapshot support under `CONFIG_TRACER_SNAPSHOT`, including snapshot buffers, max-latency tracers, snapshot commands, and snapshot mmap guard helpers.
- module notifier integration for enum eval-map insertion/removal and persistent module-address delta maintenance.
- panic and die notifier chains for ftrace dump-on-oops behavior.
- CPU hotplug state `CPUHP_TRACE_RB_PREPARE` and cpumasks for possible/tracing CPUs.
- security lockdown checks using `security_locked_down(LOCKDOWN_TRACEFS)` on tracefs access and tracer registration.
- stacktrace/user-stack support, RCU, mutexes, raw spinlocks, arch spinlocks, static keys, workqueues, seq_file, splice, mmap VM ops, and user-copy helpers.

Tracefs ABI files created here include `available_tracers`, `current_tracer`, `tracing_cpumask`, `trace_options`, `trace`, `trace_pipe`, `buffer_size_kb`, `buffer_total_size_kb`, `trace_clock`, `timestamp_mode`, `buffer_subbuf_size_kb`, `free_buffer`, `trace_marker`, `trace_marker_raw`, `buffer_percent`, `syscall_user_buf_size`, `tracing_on`, `error_log`, `README`, `saved_cmdlines`, `saved_cmdlines_size`, `saved_tgids`, `tracing_thresh`, optional `eval_map`, optional `dyn_ftrace_total_info`, optional `snapshot`, and per-CPU `trace`, `trace_pipe`, `trace_pipe_raw`, `stats`, `buffer_size_kb`, `buffer_meta`, and snapshot files.

## Risks and Edge Cases

- Lock ordering is critical. Many paths intentionally take `event_mutex` before `trace_types_lock`; buffer readers use `trace_event_read_lock()` plus `trace_access_lock()`; resizing and tracer switching stop buffers under locks. New call sites must not invert these relationships.
- `tracing_is_enabled()` is documented as racy and should not be used where exact state is required. `tracer_tracing_is_on()` is the accurate check.
- Ring-buffer resize and sub-buffer-order changes have severe failure paths when snapshot buffer resizing fails after main-buffer changes. The code attempts rollback, but if rollback also fails it sets `tracing_disabled = 1`.
- Trace iterator output handles partial lines, seq buffer overflow, and copied temporary events. Incorrect printer behavior can create `[LINE TOO BIG]`, lost output, or repeated events.
- Trace marker writes depend on preemption-disabled per-CPU user-copy buffers. `trace_user_fault_read()` retries around context switches and warns after too many retries.
- Raw buffer splice/read/mmap requires sub-buffer alignment and disallows user mmap for memmapped or vmalloc backup instances.
- Persistent last-boot metadata is only trusted after validation. Invalid module names, oversized scratch metadata, or invalid saved clock IDs cause scratch reset. Address translation can still fall back to original addresses when deltas do not resolve to valid kernel text/rodata/data.
- `tracepoint_printk` serializes formatting through a single iterator and raw spinlock. It is intentionally gated by a static key and may be disabled after boot.
- `trace_array_destroy()` refuses to remove arrays with extra references or active pipe readers. Auto-remove uses workqueue context to avoid freeing active arrays directly.
- Lockdown mode disables tracing interfaces and tracer registration, which changes boot and runtime availability.
- `ftrace_dump()` uses a static iterator and atomic guard to prevent concurrent dumps; it disables tracing while dumping and avoids user-object symbol lookups in panic context.

## Test Signals

Useful validation signals for this file:

- Boot with tracing enabled and verify `tracefs` initialization: `/sys/kernel/tracing/current_tracer`, `available_tracers`, `trace`, `trace_pipe`, `tracing_on`, `trace_options`, `buffer_size_kb`, and per-CPU directories exist.
- Exercise tracer registration/selftests through kernels built with `CONFIG_FTRACE_STARTUP_TEST`; failed tracer selftests should remove the tracer from `available_tracers`.
- Write valid and invalid tracer names to `current_tracer`; valid switches should reset buffers and update `current_tracer`, while invalid names return `-EINVAL` and active `trace_pipe` readers should make switching return `-EBUSY`.
- Toggle `tracing_on` and confirm `trace_pipe` waiters wake when tracing is disabled.
- Resize `buffer_size_kb` globally and per-CPU; invalid CPU masks, zero values, and allocation failures should produce errors without corrupting entries accounting.
- Change `trace_clock`; buffers should reset so mixed timestamp domains are not present, and `timestamp_mode` should reflect ring-buffer absolute/delta mode.
- Write to `trace_marker` and `trace_marker_raw`; formatted and raw events should appear in `trace`/`trace_pipe`, and marker copy behavior should work for instances with `copy_marker`.
- Read `trace_pipe` and `trace_pipe_raw` using blocking, nonblocking, splice, ioctl reader-page, and mmap paths to validate wait semantics, alignment requirements, and cleanup.
- Create and remove trace instances under `instances/`; removal should fail while references or pipe readers are active and should clean tracefs/event/ftrace resources afterward.
- Use `error_log` consumers that call `tracing_log_err()` and verify bounded log rotation, caret placement, and truncation clearing.
- Boot with `ftrace_dump_on_oops` or trigger sysrq-style dumps and verify global/named instance output and original-CPU selection.
- Test persistent `trace_instance=` mappings or backups, then reboot and read `last_boot_info`; address adjustment, clock restoration, and clearing on current-boot use are the key signals.
