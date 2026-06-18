# subset-b-006067 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/preemptirq_delay_test.c -->
# sources/distributed-fs/ceph-client/kernel/trace/preemptirq_delay_test.c

## Purpose
`preemptirq_delay_test.c` is a small kernel module used to create controlled preemption-disabled and IRQ-disabled latency windows. It is intended to exercise latency tracers by generating deterministic sections where either local interrupts or preemption are disabled for a configurable number of microseconds.

## Important APIs, types, and functions
The user-facing controls are module parameters: `delay`, `test_mode`, `burst_size`, and `cpu_affinity`. The important routines are `busy_wait()`, `irqoff_test()`, `preemptoff_test()`, `execute_preemptirqtest()`, the ten generated `preemptirqtest_N()` wrappers, `preemptirq_delay_run()`, `preemptirq_run_test()`, and the sysfs `trigger_store()` handler.

## Control flow
Module initialization runs one test immediately, then creates `/sys/kernel/preemptirq_delay_test/trigger`. A write to `trigger` launches a kthread named after the selected mode. The thread optionally pins itself to `cpu_affinity`, runs up to `burst_size` of the generated wrapper functions, completes `done`, then sleeps until `kthread_stop()` is issued by the caller. `test_mode=irq` wraps the busy wait in `local_irq_save()/local_irq_restore()`, `preempt` wraps it in `preempt_disable()/preempt_enable()`, and `alternate` alternates by wrapper index.

## State and persistence
All state is transient module state. Parameters are read-only module parameters after load, `done` synchronizes the launching thread with the worker, and the sysfs kobject persists until module exit. No trace data is stored here; the latency tracers under test observe the generated delays.

## Dependencies and integration points
It integrates with kthreads, completions, cpumasks, sysfs kobjects, trace clock timing, local IRQ control, and preemption control. The ten unique wrappers deliberately create distinct call sites so stack traces from latency tracers are not all identical.

## Risks and test signals
Risks include intentionally stalling a CPU with IRQs or preemption disabled, invalid CPU affinity causing a logged `set_cpus_allowed_ptr()` failure, `test_mode` strings outside the accepted set producing no delay, and large `delay`/`burst_size` values causing disruptive latency. Test signals are tracer reports matching the configured delay, distinct stack traces for each burst wrapper, correct sysfs retrigger behavior, and affinity causing events to appear on the selected CPU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/preemptirq_delay_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/remote_test.c -->
# sources/distributed-fs/ceph-client/kernel/trace/remote_test.c

## Purpose
`remote_test.c` is a test module for the trace remote interface. It registers a remote tracing producer named `test`, backs the remote trace buffer with per-CPU `simple_ring_buffer` instances, and exposes a tracefs write hook that injects a synthetic remote event.

## Important APIs, types, and functions
Important state is `remote_test_buffer_desc`, per-CPU `simple_rbs`, and `simple_rbs_lock`. Main callbacks are `remote_test_load()`, `remote_test_unload()`, `remote_test_enable_tracing()`, `remote_test_swap_reader_page()`, `remote_test_reset()`, `remote_test_enable_event()`, and `remote_test_init_tracefs()`. The event write path is `write_event_write()`, which reserves `struct remote_event_format_selftest` and commits it to the current CPU simple ring buffer.

## Control flow
`remote_test_init()` calls `trace_remote_register("test", ...)` with the generated `remote_event_selftest` descriptor. When trace remote requests a buffer, `remote_test_load()` allocates a `trace_buffer_desc`, calls `trace_remote_alloc_buffer()`, and builds one `simple_ring_buffer` per descriptor CPU. Unload tears down the simple buffers, frees the remote descriptor, and clears the global pointer. A user write to tracefs `write_event` parses an integer, checks that the selftest event is enabled, disables preemption, reserves space in the current CPU simple ring buffer, fills the remote event id and payload id, then commits.

## State and persistence
The loaded buffer descriptor and per-CPU simple buffers are runtime-only. `simple_rbs_lock` serializes test writes against load/unload, while trace remote serializes its own callbacks. Event enablement uses the generated remote event's `enabled` field and is explicitly noted as racy but sufficient for this test module.

