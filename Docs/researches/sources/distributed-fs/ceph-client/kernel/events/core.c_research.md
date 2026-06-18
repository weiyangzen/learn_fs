# Research: sources/distributed-fs/ceph-client/kernel/events/core.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006028`: lines 1-10414, `Docs/researches/chunks/subset-b-006028_research.md`
- `subset-b-006029`: lines 10415-15411, `Docs/researches/chunks/subset-b-006029_research.md`

## Chunk Research

### subset-b-006028: lines 1-10414

# sources/distributed-fs/ceph-client/kernel/events/core.c lines 1-10414

## Scope

This chunk covers the first 10,414 lines of the Linux perf events core implementation carried in the Ceph client kernel source snapshot. It starts at the file header and includes the core perf event context model, PMU scheduling, cgroup and guest mediated PMU hooks, event lifetime and file operations, mmap/AUX buffer handling, sample construction, and many synthesized side-band records. The mapped range ends at the first field of `struct perf_text_poke_event`; the text-poke match/output functions continue after this chunk and should be handled by a later chunk.

Although this repository is Ceph-oriented, this file is generic kernel performance-monitoring infrastructure. CephFS code can be observed through it, but Ceph file-system behavior is not implemented here.

## Purpose

`kernel/events/core.c` is the central implementation behind the Linux `perf_event_open` ABI and in-kernel perf event APIs. In this chunk, it:

- Maintains per-CPU and per-task `perf_event_context` state and their per-PMU subcontexts.
- Schedules pinned and flexible event groups on and off PMUs during task switches, cgroup switches, guest transitions, event enable/disable, and PMU multiplexing timer rotations.
- Implements time accounting for enabled/running durations, including cgroup-scoped time and mediated guest-PMU exclusion.
- Owns event lifetime: reference counts, parent/child inherited events, group attach/detach, context migration locking, owner-task lists, and RCU-delayed free.
- Implements the user-facing file operations for perf event file descriptors: `read`, `poll`, `ioctl`, `mmap`, `release`, and `fasync`.
- Builds samples and non-sample records into perf ring buffers, including `SAMPLE`, `READ`, `FORK`, `EXIT`, `COMM`, `NAMESPACES`, `CGROUP`, `MMAP`, `AUX`, lost samples, context switches, throttling, ksymbols, BPF events, and deferred callchains.

The code is performance critical: many paths run with IRQs disabled, under scheduler locks, or in NMI-adjacent sampling paths.

## Important APIs, Types, And Functions

Remote execution and context locks:

- `remote_function_call`, `remote_function_f`, `task_function_call()`, and `cpu_function_call()` run small functions on the CPU where a task or per-CPU event is active.
- `event_function_call()` and `event_function_local()` are the common wrappers used to mutate an event in its active context while validating that `event->ctx`, `ctx->task`, and `cpuctx->task_ctx` still match.
- `perf_ctx_lock()`, `perf_ctx_unlock()`, and the `class_perf_ctx_lock_t` cleanup helper lock the CPU context and optional task context together.
- `TASK_TOMBSTONE` marks task contexts being torn down so remote calls do not treat them as live tasks.

Core state:

- `enum event_type_t` distinguishes flexible, pinned, time, frozen, CPU, cgroup, and guest scheduling operations.
- `perf_cpu_context` is the per-CPU root context. `perf_cpu_task_ctx()` exposes the currently loaded task context when IRQs are disabled.
- Global counters such as `nr_mmap_events`, `nr_comm_events`, `nr_task_events`, `nr_switch_events`, `nr_ksymbol_events`, `nr_bpf_events`, `nr_cgroup_events`, `nr_text_poke_events`, and `nr_build_id_events` gate expensive side-band work.
- `pmus`, `pmus_lock`, `pmus_srcu`, online CPU masks, and `perf_event_cache` are file-global registries and allocators used by later PMU registration/open paths.

Sysctls and throttling:

- `sysctl_perf_event_paranoid`, `sysctl_perf_event_mlock`, `sysctl_perf_event_sample_rate`, and `sysctl_perf_cpu_time_max_percent` expose perf policy knobs.
- `perf_event_max_sample_rate_handler()`, `perf_cpu_time_max_percent_handler()`, `update_perf_cpu_limits()`, and `perf_sample_event_took()` enforce dynamic sample-rate throttling when interrupt sampling consumes too much CPU time.
- `perf_event_throttle()`, `perf_event_unthrottle()`, and group variants stop and resume overactive groups and log throttle records.

Time accounting and cgroups:

- `perf_event_set_state()`, `perf_event_update_time()`, `perf_event_update_sibling_time()`, `perf_event_time()`, and `perf_event_time_now()` maintain `total_time_enabled` and `total_time_running`.
- `update_perf_time_ctx()` maintains `time`, `stamp`, and lockless `offset` fields used from NMI-safe paths.
- Under `CONFIG_CGROUP_PERF`, `perf_cgroup_match()`, `perf_cgroup_switch()`, `perf_cgroup_connect()`, `perf_cgroup_event_enable()`, `perf_cgroup_event_disable()`, and cgroup time helpers scope per-CPU events to recursive cgroup membership.

Group and scheduling logic:

- `perf_event_groups` use rb-trees keyed by CPU, PMU, cgroup, and `group_index` to keep pinned/flexible groups ordered.
- `list_add_event()`, `list_del_event()`, `perf_group_attach()`, `perf_group_detach()`, and `perf_child_detach()` maintain context and group membership.
- `event_sched_in()`, `group_sched_in()`, `event_sched_out()`, `group_sched_out()`, `ctx_sched_in()`, `ctx_sched_out()`, `ctx_resched()`, and `perf_event_sched_in()` program and deprogram PMU state while preserving CPU pinned, task pinned, CPU flexible, task flexible priority.
- `perf_mux_hrtimer_handler()`, `perf_mux_hrtimer_restart()`, `ctx_event_to_rotate()`, `rotate_ctx()`, and `perf_rotate_context()` implement multiplexing for flexible groups that cannot all run at once.
- Scheduler hooks `__perf_event_task_sched_out()` and `__perf_event_task_sched_in()` handle task switch out/in, PMU `sched_task` callbacks, side-band switch records, cgroup switches, and fast context-swap optimization for equivalent cloned contexts.

Event lifetime:

- `perf_event_ctx_lock_nested()`, `perf_event_ctx_lock()`, `perf_event_ctx_unlock()`, `perf_lock_task_context()`, `perf_pin_task_context()`, and `perf_unpin_context()` stabilize contexts across migration and exit.
- `alloc_perf_context()`, `find_get_context()`, `find_get_pmu_context()`, `put_pmu_ctx()`, `put_ctx()`, `__free_event()`, `_free_event()`, `free_event()`, `put_event()`, and `perf_event_release_kernel()` own allocation, reference counts, RCU free, and teardown.
- `exclusive_event_init()`, `exclusive_event_installable()`, and `exclusive_event_destroy()` enforce `PERF_PMU_CAP_EXCLUSIVE`.
- `perf_get_aux_event()` and `perf_put_aux_event()` link events using AUX-output or AUX-sample relationships to a group leader that owns the AUX buffer.

