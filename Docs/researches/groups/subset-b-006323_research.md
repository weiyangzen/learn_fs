# subset-b-006323 Research

This grouped report covers the requested Linux sample files under `sources/distributed-fs/ceph-client/samples`. Each file section is source-path titled and wrapped with the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/configfs/configfs_sample.c -->
# sources/distributed-fs/ceph-client/samples/configfs/configfs_sample.c

Purpose: demonstration kernel module for configfs subsystems and the helper macros in `linux/configfs.h`. It shows a childless subsystem, subsystems that create items, subsystems that create groups, and deeper item/group nesting.

Important APIs/functions: uses `struct configfs_subsystem`, `struct config_group`, `struct config_item`, `struct config_item_type`, `CONFIGFS_ATTR*`, `config_item_init_type_name`, `config_group_init_type_name`, `configfs_register_subsystem`, and `configfs_unregister_subsystem`. Attribute stores parse integers with `kstrtoint`; release callbacks free dynamically allocated children with `kfree`.

Control flow: module initialization initializes subsystem mutexes/groups, registers the sample subsystems, and unwinds earlier registrations on failure. Runtime control is driven by configfs mkdir/rmdir/read/write operations: `make_item` allocates simple children, `make_group` allocates child groups, attribute show/store methods expose per-object values, and release hooks free objects when configfs drops references. Exit unregisters all subsystems.

State and persistence: all state is in kernel memory and configfs dentries. Values such as `showme` and `storeme` persist only while the module and configfs objects exist. `showme` intentionally increments on read to demonstrate side effects.

Dependencies and integration: depends on `CONFIGFS_FS` and sample config support. Integrates with user space through `/sys/kernel/config` directories and files, not through Ceph-specific code.

Risks: examples are intentionally minimal and rely on correct configfs lifetime rules; leaked references or missing release callbacks would leak memory. Attribute writes accept plain decimal integers and return parser errors directly. This sample should not be treated as a policy or persistence layer.

Test signals: build with `CONFIG_SAMPLE_CONFIGFS`, load the module, mount configfs, create/remove sample items and groups, read description files, write `storeme`, and confirm object cleanup by removing the module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/configfs/configfs_sample.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/connector/Makefile -->
# sources/distributed-fs/ceph-client/samples/connector/Makefile

Purpose: kbuild glue for the connector sample.

Important APIs/functions: builds `cn_test.o` when `CONFIG_SAMPLE_CONNECTOR` is enabled and builds the user program `ucon` when `CONFIG_CC_CAN_LINK` permits host/user linking. Adds `-I usr/include` to user C flags so exported kernel UAPI headers are found.

Control flow: no runtime code; kbuild selects one kernel module and one optional user-space utility.

State and persistence: none.

Dependencies and integration: integrates with Linux sample build infrastructure and connector UAPI headers.

Risks: user program availability depends on a usable linker and installed/exported UAPI headers.

Test signals: `make samples/connector/` or a full kernel samples build should produce `cn_test.ko` and, on link-capable builds, `ucon`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/connector/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/connector/cn_test.c -->
# sources/distributed-fs/ceph-client/samples/connector/cn_test.c

Purpose: kernel-side connector/netlink test module that registers connector callbacks and periodically sends messages to user-space listeners.

Important APIs/functions: uses `struct cb_id`, `struct cn_msg`, `cn_add_callback`, `cn_del_callback`, `cn_netlink_send`, `timer_setup`, `mod_timer`, and `timer_delete_sync`. `cn_test_callback` logs received connector messages; `cn_test_timer_func` allocates a `cn_msg`, fills a counter string, sends it, and re-arms the timer.

Control flow: init registers two callbacks for adjacent connector IDs, starts a one-second timer, and logs the final ID. The timer repeatedly sends `counter = N` messages. Exit deletes the timer synchronously and unregisters both callbacks.

State and persistence: global connector ID, timer object, timer counter, and a legacy `nls` socket pointer. State is volatile and reset on module load.

Dependencies and integration: depends on the connector subsystem and netlink. Pairs with `samples/connector/ucon.c`, which subscribes and optionally sends test messages.

Risks: timer callback allocates with `GFP_ATOMIC`, so allocation failure silently drops a tick. The disabled notification example shows raw netlink skb construction and should remain example-only. Callback registration/unregistration depends on restoring `cn_test_id.val` correctly during unwind.

Test signals: load `cn_test.ko`, run `ucon`, observe one-second connector messages, run `ucon -s` to send bursts, and inspect kernel logs for callback output and clean unregister on unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/connector/cn_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/connector/ucon.c -->
# sources/distributed-fs/ceph-client/samples/connector/ucon.c

Purpose: user-space netlink connector utility for the `cn_test` module.

Important APIs/functions: opens `PF_NETLINK`/`NETLINK_CONNECTOR`, binds to all connector groups, builds `struct nlmsghdr` plus `struct cn_msg` in `netlink_send`, uses `poll`, `recv`, and `send`, and prints received `NLMSG_DONE` messages.

Control flow: parses `-h` and `-s`; optional output file is opened append/update. Default mode binds and waits in a poll loop, printing timestamps and connector IDs for received messages. Send mode constructs a zero-length `cn_msg` for `CN_NETLINK_USERS + 3` / `0x456` and sends 10 batches of 1000 messages.

State and persistence: process-local sequence number and optional output file. No durable state except appended logs.

Dependencies and integration: requires connector UAPI headers and the `cn_test` module using matching IDs. Uses netlink protocol number 11.

Risks: fixed stack buffers assume small messages; the send path does not bound arbitrary future message lengths. Binding to `nl_groups = -1` subscribes broadly. File-open error message references `argv[1]` rather than the actual output argument.

Test signals: run `ucon` while `cn_test.ko` is loaded to see periodic counters; run `ucon -s` and check kernel log callback lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/connector/ucon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/coresight/Makefile -->
# sources/distributed-fs/ceph-client/samples/coresight/Makefile

Purpose: builds the CoreSight syscfg sample module.

Important APIs/functions: maps `CONFIG_SAMPLE_CORESIGHT_SYSCFG` to `coresight-cfg-sample.o` and adds an include path for `drivers/hwtracing/coresight`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: depends on CoreSight syscfg internal headers being available in the kernel source tree.

Risks: include path reaches into driver internals, so sample build is sensitive to CoreSight header movement.

Test signals: enabling `CONFIG_SAMPLE_CORESIGHT_SYSCFG` should compile `coresight-cfg-sample.ko`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/coresight/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/coresight/coresight-cfg-sample.c -->
# sources/distributed-fs/ceph-client/samples/coresight/coresight-cfg-sample.c

Purpose: module that registers an alternate CoreSight `autofdo2` system configuration with preset strobing parameters.

Important APIs/functions: defines `struct cscfg_config_desc`, `struct cscfg_load_owner_info`, feature reference names, preset parameter table, `cscfg_load_config_sets`, and `cscfg_unload_config_sets`.

Control flow: init passes the config and empty feature list to the CoreSight syscfg loader. Exit unloads all sets owned by the module owner handle.

State and persistence: static preset tables and descriptors exist while the module is loaded; registered CoreSight syscfg state is removed on module unload.

Dependencies and integration: integrates with CoreSight ETM syscfg infrastructure and references the built-in `strobing` feature by name.

Risks: feature name and parameter count must match CoreSight expectations. Incorrect preset dimensions would misconfigure tracing. This is a registration example and does not validate hardware availability itself.

Test signals: build/load with CoreSight syscfg support, inspect registered configurations, select `autofdo2` presets, and unload to confirm owner cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/coresight/coresight-cfg-sample.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/damon/Kconfig -->
# sources/distributed-fs/ceph-client/samples/damon/Kconfig

Purpose: Kconfig menu for three DAMON sample modules: working set estimation, proactive reclamation, and memory tiering.

Important APIs/functions: declares `SAMPLE_DAMON_WSSE`, `SAMPLE_DAMON_PRCL`, and `SAMPLE_DAMON_MTIER`. The first two depend on `DAMON && DAMON_VADDR`; memory tiering depends on `DAMON && DAMON_PADDR`.

Control flow: configuration only; selected symbols drive `samples/damon/Makefile`.

State and persistence: none at runtime.

Dependencies and integration: ties samples to DAMON virtual-address and physical-address monitoring capabilities.

Risks: help text for MTIER contains typos but conveys the intended two-node NUMA/CXL-like topology. Enabling samples without understanding DAMON actions can reclaim or migrate memory.

Test signals: `make menuconfig` should expose "DAMON Samples"; selected symbols should produce the corresponding sample objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/damon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/damon/Makefile -->
# sources/distributed-fs/ceph-client/samples/damon/Makefile

Purpose: maps DAMON sample Kconfig symbols to module objects.

Important APIs/functions: `obj-$(CONFIG_SAMPLE_DAMON_WSSE) += wsse.o`, `obj-$(CONFIG_SAMPLE_DAMON_PRCL) += prcl.o`, and `obj-$(CONFIG_SAMPLE_DAMON_MTIER) += mtier.o`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: integrates with kbuild and symbols from `samples/damon/Kconfig`.

Risks: no conditional dependency logic here; Kconfig must enforce DAMON support.

Test signals: selected sample config symbols should compile the matching `.ko` files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/damon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/damon/mtier.c -->
# sources/distributed-fs/ceph-client/samples/damon/mtier.c

Purpose: DAMON physical-address sample for memory tiering. It migrates hot pages from node 1 to node 0 and cold pages from node 0 to node 1 while using DAMOS quota goals to target node 0 utilization/free ratios.