## Dependencies and integration points
The file depends on `trace_remote`, `tracefs`, `simple_ring_buffer`, generated remote event definitions, per-CPU storage, and `trace_clock_global()`. It integrates with the trace remote control plane via `struct trace_remote_callbacks` and with user tests through a tracefs file that writes synthetic events.

## Risks and test signals
Risks include races between write paths and module unload, incomplete cleanup after partial per-CPU allocation failure, rejecting writes when the event or CPU buffer is not enabled, and misuse of this intentionally simple enable-event implementation as production policy. Test signals include successful remote buffer load/unload cycles, per-CPU simple ring buffer creation, `write_event` producing decodable `selftest` records, reset/swap callbacks changing reader state, and clean failure on disabled event or missing buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/remote_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/remote_test_events.h -->
# sources/distributed-fs/ceph-client/kernel/trace/remote_test_events.h

## Purpose
`remote_test_events.h` declares the single synthetic event format used by `remote_test.c` to exercise trace remote event generation.

## Important APIs, types, and functions
It defines `REMOTE_TEST_EVENT_ID` as `1` and declares `REMOTE_EVENT(selftest, ...)` with one `u64 id` field and a printk format of `id=%llu`. The `REMOTE_EVENT` macro expands through the trace remote event-generation headers included by `remote_test.c`.

## Control flow
There is no runtime control flow in the header. Inclusion under `REMOTE_EVENT_INCLUDE_FILE` causes generated metadata, event format structures, and the `remote_event_selftest` object used by the test module.

## State and persistence
The header has no mutable state. Its stable event id and field layout become part of the generated remote event ABI for the test module.

## Dependencies and integration points
It depends on the trace remote event macro language, specifically `RE_STRUCT`, `re_field`, and `RE_PRINTK`. It is tightly coupled to `remote_test.c`, which validates event id `REMOTE_TEST_EVENT_ID` and writes `struct remote_event_format_selftest`.

## Risks and test signals
Risks are event-id collisions if additional test events are added carelessly, format mismatch with `remote_test.c`, and changing the field type without updating readers. Test signals are generated format availability, successful enable/disable by id `1`, and trace output rendering the written id value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/remote_test_events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rethook.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rethook.c

## Purpose
`rethook.c` implements the generic return-hook infrastructure used by facilities such as kretprobes. It manages per-task shadow stacks of hooked return addresses, preallocated hook nodes, trampoline handling, handler invocation, and cleanup when hooked tasks exit before returning.

## Important APIs, types, and functions
Public APIs include `rethook_alloc()`, `rethook_stop()`, `rethook_free()`, `rethook_try_get()`, `rethook_hook()`, `rethook_recycle()`, `rethook_flush_task()`, `rethook_find_ret_addr()`, and `rethook_trampoline_handler()`. Important types are `struct rethook`, `struct rethook_node`, `rethook_handler_t`, task `rethooks` llist storage, and the `objpool` used to preallocate nodes.

## Control flow
Clients allocate a `struct rethook` with a non-NULL handler and a fixed node pool. At function entry, with preemption disabled, a client obtains a node with `rethook_try_get()`, architecture code rewrites the return path through `rethook_hook()`, and the node is pushed onto `current->rethooks`. When the architecture trampoline fires, `rethook_trampoline_handler()` finds the original return address, restores the instruction pointer, runs handlers for nodes on the matching frame, applies optional architecture return-address fixup, unlinks the used shadow-stack nodes, and recycles them. If a task exits with unreached return hooks, `rethook_flush_task()` recycles all leftover nodes.

## State and persistence
State is runtime-only and split between the rethook object, its RCU-protected handler pointer, the object pool, and each task's lockless list of active nodes. `rethook_stop()` publishes a NULL handler to prevent new gets and to switch recycling into delayed RCU pool dropping. `rethook_free()` is asynchronous; callers must not touch the object afterward.