User ABI file operations:

- `perf_read()`, `__perf_read()`, `perf_read_one()`, `perf_read_group()`, `perf_event_read_value()`, and `perf_event_read_local()` read counts, IDs, lost samples, and enabled/running times.
- `_perf_ioctl()` handles `PERF_EVENT_IOC_ENABLE`, `DISABLE`, `RESET`, `REFRESH`, `PERIOD`, `ID`, `SET_OUTPUT`, `SET_FILTER`, `SET_BPF`, `PAUSE_OUTPUT`, `QUERY_BPF`, and `MODIFY_ATTRIBUTES`.
- `perf_event_period()`, `_perf_event_period()`, and `__perf_event_period()` validate and update fixed-period or frequency sampling periods.
- `perf_fops` connects `release`, `read`, `poll`, `ioctl`, compat ioctl, `mmap`, and `fasync` to the perf event fd.

Mmap, ring buffer, and AUX:

- `perf_event_init_userpage()` and `perf_event_update_userpage()` maintain `struct perf_event_mmap_page` fields visible to userspace.
- `ring_buffer_attach()`, `ring_buffer_get()`, `ring_buffer_put()`, `ring_buffer_wakeup()`, and `perf_event_wakeup()` manage `perf_buffer` ownership and wakeups.
- `perf_mmap()`, `perf_mmap_rb()`, `perf_mmap_aux()`, `perf_mmap_open()`, `perf_mmap_close()`, `map_range()`, and memlock accounting helpers allocate, map, account, and free data/AUX buffers.
- `perf_pmu_output_stop()` stops active AUX writers when an AUX buffer is being unmapped or redirected.

Sampling and records:

- `perf_prepare_sample()`, `perf_prepare_header()`, `perf_output_sample()`, `perf_event_output()`, `perf_event_output_forward()`, and `perf_event_output_backward()` build and emit sample records.
- Helpers populate IP, TID, time, ID, CPU, read format, callchain, raw data, branch stack, user/intr registers, user stack, weight, data source, transaction, physical address, cgroup ID, page sizes, and AUX snapshots.
- `perf_callchain()` can request deferred user unwinding through `unwind_deferred_request()` and later emits `PERF_RECORD_CALLCHAIN_DEFERRED`.
- Side-band emitters in this chunk cover read records, fork/exit, comm, namespaces, cgroups, mmap/mmap2/build-id, AUX, lost samples, context switch, throttle/unthrottle, ksymbol, and BPF events.

Guest integration:

- Under `CONFIG_GUEST_PERF_EVENTS`, `perf_register_guest_info_callbacks()` and `perf_unregister_guest_info_callbacks()` install KVM/guest callbacks through static calls.
- Under `CONFIG_PERF_GUEST_MEDIATED_PMU`, `perf_create_mediated_pmu()`, `perf_release_mediated_pmu()`, `perf_load_guest_context()`, and `perf_put_guest_context()` coordinate mediated vPMU ownership and temporarily schedule out host `exclude_guest` events.

## Control Flow

Opening or installing an event starts by finding or allocating a task or CPU context, finding a PMU context, initializing event state, and then calling `perf_install_in_context()`. If the target is a CPU context, installation uses `cpu_function_call()`. If the target is a task context, it uses `task_function_call()` when the task is running or installs under `ctx->lock` when it is not. The install path freezes time, links the event into context/group structures, and reschedules the affected PMU priority class.

Context scheduling flows through the scheduler hooks. On switch out, `__perf_event_task_sched_out()` optionally emits switch records, then `perf_event_context_sched_out()` schedules task events out or performs a clone-context swap optimization if two contexts are equivalent. On switch in, `__perf_event_task_sched_in()` calls `perf_event_context_sched_in()`, which first schedules pinned events then flexible events while preserving CPU-event priority. Cgroup switches are handled as a separate per-CPU reschedule when `cpuctx->cgrp` no longer matches the next task.

Enable, disable, refresh, period changes, and removal all cross into the event's owning context. Public wrappers lock `ctx->mutex`, then the actual mutation runs under `ctx->lock` through `event_function_call()` or `event_function_local()`. Disabling a group leader schedules out the group, while enabling a group member only runs it if the leader is active. Removal schedules out the event, disables cgroup accounting, detaches from group/child lists as requested by flags, removes it from the context list, and clears task-context activity if it was the last event.

Reads first try to update active events on their `oncpu` with `smp_call_function_single()`. Inactive events are read by taking `ctx->lock` and updating time in place. Group reads transact through PMU callbacks and validate inherited parent/child group shape before summing values.

The mmap path validates shared page-aligned mappings, security policy, inherited-task restrictions, memlock limits, and power-of-two buffer sizing. Data buffers are mapped at `vm_pgoff == 0`; AUX buffers map above the data buffer with offset and size taken from the user page. On close, AUX mappings stop writers before freeing AUX pages, and final data mapping close detaches all events redirected into the unreachable buffer.

Sample output follows a common pipeline: `perf_prepare_sample()` fills requested fields and dynamic-size accounting, `perf_prepare_header()` sets record type/size/misc, `perf_output_begin*()` reserves ring-buffer space, `perf_output_sample()` serializes fields in ABI order, and `perf_output_end()` publishes the record.

Side-band events use `perf_iterate_sb()` to find eligible CPU-wide and current-task events. Each record type has a match predicate based on event attributes, a record-specific payload builder, and output through `perf_output_begin()`. The task-exit path can pass a specific task context so EXIT records are delivered before the context is released.

## State And Persistence Behavior

Most state is in memory and lifetime-bound to tasks, CPUs, PMUs, event file descriptors, ring buffers, cgroups, and VMA mappings. There is no disk persistence in this chunk.

Persistent user-visible state exists through kernel ABI objects:

- A perf event fd owns `struct perf_event` until `release` or `perf_event_release_kernel()` drops the final reference.
- Ring buffers persist while mapped or referenced by redirected output events. Their user page is a live shared-memory ABI with seqlock-style updates.
- Event counts, lost-sample counters, enabled/running totals, child totals, read sizes, header sizes, group generation, and context generation are maintained across scheduling and inheritance.
- Task contexts may be cloned during fork and later uncloned when modified. `generation` and `parent_gen` decide whether switch-time context swapping is legal.
- `perf_ctx_data` attaches PMU-specific task data either per task or globally for system-wide events and is released with RCU after task/global detach.
- Cgroup perf state uses per-CPU `perf_cgroup_info` time snapshots and active flags. Cgroup event configuration pins the cgroup CSS until detached.
- Sysctl values change global sampling policy and dynamic throttling state. `perf_sample_event_took()` may lower the sample rate until userspace changes policy again.
- `event->rb`, `event->ctx`, `ctx->task`, `event->owner`, and per-PMU context lists are protected by a mixture of RCU, refcounts, mutexes, raw spinlocks, acquire/release stores, and explicit memory barriers.