Important APIs/functions: module parameters configure node address ranges, node0 memory used/free basis points, `enabled`, and `detect_node_addresses`. Uses `damon_new_ctx`, `damon_set_attrs`, `damon_select_ops(DAMON_OPS_PADDR)`, `damon_new_target`, `damon_new_region`, `damon_new_scheme`, `damos_new_quota_goal`, `damos_new_filter`, `damon_start`, and `damon_stop`.

Control flow: enabling builds two contexts with `damon_sample_mtier_build_ctx`: one promote context for node 1 using `DAMOS_MIGRATE_HOT`, one demote context for node 0 using `DAMOS_MIGRATE_COLD`. Init starts them if `enabled` was preset. The parameter store toggles start/stop after validating `damon_initialized()`.

State and persistence: two global `damon_ctx *` pointers and module parameters. DAMON contexts and schemes persist until disabled or module removal; no on-disk state.

Dependencies and integration: depends on DAMON physical address operations, NUMA node metadata, DAMOS migration actions, and page young filtering.

Risks: incorrect physical ranges or node IDs can monitor the wrong memory. Migration actions can affect performance and placement. Error paths destroy contexts, but there is no module exit hook, so this sample relies on enable/disable semantics and DAMON lifecycle assumptions.

Test signals: enable on a two-node system with `detect_node_addresses=1` or explicit ranges, inspect DAMON activity and node memory balance, then disable and confirm `damon_stop` destroys both contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/damon/mtier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/damon/prcl.c -->
# sources/distributed-fs/ceph-client/samples/damon/prcl.c

Purpose: DAMON virtual-address sample for proactive reclamation of cold regions in a target process.

Important APIs/functions: `target_pid` and `enabled` module parameters; `damon_new_ctx`, `damon_select_ops(DAMON_OPS_VADDR)`, `find_get_pid`, `damon_new_scheme` with `DAMOS_PAGEOUT`, `damon_start`, `damon_call`, and `damon_stop`.

Control flow: enabling creates a VADDR context, attaches one target pid, creates a scheme matching page-sized regions with zero accesses and age at least 50, starts DAMON, and registers a repeated callback that logs WSS by summing accessed regions. Disabling stops and destroys the context.

State and persistence: global context and PID reference while enabled; no persistent storage.

Dependencies and integration: depends on DAMON VADDR support and process PID lifetime. Integrates with kernel logs for WSS reporting.

Risks: target PID may disappear; code obtains a pid reference but does not explicitly `put_pid` outside context destruction assumptions. `DAMOS_PAGEOUT` can reclaim pages from the selected process and affect workload latency.

Test signals: load with `target_pid=<pid> enabled=1`, monitor `dmesg` for WSS and pageout behavior, then write `0` to the enabled parameter and confirm stop logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/damon/prcl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/damon/wsse.c -->
# sources/distributed-fs/ceph-client/samples/damon/wsse.c

Purpose: DAMON virtual-address working set size estimation sample for a single process.

Important APIs/functions: module parameters `target_pid` and callback-backed `enabled`; `damon_new_ctx`, `damon_select_ops(DAMON_OPS_VADDR)`, `damon_new_target`, `find_get_pid`, `damon_start`, `damon_call`, and repeated `damon_for_each_target`/`damon_for_each_region`.

Control flow: enabling creates and starts a DAMON context for the target process, then schedules a repeated callback that sums all regions with `nr_accesses > 0` and logs `wss`. Disabling stops and destroys the context.

State and persistence: runtime-only DAMON context and pid reference. Module parameters persist only while loaded.

Dependencies and integration: depends on DAMON VADDR support and kernel logging.

Risks: no reclamation action is taken, but monitoring overhead and PID-lifetime issues remain. Repeated logging can be noisy.

Test signals: run with a known process pid, compare logged WSS with workload memory behavior, and verify disable stops callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/damon/wsse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/fanotify/Makefile -->
# sources/distributed-fs/ceph-client/samples/fanotify/Makefile

Purpose: builds the fanotify filesystem error monitor user program.

Important APIs/functions: `userprogs-always-y += fs-monitor`; adds exported UAPI include path and `-Wall`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: depends on user-space compile support and fanotify UAPI headers.

Risks: no kernel config guard in this Makefile; runtime requires fanotify support and permission.

Test signals: samples build should produce `fs-monitor`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/fanotify/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/fanotify/fs-monitor.c -->
# sources/distributed-fs/ceph-client/samples/fanotify/fs-monitor.c

Purpose: user-space sample that subscribes to `FAN_FS_ERROR` events for a filesystem and prints error and file-handle metadata.

Important APIs/functions: `fanotify_init(FAN_CLASS_NOTIF | FAN_REPORT_FID)`, `fanotify_mark(... FAN_MARK_FILESYSTEM, FAN_FS_ERROR, ...)`, `FAN_EVENT_OK`, `FAN_EVENT_NEXT`, `fanotify_event_info_error`, and `fanotify_event_info_fid`.

Control flow: requires a path argument, initializes fanotify, marks the filesystem, then continuously reads events into a buffer. `handle_notifications` validates event masks/fds and iterates variable-length info records for error and FID details.

State and persistence: fanotify file descriptor and stack buffer; output is printed to stdout. No persistence.

Dependencies and integration: depends on fanotify filesystem error reporting and UAPI definitions, with local fallback definitions for older libc headers.

Risks: infinite loop with fatal `errx` on read/mark failures. File handle decoding only recognizes `FILEID_INO32_GEN` and invalid superblock errors. Requires privileges sufficient for filesystem marks.

Test signals: run against a filesystem path as root or with appropriate capabilities, inject or provoke fs errors on a supporting filesystem, and inspect printed error count and FID records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/fanotify/fs-monitor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/fprobe/Makefile -->
# sources/distributed-fs/ceph-client/samples/fprobe/Makefile

Purpose: builds the fprobe sample module.

Important APIs/functions: maps `CONFIG_SAMPLE_FPROBE` to `fprobe_example.o`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: depends on fprobe/ftrace support selected by Kconfig.

Risks: none beyond sample config correctness.

Test signals: enabling `CONFIG_SAMPLE_FPROBE` should build `fprobe_example.ko`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/fprobe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/fprobe/fprobe_example.c -->
# sources/distributed-fs/ceph-client/samples/fprobe/fprobe_example.c

Purpose: kernel module demonstrating fprobe entry/exit handlers on one or more kernel symbols, defaulting to `kernel_clone`.

Important APIs/functions: `struct fprobe`, `register_fprobe`, `register_fprobe_syms`, `unregister_fprobe`, `stack_trace_save`, `stack_trace_print`, and module params `symbol`, `nosymbol`, `stackdump`, `use_trace`.

Control flow: init configures entry and exit handlers. If `symbol` contains `*`, it registers a filter-based probe with optional `nosymbol`; if a single symbol, it registers directly; otherwise it splits comma-separated symbols and registers all. Handlers log entry/return and optionally dump a stack. Exit unregisters and logs hit/miss counts.

State and persistence: global `sample_probe`, `nhit`, and module parameters. No persistent storage.

Dependencies and integration: depends on fprobe/ftrace instrumentation and kallsyms visibility for requested symbols.

Risks: tracing hot or recursive paths can flood logs and affect performance. `trace_printk` is intentionally debug-only. Symbol filters must avoid probing unsafe paths.

Test signals: insert with `symbol=kernel_clone`, fork processes, inspect logs and `nmissed`; repeat with wildcard and `nosymbol` filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/fprobe/fprobe_example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/ftrace/Makefile -->
# sources/distributed-fs/ceph-client/samples/ftrace/Makefile

Purpose: builds several ftrace direct-call, ftrace ops, and trace-array sample modules.

Important APIs/functions: maps `CONFIG_SAMPLE_FTRACE_DIRECT` to `ftrace-direct.o`, `ftrace-direct-too.o`, and `ftrace-direct-modify.o`; maps `CONFIG_SAMPLE_FTRACE_DIRECT_MULTI` to multi-direct variants; maps `CONFIG_SAMPLE_FTRACE_OPS` and `CONFIG_SAMPLE_TRACE_ARRAY`. Adds `-I$(src)` for `sample-trace-array.o`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: depends on ftrace, architecture trampoline support, and trace event headers.

Risks: architecture-specific assembly in the C files controls actual build success.

Test signals: enable each sample config and build; unsupported architectures should fail at Kconfig or compile gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/ftrace/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/ftrace/ftrace-direct-modify.c -->
# sources/distributed-fs/ceph-client/samples/ftrace/ftrace-direct-modify.c

Purpose: demonstrates replacing an ftrace direct trampoline at runtime for a single traced function (`schedule`).

Important APIs/functions: architecture-specific `my_tramp1`/`my_tramp2`, `my_direct_func1`, `my_direct_func2`, `struct ftrace_ops`, `ftrace_set_filter_ip`, `register_ftrace_direct`, `modify_ftrace_direct`, `unregister_ftrace_direct`, and a kernel thread.

Control flow: init filters the ops to `schedule`, registers `my_tramp1`, and starts a thread. Every two seconds the thread toggles between trampolines via `modify_ftrace_direct`; exit stops the thread and unregisters the current direct trampoline.

State and persistence: global direct ops, current trampoline address, trampoline array, and worker task. Runtime-only.

Dependencies and integration: depends on ftrace direct support and correct per-architecture calling convention assembly.

Risks: incorrect trampoline register preservation can crash the kernel. Tracing `schedule` is high frequency; `trace_printk` can perturb scheduling. Exit assumes `simple_tsk` was created when registration succeeded.