## Dependencies and integration points
The file depends on architecture-specific return-hook support (`arch_rethook_prepare`, `arch_rethook_trampoline`, optional `arch_rethook_fixup_return`), task lifetime cleanup, RCU, preemption control, lockless lists, objpool, kallsyms/kprobes headers, and `NOKPROBE_SYMBOL` annotations to keep core paths from being probed recursively.

## Risks and test signals
Risks include handler lifetime misuse after `rethook_free()`, node pool exhaustion, missing preemption disable around node acquisition, RCU-unavailable contexts rejected by validation builds, incorrect frame matching causing wrong return-address recovery, and fatal BUG if a trampoline cannot find the real return address. Test signals include nested return hooks on the same task, task exit with pending hooks, handler unregister under load, pool exhaustion behavior, stack traces using `rethook_find_ret_addr()`, and architecture-specific trampoline/fixup correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rethook.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/ring_buffer.c -->
# sources/distributed-fs/ceph-client/kernel/trace/ring_buffer.c

## Purpose
`ring_buffer.c` is the generic lockless tracing ring buffer used by kernel tracing. It provides per-CPU trace buffers, event reservation/commit, consuming and non-consuming readers, page extraction, overwrite/drop accounting, resizing, sub-buffer order changes, user mapping support, fixed memory range boot buffers, remote read-only buffers, wait/poll wakeups, hotplug allocation, and optional startup validation.

## Important APIs, types, and functions
Core exported allocation APIs are `__ring_buffer_alloc()`, `__ring_buffer_alloc_range()`, `__ring_buffer_alloc_remote()`, and `ring_buffer_free()`. Writer APIs include `ring_buffer_lock_reserve()`, `ring_buffer_unlock_commit()`, `ring_buffer_discard_commit()`, `ring_buffer_write()`, timestamp helpers, record enable/disable/off/on APIs, and nesting helpers. Reader APIs include `ring_buffer_peek()`, `ring_buffer_consume()`, `ring_buffer_read_start()`, `ring_buffer_iter_peek()`, `ring_buffer_iter_advance()`, `ring_buffer_read_finish()`, `ring_buffer_alloc_read_page()`, `ring_buffer_read_page()`, and `ring_buffer_free_read_page()`. Management APIs include resize, reset, empty/stat queries, `ring_buffer_subbuf_order_set()`, `ring_buffer_map()`, `ring_buffer_unmap()`, `ring_buffer_map_get_reader()`, `ring_buffer_poll_remote()`, and optional `ring_buffer_swap_cpu()`.

The central data structures are `struct trace_buffer`, `struct ring_buffer_per_cpu`, `struct buffer_page`, `struct buffer_data_page`, `struct ring_buffer_iter`, `struct rb_irq_work`, and boot/remote metadata structures such as `struct ring_buffer_meta`, `struct ring_buffer_cpu_meta`, and `struct trace_buffer_meta`.

## Control flow
Allocation creates a global `trace_buffer`, allocates per-CPU state for the current CPU, initializes a circular list of buffer pages plus a detached reader page, registers a CPU hotplug instance, and later allocates buffers for newly prepared CPUs. Writers disable preemption, validate buffer and CPU enablement, enter recursion protection, calculate event length and timestamp encoding, reserve space on the current CPU tail page, move the tail to a new page when necessary, optionally advance the head in overwrite mode, write event metadata, and later commit to the commit page. The outermost commit publishes all nested interrupt/NMI reservations in stack order and queues waiters via irq_work.

Readers take the per-CPU reader lock, swap the detached reader page with the current head page when the reader page is exhausted, decode internal timestamp events, and return only data events to consumers. Iterators maintain a private copied event and reset when a consuming read or resize invalidates their cached position. Page-read APIs either copy partial data into a caller page or swap out a whole reader page for high-throughput consumers. Mapping APIs pin a meta page and sub-buffer id table so user space can mmap the meta page plus sub-buffers and ask the kernel to advance the reader.