The code deliberately avoids persisting stale mappings: file-based address filters are cleared on exec and recalculated on executable mmap events. AUX buffer lifetime is tied to mmap references and writer-stop ordering, so unmapping invalidates future AUX writes.

## Dependencies And Integration Points

This chunk depends heavily on kernel scheduler, RCU, locking, cgroup, mm, file, anon-inode, BPF, tracepoint, hw-breakpoint, build-id, task-work, min-heap, and architecture perf hooks. Important cross-file dependencies include:

- `include/linux/perf_event.h` and `kernel/events/internal.h` for `struct perf_event`, `struct pmu`, `struct perf_event_context`, `struct perf_buffer`, sample data, ring-buffer helpers, and PMU callback contracts.
- Architecture callbacks such as `perf_arch_misc_flags()`, `perf_arch_instruction_pointer()`, `perf_reg_value()`, `perf_get_regs_user()`, page-table leaf-size helpers, and optional `arch_perf_update_userpage()`.
- PMU callbacks: `add`, `del`, `start`, `stop`, `read`, `start_txn`, `commit_txn`, `cancel_txn`, `event_idx`, `check_period`, `addr_filters_sync`, `snapshot_aux`, `sched_task`, `event_mapped`, `event_unmapped`, and PMU filters/capabilities.
- Scheduler hooks call `__perf_event_task_sched_out()` and `__perf_event_task_sched_in()`.
- Process lifecycle hooks call `perf_event_fork()`, `perf_event_comm()`, `perf_event_namespaces()`, `perf_event_exec()`, and later exit paths outside this chunk.
- MM hooks call `perf_event_mmap()` and address-filter adjusters on VMA changes.
- Cgroup hooks use `perf_event_cgroup()` to emit cgroup records when cgroups are created or observed.
- KVM/guest integrations register callbacks and mediated-vPMU state transitions.
- BPF and ksymbol integrations emit load/unload records and optionally BPF JIT symbol records.
- Security hooks `security_perf_event_read()`, `security_perf_event_write()`, and `security_perf_event_free()` enforce LSM policy.

For this Ceph client source tree, the direct integration point is mostly observability: perf can sample CephFS kernel code, emit mmap/comm/task/cgroup/BPF context around Ceph workloads, and expose counts through standard Linux perf tooling.

## Risks And Edge Cases

Concurrency is the dominant risk. Many operations race with task migration, context switch, PMU hotplug/unregister, event fd close, inherited child teardown, mmap close, AUX output, and NMI sampling. The code relies on strict lock ordering and RCU/refcount protocols; changing those protocols can introduce deadlocks or use-after-free bugs.

Context migration is fragile. `event->ctx` can change while userspace operations wait for `ctx->mutex`, so callers must use `perf_event_ctx_lock()` rather than directly locking a cached context. TASK_TOMBSTONE handling is required for exit paths that remove events from contexts no longer associated with a live task.

Time accounting can silently drift if EVENT_TIME edges are missed. The code updates user pages when context time starts, preserves `EVENT_TIME|EVENT_FROZEN` during certain reschedules, and uses acquire/release barriers for lockless `perf_event_time_now()`. Removing these barriers or skipping sibling updates can break enabled/running ratios.

Group scheduling must be all-or-nothing. `group_sched_in()` starts a PMU transaction and rolls back partial group installs on failure. Pinned groups that cannot schedule are moved to `PERF_EVENT_STATE_ERROR` and wake poll/fasync waiters. Flexible failures must restart multiplexing timers instead.

Cgroup matching is recursive and per-CPU. Events scoped to a cgroup match descendants; `perf_cgroup_ensure_storage()` must size per-CPU heaps for nested cgroups. Bugs here can either miss descendant activity or overflow the merge iterator.

Mmap/AUX lifetime is subtle. AUX close must stop writers before freeing AUX pages. Redirected output means an event's ring buffer can be shared with other events, so final close must detach other writers without corrupting `rb->event_list`. Failed mappings have custom cleanup because VM close callbacks are not invoked.

The sample ABI has strict field order and 16-bit `header.size` limits. Dynamic fields such as callchains, raw fragments, user stacks, register masks, branch counters, and AUX samples must fit and be 8-byte aligned. The code clamps user stack and AUX sample sizes to avoid overflowing headers.

User data exposure risks are handled by alignment zero-fill for strings and cautious nofault access. Cgroup paths, mmap names, comm strings, ksymbol names, build IDs, user stack bytes, physical addresses, and namespace device/inode data all cross into user-visible perf buffers.

Guest and mediated PMU support can conflict with host events. The code rejects creating include-guest events while mediated PMU VMs exist and schedules out exclude-guest host events when a mediated guest context loads. Incorrect accounting can leak host PMU ownership into a guest or block valid host events.

The range ends mid-feature at `struct perf_text_poke_event`. The presence of `nr_text_poke_events` and the struct start show that text-poke tracking belongs to this file, but its implementation is outside this chunk and should not be considered complete from this report alone.

## Test Signals

Useful validation signals for this chunk include:

- Kernel build coverage for all relevant configs: `CONFIG_PERF_EVENTS`, `CONFIG_CGROUP_PERF`, `CONFIG_PERF_GUEST_MEDIATED_PMU`, `CONFIG_GUEST_PERF_EVENTS`, `CONFIG_COMPAT`, `CONFIG_NO_HZ_FULL`, BPF, namespace, hugepage, and no-MMU/MMU variants.
- Lockdep, RCU stall, KASAN, KCSAN, UBSAN, and refcount debug runs while creating, enabling, disabling, reading, mmaping, redirecting, inheriting, and closing perf events.
- `perf_event_open` selftests for read formats, group reads, pinned/flexible groups, inherit and inherit_stat, sample_id_all, frequency mode, refresh limits, period changes, BPF attachment, filters, and error-state behavior.
- Scheduler stress with many per-task and per-CPU events across CPU migration, fork/exec/exit, cgroup movement, and CPU hotplug. Expected signals are no lost context references, no deadlocks, correct switch/task/comm/mmap records, and stable enabled/running ratios.
- Cgroup perf tests validating recursive matching, cgroup switch rescheduling, per-CPU heap sizing for nested cgroups, and `PERF_RECORD_CGROUP` output path alignment.
- Ring-buffer tests covering repeated mmap of the same buffer, invalid non-power-of-two sizes, memlock denial, `PERF_EVENT_IOC_SET_OUTPUT`, failed `map_range()` cleanup, AUX mapping offset/size validation, AUX unmap while active, and wakeup/poll/fasync behavior.
- Sampling ABI tests for every sample field combination in this chunk, including register masks, user stack truncation, callchain/deferred callchain, branch stacks with hardware index and counters, physical address/page-size lookup, cgroup ID, AUX snapshots, raw fragments, and lost-sample records.
- Dynamic throttling tests that force long sample handlers and verify `perf_event_max_sample_rate` reduction, throttle/unthrottle records, frequency-mode period adjustment, and nohz tick dependency behavior.
- Guest/KVM tests for callback registration, guest IP/misc sampling, mediated PMU create/release failure modes, and load/put guest context scheduling of exclude-guest events.
- Side-band record tests for fork/exit, comm exec flag, namespaces under different namespace configs, mmap versus mmap2/build-id, ksymbol register/unregister, BPF program load/unload, and context switch CPU-wide versus task-local payload differences.