Test signals: load module and inspect trace buffer for alternating direct function messages; unload and verify direct registration is removed cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/ftrace/ftrace-direct-modify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/ftrace/ftrace-direct-multi-modify.c -->
# sources/distributed-fs/ceph-client/samples/ftrace/ftrace-direct-multi-modify.c

Purpose: demonstrates runtime trampoline replacement for one ftrace direct registration attached to multiple functions.

Important APIs/functions: `ftrace_set_filter_ip` for `wake_up_process` and `schedule`, `register_ftrace_direct`, `modify_ftrace_direct`, `unregister_ftrace_direct`, architecture trampolines that pass the traced IP to `my_direct_func1/2`.

Control flow: init filters both functions and registers one direct trampoline. A kernel thread toggles the direct target every two seconds. Exit stops the thread and unregisters the current trampoline.

State and persistence: global trampoline pointer, two trampoline addresses, ftrace ops, and task pointer.

Dependencies and integration: integrates with multi-function ftrace direct support and architecture-specific ftrace ABI.

Risks: same trampoline must safely handle both traced functions and preserve arguments. Logging from scheduler/wakeup paths can be noisy and timing-sensitive.

Test signals: load with `CONFIG_SAMPLE_FTRACE_DIRECT_MULTI`, trigger scheduling/wakeup activity, confirm trace messages include IP values and alternate functions, then unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/ftrace/ftrace-direct-multi-modify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/ftrace/ftrace-direct-multi.c -->
# sources/distributed-fs/ceph-client/samples/ftrace/ftrace-direct-multi.c

Purpose: static multi-function ftrace direct-call sample.

Important APIs/functions: architecture-specific `my_tramp`, `my_direct_func(unsigned long ip)`, `struct ftrace_ops`, `ftrace_set_filter_ip`, `register_ftrace_direct`, and `unregister_ftrace_direct`.

Control flow: init filters both `wake_up_process` and `schedule`, registers `my_tramp`, and direct calls `my_direct_func` with the traced instruction pointer. Exit unregisters the direct call.

State and persistence: one `ftrace_ops` object and registered trampoline while loaded.

Dependencies and integration: depends on ftrace direct multi-target support and arch assembly.

Risks: probing scheduler paths with `trace_printk` is invasive. Any argument/IP recovery bug is architecture-specific and severe.

Test signals: load, generate scheduler/wakeup activity, read ftrace output for `ip` lines, and unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/ftrace/ftrace-direct-multi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/ftrace/ftrace-direct-too.c -->
# sources/distributed-fs/ceph-client/samples/ftrace/ftrace-direct-too.c

Purpose: second ftrace direct example that instruments `handle_mm_fault` and demonstrates trampolines for a function with multiple arguments.

Important APIs/functions: `my_direct_func(struct vm_area_struct *, unsigned long, unsigned int, struct pt_regs *)`, `my_tramp`, `ftrace_set_filter_ip`, `register_ftrace_direct`, `unregister_ftrace_direct`, and architecture stack/register save code.

Control flow: init filters `handle_mm_fault` and registers the trampoline; the trampoline passes original arguments to `my_direct_func`, which logs process name/pid and fault address. Exit unregisters.

State and persistence: ftrace ops only while module is loaded.

Dependencies and integration: depends on memory-management symbol visibility and ftrace direct support.

Risks: page fault paths are hot and sensitive. Trampoline argument preservation must match each architecture’s ABI exactly.

Test signals: load and cause page faults; inspect trace output for process and address lines; unload without lingering ftrace filter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/ftrace/ftrace-direct-too.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/ftrace/ftrace-direct.c -->
# sources/distributed-fs/ceph-client/samples/ftrace/ftrace-direct.c

Purpose: minimal ftrace direct-call sample for `wake_up_process`.

Important APIs/functions: `my_direct_func(struct task_struct *p)`, architecture-specific `my_tramp`, `ftrace_set_filter_ip`, `register_ftrace_direct`, and `unregister_ftrace_direct`.

Control flow: init filters `wake_up_process` and registers the trampoline; the direct function logs the woken task’s command and pid. Exit unregisters the trampoline.

State and persistence: single global `ftrace_ops` while loaded.

Dependencies and integration: ftrace direct and architecture trampoline support.

Risks: wakeup paths are frequent; logging can cause overhead. Architecture assembly must preserve calling context.

Test signals: load, trigger task wakeups, inspect trace buffer for task names, unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/ftrace/ftrace-direct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/ftrace/ftrace-ops.c -->
# sources/distributed-fs/ceph-client/samples/ftrace/ftrace-ops.c

Purpose: self-test style module showing custom `ftrace_ops` registration, filter setup, optional register saving, recursion/RCU assist flags, and hit-count validation.

Important APIs/functions: module params `nr_function_calls`, `nr_ops_relevant`, `nr_ops_irrelevant`, `save_regs`, `assist_recursion`, `assist_rcu`, `check_count`, and `persist`; `struct ftrace_ops`; `ftrace_set_filter_ip`; `register_ftrace_function`; `unregister_ftrace_function`; local `tracee_relevant` and `tracee_irrelevant`.

Control flow: init allocates arrays of relevant and irrelevant ops, configures each with filter IP and flags, registers them, calls tracee functions repeatedly, optionally verifies hit counts, and unregisters unless `persist` is requested. Exit unregisters/destroys persistent ops.

State and persistence: allocated `sample_ops` arrays and per-op call counters. Persist mode intentionally leaves registrations active until module exit.

Dependencies and integration: integrates with core ftrace callback API, not direct trampolines.

Risks: bad parameter values can allocate many ops and create tracing overhead. `persist` changes lifecycle. Count checks can fail if callbacks are missed or tracing semantics change.

Test signals: load with small counts and `check_count=1`, verify success or expected warnings; try `save_regs`, `assist_recursion`, and `persist` combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/ftrace/ftrace-ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/ftrace/sample-trace-array.c -->
# sources/distributed-fs/ceph-client/samples/ftrace/sample-trace-array.c

Purpose: sample module showing kernel access to a named ftrace instance (`trace_array`) and custom trace events.

Important APIs/functions: `trace_array_get_by_name`, `trace_array_put`, `trace_array_set_clr_event`, `trace_array_printk`, `trace_array_init_printk`, `DECLARE_WORK`, `DEFINE_TIMER`, `kthread_run`, and tracepoints from `sample-trace-array.h`.

Control flow: init gets/creates a trace instance, enables the sample event, initializes trace-array printk, starts a periodic timer and worker/thread activity. The worker writes trace-array printk messages; the kthread emits custom trace events in a loop. Exit stops the thread, deletes the timer, disables the event, and puts the trace array.

State and persistence: global `struct trace_array *tr`, timer, work item, and thread. Trace buffer contents persist in the tracing instance until cleared or removed by tracing infrastructure.

Dependencies and integration: depends on ftrace instances, trace events, and local header definitions.

Risks: trace instance lifetime must be balanced. Timers/work must be stopped before releasing `tr`. Trace output can be noisy.

Test signals: load module, inspect `/sys/kernel/tracing/instances/sample-instance`, check event records and trace_printk output, unload and verify event disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/ftrace/sample-trace-array.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/ftrace/sample-trace-array.h -->
# sources/distributed-fs/ceph-client/samples/ftrace/sample-trace-array.h

Purpose: trace event header for `sample-trace-array.c`.

Important APIs/functions: uses Linux tracepoint macros including `TRACE_SYSTEM`, include guard pattern, `TRACE_EVENT`, `TP_PROTO`, `TP_ARGS`, `TP_STRUCT__entry`, `TP_fast_assign`, `TP_printk`, and `include/trace/define_trace.h`.

Control flow: compile-time macro expansion defines the sample event class and generated trace functions.

State and persistence: no runtime state in the header; generated tracepoint state is owned by tracing infrastructure.

Dependencies and integration: included with `CREATE_TRACE_POINTS` in the C file and must stay in include path via the Makefile.

Risks: tracepoint field layout is ABI-like for readers; changing names/types breaks consumers. Include guard and `TRACE_INCLUDE_FILE/PATH` must match file location.

Test signals: successful compile generates the trace event; runtime event appears under tracing events for the sample system.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/ftrace/sample-trace-array.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hid/Makefile -->
# sources/distributed-fs/ceph-client/samples/hid/Makefile

Purpose: complex kbuild/userspace build file for HID-BPF samples and skeleton generation.

Important APIs/functions: builds `hid_mouse` and `hid_surface_dial`; builds libbpf and bootstrap bpftool under sample-local output directories; generates `vmlinux.h`, BPF objects, linked BPF skeleton headers, and user objects. Probes LLVM/BTF capabilities and adds architecture-specific flags.

Control flow: kbuild invokes libbpf/bpftool prerequisites, validates LLVM BPF target, emits BPF bytecode with clang/opt/llc, generates skeletons with bpftool, then links user programs with libbpf, elf, and zlib.

State and persistence: generated build artifacts under the sample object tree, `libbpf/`, `bpftool/`, `vmlinux.h`, `.bpf.o`, `.skel.h`, and user binaries.

Dependencies and integration: depends on kernel BTF or `VMLINUX_H`, LLVM BPF backend, bpftool, libbpf, libelf, zlib, and architecture include quirks.

Risks: fragile toolchain detection, generated artifact cleanup requirements, and cross-compile include issues. Build reaches into kernel tools and selftests include paths.

Test signals: `make samples/hid/` should build skeletons and two user programs; missing BTF or LLVM target should fail with explicit errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hid/hid_bpf_helpers.h -->
# sources/distributed-fs/ceph-client/samples/hid/hid_bpf_helpers.h

Purpose: declares HID-BPF kfuncs used by sample BPF programs.