## State and persistence
Normal buffers are volatile in-memory structures. Per-CPU state tracks head, tail, commit, reader page, counters for entries, bytes, overruns, dropped events, commit overruns, read position, lost events, resize disablement, record disablement, mapping state, and timestamp state. Fixed-range allocation can recover metadata and trace contents from a previous boot when magic, structure sizes, total size, offsets, sub-buffer order, indexes, and event streams validate. Remote buffers are read-only from this side and mirror writer state through a meta page and remote callbacks.

## Dependencies and integration points
The implementation depends on trace event ABI types, `trace_clock_local` by default, CPU hotplug, per-CPU CPU masks, irq_work, wait queues, raw spinlocks, arch spinlocks, local atomics, RCU synchronization, VM mapping APIs, cache flushing, memory allocation, OOM-origin marking, CPU isolation housekeeping selection for irq_work, and security lockdown for startup self-tests. It is the backing store for ftrace and related tracing code, and its remote mode integrates with `trace_remote` descriptors and callback hooks.

## Risks and test signals
Primary risks are concurrency bugs in head/tail/commit page transitions, timestamp corruption under nested interrupts or unstable clocks, incorrect memory barriers causing readers to see partial events, resize or sub-buffer-order changes racing readers, mmap metadata getting out of sync with page swaps, remote meta interpretation errors, boot-buffer recovery accepting corrupt data, CPU hotplug publication races, and record disable counters becoming unbalanced. Test signals include `CONFIG_RING_BUFFER_STARTUP_TEST`, `CONFIG_RING_BUFFER_VALIDATE_TIME_DELTAS`, ring buffer benchmark coverage, concurrent writers with IRQ/NMI nesting, overwrite and non-overwrite full-buffer behavior, iterator reset after consuming reads, page extraction with missed-events flags, mmap read advancement, remote buffer polling/reset/swap, CPU hotplug, resize while tracing, and boot-range recovery after kexec-style reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/ring_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/ring_buffer_benchmark.c -->
# sources/distributed-fs/ceph-client/kernel/trace/ring_buffer_benchmark.c

## Purpose
`ring_buffer_benchmark.c` is a module that stress-tests and benchmarks the tracing ring buffer. It creates a producer that hammers a one-megabyte overwrite buffer for fixed intervals and optionally creates a consumer that alternates between event-by-event and page-based reads.

## Important APIs, types, and functions
Important module parameters are `disable_reader`, `write_iteration`, `producer_nice`, `consumer_nice`, `producer_fifo`, and `consumer_fifo`. Core routines are `read_event()`, `read_page()`, `ring_buffer_consumer()`, `ring_buffer_producer()`, `ring_buffer_consumer_thread()`, `ring_buffer_producer_thread()`, module init, and module exit. It uses `ring_buffer_alloc()`, `ring_buffer_lock_reserve()`, `ring_buffer_unlock_commit()`, `ring_buffer_consume()`, `ring_buffer_alloc_read_page()`, `ring_buffer_read_page()`, `ring_buffer_reset()`, `ring_buffer_entries()`, and `ring_buffer_overruns()`.

## Control flow
Module init allocates an overwrite buffer, optionally creates a consumer thread, starts the producer thread, and applies nice or FIFO scheduling policy. The producer repeatedly resets the buffer, wakes the consumer if present, runs for `RUN_TIME` seconds writing CPU ids into reserved events, periodically wakes the consumer, then asks the consumer to drain and reports throughput statistics through `trace_printk()`. The consumer toggles each cycle between `ring_buffer_consume()` and `ring_buffer_read_page()` so both read paths are covered.

## State and persistence
State is runtime module state: the shared buffer, producer/consumer task pointers, completions, `reader_finish`, read counters, and a sticky `test_error`. Nothing persists beyond module unload. Trace output records benchmark results in the tracing infrastructure.

## Dependencies and integration points
The benchmark depends on kthreads, completions, scheduler priority helpers, ktime, local atomics in page layout validation, and the generic ring buffer API. It is a diagnostic module rather than a production tracing component.