### subset-b-006029: lines 10415-15411

# sources/distributed-fs/ceph-client/kernel/events/core.c lines 10415-15411

## Scope

This chunk covers the late `kernel/events/core.c` implementation from side-band perf records and generic overflow handling through software/tracepoint/probe PMUs, address filters, PMU registration, perf event allocation, the `perf_event_open()` syscall, kernel counter creation, PMU context migration, task inheritance/exit handling, CPU hotplug setup, subsystem initialization, sysfs registration, and perf cgroup hooks.

The chunk begins in the `PERF_RECORD_TEXT_POKE` output path and ends with the branch-stack static call declaration after cgroup integration. Earlier chunks define much of the event context scheduling, ring buffer, mmap, callchain, cgroup accounting, and PMU helper machinery used here; this range is where user-visible event creation and many PMU lifecycle APIs are wired together.

## Purpose

The code in this chunk turns perf event attributes into active kernel objects, routes software and tracing events to matching perf events, records overflow samples, exposes PMUs through sysfs, and manages event lifetime across task fork/exit, CPU hotplug, PMU unregister, and cgroup movement. It is a central control-plane section for the perf subsystem.

Several responsibilities are interleaved:

- Emitting side-band records for text patching, instruction-trace start, and AUX hardware output ids.
- Accounting and throttling interrupts before invoking event overflow handlers, BPF perf-event programs, signal delivery, fasync wakeups, and AUX pause/resume.
- Maintaining per-CPU software-event hash tables and PMUs for generic software events, tracepoints, kprobes, uprobes, CPU clock, and task clock.
- Parsing and installing address filters from userspace strings, then applying file-backed filters to a task's current VMAs.
- Registering and unregistering PMUs, including type id assignment, per-CPU PMU contexts, sysfs devices, default operation stubs, and safe detachment of existing events.
- Allocating `struct perf_event`, validating `perf_event_attr`, selecting the owning PMU, finding task/CPU contexts, installing events, and handling the `perf_event_open()` syscall's grouping, output redirection, permission, cgroup, AUX, and error paths.
- Creating in-kernel perf counters for kernel clients.
- Migrating PMU contexts during topology changes and unwinding events during task exit, failed fork, CPU offline, reboot, and PMU unregister.
- Initializing perf state at boot and registering the perf cgroup subsystem.

## Important APIs, Types, and Functions