Important APIs/functions: extern `__ksym` declarations for `hid_bpf_get_data`, `hid_bpf_attach_prog`, `hid_bpf_allocate_context`, `hid_bpf_release_context`, and `hid_bpf_hw_request`.

Control flow: header-only; BPF verifier/libbpf resolves kfunc symbols at load time.

State and persistence: none.

Dependencies and integration: included by `.bpf.c` files after `vmlinux.h` and BPF helper headers.

Risks: declarations must match kernel kfunc signatures exactly or BPF load will fail.

Test signals: BPF programs using this header should compile and load on kernels with HID-BPF kfunc support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hid/hid_bpf_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hid/hid_mouse.bpf.c -->
# sources/distributed-fs/ceph-client/samples/hid/hid_mouse.bpf.c

Purpose: HID-BPF struct-ops program that swaps and inverts mouse X/Y behavior and patches the report descriptor.

Important APIs/functions: `hid_bpf_get_data`, `BPF_PROG(hid_event)`, helper functions `hid_y_event` and `hid_x_event`, `BPF_PROG(hid_rdesc_fixup)`, and `struct hid_bpf_ops mouse_invert` in `.struct_ops.link`.

Control flow: device events fetch nine report bytes, negate Y and X 16-bit values, and write them back. Descriptor fixup fetches descriptor bytes and swaps usage bytes at fixed offsets for X and Y.

State and persistence: no maps or durable state; mutations affect in-flight reports and the attached HID device while the struct-ops link is active.

Dependencies and integration: loaded by `hid_mouse.c` skeleton and attached to a specific HID device ID.

Risks: assumes a particular report format and descriptor offsets; on other devices it can corrupt input interpretation. Fixed-size data access must pass verifier bounds checks.

Test signals: attach to the intended Etekcity mouse, inspect `bpf_printk` output, and confirm axes are swapped/inverted; detach by stopping loader.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hid/hid_mouse.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hid/hid_mouse.c -->
# sources/distributed-fs/ceph-client/samples/hid/hid_mouse.c

Purpose: user-space libbpf loader for the HID mouse BPF sample.

Important APIs/functions: generated `hid_mouse.skel.h`, `hid_mouse__open`, `hid_mouse__load`, `bpf_map__attach_struct_ops`, `hid_mouse__destroy`, `get_hid_id`, signal handlers, and sysfs `uevent` probing.

Control flow: validates a HID sysfs path, extracts the HID numeric ID from the device directory name, sets `skel->struct_ops.mouse_invert->hid_id`, loads the BPF object, attaches struct ops, then sleeps until signal.

State and persistence: process holds the BPF link while running; no persistent files.

Dependencies and integration: requires libbpf, generated skeleton, and a HID device path such as `/sys/bus/hid/devices/...`.

Risks: `basename((char *)path)` mutates/uses argv storage and assumes a fixed HID name length. The program exits from signal handler without explicit link cleanup beyond process teardown.

Test signals: run with a target HID path, confirm load/attach succeeds, move the device, then Ctrl-C and confirm behavior returns to normal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hid/hid_mouse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hid/hid_surface_dial.bpf.c -->
# sources/distributed-fs/ceph-client/samples/hid/hid_surface_dial.bpf.c

Purpose: HID-BPF program that morphs a Microsoft Surface Dial into mouse-like wheel/button behavior and optionally configures haptic feedback.

Important APIs/functions: HID event struct-op clears touch/X/Y fields; syscall program `set_haptic` uses `hid_bpf_allocate_context`, `hid_bpf_hw_request`, and `hid_bpf_release_context`; descriptor fixup changes HID usages, resolution multiplier, physical resolution, and relative flags.

Control flow: on events, report bytes are edited in place. On loader-triggered test-run syscall, feature report 1 is read, haptic auto-trigger is set or cleared based on resolution, then written back. Descriptor fixup rewrites fixed offsets for touch/button, dial/wheel, resolution, and X/Y relative mode.

State and persistence: global BPF data variables `resolution`, `physical`, and `haptic_data`; attached struct ops alter the device while active.

Dependencies and integration: loaded by `hid_surface_dial.c`, which sets data variables and calls the syscall program using `bpf_prog_test_run_opts`.

Risks: fixed descriptor offsets are device-specific. Feature report manipulation can misconfigure unsupported devices. Static `haptic_data` is shared BPF global state.

Test signals: attach to Surface Dial, vary `-r`, observe wheel events and haptic behavior, and inspect BPF printk logs for feature request results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hid/hid_surface_dial.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hid/hid_surface_dial.c -->
# sources/distributed-fs/ceph-client/samples/hid/hid_surface_dial.c

Purpose: user-space libbpf loader and controller for the Surface Dial HID-BPF sample.

Important APIs/functions: generated `hid_surface_dial.skel.h`, `hid_surface_dial__open/load/destroy`, `bpf_map__attach_struct_ops`, `bpf_prog_test_run_opts`, and data variable assignment for `resolution` and `physical`.

Control flow: parses optional `-r`, extracts HID ID from sysfs path, sets struct-ops HID ID, loads BPF, writes BPF globals, attaches struct ops, calls `set_haptic`, and waits until signal.

State and persistence: active BPF link and configured BPF globals while the process is alive.

Dependencies and integration: requires libbpf, generated skeleton, HID-BPF kernel support, and Surface Dial-style report layout.

Risks: `physical = resolution / 72` can be zero for low values. `set_haptic` errors are printed but main continues into wait loop. Fixed path parsing assumes the HID directory naming scheme.

Test signals: run with Surface Dial sysfs path and `-r 72` or `-r 3600`, confirm attach and haptic setting, then interrupt and verify detachment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hid/hid_surface_dial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hidraw/Makefile -->
# sources/distributed-fs/ceph-client/samples/hidraw/Makefile

Purpose: builds the hidraw user-space example.

Important APIs/functions: `userprogs-always-y += hid-example`; includes exported UAPI headers.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: depends on hidraw UAPI headers.

Risks: runtime device compatibility is not represented in the build.

Test signals: samples build should produce `hid-example`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hidraw/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hidraw/hid-example.c -->
# sources/distributed-fs/ceph-client/samples/hidraw/hid-example.c

Purpose: user-space hidraw API example that queries descriptors/device info and performs feature/input/output report operations.

Important APIs/functions: `open` on `/dev/hidraw0` or argv path, ioctls `HIDIOCGRDESCSIZE`, `HIDIOCGRDESC`, `HIDIOCGRAWNAME`, `HIDIOCGRAWPHYS`, `HIDIOCGRAWINFO`, `HIDIOCSFEATURE`, `HIDIOCGFEATURE`, plus `read` and `write`.

Control flow: opens device nonblocking, prints report descriptor, name, physical path, bus/vendor/product info, sends and reads feature report 9, writes report 1, attempts a nonblocking read, and closes.

State and persistence: local buffers only; feature/output reports may affect the device.

Dependencies and integration: integrates with `/dev/hidraw*` and Linux input bus constants.

Risks: hard-coded report IDs and payloads are not safe for arbitrary HID devices. Nonblocking read may fail with `EAGAIN`. Fallback ioctl macros support older headers.

Test signals: run against a known hidraw device and compare descriptor/info output with `udevadm` or sysfs; verify expected feature report behavior for that device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hidraw/hid-example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hung_task/Makefile -->
# sources/distributed-fs/ceph-client/samples/hung_task/Makefile

Purpose: builds the hung task sample module.

Important APIs/functions: maps `CONFIG_SAMPLE_HUNG_TASK` to `hung_task_tests.o`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: depends on sample Kconfig and debugfs APIs used by the module.

Risks: none in the Makefile; module is intentionally disruptive at runtime.

Test signals: enabling `CONFIG_SAMPLE_HUNG_TASK` builds `hung_task_tests.ko`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hung_task/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hung_task/hung_task_tests.c -->
# sources/distributed-fs/ceph-client/samples/hung_task/hung_task_tests.c

Purpose: debugfs sample for provoking hung-task diagnostics using mutex, semaphore, and rwsem contention.

Important APIs/functions: `debugfs_create_dir`, `debugfs_create_file`, `debugfs_remove_recursive`, `DEFINE_MUTEX`, `DEFINE_SEMAPHORE`, `DECLARE_RWSEM`, `guard(mutex)`, `down/up`, `down_read/up_read`, `down_write/up_write`, `msleep_interruptible`, and `simple_read_from_buffer`.

Control flow: init creates `/sys/kernel/debug/hung_task/` files. Reading each file acquires the corresponding lock, sleeps for 256 seconds, and returns dummy data. Multiple readers create lock wait scenarios for hung task reports. Exit removes debugfs entries.

State and persistence: static locks and debugfs dentries while loaded.

Dependencies and integration: debugfs and hung task detector configuration.

Risks: explicitly can freeze or panic test systems depending on hung task settings. Long sleeps under locks are deliberate and should not run on production systems.

Test signals: load in a test VM, read a debugfs file from two processes, and verify hung-task output references the tested lock class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hung_task/hung_task_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hw_breakpoint/Makefile -->
# sources/distributed-fs/ceph-client/samples/hw_breakpoint/Makefile

Purpose: builds the hardware breakpoint sample module.

Important APIs/functions: maps `CONFIG_SAMPLE_HW_BREAKPOINT` to `data_breakpoint.o`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: depends on perf hardware breakpoint support.

Risks: none in build file.

Test signals: enabling `CONFIG_SAMPLE_HW_BREAKPOINT` should compile the sample.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hw_breakpoint/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hw_breakpoint/data_breakpoint.c -->
# sources/distributed-fs/ceph-client/samples/hw_breakpoint/data_breakpoint.c