## Risks and test signals
Risks include deliberately high CPU load and stalls, low-priority defaults causing misleading throughput, consumer/producer completion races, assumptions about ring-buffer page event layout, and false errors if ring-buffer internals change. Test signals include absence of `TEST_ERROR()` warnings, correct CPU id payloads in both event and page readers, trace_printk throughput summaries, nonzero hit rate, sane overrun/read/entry totals, and clean stop on module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/ring_buffer_benchmark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rpm-traces.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rpm-traces.c

## Purpose
`rpm-traces.c` instantiates and exports runtime power-management tracepoints.

## Important APIs, types, and functions
The file defines `CREATE_TRACE_POINTS` before including `<trace/events/rpm.h>`, causing the tracepoint definitions for RPM events to be emitted. It exports `rpm_return_int`, `rpm_idle`, `rpm_suspend`, and `rpm_resume` with `EXPORT_TRACEPOINT_SYMBOL_GPL()`.

## Control flow
There are no functions in this file. Build-time inclusion of `trace/events/rpm.h` creates the tracepoints, and the export statements make them available to GPL modules.

## State and persistence
Tracepoint state is managed by the tracing subsystem. This file owns no persistent data of its own.

## Dependencies and integration points
It depends on the tracepoint event definitions in `<trace/events/rpm.h>` and on module symbol export infrastructure. Runtime PM code and GPL modules can use the exported symbols to emit or attach to RPM trace activity.

## Risks and test signals
Risks are limited but include duplicate tracepoint instantiation if `CREATE_TRACE_POINTS` is incorrectly defined elsewhere for the same header, ABI expectations around exported tracepoint names, and build breakage if event definitions change. Test signals include tracefs listing the RPM events and modules resolving the exported GPL tracepoint symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rpm-traces.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/Kconfig

## Purpose
`kernel/trace/rv/Kconfig` defines the Runtime Verification configuration menu, event helper symbols, monitor-category symbols, monitor Kconfig inclusions, and reactor options.

## Important APIs, types, and functions
Key config symbols are `RV`, `RV_PER_TASK_MONITORS`, event selectors such as `RV_MON_EVENTS`, `RV_MON_MAINTENANCE_EVENTS`, `DA_MON_EVENTS_*`, `LTL_MON_EVENTS_ID`, `HA_MON_EVENTS_*`, monitor type helpers `RV_LTL_MONITOR` and `RV_HA_MONITOR`, and reactors `RV_REACTORS`, `RV_REACT_PRINTK`, and `RV_REACT_PANIC`.

## Control flow
Selecting `RV` enables tracing and exposes runtime verification infrastructure. The file then sources individual monitor Kconfig files grouped by scheduler, rtapp, deadline, and generic categories. Event helper symbols select shared trace event support needed by generated monitor code. Reactor config entries depend on `RV_REACTORS` and are enabled by default when reactors are available.

## State and persistence
Kconfig choices persist in the kernel build configuration, not at runtime. `RV_PER_TASK_MONITORS` sets a compile-time integer bound from 1 to 8 with default 2.

## Dependencies and integration points
This file integrates RV with the kernel tracing subsystem via `select TRACING`, with many monitor subdirectories through `source` statements, and with reactor implementations built from the matching Makefile. The comments mark insertion points for generated or future monitors.

## Risks and test signals
Risks include accidentally selecting event infrastructure without its dependent monitor semantics, missing a new monitor's Kconfig source line, default-on reactors surprising minimal builds, and compile failures if a sourced monitor path is absent. Test signals include `olddefconfig` visibility, builds with `CONFIG_RV=n` and `CONFIG_RV=y`, individual monitor selection, and reactor symbols producing expected object inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/Makefile -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/Makefile

## Purpose
`kernel/trace/rv/Makefile` maps Runtime Verification Kconfig symbols to compiled objects and adds the local include path needed for RV trace event headers.

## Important APIs, types, and functions
The main build directives are `ccflags-y += -I $(src)`, `obj-$(CONFIG_RV) += rv.o`, one `obj-$(CONFIG_RV_MON_*)` entry per monitor, and reactor object entries for `rv_reactors.o`, `reactor_printk.o`, and `reactor_panic.o`.