- `perf_event_text_poke()` builds `PERF_RECORD_TEXT_POKE` records with old/new instruction bytes, u64 padding, kernel misc flags, and address metadata, then broadcasts to side-band listeners with `perf_iterate_sb()`. `perf_event_text_poke_output()` filters events by `event->attr.text_poke`, initializes sample id data, writes the record body, and appends the id sample.
- `perf_event_itrace_started()`, `perf_log_itrace_start()`, and `perf_report_aux_output_id()` provide AUX/instruction-trace side-band records. `perf_log_itrace_start()` emits `PERF_RECORD_ITRACE_START` once for eligible parent events, while `perf_report_aux_output_id()` emits `PERF_RECORD_AUX_OUTPUT_HW_ID` and is exported for PMU drivers.
- `__perf_event_account_interrupt()` updates per-event interrupt sequence accounting, throttles groups after `max_samples_per_tick`, keeps the scheduler tick alive for throttled perf events, and adjusts frequency-mode sampling periods based on elapsed `perf_clock()` time.
- `__perf_event_overflow()` is the generic sampling overflow path. It ignores non-sampling events, accounts interrupts, pauses/resumes AUX as requested, optionally runs a `BPF_PROG_TYPE_PERF_EVENT` program, handles `event_limit`, schedules synchronous `SIGTRAP` task work, calls the event's overflow handler, and queues async wakeups.
- `perf_swevent_set_period()`, `perf_swevent_overflow()`, and `perf_swevent_event()` implement software-event counting and sampling. They keep `event->count` and `hw.period_left` coherent, convert period crossings into one or more overflow callbacks, and serialize active checks with IRQ disable when software events may race event removal.
- `struct swevent_htable` stores per-CPU software-event hash tables. `swevent_hlist_get*()` and `swevent_hlist_put*()` allocate/free per-CPU hash lists with reference counts and RCU teardown.
- `do_perf_sw_event()`, `___perf_sw_event()`, and `__perf_sw_event()` route `PERF_TYPE_SOFTWARE` events through per-CPU hash buckets under RCU and recursion protection.
- `perf_swevent`, `perf_cpu_clock`, and `perf_task_clock` are software PMUs. CPU and task clock PMUs use hrtimers to generate sampling ticks, update counts from `local_clock()` or task context time, and convert frequency mode to fixed periods.
- Trace integration under `CONFIG_EVENT_TRACING` includes `perf_tracepoint`, `perf_kprobe`, and `perf_uprobe` PMUs; `perf_tp_event()` submits tracepoint raw records to matching events and optionally to a target task; `perf_trace_run_bpf_submit()` runs tracepoint BPF filters before perf submission.
- `perf_event_set_bpf_prog()` and `perf_event_free_bpf_prog()` attach/detach BPF programs to perf events. `__perf_event_set_bpf_prog()` distinguishes tracing events from generic perf-event BPF overflow handlers and enforces program type, sleepability, kprobe override, writable context, and tracepoint context-size rules.
- Address-filter helpers include `perf_addr_filter_new()`, `perf_addr_filters_splice()`, `perf_event_parse_addr_filter()`, `perf_event_set_addr_filter()`, and `perf_event_addr_filters_apply()`. They parse `filter`, `start`, and `stop` filters for kernel ranges or file paths, validate PMU support, atomically replace filter lists, and recompute per-event ranges from VMAs.
- `perf_copy_attr()` is the userspace ABI gate for `perf_event_attr`. It handles struct-size compatibility, reserved fields, sample/read/branch masks, branch privilege checks, user/intr register validation, stack dump size/alignment, cgroup support, weight field exclusivity, inheritance consistency, and `sigtrap` constraints.
- `perf_event_set_output()` redirects one event's ring-buffer output to another event after checking circularity, CPU/task compatibility, clock compatibility, write direction, AUX PMU compatibility, active mmap state, and output buffer lifetime.
- `perf_event_set_clock()` switches event timestamping to supported `clockid_t` sources and rejects non-NMI-safe clocks for PMUs that can sample in NMI context.
- `perf_check_permission()` combines `perfmon_capable()`, optional `CAP_KILL` for `sigtrap`, and ptrace access checks for task-targeted events.
- `perf_pmu_register()` assigns a PMU type id, creates a sysfs device when the bus is already running, allocates per-CPU `struct perf_cpu_pmu_context` pointers, installs default PMU operation stubs, initializes event lists, and publishes the PMU through the idr and global RCU list.
- `perf_pmu_unregister()` removes a PMU from discovery, synchronizes SRCU/RCU readers, refuses forced removal if `event_unmapped` events remain, detaches all existing events, and frees per-CPU contexts/sysfs state.
- `perf_try_init_event()` calls a PMU's `event_init()` with module ref protection, handles sibling-list locking for hardware groups, validates extended register and exclude capabilities, and applies scoped PMU read capability for topology-scoped PMUs.
- `perf_init_event()` selects a PMU from parent PMU, explicit type id, hardware/cache aliasing, or global PMU probing. It supports extended hardware type encodings and PMUs that rewrite `event->attr.type` to redirect initialization.
- `account_event()` increments global feature counters for mmap, build-id, comm, namespace, cgroup, task, frequency, context switch, branch stack, ksymbol, BPF, and text-poke events, enables scheduler hooks when needed, and attaches side-band per-CPU events.
- `perf_event_alloc()` initializes a new `struct perf_event`: lists, wait queues, work items, locks, refcounts, pid namespace, id, target task, inherited handler/BPF state, default output handler, hardware period fields, PMU selection, task-data attachment, AUX compatibility, cgroup connection, exclusive-event state, address-filter storage, callchain buffers, security hooks, mediated PMU accounting, global accounting, and PMU event-list membership.
- `SYSCALL_DEFINE5(perf_event_open)` is the userspace event creation entry point. It copies attributes, runs security and privilege checks, reserves an fd, resolves group/output fds and target tasks, allocates the event, validates sampling capability, sets clock source, obtains and locks the target context, validates grouping constraints, finds the PMU context, configures output/AUX/exclusive state, creates the anon inode file, optionally migrates a pure software group into a hardware context, precalculates sample header sizes, installs the event, and publishes the fd.
- `perf_event_create_kernel_counter()` creates kernel-owned counters without grouping or AUX output, installs them into task or CPU contexts, and marks `owner = TASK_TOMBSTONE` to distinguish them from user events.
- `perf_pmu_migrate_context()` removes all events for a scoped PMU from one CPU context, waits for RCU quiescence, and reinstalls siblings before leaders on another CPU. It is used by CPU topology/hotplug code when the representative CPU for a scope changes.
- Task lifecycle helpers include `perf_event_exit_event()`, `perf_event_exit_task_context()`, `perf_event_exit_task()`, `perf_event_free_task()`, `inherit_event()`, `inherit_group()`, `inherit_task_group()`, `perf_event_init_context()`, and `perf_event_init_task()`. They sync child counts to parents, detach events on exit, mark contexts as tombstones, clone inheritable event groups during fork, and manage cloned context relationships.
- Boot/hotplug helpers include `perf_event_init_all_cpus()`, `perf_swevent_init_cpu()`, `perf_event_clear_cpumask()`, `perf_event_exit_cpu_context()`, `perf_event_setup_cpumask()`, `perf_event_init_cpu()`, `perf_event_exit_cpu()`, `perf_reboot()`, and `perf_event_init()`.
- Sysfs/cgroup integration is handled by PMU device attributes (`type`, `perf_event_mux_interval_ms`, `nr_addr_filters`, `cpumask`), `perf_event_sysfs_init()`, `perf_event_sysfs_show()`, and the `perf_event_cgrp_subsys` callbacks.

Key state carriers in this chunk are `struct perf_event`, `struct hw_perf_event`, `struct perf_event_attr`, `struct perf_event_context`, `struct perf_event_pmu_context`, `struct perf_cpu_pmu_context`, `struct pmu`, `struct perf_buffer`, `struct perf_sample_data`, `struct perf_raw_record`, `struct perf_addr_filter`, `struct perf_addr_filters_head`, `struct swevent_htable`, `struct swevent_hlist`, `struct cgroup_subsys_state`, and `struct perf_cgroup`.

## Control Flow

Side-band record flow starts with a cheap global counter check, for example `nr_text_poke_events`, before constructing the record. Records are matched per event (`attr.text_poke`, PMU capability, attach state), sample id headers are initialized, `perf_output_begin()` reserves ring-buffer space, fixed fields and variable byte payloads are copied, id samples are appended, and `perf_output_end()` commits the data.

Overflow handling has a strict order. `perf_event_overflow()` asserts interrupts are disabled for hardware PMI entry and delegates to `__perf_event_overflow()`. The generic handler rejects non-sampling events, updates interrupt throttling and frequency period feedback, pauses AUX output if requested, runs an attached perf-event BPF program that can suppress normal output, updates pending poll state and event-limit disable state, arranges `SIGTRAP` task work for synchronous signals, calls the event's overflow handler, queues fasync wakeups, and resumes AUX output if requested. Software events reach the same path through `perf_swevent_event()` after count/period accounting.

Software-event dispatch is per CPU. `__perf_sw_event()` disables preemption, enters a recursion context, initializes sample data in `___perf_sw_event()`, then `do_perf_sw_event()` looks up the event type/id bucket in the current CPU's RCU-protected software hash table. Each matching active event receives count increments and possibly overflow processing. Event add/delete for software PMUs simply inserts/removes the event's `hlist_entry` from the current CPU hash bucket under context serialization.

Tracepoint submission receives raw trace records from tracing code. `perf_trace_run_bpf_submit()` first executes tracepoint BPF programs attached to the trace event call and can consume the recursion context early if BPF or an empty perf list stops delivery. `perf_tp_event()` updates trace buffer metadata, iterates the tracepoint perf event hlist, applies stopped/exclude/filter checks, stores raw data into `perf_sample_data`, and routes each event through software-event sampling. If a target task is supplied, it additionally locks that task's perf context and scans pinned/flexible tracepoint groups for delivery; synchronous signal delivery is intentionally skipped for target-task delivery.

