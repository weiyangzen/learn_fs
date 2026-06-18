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