Purpose: kernel module that installs a write hardware breakpoint on a named kernel symbol, defaulting to `jiffies`.

Important APIs/functions: `module_param_string(ksym, ...)`, `__symbol_get`, `__symbol_put`, `hw_breakpoint_init`, `register_wide_hw_breakpoint`, `unregister_wide_hw_breakpoint`, and `sample_hbp_handler`.

Control flow: init resolves the symbol address, initializes a `perf_event_attr` for 4-byte write watchpoint, registers per-CPU breakpoints, and logs installation. Handler prints that the symbol changed and dumps stack. Exit unregisters and releases the symbol.

State and persistence: global per-CPU `perf_event` pointer and held symbol reference while loaded.

Dependencies and integration: perf hardware breakpoints, kallsyms/exported symbol resolution, architecture breakpoint support.

Risks: default `jiffies` changes frequently and can produce heavy stack dumps. Breakpoint length is fixed at four bytes and may not match all symbol types. `__symbol_get` only works for exported symbols.

Test signals: load with a low-frequency writable exported symbol, write or wait for changes, inspect handler stack dumps, and unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/hw_breakpoint/data_breakpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kdb/Makefile -->
# sources/distributed-fs/ceph-client/samples/kdb/Makefile

Purpose: builds the KDB hello command sample.

Important APIs/functions: maps `CONFIG_SAMPLE_KDB` to `kdb_hello.o`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: depends on KDB support.

Risks: none in Makefile.

Test signals: enabling `CONFIG_SAMPLE_KDB` compiles the module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kdb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kdb/kdb_hello.c -->
# sources/distributed-fs/ceph-client/samples/kdb/kdb_hello.c

Purpose: registers a simple dynamic KDB command named `hello`.

Important APIs/functions: `kdbtab_t`, `kdb_register`, `kdb_unregister`, `kdb_printf`, and `KDB_ARGCOUNT`.

Control flow: init registers the command. The command prints `Hello world!` or a provided string, though the argument-count condition appears inconsistent because `argc > 1` rejects the documented optional string. Exit unregisters the command.

State and persistence: KDB command table entry while loaded.

Dependencies and integration: requires KDB debugger support and module loading.

Risks: sample command logic may reject one-argument usage depending on KDB `argc` semantics. KDB is a privileged debugger interface.

Test signals: load module, enter KDB, run `hello` and `hello name`, verify output or argument-count behavior, then unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kdb/kdb_hello.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kfifo/Makefile -->
# sources/distributed-fs/ceph-client/samples/kfifo/Makefile

Purpose: builds four kfifo sample modules.

Important APIs/functions: maps `CONFIG_SAMPLE_KFIFO` to `bytestream-example.o`, `dma-example.o`, `inttype-example.o`, and `record-example.o`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: kfifo APIs and procfs/scatterlist APIs used by modules.

Risks: all samples are selected together.

Test signals: enabling `CONFIG_SAMPLE_KFIFO` builds all four objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kfifo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kfifo/bytestream-example.c -->
# sources/distributed-fs/ceph-client/samples/kfifo/bytestream-example.c

Purpose: demonstrates byte-stream `kfifo` operations and procfs read/write integration.

Important APIs/functions: `DECLARE_KFIFO` or `kfifo_alloc`, `INIT_KFIFO`, `kfifo_in`, `kfifo_out`, `kfifo_put`, `kfifo_get`, `kfifo_skip`, `kfifo_peek`, `kfifo_from_user`, `kfifo_to_user`, `proc_create`, and `remove_proc_entry`.

Control flow: init initializes the fifo, runs `testfunc` to exercise expected wraparound values, then creates `/proc/bytestream-fifo`. Proc reads/writes move bytes between user buffers and fifo under separate read/write mutexes. Exit removes proc entry and frees dynamic fifo if enabled.

State and persistence: static or allocated FIFO contents and proc entry while loaded.

Dependencies and integration: procfs and kfifo library.

Risks: separate read and write mutexes do not serialize simultaneous read/write against each other; this is a sample, not a full driver queue. Test failure aborts module load.

Test signals: load module, verify "test passed" in logs, write/read `/proc/bytestream-fifo`, and unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kfifo/bytestream-example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kfifo/dma-example.c -->
# sources/distributed-fs/ceph-client/samples/kfifo/dma-example.c

Purpose: demonstrates preparing kfifo memory as scatterlists for DMA-like receive and transmit operations.

Important APIs/functions: `kfifo_alloc`, `kfifo_in`, `kfifo_put`, `kfifo_skip`, `kfifo_dma_in_prepare`, `kfifo_dma_in_finish`, `kfifo_dma_out_prepare`, `kfifo_dma_out_finish`, `sg_init_table`, and `sg_page`.

Control flow: init allocates a byte fifo, seeds data, prepares scatterlist entries for free receive space, simulates receiving zero bytes, prepares transmit entries for eight bytes, simulates transmitting five bytes, checks remaining length is seven, and exits. Module exit frees the fifo.

State and persistence: allocated fifo until module unload.

Dependencies and integration: kfifo DMA helpers and scatterlist API; no actual DMA engine is used.

Risks: early error paths after allocation can return without freeing fifo because this is a compact sample. Real drivers must map/unmap DMA and handle partial completion carefully.

Test signals: module load logs scatterlist layout and "test passed"; unload frees fifo.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kfifo/dma-example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kfifo/inttype-example.c -->
# sources/distributed-fs/ceph-client/samples/kfifo/inttype-example.c

Purpose: demonstrates typed `kfifo` storing `int` elements and exposing it through procfs.

Important APIs/functions: `DEFINE_KFIFO` or `DECLARE_KFIFO_PTR`, typed `kfifo_put/get/in/out/peek/skip`, `kfifo_from_user`, `kfifo_to_user`, procfs operations, and mutexes.

Control flow: init initializes the FIFO, runs a wraparound correctness test using expected integer values, and creates `/proc/int-fifo`. Proc operations copy raw integer-sized FIFO data to/from user buffers. Exit removes the proc entry and frees dynamic allocation if used.

State and persistence: FIFO contents remain in kernel memory while module is loaded.

Dependencies and integration: kfifo typed API and procfs.

Risks: user-space reads/writes raw integer bytes, so ABI is host-endian and not self-describing. Separate read/write mutexes do not fully serialize producers and consumers.

Test signals: load and check "test passed"; write binary integer data to `/proc/int-fifo` and read it back.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kfifo/inttype-example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kfifo/record-example.c -->
# sources/distributed-fs/ceph-client/samples/kfifo/record-example.c

Purpose: demonstrates record-oriented kfifo usage with variable-length records and procfs integration.

Important APIs/functions: `struct kfifo_rec_ptr_1` or `STRUCT_KFIFO_REC_1`, `kfifo_in`, `kfifo_out`, `kfifo_peek_len`, `kfifo_skip`, `kfifo_from_user`, `kfifo_to_user`, and procfs operations.

Control flow: init allocates/initializes the record fifo, inserts several strings, exercises record peek/skip/out behavior against expected values, then creates `/proc/record-fifo`. Reads return complete records up to buffer limits; writes enqueue user-provided records. Exit removes proc entry and frees allocation.

State and persistence: record fifo contents in kernel memory while loaded.

Dependencies and integration: kfifo record API and procfs.

Risks: record size header is one byte in this sample, limiting record length. Procfs users must handle record boundaries. Error paths are sample-grade.

Test signals: module load should pass the built-in expected-result test; procfs reads should preserve record boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kfifo/record-example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kmemleak/Makefile -->
# sources/distributed-fs/ceph-client/samples/kmemleak/Makefile

Purpose: builds the kmemleak test sample.

Important APIs/functions: maps `CONFIG_SAMPLE_KMEMLEAK` to `kmemleak-test.o`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: depends on kmemleak sample config.

Risks: none in Makefile; runtime intentionally creates leaks.

Test signals: enabling the config builds `kmemleak-test.ko`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kmemleak/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kmemleak/kmemleak-test.c -->
# sources/distributed-fs/ceph-client/samples/kmemleak/kmemleak-test.c

Purpose: intentionally allocates different kinds of memory to exercise kmemleak leak detection.

Important APIs/functions: uses `kmalloc`, `vmalloc`, optional `kmem_cache_alloc(files_cachep)` when modules are disabled, `kzalloc`, `list_add_tail`, per-CPU storage via `DEFINE_PER_CPU`, `__alloc_percpu`, and module init/exit.

Control flow: init logs several orphan `kmalloc` and `vmalloc` allocations, builds a list of allocated `test_node` objects that remain reachable while loaded, allocates one pointer per possible CPU, and allocates an anonymous percpu block. Exit removes list nodes from `test_list` without freeing them so they become kmemleak candidates after module removal.

State and persistence: leaked allocations persist after load for kmemleak to discover. List-linked objects are intentionally reachable until exit unlinks them; per-CPU pointers keep their allocations reachable from per-CPU storage.

Dependencies and integration: depends on `CONFIG_DEBUG_KMEMLEAK` for meaningful runtime behavior.

Risks: intentionally leaks memory and should only be used in test kernels. Results depend on scan timing, module removal, percpu root scanning, and kmemleak configuration.

Test signals: load module, trigger `/sys/kernel/debug/kmemleak` scans, compare reported orphan allocations, unload to make list nodes unreachable, and scan again.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kmemleak/kmemleak-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kobject/Makefile -->
# sources/distributed-fs/ceph-client/samples/kobject/Makefile

Purpose: builds kobject and kset sample modules.