Address-filter installation starts from an ioctl filter string. `perf_event_set_filter()` copies the user string; tracing events temporarily drop `ctx->mutex` and delegate to ftrace filter code, while address-filter-capable PMUs parse into a temporary list. `perf_event_parse_addr_filter()` walks tokens in action/source states, creates one `perf_addr_filter` per filter, resolves file paths for file-backed filters, rejects unsupported CPU-wide file filters, and counts file filters. PMU validation runs before `perf_addr_filters_splice()` atomically replaces the live list. Each child event then recomputes hardware ranges, optionally scanning the target mm's VMAs under `mmap_read_lock()`, increments `addr_filters_gen`, and restarts the event for hardware sync.

PMU registration is serialized by `pmus_lock`. `perf_pmu_register()` allocates an idr slot, optionally creates a sysfs device, allocates one PMU context pointer per possible CPU, fills operation stubs for missing callbacks, initializes event lists, then atomically replaces the idr placeholder with the fully initialized PMU and adds it to the RCU list. Unregistration first hides the PMU from creation, synchronizes SRCU/RCU readers, handles the `event_unmapped` busy case, removes the id, detaches events one by one with refcount protection, waits until the PMU event list is empty, and finally frees PMU resources.

Event allocation is a staged pipeline. `perf_event_alloc()` validates target CPU/task and `sigtrap`, allocates and initializes the event object, chooses inherited or default overflow handlers, initializes sample period state, rejects unsupported inherited sample-read combinations, normalizes branch sampling, selects and initializes a PMU, attaches extra task data if the PMU requested it, rejects invalid uncore task/cgroup combinations, validates AUX output/pause mode, connects cgroups, initializes exclusive state, allocates address-filter ranges, obtains callchain buffers for parent events, runs LSM and mediated PMU accounting, updates global counters, and links the event into the PMU's event list.

`perf_event_open()` wraps allocation with userspace and grouping policy. After attribute/security checks, it reserves an fd before taking SRCU protection over PMU discovery. It resolves `group_fd`, optional output redirection, and target task/cgroup. After allocation it validates sampling interrupts and clock id, checks task permissions under `exec_update_lock`, obtains a task or CPU context, validates context liveness and CPU online state, verifies group topology and same-context/same-clock/same-CPU constraints, finds the final PMU context, sets output and AUX relationships, checks exclusive installability, creates the anon inode file, commits any needed group migration from software to hardware context, precalculates sample sizes, installs the event, publishes owner bookkeeping, and finally installs the fd. Every earlier failure path unwinds fd, task, context, PMU context, and event references in reverse order.

Kernel counter creation is a smaller version of `perf_event_open()`: it rejects AUX grouping modes, allocates the event under PMU SRCU, marks it kernel-owned, finds context and PMU context, validates CPU online/exclusive state, installs the event, and returns the `struct perf_event *` directly.

Task inheritance runs during fork initialization. `perf_event_init_task()` initializes per-task perf fields and calls `perf_event_init_context()` when the parent has a perf context. The parent context is pinned and locked, pinned groups are inherited first, flexible rotation is temporarily disabled while flexible groups are inherited, and a fully inherited child context is marked as a clone of the parent or parent's parent. `inherit_event()` resolves inherited children back to the original parent event, allocates a child event against the child task, attaches it to the child context, links it under the parent event's `child_mutex`, clones active/off state and frequency period, and sets `PERF_ATTACH_CHILD`.

Task exit reverses the relationship. `perf_event_exit_task()` removes owner entries with a release store on `event->owner`, tears down the task context, emits task exit side-band records for task and CPU contexts, and detaches perf context data. `perf_event_exit_task_context()` pins and locks the context, schedules events out, detaches the context from the task by setting `TASK_TOMBSTONE`, optionally emits `PERF_RECORD_EXIT`, exits every event, and waits for references during failed-fork cleanup. Child events sync counts back to parents before removal.

CPU hotplug and boot initialization maintain global CPU masks and contexts. `perf_event_init_all_cpus()` allocates topology masks and initializes per-CPU software tables, side-band lists, scheduling callback lists, and CPU contexts. CPU online allocates missing software hash lists, updates representative CPU masks per PMU scope, and marks the CPU context online. CPU offline clears CPU masks, migrates scoped PMU events to replacement CPUs when possible, schedules out remaining context events on the dead CPU, and marks the CPU context offline. Reboot iterates online CPUs through the same exit path.

## State and Persistence Behavior

Most sample and record objects are stack-local and transient. Side-band record structures, `perf_sample_data`, raw trace records, hrtimer sample data, and overflow-local state are constructed per event and are committed only to perf ring buffers or discarded on reservation failure.

`struct perf_event` is persistent until its fd/kernel reference and all inherited/async references are dropped. This chunk initializes its list nodes, locks, refcounts, id, namespace, target task, owner, PMU pointer, context pointer, PMU context pointer, hardware sampling period, output handler, BPF program pointer, address filters, AUX relationships, and capability bits. Error paths rely on `put_event()`/`free_event()` and destroy callbacks to undo partially initialized state.

PMU state persists globally after registration. `pmu_idr` maps type ids to PMUs; `pmus` is the RCU-discovered PMU list; `pmu->cpu_pmu_context` stores per-CPU PMU contexts; `pmu->events` tracks events for unregister detachment. Sysfs devices under the `event_source` bus persist after `perf_event_sysfs_init()` and are freed by `perf_pmu_free()` on unregister.

Software-event hash tables are per-CPU and refcounted. `swevent_hlist_get()` allocates per-CPU lists while the PMU is in use; event add/delete mutates hash buckets; `swevent_hlist_put()` releases the lists via `kfree_rcu()` once the last software event for that class is gone. Static keys in `perf_swevent_enabled[]` are incremented/decremented with parent software events.

Global counters such as `nr_mmap_events`, `nr_build_id_events`, `nr_comm_events`, `nr_namespaces_events`, `nr_cgroup_events`, `nr_task_events`, `nr_freq_events`, `nr_switch_events`, `nr_ksymbol_events`, `nr_bpf_events`, and `nr_text_poke_events` persist while parent events exist. `account_event()` also manages `perf_sched_count` and enables the `perf_sched_events` static branch before events that require scheduler hooks become visible.

Address filters persist on parent events in `event->addr_filters.list` plus hardware-ready ranges in `event->addr_filter_ranges`. File path filters hold path references; `free_filters_list()` drops them. Children share filter definitions through parent lookup but can carry cloned ranges valid until exec.

Inherited events persist in the child context and are linked into the original parent event's `child_list`. Counts and total enabled/running time are folded into parent child counters on exit when `PERF_ATTACH_CHILD` remains set. Orphaned parent events suppress new inheritance and release existing children during event teardown.