## Control flow
Kbuild evaluates each `obj-$(CONFIG_...)` assignment and includes only objects whose config symbol is enabled. Monitor objects are organized under `monitors/<name>/<name>.o`, matching the Kconfig source structure.

## State and persistence
The file has no runtime state. It encodes build-time persistence by determining which RV objects are part of the kernel or module build.

## Dependencies and integration points
It depends on Kconfig symbols defined in `rv/Kconfig` and monitor-specific Kconfig files. The include flag integrates generated/local trace event headers with monitor compilation.

## Risks and test signals
Risks include Kconfig/Makefile symbol mismatches, forgotten object entries for new monitors, stale entries for removed monitors, and missing include path breaking event headers. Test signals are all RV monitor config combinations building cleanly and generated monitor additions updating both Kconfig and Makefile insertion points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/deadline/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/deadline/Kconfig

## Purpose
This Kconfig file defines `CONFIG_RV_MON_DEADLINE`, the umbrella runtime-verification monitor option for deadline scheduler and server specifications.

## Important APIs, types, and functions
The single symbol is `RV_MON_DEADLINE`, a boolean depending on `RV`. Its help text describes it as enabling all deadline scheduler specifications supported by the current kernel and points to `Documentation/trace/rv/monitor_deadline.rst`.

## Control flow
When `RV` is enabled, the user can select `deadline monitor`. The top-level RV Makefile then compiles `monitors/deadline/deadline.o` when `CONFIG_RV_MON_DEADLINE=y`.

## State and persistence
The selected value persists only as a build configuration. Runtime enablement is handled later by the RV monitor registration code.

## Dependencies and integration points
It depends on the core RV menu and integrates with `kernel/trace/rv/Kconfig` through a `source` statement and with the RV Makefile through the matching object entry.

## Risks and test signals
Risks include the umbrella option becoming stale as specific deadline submonitors evolve, documentation mismatch, and enabling a container without required downstream monitor objects. Test signals include menu visibility only under `CONFIG_RV`, successful builds with the option enabled, and the runtime RV monitor list showing the deadline container.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/deadline/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/deadline/deadline.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/deadline/deadline.c

## Purpose
`deadline.c` registers a Runtime Verification monitor container named `deadline`. It groups deadline scheduler specifications and exposes shared state used by other deadline-related monitors.

## Important APIs, types, and functions
The key object is `struct rv_monitor rv_deadline`, with name `deadline`, a descriptive string, no custom enable/disable/reset callbacks, and initial `enabled = 0`. The file also defines `struct sched_class *rv_ext_sched_class` for use by other monitors. Lifecycle functions are `register_deadline()` and `unregister_deadline()`.

## Control flow
On module init, `register_deadline()` checks `CONFIG_SCHED_CLASS_EXT`; when enabled it resolves `ext_sched_class` with `kallsyms_lookup_name()` and warns if absent. It then registers the monitor with `rv_register_monitor(&rv_deadline, NULL)`. Module exit unregisters it with `rv_unregister_monitor()`.

## State and persistence
Runtime state is the registered RV monitor object and the optional cached pointer to `ext_sched_class`. There is no persistent storage, and the monitor has no internal enable or reset state beyond the RV core's handling of `rv_monitor.enabled`.

## Dependencies and integration points
It depends on the RV core, module init/exit infrastructure, kallsyms, scheduler class declarations from `deadline.h`, and optionally the sched_ext class symbol. Other deadline monitors can use `rv_ext_sched_class` to recognize external scheduler-class interactions.

## Risks and test signals
Risks include `kallsyms_lookup_name()` returning NULL when sched_ext is expected, the container registering successfully even though dependent monitors may lack ext scheduler awareness, and no enable/disable callbacks for container-specific validation. Test signals include successful RV monitor registration, warning behavior with `CONFIG_SCHED_CLASS_EXT` but missing `ext_sched_class`, clean unregister on module unload, and downstream deadline monitors finding `rv_ext_sched_class` when sched_ext is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/deadline/deadline.c -->