Important APIs/functions: maps `CONFIG_SAMPLE_KOBJECT` to `kobject-example.o` and `kset-example.o`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: kobject/sysfs support.

Risks: both examples are built together when selected.

Test signals: enabling `CONFIG_SAMPLE_KOBJECT` compiles both modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kobject/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kobject/kobject-example.c -->
# sources/distributed-fs/ceph-client/samples/kobject/kobject-example.c

Purpose: minimal kobject/sysfs example exposing three integer attributes under `/sys/kernel/kobject_example`.

Important APIs/functions: `kobject_create_and_add`, `sysfs_create_group`, `kobject_put`, `struct kobj_attribute`, `__ATTR`, `kstrtoint`, and show/store callbacks for `foo`, `baz`, and `bar`.

Control flow: init creates the kobject under `kernel_kobj`, creates one attribute group, and unwinds on failure. Attribute stores parse decimal integers into globals; show emits values. Exit puts the kobject.

State and persistence: global integers exist while module is loaded; sysfs files expose them. No persistence across unload.

Dependencies and integration: sysfs and kernel kobject infrastructure.

Risks: no locking around integer attributes, acceptable for sample but not robust shared state. Permissions allow writable attributes for root.

Test signals: load, read/write `/sys/kernel/kobject_example/{foo,baz,bar}`, check values, unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kobject/kobject-example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kobject/kset-example.c -->
# sources/distributed-fs/ceph-client/samples/kobject/kset-example.c

Purpose: demonstrates custom kobject type, attributes, release method, default groups, visibility callback, and kset membership.

Important APIs/functions: `struct foo_obj`, `struct foo_attribute`, `sysfs_ops`, `kobj_type`, `kset_create_and_add`, `kobject_init_and_add`, `kobject_uevent`, `kobject_put`, `__ATTR`, `ATTRIBUTE_GROUPS`, and per-object show/store callbacks.

Control flow: init creates a kset and three objects (`foo`, `bar`, `baz`). Each object has default attributes and sends an add uevent. Attribute callbacks access per-object integers. Exit puts each object and unregisters the kset; release callbacks free object memory.

State and persistence: per-object integer fields under sysfs while loaded.

Dependencies and integration: sysfs, kobjects, ksets, and uevent infrastructure.

Risks: attributes are sample-level and unlocked. Visibility callback changes mode for one attribute and must stay consistent with default groups. Correct release callback is critical for memory lifetime.

Test signals: load and inspect `/sys/kernel/kset_example/`, read/write object attributes, observe uevents, unload and verify release logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kobject/kset-example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kprobes/Makefile -->
# sources/distributed-fs/ceph-client/samples/kprobes/Makefile

Purpose: builds kprobe and kretprobe sample modules.

Important APIs/functions: maps `CONFIG_SAMPLE_KPROBES` to `kprobe_example.o` and `CONFIG_SAMPLE_KRETPROBES` to `kretprobe_example.o`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: Kprobes/Kretprobes kernel support.

Risks: none in build file.

Test signals: enabling each config compiles its sample module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kprobes/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kprobes/kprobe_example.c -->
# sources/distributed-fs/ceph-client/samples/kprobes/kprobe_example.c

Purpose: kprobe sample that instruments a configurable kernel symbol, defaulting to `kernel_clone`.

Important APIs/functions: `struct kprobe`, `register_kprobe`, `unregister_kprobe`, `pre_handler`, `post_handler`, `NOKPROBE_SYMBOL`, and arch-specific `pt_regs` field logging.

Control flow: init sets pre/post handlers and registers the probe. On hit, pre-handler logs symbol address and instruction pointer/status fields for the current architecture; post-handler logs flags/status. Exit unregisters.

State and persistence: global probe and module parameter `symbol`.

Dependencies and integration: kprobes, kallsyms, and architecture-specific register layouts.

Risks: probing hot or unsafe symbols can destabilize or flood logs. Handler code must be marked `NOKPROBE_SYMBOL` to avoid recursive probing.

Test signals: load with default or `symbol=<name>`, exercise the symbol, inspect logs, unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kprobes/kprobe_example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kprobes/kretprobe_example.c -->
# sources/distributed-fs/ceph-client/samples/kprobes/kretprobe_example.c

Purpose: kretprobe sample that measures return value and duration of a configurable function, defaulting to `kernel_clone`.

Important APIs/functions: `struct kretprobe`, `struct kretprobe_instance`, `register_kretprobe`, `unregister_kretprobe`, `regs_return_value`, `ktime_get`, `ktime_sub`, and per-instance `data_size`.

Control flow: init assigns target symbol and registers a kretprobe with entry and return handlers. Entry skips kernel threads, timestamps user-process calls, and return handler logs return value and elapsed nanoseconds. Exit unregisters and reports missed instances.

State and persistence: global kretprobe and per-active-instance timestamp data.

Dependencies and integration: kretprobe support and function return instrumentation.

Risks: `maxactive=20` may be too low for high-concurrency symbols; missed probes are reported on exit. Probing hot functions adds overhead.

Test signals: load with `func=kernel_clone`, fork processes, inspect duration logs and `nmissed` on unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/kprobes/kretprobe_example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/landlock/Makefile -->
# sources/distributed-fs/ceph-client/samples/landlock/Makefile

Purpose: builds the Landlock sandboxer user program and provides convenience `all`/`clean` targets.

Important APIs/functions: `userprogs-always-y := sandboxer`, exported UAPI include path, recursive `make -C ../.. samples/landlock/`, and clean target.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: Linux Landlock UAPI headers and kbuild sample user program support.

Risks: BSD-3-Clause SPDX differs from GPL-heavy samples, matching the source file.