Task contexts persist in `task->perf_event_ctxp` until exit or failed fork cleanup. Exit marks `ctx->task = TASK_TOMBSTONE` and clears the RCU pointer so new creation sees a dead context. Clone contexts track `parent_ctx` and generation to optimize context switching until uncloned.

CPU and topology masks persist for PMU-scope routing. `perf_online_mask` and scope masks for core/die/cluster/package/system-wide define representative CPUs for scoped PMUs and are updated on CPU online/offline, with event migration if a representative CPU disappears.

Cgroup perf state persists in `struct perf_cgroup` objects allocated by the cgroup subsystem, with per-CPU `perf_cgroup_info` storage and attach callbacks that switch tasks into their new perf cgroup accounting state.

## Dependencies and Integration Points

- Ring-buffer output: `perf_output_begin()`, `perf_output_put()`, `__output_copy()`, `perf_event__output_id_sample()`, `perf_output_end()`, output handlers, fasync wakeups, and mmap mutex/refcount rules.
- PMU driver callbacks: `event_init`, `add`, `del`, `start`, `stop`, `read`, `pmu_enable`, `pmu_disable`, transaction callbacks, `check_period`, `event_idx`, `addr_filters_validate`, `event_unmapped`, capabilities flags, scope, module refs, and attr groups.
- BPF integration: `BPF_PROG_TYPE_PERF_EVENT` overflow programs, tracepoint/kprobe/uprobe program attachment, trace call BPF filters, BPF cookies, program refcounts, sleepable program checks, writable kprobe context checks, and tracepoint max-context-offset validation.
- Tracing integration: ftrace profile filters, tracepoint raw records, trace event flags, syscall tracepoint detection, kprobe/uprobe PMUs, probe destroy/init hooks, and trace buffer metadata updates.
- Scheduler and task lifecycle: scheduler static branches, task work for `sigtrap`, `exec_update_lock`, task context pinning, fork inheritance, exit notifications, owner lists, `TASK_TOMBSTONE`, and delayed put hooks.
- CPU hotplug and topology: `perf_online_mask`, topology sibling/die/cluster/core masks, CPU PMU contexts, online/offline state, CPU function calls, and reboot notifier ordering.
- Cgroup integration: cgroup fd connection for events, `perf_event_cgroup()` side-band records, cgroup task attach movement, and `CONFIG_CGROUP_PERF` sample-type gating.
- Security and privilege: `security_perf_event_open()`, `security_perf_event_alloc()`, `security_locked_down(LOCKDOWN_PERF)`, `perf_allow_kernel()`, `perfmon_capable()`, `capable(CAP_SYS_ADMIN)`, `CAP_KILL`, `ptrace_may_access()`, and branch/kernel data leakage checks.
- Userspace ABI: `perf_event_open(2)`, `perf_event_attr` size compatibility, anonymous inode perf fds, group and output fd flags, clock ids, sample/read/branch format masks, signal trap semantics, address-filter strings, and PMU sysfs attributes.
- Memory management: file path lookup and VMA scanning for filters, `get_task_mm()`, `mmap_read_lock()`, RCU/SRCU protection, kfree_rcu, per-CPU allocation, idr allocation, and module refs.
- Existing perf core helpers from earlier/later chunks: context lookup/install/remove, event scheduling, group iteration, ring-buffer attach, AUX event pairing, callchain buffers, exclusive events, mediated PMU accounting, sample header sizing, free-event cleanup, and side-band event iteration.

## Risks and Edge Cases

- Overflow handling is concurrency-sensitive. Hardware PMIs enter with interrupts disabled, software events disable IRQs around active-state checks, and event removal depends on this serialization. Missing these constraints can race `perf_event_release_kernel()` or `perf_remove_from_context()` and lead to use-after-free.
- `event_limit` and `pending_kill` handling combine wakeups, in-atomic disable, and PMU stop. Incorrect ordering can lose `POLL_HUP`, leave an event running after its limit, or stop a PMU event while still delivering samples.
- `sigtrap` overflow delivery depends on task-work queuing and `pending_work` uniqueness. The code hashes the interrupted IP to detect repeated kernel overflows before userspace progress; false assumptions here can miss duplicate signals or warn spuriously.
- BPF overflow programs run under recursion protection and RCU. Attaching the wrong program type, allowing stack collection with incompatible precise IP settings, or mishandling program refs on inherited events would be a correctness and lifetime risk.
- Software-event period arithmetic uses signed `period_left` and cmpxchg loops. Off-by-one or overflow errors can generate extra samples, suppress expected samples, or leave hrtimer events in a stuck state.
- Software event hash-list allocation is per possible CPU and reference counted. Partial allocation failure must roll back earlier CPUs; hotplug allocation must handle nonzero refcounts and missing lists.
- Tracepoint target-task delivery cannot deliver synchronous signals to another task. Reusing normal signal paths there would be semantically wrong and potentially unsafe.
- Address-filter parsing is stateful and manually tokenized. Invalid state transitions, forgotten `filename` cleanup, failure to reset `nr_file_filters`, or accepting file filters for CPU-wide events could leak references or install unsupported filters.
- `perf_event_set_filter()` deliberately drops `ctx->mutex` for tracing filters to avoid ftrace deadlock. Code around this path must not assume the event context cannot move during the unlocked interval.
- Hrtimer cancellation cannot use `hrtimer_cancel()` from the hrtimer callback path; `perf_swevent_cancel_hrtimer()` uses `hrtimer_try_to_cancel()` and relies on `PERF_HES_STOPPED` for eventual stop. Changing this can deadlock CPU/task clock events.
- PMU registration publishes only after initialization through idr placeholder replacement. Publishing earlier would allow `perf_try_init_event()` to call incomplete callbacks or see missing per-CPU contexts.
- PMU unregistration must synchronize both SRCU and regular RCU because PMU discovery uses both. Detaching events before those grace periods risks handling partially constructed events or racing creation.
- `event_unmapped` PMUs cannot be force-unregistered while events remain because `perf_mmap_close()` needs PMU callbacks. The busy rollback path must restore idr/list visibility correctly.
- `perf_try_init_event()` temporarily sets `event->pmu` before `event_init()`. Every failure path must clear it and drop the module ref; destroy callbacks must only run after successful `event_init()`.
- PMU scope handling depends on topology masks and representative CPUs. CPU hotplug must migrate scoped PMU events before scheduling out the old CPU context, or reads can target offline representatives.
- `perf_event_alloc()` has many partially initialized resources: target task refs, PMU refs, cgroup refs, exclusive state, address-filter ranges, callchain buffers, security state, mediated accounting, and global counters. Cleanup must remain symmetric with allocation order.
- Inherited events cannot form recursive parent chains; `inherit_event()` collapses to the original parent. Breaking this can produce deep hierarchies and incorrect child count aggregation.
- Group migration in `perf_event_open()` is a point-of-no-return operation. Siblings are installed before leaders so leaders do not activate groups with siblings still in an old context. Reordering can schedule inconsistent groups.
- `perf_event_set_output()` must hold both mmap mutexes in stable address order. Missing the double-lock rule can deadlock, and missing ring-buffer mmap-count rechecks can attach to a closing buffer.
- Clock selection rejects non-NMI-safe clocks for PMUs that can sample in NMI. Allowing realtime/boottime/TAI clocks for NMI PMUs can call unsafe timekeeping code from NMI context.
- `perf_copy_attr()` is a security boundary. New sample, read, branch, or reserved bits must be validated here or userspace can smuggle unsupported ABI state into later PMU code.
- Task exit uses release ordering when clearing `event->owner` after list deletion. Weakening this can race `perf_release()` owner serialization.
- Failed fork cleanup waits for event/context references because `copy_process()` can free the task regardless of references. Removing this wait risks use-after-free from `_free_event()` target-task puts.
- Cgroup attach uses `task_function_call()` with preemption disabled in the target task. Incorrect context assumptions can leave perf cgroup state stale across migration.

## Test Signals

- Side-band tests should validate `PERF_RECORD_TEXT_POKE` size/padding/id sample layout, no output when `nr_text_poke_events` is zero, `PERF_RECORD_ITRACE_START` single emission after attach-state update, and `PERF_RECORD_AUX_OUTPUT_HW_ID` output from a PMU driver.
- Overflow tests should cover non-sampling PMI folding, max-samples-per-tick throttling, frequency period adjustment, event-limit `POLL_HUP`, AUX pause/resume, BPF program suppression of output, fasync wakeups, and hrtimer `HRTIMER_NORESTART` on overflow disable.
- `sigtrap` tests should cover task-only requirement, `remove_on_exec` requirement, `CAP_KILL`/ptrace permission fallback, valid sample address capture, duplicate pending work, and kernel-excluded events overflowing before userspace progress.
- Software-event tests should cover recursion context rejection, per-CPU hlist allocation rollback, add/delete RCU visibility, stopped/exclude filtering, sample-period fast path for period one, `PERF_SAMPLE_PERIOD`, frequency conversion in hrtimer init, and static-key refcounting on destroy.
- Tracepoint/probe tests should cover BPF trace filter suppression, tracepoint raw-data sample reset between events, target-task delivery, ftrace filter set while dropping `ctx->mutex`, kprobe/uprobe privilege checks, retprobe/ref-counter config parsing, and branch-stack rejection for tracing/probe PMUs.
- BPF attachment tests should cover generic perf-event BPF handlers, tracing event program type mismatches, sleepable kprobe allowed only for uprobes, kprobe override only on kprobes, writable context only on uprobes, tracepoint max context offset rejection, inherited BPF program refcounts, and detach paths.
- Address-filter tests should cover valid kernel ranges, valid file ranges on per-task events, `filter` with zero size rejection, invalid token order, missing filename, non-regular path, CPU-wide file filter rejection, PMU validation failure cleanup, filter replacement, child range application, VMA remap updates, and `nr_file_filters` reset on parse failure.
- PMU registration tests should cover anonymous-name rejection, invalid scope rejection, fixed type id mismatch warnings, sysfs device allocation failure cleanup, per-CPU PMU context allocation failure cleanup, default transaction stubs for `pmu_enable`, default no-op callbacks, idr publication, and unregister with active events.
- PMU unregister tests should cover creation blocked after idr removal, SRCU/RCU synchronization, `event_unmapped` busy rollback, detaching BPF programs and address filters, destroy callback invocation once, PMU context release, module put, and event list empty wait.
- Attribute ABI tests should cover short and oversize `perf_event_attr`, reserved field rejection, invalid sample/read/branch masks, branch privilege propagation and permission checks, register masks, user stack alignment/size, cgroup sample support off, weight field exclusivity, `inherit_thread` without `inherit`, `remove_on_exec` with `enable_on_exec`, and `sigtrap` without `remove_on_exec`.
- `perf_event_open()` tests should cover invalid flags, kernel sampling permission, namespace privilege, sample frequency/period bounds, physical-address permission, lockdown for interrupt regs, cgroup pid/cpu constraints, bad group fds, revoked group leaders, `FD_OUTPUT`/`FD_NO_GROUP`, target task lookup, inherit mismatch, sampling on `NO_INTERRUPT` PMUs, clock id safety, dead contexts, offline CPUs, recursive groups, cross-CPU groups, cross-context groups, pinned/exclusive siblings, hardware/software group migration, output redirection failures, sample size overflow, AUX pairing failure, exclusive install busy, anon inode failure, and full error unwinding.
- Kernel counter tests should cover AUX rejection, CPU offline rejection, exclusive busy rejection, task versus per-CPU context creation, kernel owner marking, custom overflow handler propagation, and cleanup on PMU context failure.
- Inheritance tests should cover `inherit` disabled, `inherit_thread` with and without `CLONE_THREAD`, `sigtrap` plus `CLONE_CLEAR_SIGHAND`, orphaned parent suppression, original-parent flattening, active/off state inheritance, frequency period cloning, AUX sibling pairing, cloned context parent generation, and failed-fork teardown.
- Task exit tests should cover owner list release ordering, child count/time aggregation with `inherit_stat`, parent wakeups, task context tombstone behavior, `PERF_RECORD_EXIT` ordering before further samples, CPU-context exit records, detach of perf context data, and wait for references in `perf_event_free_task()`.
- CPU hotplug tests should cover software hlist creation on online, scope mask representative selection at boot and after hotplug, PMU context migration from removed representative CPUs, scheduling out remaining events on offline CPUs, `cpuctx->online` gating for event creation, and reboot notifier ordering.
- Sysfs/cgroup tests should cover PMU bus registration after early PMU registration, PMU device creation for preexisting PMUs, visibility of `nr_addr_filters` and `cpumask`, mux interval store updating all online CPU PMU contexts, event string show output, cgroup css allocation/free failure paths, cgroup online side-band records, and cgroup attach switching tasks.

## Chunk Boundary Notes

This chunk is the main event creation and lifecycle section of `core.c`, but it relies on earlier/later code for context scheduling internals, ring-buffer implementation, event file operations, `_free_event()` cleanup, mmap handling, AUX buffer management, callchain storage, PMU context reference helpers, cgroup switching details, and side-band record iteration. The final per-file research should merge this with surrounding chunks so `perf_event_open()`, PMU registration, overflow delivery, task inheritance, and CPU hotplug are described as one continuous perf-core lifecycle.