Test signals: `make samples/landlock/` should produce `sandboxer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/landlock/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/landlock/sandboxer.c -->
# sources/distributed-fs/ceph-client/samples/landlock/sandboxer.c

Purpose: user-space Landlock sandbox launcher that restricts filesystem, TCP bind/connect, abstract Unix socket, and signal access before executing a command.

Important APIs/functions: syscall wrappers for `landlock_create_ruleset`, `landlock_add_rule`, and `landlock_restrict_self`; `populate_ruleset_fs`, `populate_ruleset_net`, `check_ruleset_scope`, `prctl(PR_SET_NO_NEW_PRIVS)`, and `execvpe`.

Control flow: main checks ABI version, masks unsupported access rights for older Landlock ABIs up to version 9, reads environment variables (`LL_FS_RO`, `LL_FS_RW`, `LL_TCP_BIND`, `LL_TCP_CONNECT`, `LL_SCOPED`, `LL_FORCE_LOG`), creates a ruleset, adds path and port rules, sets no-new-privs, restricts self, closes the ruleset, and executes the target command.

State and persistence: environment variables are consumed/unset before exec; ruleset applies to the process and descendants. No files are persisted.

Dependencies and integration: Landlock LSM enabled in the kernel, UAPI headers, normal Unix path and port semantics.

Risks: missing mandatory filesystem env vars aborts. If execute/interpreter/library paths are not allowed, `execvpe` fails. ABI downgrade behavior intentionally removes unsupported rights, which can be more restrictive for older kernels.

Test signals: run with read/write path env vars and a shell command, verify allowed paths work and denied paths fail; test optional TCP and scoped restrictions on kernels supporting those ABIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/landlock/sandboxer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/livepatch/Makefile -->
# sources/distributed-fs/ceph-client/samples/livepatch/Makefile

Purpose: builds livepatch demonstration modules and their support modules.

Important APIs/functions: maps `CONFIG_SAMPLE_LIVEPATCH` to `livepatch-sample.o`, shadow-variable demo modules, and callback demo modules.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: livepatch infrastructure.

Risks: all livepatch samples are selected together and must match target symbol names in their companion modules/kernel.

Test signals: enabling `CONFIG_SAMPLE_LIVEPATCH` builds all listed modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/livepatch/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/livepatch/livepatch-callbacks-busymod.c -->
# sources/distributed-fs/ceph-client/samples/livepatch/livepatch-callbacks-busymod.c

Purpose: support module for livepatch callback demonstrations; provides a delayed-work function that can be patched and can intentionally stall transitions.

Important APIs/functions: module parameter `sleep_secs`, `DECLARE_DELAYED_WORK`, `schedule_delayed_work`, `cancel_delayed_work_sync`, `msleep`, and `busymod_work_func`.

Control flow: init schedules work immediately. The work function logs, sleeps for the configured seconds, and exits. Exit cancels the delayed work synchronously.

State and persistence: global delayed work and parameter while loaded.

Dependencies and integration: livepatch callback demo targets `busymod_work_func` in this module.

Risks: long `sleep_secs` deliberately parks execution in a patch target and can stall livepatch transitions.

Test signals: load with `sleep_secs=30`, load `livepatch-callbacks-demo.ko`, and observe callback/transition behavior in logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/livepatch/livepatch-callbacks-busymod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/livepatch/livepatch-callbacks-demo.c -->
# sources/distributed-fs/ceph-client/samples/livepatch/livepatch-callbacks-demo.c

Purpose: livepatch sample demonstrating pre/post patch and unpatch callbacks for vmlinux and module objects.

Important APIs/functions: `struct klp_patch`, `struct klp_object`, `struct klp_func`, callbacks `.pre_patch`, `.post_patch`, `.pre_unpatch`, `.post_unpatch`, `klp_enable_patch`, `MODULE_INFO(livepatch, "Y")`, and module parameter `pre_patch_ret`.

Control flow: init enables a patch containing callback-only objects for vmlinux and `livepatch_callbacks_mod`, plus a patch for `livepatch_callbacks_busymod:busymod_work_func`. Callback helpers log object/module state and `pre_patch_ret` can force failure. Exit does nothing; disabling is controlled through livepatch sysfs.

State and persistence: registered livepatch remains managed by livepatch core until disabled/removed.

Dependencies and integration: targets support modules by name and demonstrates livepatch sysfs enable/disable behavior.

Risks: nonzero pre-patch return can reject module loading/patching. Target symbol names must match. Empty module exit is standard for livepatch but surprises ordinary module expectations.

Test signals: follow source usage comments, vary load order and `pre_patch_ret`, and watch callback order/state logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/livepatch/livepatch-callbacks-demo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/livepatch/livepatch-callbacks-mod.c -->
# sources/distributed-fs/ceph-client/samples/livepatch/livepatch-callbacks-mod.c

Purpose: simple support module for livepatch callback demos.

Important APIs/functions: basic `module_init`/`module_exit` with `pr_info` logging.

Control flow: init and exit only log function names. It exists as a named module object for `livepatch-callbacks-demo.c`.

State and persistence: module loaded/unloaded state only.

Dependencies and integration: target module name is referenced by the livepatch callback demo.

Risks: none beyond load-order interactions intentionally shown by the demo.

Test signals: load before or after the livepatch demo and observe callback logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/livepatch/livepatch-callbacks-mod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/livepatch/livepatch-sample.c -->
# sources/distributed-fs/ceph-client/samples/livepatch/livepatch-sample.c

Purpose: minimal kernel livepatch that replaces `/proc/cmdline` display function.

Important APIs/functions: replacement `livepatch_cmdline_proc_show`, `struct klp_func` targeting `cmdline_proc_show`, vmlinux `struct klp_object`, `struct klp_patch`, `klp_enable_patch`, and `MODULE_INFO(livepatch, "Y")`.

Control flow: init enables the patch; after transition, reads of `/proc/cmdline` call the replacement and print a fixed string. Exit is empty; the patch must be disabled via livepatch sysfs before removal.

State and persistence: livepatch core state and sysfs `enabled` flag while module exists.

Dependencies and integration: depends on target symbol name and livepatch infrastructure.

Risks: symbol name changes break the sample. Empty exit requires users to disable through `/sys/kernel/livepatch/.../enabled`.

Test signals: compare `/proc/cmdline` before/after load, disable through sysfs, confirm original output returns, then remove module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/livepatch/livepatch-sample.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/livepatch/livepatch-shadow-fix1.c -->
# sources/distributed-fs/ceph-client/samples/livepatch/livepatch-shadow-fix1.c

Purpose: first livepatch fix for the shadow-variable demo, preventing a deliberate memory leak by attaching leaked pointers as shadow variables.

Important APIs/functions: `klp_shadow_alloc`, `klp_shadow_get`, `klp_shadow_free`, `klp_shadow_free_all`, `shadow_leak_ctor`, replacement `livepatch_fix1_dummy_alloc` and `livepatch_fix1_dummy_free`, and livepatch metadata targeting `livepatch_shadow_mod`.

Control flow: patched allocation creates dummy plus extra allocation, then stores the extra pointer in shadow variable `SV_LEAK`. Patched free retrieves and frees the shadow leak before freeing dummy. Exit frees remaining `SV_LEAK` variables.

State and persistence: shadow variables associated with dummy object addresses while objects exist.

Dependencies and integration: targets `dummy_alloc` and `dummy_free` symbols in `livepatch-shadow-mod.c`.

Risks: objects allocated before patch lack shadow variables and are reported as leaked. Constructor failure unwinds allocations. Shadow variable ID must not collide with other livepatches for the same objects.

Test signals: load buggy module, then fix1, watch logs for prevented leaks, disable/remove and verify shadow cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/livepatch/livepatch-shadow-fix1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/livepatch/livepatch-shadow-fix2.c -->
# sources/distributed-fs/ceph-client/samples/livepatch/livepatch-shadow-fix2.c

Purpose: second shadow-variable livepatch that extends in-flight dummy objects with a check counter while preserving leak cleanup.

Important APIs/functions: `klp_shadow_get_or_alloc`, `klp_shadow_get`, `klp_shadow_free`, `klp_shadow_free_all`, replacement `livepatch_fix2_dummy_check` and `livepatch_fix2_dummy_free`, shadow IDs `SV_LEAK` and `SV_COUNTER`.

Control flow: patched check allocates/increments a per-dummy counter and returns expiry status. Patched free releases any leak pointer and counter before freeing the dummy. Exit frees all remaining counters.

State and persistence: per-object shadow counters and leak pointers during object lifetime.

Dependencies and integration: targets `dummy_check` and `dummy_free` in `livepatch_shadow_mod`, often layered after fix1.

Risks: combining multiple livepatches requires compatible replacement semantics. `GFP_NOWAIT` counter allocation can fail, resulting in missing counts.

Test signals: load shadow module, fix1, then fix2; observe check counters printed at cleanup and no unbounded leaked allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/livepatch/livepatch-shadow-fix2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/livepatch/livepatch-shadow-mod.c -->
# sources/distributed-fs/ceph-client/samples/livepatch/livepatch-shadow-mod.c

Purpose: intentionally buggy support module for livepatch shadow-variable examples.

Important APIs/functions: `struct dummy`, `dummy_alloc`, `dummy_free`, `dummy_check`, global `dummy_list`, `DEFINE_MUTEX`, delayed works `alloc_dwork` and `cleanup_dwork`, `schedule_delayed_work`, `cancel_delayed_work_sync`, `list_add`, `list_for_each_entry_safe`, and `kfree`.

Control flow: init schedules periodic allocation and cleanup workers. Allocation creates dummy objects and an intentionally leaked extra allocation. Cleanup scans the list, removes expired dummies, and calls `dummy_free`. Exit cancels workers and frees remaining list entries.

State and persistence: in-memory list of dummy objects and periodic work state while loaded; intentional leak allocations persist unless livepatch fixes catch them.

Dependencies and integration: livepatch fix modules target its noinline functions by symbol name.

Risks: intentionally leaks memory before patches are applied. Workqueue and list cleanup must be synchronized on exit. Target functions must remain noinline/available for livepatching.

Test signals: load alone and observe leak behavior/logs; then load fix modules and observe leak prevention and counter extension.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/livepatch/livepatch-shadow-mod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/mei/Makefile -->
# sources/distributed-fs/ceph-client/samples/mei/Makefile

Purpose: builds the Intel MEI AMT version user-space sample.

Important APIs/functions: `userprogs-always-y += mei-amt-version`; includes exported UAPI headers.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: MEI UAPI headers and sample user build support.

Risks: runtime requires `/dev/mei*` and an AMT host interface client.

Test signals: samples build should produce `mei-amt-version`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/mei/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/mei/mei-amt-version.c -->
# sources/distributed-fs/ceph-client/samples/mei/mei-amt-version.c

Purpose: user-space sample that connects to Intel AMT over MEI and prints AMT code/BIOS version information.

Important APIs/functions: `struct mei`, `mei_init`, `mei_deinit`, `mei_recv_msg`, `mei_send_msg`, MEI ioctls such as client connect, AMT host interface message structs, `amt_verify_response_header`, `amt_verify_code_versions`, `amt_host_if_call`, and `amt_get_code_versions`.

Control flow: main opens a MEI device, connects to the AMT host interface GUID, builds a code-versions request, sends it, receives a response, verifies command/status/length, and prints BIOS plus firmware component versions.

State and persistence: file descriptor and dynamically allocated response/request buffers during process execution only.

Dependencies and integration: Intel MEI character device, AMT firmware client, kernel MEI UAPI, and endian/packing assumptions in host interface structures.

Risks: device or firmware may be absent, busy, or return partial messages. Header validation is critical to avoid trusting malformed firmware responses. Running may require permissions to access `/dev/mei*`.

Test signals: run on AMT-capable Intel hardware with MEI enabled; verify successful connect and version list output; test error handling on systems without MEI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/mei/mei-amt-version.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/nitro_enclaves/Makefile -->
# sources/distributed-fs/ceph-client/samples/nitro_enclaves/Makefile

Purpose: standalone Makefile for the Nitro Enclaves ioctl user-space sample.

Important APIs/functions: builds `ne_ioctl_sample` from `ne_ioctl_sample.c` with `$(CC)`, `-Wall`, and `-lpthread`; provides `clean`.

Control flow: build-only.

State and persistence: generated executable.

Dependencies and integration: pthreads, Nitro Enclaves UAPI headers, and local compiler.

Risks: unlike kbuild `userprogs`, this standalone target must be invoked in its directory or with suitable paths.

Test signals: `make` creates `ne_ioctl_sample`; `make clean` removes it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/nitro_enclaves/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/nitro_enclaves/ne_ioctl_sample.c -->
# sources/distributed-fs/ceph-client/samples/nitro_enclaves/ne_ioctl_sample.c

Purpose: comprehensive user-space sample for creating, loading, configuring, starting, and monitoring an AWS Nitro Enclave through `/dev/nitro_enclaves` ioctls.

Important APIs/functions: `NE_CREATE_VM`, enclave fd polling thread, memory allocation with hugepage-aligned regions, image loading into user memory regions, `NE_SET_USER_MEMORY_REGION`, `NE_ADD_VCPU`, `NE_START_ENCLAVE`, vsock heartbeat check, and pthread/poll/ioctl helpers.

Control flow: main parses enclave image and resource options, opens the NE device, creates a VM/enclave fd, starts a polling thread for enclave fd events, allocates user memory regions, loads the enclave image across regions, registers memory with the driver, adds vCPUs, starts the enclave, waits/checks for boot heartbeat over vsock, sleeps for demonstration lifetime, and frees resources.

State and persistence: process owns enclave fd, slot UID, allocated memory mappings, vCPU IDs, poll thread, and start info while running. Enclave lifetime is tied to descriptors and driver state.

Dependencies and integration: Nitro Enclaves kernel driver, `/dev/nitro_enclaves`, ioctl UAPI, pthreads, poll, mmap/madvise-like memory behavior, and vsock connectivity.

Risks: large memory allocation/registration can fail or exhaust host resources. Image loading must align region sizes and offsets. Enclave creation/start ioctls are privileged and hardware/platform-specific. Cleanup must handle partial setup to avoid leaked mappings or live enclave resources.

Test signals: compile on an EC2 Nitro Enclaves-capable instance, run with a valid EIF, verify create/load/start logs and heartbeat response, then confirm enclave fd poll events and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/nitro_enclaves/ne_ioctl_sample.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pfsm/Makefile -->
# sources/distributed-fs/ceph-client/samples/pfsm/Makefile

Purpose: builds the PFSM wakeup user-space sample.

Important APIs/functions: `userprogs-always-y += pfsm-wakeup`; includes exported UAPI headers.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: PFSM and RTC UAPI/device nodes at runtime.

Risks: runtime device paths are platform-specific.

Test signals: samples build should produce `pfsm-wakeup`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pfsm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pfsm/pfsm-wakeup.c -->
# sources/distributed-fs/ceph-client/samples/pfsm/pfsm-wakeup.c

Purpose: user-space power-fail safe mode wakeup sample coordinating RTC alarm and PFSM PMIC device wakeup setup.

Important APIs/functions: uses `/dev/rtc0`, PFSM device paths, `ioctl` on RTC/PFSM UAPI commands, `open`, `close`, time/alarm structures, and fixed `ALARM_DELTA_SEC`.

Control flow: opens RTC and PFSM PMIC devices, configures wakeup/alarm timing, arms PFSM-related wake behavior, and closes descriptors. It is a narrow platform demonstration for systems exposing the listed PMIC devices.

State and persistence: programs hardware/kernel device alarm state; no local files.

Dependencies and integration: RTC device, PFSM character devices, and platform PMIC topology.

Risks: hard-coded device nodes make it nonportable. Incorrect wake/alarm programming can affect platform power behavior.

Test signals: run on a supported PFSM platform, verify device opens/ioctls succeed, suspend/power event occurs, and wake happens around the configured alarm delta.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pfsm/pfsm-wakeup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pidfd/Makefile -->
# sources/distributed-fs/ceph-client/samples/pidfd/Makefile

Purpose: builds the pidfd metadata sample user program.

Important APIs/functions: `usertprogs-always-y += pidfd-metadata`; includes exported UAPI headers.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: pidfd-capable libc/kernel headers and sample user build support.

Risks: variable name `usertprogs-always-y` follows kernel samples conventions but is easy to confuse with `userprogs`.

Test signals: sample build should produce `pidfd-metadata`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pidfd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pidfd/pidfd-metadata.c -->
# sources/distributed-fs/ceph-client/samples/pidfd/pidfd-metadata.c

Purpose: demonstrates obtaining a pidfd with `CLONE_PIDFD` and safely opening metadata for the child through procfs.

Important APIs/functions: `clone` with `CLONE_PIDFD`, architecture-specific `__clone2` fallback for ia64, `pidfd_send_signal` syscall wrapper, `open` on `/proc/<pid>`, `openat(procfd, "status", ...)`, and `wait`.

Control flow: main creates a child that prints its pid and exits, receives a pidfd from `clone`, opens `/proc/<pid>` as a directory, verifies the pid has not been recycled by calling `pidfd_send_signal(pidfd, 0, NULL, 0)`, opens `status` relative to the proc directory fd, copies that status file to stdout, closes descriptors, and waits for the child.

State and persistence: child process, pidfd descriptor, proc directory fd, and status fd while the program runs.

Dependencies and integration: Linux pidfd syscalls, procfs fdinfo, clone semantics, and signal delivery.

Risks: syscall numbers and fallback definitions vary across architectures/libc versions. The child exits quickly, so the proc entry must be opened before reaping; the pidfd liveness check handles `EPERM` as a still-existing process.

Test signals: run on a pidfd-capable kernel, verify child pid output followed by `/proc/<pid>/status` content, and verify unsupported kernels report missing `CLONE_PIDFD`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pidfd/pidfd-metadata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pktgen/functions.sh -->
# sources/distributed-fs/ceph-client/samples/pktgen/functions.sh

Purpose: shared Bash library for pktgen sample scripts.

Important APIs/functions: logging helpers `err`, `warn`, `info`; pktgen control helpers `pg_ctrl`, `pg_thread`, `pg_set`, `proc_cmd`, legacy `pgset`; cleanup `trap_exit`; privilege helper `root_check_run_with_sudo`; NUMA/IRQ helpers `get_iface_node`, `get_iface_irqs`, `get_node_cpus`; address/port helpers `validate_addr`, `parse_addr`, `validate_ports`, and IPv6 variants.

Control flow: sourced by pktgen scripts, enables `errexit`, validates `/proc/net/pktgen` control files, writes commands, checks `Result: OK`, and exits on errors. Address helpers parse IPv4/IPv6 and CIDR ranges using shell arithmetic.

State and persistence: exports `PROC_DIR`; scripts modify `/proc/net/pktgen` state and optionally reset it on exit.

Dependencies and integration: requires Bash, root privileges or sudo, pktgen procfs, `/sys/class/net`, `/proc/interrupts`, and standard coreutils.

Risks: shell arithmetic and IPv6 parsing are sample-grade. `set -o errexit` affects callers. Commands write directly to pktgen proc files and can disrupt active generator state.

Test signals: source from pktgen scripts, run with `-x` for debug, verify invalid addresses/ports fail, and confirm pktgen proc writes report OK.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pktgen/functions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pktgen/parameters.sh -->
# sources/distributed-fs/ceph-client/samples/pktgen/parameters.sh

Purpose: common option parser and default initializer for pktgen scripts.

Important APIs/functions: `usage`, `getopts` over packet size, interface, destination IP/MAC/port, first thread, thread count, clone count, packet count, burst, delay, verbose/debug, IPv6, append mode, and UDP checksum. Exports variables consumed by scripts.

Control flow: parses options, sets defaults (`PKT_SIZE=60`, `F_THREAD=0`, `THREADS=1`, `DELAY=0`), computes `L_THREAD`, warns for missing destination details, requires `DEV`, and loads `pktgen` with `modprobe` if `/proc/net/pktgen` is absent.

State and persistence: exported shell variables and possible kernel module load.

Dependencies and integration: intended to be sourced after `functions.sh`; uses `err`, `warn`, and `info`.

Risks: being sourced exits the parent script on invalid input. Missing MAC/IP are warnings, so individual scripts may enforce them later. Assumes `modprobe` and sufficient privileges.

Test signals: invoke sample scripts with `-h`, invalid options, missing `-i`, IPv6 mode, and verify exported defaults in verbose mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pktgen/parameters.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pktgen/pktgen_bench_xmit_mode_netif_receive.sh -->
# sources/distributed-fs/ceph-client/samples/pktgen/pktgen_bench_xmit_mode_netif_receive.sh

Purpose: pktgen benchmark script for injecting generated packets into the receive path with `xmit_mode netif_receive`, useful for ingress qdisc path benchmarking.

Important APIs/functions: sources `functions.sh` and `parameters.sh`; uses `pg_ctrl reset/start`, `pg_thread rem_device_all/add_device`, `pg_set` for queue mapping, count, packet size, delay, destination, UDP destination range, `xmit_mode netif_receive`, and burst.

Control flow: runs as root, sets defaults for destination, MAC, burst, and count, validates addresses/ports, resets pktgen, configures one pktgen device per requested thread, starts pktgen, and prints result snippets for each device.

State and persistence: modifies pktgen procfs state and resets it through trap/explicit reset.

Dependencies and integration: pktgen kernel module, Bash, root/sudo, interface name, and optional qdisc setup described in comments.

Risks: default invalid MAC intentionally drops packets in RX path; using real destinations can inject traffic. Burst defaults to 1024 and can create heavy CPU load.

Test signals: configure ingress qdisc scenarios, run with `-i <dev>`, compare result throughput and qdisc behavior across scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pktgen/pktgen_bench_xmit_mode_netif_receive.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pktgen/pktgen_bench_xmit_mode_queue_xmit.sh -->
# sources/distributed-fs/ceph-client/samples/pktgen/pktgen_bench_xmit_mode_queue_xmit.sh

Purpose: pktgen benchmark script for egress qdisc path measurement using `xmit_mode queue_xmit`.

Important APIs/functions: sources shared helpers, rejects `BURST`, configures pktgen threads/devices, sets queue CPU mapping, packet count/size/delay/destination, optional UDP destination range, and `xmit_mode queue_xmit`.

Control flow: runs as root, parses parameters, sets defaults, validates address/ports, resets pktgen, configures each thread device, starts run, and prints result snippets.

State and persistence: modifies `/proc/net/pktgen`; reset occurs before configuration and via sourced trap behavior.

Dependencies and integration: pktgen, egress qdisc stack, root privileges, and selected network device.

Risks: can generate heavy traffic through egress path. Burst is explicitly unsupported because queue_xmit mode rejects burst greater than one.

Test signals: run against a test interface with egress qdisc configurations and compare pktgen result output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/pktgen/pktgen_bench_xmit_mode_queue_xmit.sh -->
