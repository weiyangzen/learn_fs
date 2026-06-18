# Research: subset-b-005914

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sbitmap.h -->
# sources/distributed-fs/ceph-client/include/linux/sbitmap.h

Purpose: declares the scalable bitmap and bitmap-queue interfaces used by high-concurrency allocators, especially block multiqueue tag maps, where a single cacheline bitmap would become a contention point.

Important APIs and types: `struct sbitmap_word`, `struct sbitmap`, `struct sbitmap_queue`, `struct sbq_wait_state`, and `struct sbq_wait` define the bitmap, deferred-clear mask, per-CPU allocation hints, wait queues, and waiter accounting. Core APIs include `sbitmap_init_node()`, `sbitmap_resize()`, `sbitmap_get()`, `sbitmap_put()`, `sbitmap_weight()`, debug show helpers, `sbitmap_queue_init_node()`, `__sbitmap_queue_get()`, batch/shallow allocation helpers, `sbitmap_queue_clear()`, wake helpers, and wait-queue wrappers.

Control flow: allocation searches set bits across cacheline-separated words using per-CPU hints unless strict round-robin is requested. Freeing uses `cleared` masks first, then deferred clear/swap logic in the implementation returns bits to `word`; queue users sleep on rotating wait queues and are woken in batches after completions.

State and persistence: all state is in-memory and lifetime-bound to the initialized bitmap or queue. Persistent behavior is limited to counters and hints that affect allocation locality, fairness, and wake batching.

Dependencies and integration points: depends on bitops, atomics, percpu storage, raw spinlocks, wait queues, and seq_file debug output. It integrates with block-layer tag allocation and any subsystem needing scalable bounded-resource IDs.

Risks and test signals: risks include missed wakeups when shallow depth is not registered, stale per-CPU hints after resize, memory-ordering regressions around successful acquire allocation, deferred-clear races, and starvation with round-robin changes. Test with concurrent get/put stress, queue exhaustion/wakeup tests, resize tests, shallow-depth coverage, CPU hotplug/preemption scenarios, and debugfs bitmap output sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sbitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/scatterlist.h -->
# sources/distributed-fs/ceph-client/include/linux/scatterlist.h

Purpose: defines Linux scatter-gather list entries and helpers for representing non-contiguous memory as DMA, block I/O, crypto, networking, or driver transfer segments.

Important APIs and types: `struct scatterlist`, `struct sg_table`, `struct sg_append_table`, `struct sg_page_iter`, `struct sg_dma_page_iter`, and `struct sg_mapping_iter` are the main types. Helpers include `sg_set_page()`, `sg_set_folio()`, `sg_set_buf()`, `sg_page()`, `sg_next()`, chain/end marker helpers, DMA accessors, allocation/free routines, table-from-pages builders, split/copy/zero helpers, page iterators, and mapping iterators.

Control flow: callers initialize entries or tables, optionally chain multiple chunks, pass them through DMA mapping, then iterate either by SG entry, mapped DMA entry, page, or temporary mapped page window. Low bits of `page_link` encode chain and end markers, so access must go through helpers.

State and persistence: SG state is transient in-kernel transfer metadata: page pointer, offset, length, DMA address/length, optional DMA flags, and table entry counts. It does not persist data; it describes memory ownership and mapping state that callers must unmap/free correctly.

Dependencies and integration points: depends on MM page/folio helpers, DMA address types, architecture I/O, SWIOTLB/bus-address flags, and optional SG pools. It is a central contract between memory buffers and DMA-capable subsystems.

Risks and test signals: risks include direct page pointer assignment corrupting marker bits, using `orig_nents` instead of DMA `nents` after mapping, chained-list termination bugs, highmem mapping misuse, bounced segment cleanup mistakes, and length truncation in folio helpers. Test with chained and unchained tables, DMA-map/unmap users, highmem mappings, SG copy/zero operations, page iterator offsets, and DEBUG_SG builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/scatterlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched.h -->
# sources/distributed-fs/ceph-client/include/linux/sched.h

Purpose: declares `task_struct`, task states, scheduling entities, scheduler entry points, wakeup/affinity APIs, reschedule helpers, task flags, and migrate-disable machinery used throughout the kernel.

Important APIs and types: task state constants, `struct task_struct`, `struct sched_entity`, `struct sched_rt_entity`, `struct sched_dl_entity`, `struct sched_avg`, `struct sched_statistics`, `struct uclamp_se`, `struct wake_q_node`, PF/PFA task flags, `schedule*()`, `io_schedule*()`, `wake_up_process()`, `wake_up_state()`, `set_cpus_allowed_ptr()`, scheduler policy setters, `cond_resched*()`, thread-flag helpers, and `migrate_disable()/migrate_enable()` form the main surface.

Control flow: tasks update `__state` through barrier-aware macros before sleeping, wakeups test compatible states and set runnable state, scheduling classes consume embedded fair/RT/deadline/ext entities, and affinity/migration APIs coordinate CPU masks with runqueue locks. Cond-resched paths add voluntary scheduling points, while migrate-disable pins current execution until the nesting counter returns to zero.

State and persistence: `task_struct` is the kernel’s live per-task state container: scheduling state, CPU masks, signal/parentage, credentials, MM/files/fs pointers, timers, accounting, tracing/debug state, cgroup hooks, fault counters, and architecture thread state. It persists only for task lifetime and is heavily config-dependent.

Dependencies and integration points: integrates scheduler core with MM, signals, credentials, pid namespaces, cgroups, RCU, futexes, perf, tracing, BPF, seccomp, block I/O, POSIX timers, NUMA balancing, and arch thread code.

Risks and test signals: high-risk areas are memory barriers in sleep/wakeup, task state reporting ABI, `task_struct` layout assumptions, PREEMPT_RT saved-state handling, affinity races, lazy TLB/membarrier interactions, proxy-exec blocked-on state, and migrate-disable imbalance. Test with scheduler selftests, lockdep/RCU/KCSAN, fork/exit/exec stress, CPU hotplug, RT configs, cgroup movement, signal-heavy workloads, and BPF/perf/tracing builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/affinity.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/affinity.h

Purpose: compatibility include that exposes the scheduler affinity API by including `linux/sched.h`.

Important APIs and types: this file defines no new symbols; users get affinity helpers such as `set_cpus_allowed_ptr()`, `sched_setaffinity()`, `sched_getaffinity()`, and task CPU-mask fields from `sched.h`.

Control flow: including this header forwards compilation to the central scheduler header. Runtime behavior belongs to the affinity code declared there.

State and persistence: no state is owned here.

Dependencies and integration points: the dependency is intentionally broad because it pulls `linux/sched.h`. It preserves include-path compatibility for code that wants an affinity-themed header.

Risks and test signals: risk is header dependency churn or circular include exposure. Compile-test users that include only `sched/affinity.h` for affinity declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/affinity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/autogroup.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/autogroup.h

Purpose: declares optional scheduler autogroup hooks that group interactive tasks by session for fair scheduling, plus root task-group exposure for cgroup scheduler builds.

Important APIs and types: `sched_autogroup_create_attach()`, `sched_autogroup_detach()`, `sched_autogroup_fork()`, `sched_autogroup_exit()`, `sched_autogroup_exit_task()`, proc show/set-nice helpers, and `root_task_group` are the exported contracts. Disabled configs compile to no-op stubs.

Control flow: fork/session/exit paths call these hooks to create, attach, detach, and release signal-struct autogroups; procfs can display or tune autogroup nice values.

State and persistence: autogroup state lives in scheduler and `signal_struct` fields, not in this header. It is runtime-only and tied to task/session lifetime.

Dependencies and integration points: integrates process lifetime, procfs, `signal_struct`, and CFS group scheduling. It relies on `CONFIG_SCHED_AUTOGROUP`, `CONFIG_PROC_FS`, and `CONFIG_CGROUP_SCHED`.

Risks and test signals: risks include missing no-op parity, lifecycle leaks on fork/exit failures, and proc tuning races. Test with autogroup enabled/disabled builds, session creation, task exit, proc reads/writes, and CFS group scheduling configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/autogroup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/clock.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/clock.h

Purpose: declares scheduler clock interfaces that provide fast runtime timestamps for scheduler accounting, tracing, and CPU-local timing.

Important APIs and types: `sched_clock()`, `sched_clock_noinstr()`, `running_clock()`, `sched_clock_cpu()`, `sched_clock_init()`, `sched_clock_tick()`, idle sleep/wakeup hooks, `cpu_clock()`, `local_clock()`, `local_clock_noinstr()`, clock stability controls, and IRQ-time accounting toggles are exported or stubbed by config.

Control flow: architecture or generic clock code initializes the source, scheduler/timer paths tick or mark idle transitions, and consumers choose local or CPU-specific clocks depending on monotonicity and instrumentation constraints.

State and persistence: clock stability, offsets, and per-CPU clock accounting live in scheduler clock implementation. The values are volatile runtime time sources, not persistent state.

Dependencies and integration points: depends on SMP and optional unstable/generic scheduler clock configs. Integrates scheduler accounting, tracing, idle/nohz, IRQ time accounting, and architecture clock sources.

Risks and test signals: risks include comparing clocks across CPUs, using `sched_clock()` where monotonicity is required, noinstr violations, unstable-clock drift, and IRQ-time opt-in overhead. Test with clocksource changes, suspend/idle, NOHZ, IRQ accounting, tracing noinstr validation, and multi-CPU timestamp monotonicity expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/cond_resched.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/cond_resched.h

Purpose: compatibility include for conditional reschedule helpers.

Important APIs and types: the file defines no new symbols; it exposes `cond_resched()`, `cond_resched_lock()`, and rwlock variants from `linux/sched.h`.

Control flow: callers include this narrow header but compile against the central scheduler declarations. Actual voluntary preemption behavior is implemented through `sched.h` and scheduler core.

State and persistence: no state is stored here.

Dependencies and integration points: depends entirely on `linux/sched.h`; useful for code that wants to name the latency-reduction dependency explicitly.

Risks and test signals: risk is include bloat or circular inclusion after scheduler header refactors. Compile-test source files including this header alone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/cond_resched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/coredump.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/coredump.h

Purpose: declares dumpability constants and helpers for reading/updating `mm_struct` coredump policy bits.

Important APIs and types: `SUID_DUMP_DISABLE`, `SUID_DUMP_USER`, `SUID_DUMP_ROOT`, `__mm_flags_get_dumpable()`, `__mm_flags_set_mask_dumpable()`, `set_dumpable()`, `__get_dumpable()`, and `get_dumpable()` are the main symbols.

Control flow: exec, credential, proc, and coredump paths set or inspect dumpability through `mm->flags`; callers must distinguish `SUID_DUMP_USER` from other nonzero modes because root-owned setuid dumping has different semantics.

State and persistence: state is the dumpability bitfield inside a live `mm_struct`. It lasts for the address-space lifetime and influences coredump and ptrace/proc access behavior.

Dependencies and integration points: depends on MM flag helpers and integrates scheduler task/MM code with coredump, exec, credentials, and security decisions.

Risks and test signals: risks include treating dumpability as boolean, mask drift in MM flags, and incorrect privilege-transition updates. Test setuid/exec transitions, `/proc/sys/fs/suid_dumpable`, coredump generation, ptrace/proc access checks, and mm flag helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/coredump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/cpufreq.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/cpufreq.h

Purpose: defines the scheduler-to-cpufreq utilization update hook interface used by governors such as schedutil.

Important APIs and types: `SCHED_CPUFREQ_IOWAIT`, `struct update_util_data`, `cpufreq_add_update_util_hook()`, `cpufreq_remove_update_util_hook()`, `cpufreq_this_cpu_can_update()`, `map_util_freq()`, and `map_util_perf()` are exported when CPU frequency support is enabled.

Control flow: cpufreq code registers a per-CPU callback; scheduler utilization updates invoke it with timestamp and flags, including I/O wait boost signals. Mapping helpers translate scheduler utilization/capacity into frequency or performance requests.

State and persistence: hook state is per-CPU runtime callback data owned by cpufreq/scheduler code. No persistent policy is stored here.

Dependencies and integration points: integrates scheduler PELT utilization, CPU capacity, and cpufreq policy updates. Depends on `CONFIG_CPU_FREQ` and cpufreq policy definitions.

Risks and test signals: risks include stale per-CPU hooks during policy teardown, divide-by-zero capacity assumptions, I/O wait flag mishandling, and cross-CPU update races. Test schedutil governor behavior, hotplug, policy changes, I/O wait workloads, and CPU_FREQ disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/cpufreq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/cputime.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/cputime.h

Purpose: declares task and thread-group CPU time accounting helpers, adjusted cputime APIs, POSIX CPU timer integration, and paravirtual steal-time hooks.

Important APIs and types: `task_cputime()`, `task_gtime()`, `task_cputime_scaled()`, `task_cputime_adjusted()`, `thread_group_cputime_adjusted()`, `cputime_adjust()`, `thread_group_cputime()`, `thread_group_sample_cputime()`, `get_running_cputimer()`, group accounting helpers, `prev_cputime_init()`, `task_sched_runtime()`, and optional paravirt steal-clock static calls are central.

Control flow: tick/accounting paths accumulate per-task user/system/guest time, optionally update active POSIX thread-group cputimers, and expose adjusted monotonic values to proc/resource/timer consumers. Generic virtual CPU accounting may compute live values instead of reading stored fields.

State and persistence: state lives in `task_struct`, `signal_struct`, `prev_cputime`, and atomic thread-group counters. It persists for task/thread-group lifetime and is folded into exit accounting.

Dependencies and integration points: depends on `sched/signal.h`, POSIX timers, virtual CPU accounting, scaled cputime arch support, and paravirt steal time. It bridges scheduler runtime accounting with procfs, rusage, and CPU timers.

Risks and test signals: risks include non-monotonic adjusted time, accounting after `__exit_signal()`, active timer races, guest/steal time drift, and config fallback differences. Test CPU timer expiry, `/proc` stat fields, rusage, virtual accounting configs, paravirt guests, and thread exit while timers are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/cputime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/deadline.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/deadline.h

Purpose: provides SCHED_DEADLINE classification helpers and root-domain bandwidth accounting hooks.

Important APIs and types: `dl_prio()`, `dl_task()`, `dl_time_before()`, `dl_add_task_root_domain()`, `dl_clear_root_domain()`, `dl_clear_root_domain_cpu()`, `dl_task_needs_bw_move()`, `dl_bw_visited()`, `dl_server()`, `dl_task_of()`, and `dl_is_implicit()` are the key symbols.

Control flow: scheduler and cpuset affinity paths use these helpers to identify deadline-priority tasks, compare wrapping deadlines, move bandwidth accounting between root domains, and distinguish real tasks from deadline server entities.

State and persistence: state is embedded in `sched_dl_entity` and root-domain bandwidth data elsewhere. The header only classifies and declares accessors.

Dependencies and integration points: depends on `sched.h`, root domains, cpusets, and deadline scheduler internals.

Risks and test signals: risks include confusing policy with PI-boosted priority, incorrect root-domain bandwidth moves during affinity changes, and treating deadline server entities as tasks. Test deadline admission, cpuset moves, affinity shrink/expand, PI boosting, and deadline server configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/deadline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/debug.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/debug.h

Purpose: declares task, CPU, register, stack, proc-scheduler, and scheduler-text debugging interfaces.

Important APIs and types: `dump_cpu_task()`, `show_state_filter()`, `show_state()`, `show_regs()`, `show_stack()`, `sched_show_task()`, `proc_sched_show_task()`, `proc_sched_set_task()`, `__sched`, scheduler text section boundaries, and `in_sched_functions()` are exported.

Control flow: diagnostics call these helpers to dump task state or stack traces, procfs displays per-task scheduler details, and wchan logic filters addresses in scheduler text.

State and persistence: this header owns no state. It exposes debug output over live task/register/scheduler state.

Dependencies and integration points: integrates scheduler core with procfs, stack unwinding, register dump code, linker sections, and hang/debug paths.

Risks and test signals: risks include unsafe stack reads, misleading wchan filtering after section changes, proc output drift, and log noise in panic/hung-task paths. Test SysRq task dumps, hung-task output, proc scheduler files, stack traces on supported architectures, and linker section placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/ext.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/ext.h

Purpose: declares the BPF extensible scheduler class data structures, dispatch queue IDs, task state flags, and diagnostic hooks.

Important APIs and types: `SCX_SLICE_*`, built-in `SCX_DSQ_*` IDs, `struct scx_dispatch_q`, `struct scx_dsq_pcpu`, `struct scx_dsq_list_node`, `struct sched_ext_entity`, `struct scx_task_group`, task/DSQ flag enums, `INIT_DSQ_LIST_CURSOR()`, `sched_ext_dead()`, `print_scx_info()`, and lockup/stall hooks are central.

Control flow: when `CONFIG_SCHED_CLASS_EXT` is enabled, each task embeds `sched_ext_entity`; BPF schedulers enqueue tasks into built-in or user dispatch queues, manipulate slices and virtual time, and transition task states through init/ready/enabled/dead. Disabled configs provide no-op diagnostics.

State and persistence: runtime state includes per-task SCX fields, dispatch queues, DSQ sequence numbers, RCU/hash/list membership, cgroup SCX metadata, and BPF-modifiable slice/vtime fields. It exists only while the scheduler and tasks are alive.

Dependencies and integration points: depends on BPF scheduler infrastructure, rhashtable, RCU, cgroups, core scheduling, and scheduler class integration. It is the header-level contract between scheduler core and sched_ext implementation/BPF programs.

Risks and test signals: risks include DSQ ordering corruption if vtime changes while queued, task state transition races, RCU lifetime errors, bypass-mode starvation, cgroup migration drift, and lockup diagnostics missing SCX state. Test sched_ext selftests, BPF scheduler load/unload, task fork/exit, cgroup moves, DSQ iteration, preemption/kick behavior, and disabled-config stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/ext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/hotplug.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/hotplug.h

Purpose: declares scheduler callbacks used by CPU hotplug state transitions.

Important APIs and types: `sched_cpu_starting()`, `sched_cpu_activate()`, `sched_cpu_deactivate()`, optional `sched_cpu_wait_empty()`, optional `sched_cpu_dying()`, and `idle_task_exit()` form the interface.

Control flow: CPU hotplug core invokes scheduler hooks as CPUs start, become active, deactivate, drain runnable tasks, and die. Non-hotplug builds provide NULL hooks for unavailable phases.

State and persistence: state lives in runqueues, scheduler domains, and idle tasks, not in this header. It is runtime CPU topology state.

Dependencies and integration points: integrates CPU hotplug with scheduler runqueue activation, migration, and idle-task lifecycle.

Risks and test signals: risks include tasks left on deactivated CPUs, incorrect NULL hook use, and scheduler-domain mismatch after hotplug. Test CPU online/offline loops, hotplug under load, RT/deadline tasks during teardown, and no-hotplug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/hotplug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/idle.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/idle.h

Purpose: declares idle-state helpers and polling-thread flag operations used to avoid unnecessary reschedule IPIs.

Important APIs and types: `enum cpu_idle_type`, `wake_up_if_idle()`, `current_set_polling_and_test()`, `current_clr_polling_and_test()`, `current_clr_polling()`, and low-level polling bit setters/clearers are the main symbols.

Control flow: idle loops mark the current task as polling, test `TIF_NEED_RESCHED`, and clear polling before leaving idle. Memory barriers pair with remote `resched_curr()` so reschedule state is visible and IPIs are not lost.

State and persistence: state is the current thread-info polling flag and need-resched state. It is transient per idle-loop entry.

Dependencies and integration points: depends on `sched.h`, thread-info flags, preempt folding, and architecture bitops. It integrates scheduler idle handling with interrupt/IPI avoidance.

Risks and test signals: risks include missing barriers causing lost wakeups, incorrect fallback when `TIF_POLLING_NRFLAG` is absent, and arch bitop instrumentation differences. Test idle wake latency, NOHZ idle, reschedule IPIs, PREEMPT configs, and architectures with/without polling flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/idle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/init.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/init.h

Purpose: declares scheduler initialization entry points.

Important APIs and types: `sched_init()` and `sched_init_smp()` are the only exported prototypes.

Control flow: boot code calls early scheduler initialization, then SMP scheduler initialization once CPU topology and multiprocessor setup are ready.

State and persistence: scheduler runqueues, domains, classes, and boot tasks are initialized by implementation code; this header owns no state.

Dependencies and integration points: integrates kernel boot sequencing with scheduler core and SMP bring-up.

Risks and test signals: risks are ordering regressions with CPU/topology initialization. Test boot on UP/SMP configurations, early initcall ordering, and CPU hotplug after boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/isolation.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/isolation.h

Purpose: defines housekeeping CPU types and APIs for CPU isolation, nohz_full, managed IRQ isolation, and partition-aware scheduler domains.

Important APIs and types: `enum hk_type`, `housekeeping_overridden`, `housekeeping_any_cpu()`, `housekeeping_cpumask()`, `housekeeping_enabled()`, `housekeeping_affine()`, `housekeeping_test_cpu()`, `housekeeping_update()`, `housekeeping_init()`, `housekeeping_cpu()`, and `cpu_is_isolated()` are central.

Control flow: boot-time isolation and cpuset partition updates compute masks; kernel subsystems query housekeeping CPUs for timers, RCU, workqueues, managed IRQs, scheduler domains, and noise avoidance. Disabled configs return all CPUs as housekeeping.

State and persistence: housekeeping masks are runtime topology policy derived from boot parameters and cpuset isolation. They persist until updated by isolation mechanisms.

Dependencies and integration points: depends on cpumasks, tick/nohz, init, static keys, and `task_struct` affinity. It integrates scheduler domains with IRQ, timer, RCU, workqueue, and CPU isolation subsystems.

Risks and test signals: risks include scheduling kernel work onto isolated CPUs, stale masks after cpuset changes, alias confusion among housekeeping types, and disabled-config semantic drift. Test `isolcpus`, `nohz_full`, managed IRQ affinity, cpuset isolated partitions, and housekeeping queries on all configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/isolation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/jobctl.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/jobctl.h

Purpose: defines `task_struct.jobctl` flags and helper prototypes for job control stops, ptrace traps, and freezer-related stop states.

Important APIs and types: `JOBCTL_*` bit definitions, stop/trap/pending masks, `task_set_jobctl_pending()`, `task_clear_jobctl_trapping()`, and `task_clear_jobctl_pending()` are the key exports.

Control flow: signal and ptrace code sets pending stop/trap bits under signal locks, tasks consume them while entering stopped/traced states, and wakeup paths inspect `JOBCTL_STOPPED`/`JOBCTL_TRACED`.

State and persistence: state is the per-task `jobctl` bitfield, protected primarily by `sighand->siglock`. It lasts across signal-stop/ptrace/freezer transitions.

Dependencies and integration points: integrates signal delivery, ptrace, cgroup freezer, task state reporting, and scheduler wakeups.

Risks and test signals: risks include bit overlap with stop signal mask, missed clearing of trapping state, and stop/ptrace/freezer race regressions. Test job-control stop/continue, ptrace attach/detach/listen, freezer interactions, and signal wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/jobctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/loadavg.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/loadavg.h

Purpose: declares fixed-point global load-average constants and helpers.

Important APIs and types: `avenrun[]`, `get_avenrun()`, `FSHIFT`, `FIXED_1`, `LOAD_FREQ`, `EXP_1`, `EXP_5`, `EXP_15`, `calc_load()`, `calc_load_n()`, `LOAD_INT()`, `LOAD_FRAC()`, and `calc_global_load()` make up the interface.

Control flow: scheduler load code periodically samples active tasks, applies exponential decay constants, and exposes 1/5/15-minute load averages through proc/sysinfo consumers.

State and persistence: global `avenrun` stores runtime fixed-point load averages. It is not persisted across boot.

Dependencies and integration points: depends on HZ and scheduler active-count accounting. Integrates with `/proc/loadavg`, sysinfo, and NOHZ load updates.

Risks and test signals: risks include fixed-point rounding drift, wrong active-task counts under NOHZ, and ABI-visible load output changes. Test load generation, idle/nohz CPUs, proc/sysinfo values, and low-HZ/high-HZ configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/loadavg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/mm.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/mm.h

Purpose: declares scheduler-facing MM lifetime helpers, current allocation-context scopes, mmap layout hooks, memcg active charging, and membarrier MM callbacks.

Important APIs and types: `mm_alloc()`, `mmgrab()`, `mmdrop()`, `mmdrop_sched()`, lazy-TLB refcount helpers, `mmget()`, `mmget_not_zero()`, `mmput()`, `mmput_async()`, `get_task_mm()`, `mm_access()`, exit/exec MM release helpers, mmap area selectors, `in_vfork()`, `current_gfp_context()`, `memalloc_*_save/restore()`, `might_alloc()`, `set_active_memcg()`, and membarrier state/flags are central.

Control flow: task lifetime code pins `mm_struct` either by structural count or active users count, drops references with barriers needed by membarrier, and uses RT-delayed drops where necessary. Allocation paths consult current PF_MEMALLOC flags to mask GFP bits, while scoped helpers temporarily impose NOIO/NOFS/noreclaim/pinning contexts.

State and persistence: state lives in `mm_struct` refcounts/flags/membarrier state, current task PF flags, active memcg pointers, and mmap layout. It persists for task/address-space lifetime and affects allocation behavior while scopes are active.

Dependencies and integration points: integrates scheduler task lifetime with MM, memcg, coredump dumpability, GFP reclaim, vfork, membarrier, architecture mmap layout, lazy TLB, and futex/private hash configs.

Risks and test signals: risks include confusing `mm_count` with `mm_users`, missing full barriers on mm drop, leaking memalloc scopes, incorrect GFP masking precedence, unsafe `real_parent` access in vfork checks, and membarrier sync-core omissions. Test fork/exec/exit, vfork, ptrace mm access, memcg charging, reclaim recursion scenarios, PREEMPT_RT, lazy TLB configs, and membarrier selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/mm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/nohz.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/nohz.h

Purpose: declares the scheduler interface to NOHZ/dynticks balancing, load accounting, and remote CPU wakeups.

Important APIs and types: `nohz_balance_enter_idle()`, `get_nohz_timer_target()`, `calc_load_nohz_start()`, `calc_load_nohz_remote()`, `calc_load_nohz_stop()`, and `wake_up_nohz_cpu()` are exported under `CONFIG_NO_HZ_COMMON`, with no-op fallbacks otherwise.

Control flow: idle CPUs enter NOHZ balance state, load accounting starts/stops tickless adjustments, remote load updates may be performed for idle runqueues, and wakeups kick tickless CPUs when scheduler work is needed.

State and persistence: state is runtime NOHZ scheduler/load metadata maintained in scheduler core and runqueues.

Dependencies and integration points: integrates scheduler balancing and loadavg with tickless idle/full-nohz infrastructure.

Risks and test signals: risks include stale load averages from idle CPUs, missed remote wakeups, and no-op fallback drift. Test NOHZ idle, nohz_full, loadavg under idle transitions, remote wakeups to tickless CPUs, and non-NOHZ builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/nohz.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/numa_balancing.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/numa_balancing.h

Purpose: declares scheduler/MM hooks for automatic NUMA balancing based on memory access faults.

Important APIs and types: `TNF_*` fault flags, `enum numa_vmaskip_reason`, `task_numa_fault()`, `task_numa_group_id()`, `set_numabalancing_state()`, `task_numa_free()`, and `should_numa_migrate_memory()` are the key contracts.

Control flow: NUMA hinting faults report source/destination nodes and locality flags to scheduler placement logic; scheduler state influences whether a folio should migrate toward a task’s CPU; task teardown frees NUMA grouping/fault state.

State and persistence: per-task NUMA fields live in `task_struct` and associated NUMA groups/fault arrays. They persist while NUMA balancing is active for the task.

Dependencies and integration points: depends on `sched.h`, folios, NUMA balancing config, MM hinting faults, and scheduler placement.

Risks and test signals: risks include migrating shared or inaccessible memory incorrectly, stale NUMA group IDs, disabled-config behavior returning overly permissive migration, and scan-period feedback errors. Test NUMA balancing sysctl toggles, multi-node workloads, shared memory, migration failure paths, task exit, and disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/numa_balancing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/posix-timers.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/posix-timers.h

Purpose: compatibility include that exposes POSIX timer declarations through the scheduler include namespace.

Important APIs and types: this file defines no new symbols; it includes `linux/posix-timers.h`.

Control flow: scheduler or signal code can include this path and receive POSIX timer types/functions. Runtime behavior lives in POSIX timer implementation.

State and persistence: no state is owned here.

Dependencies and integration points: bridges scheduler headers and POSIX timer declarations.

Risks and test signals: risk is include layering drift. Compile-test scheduler/signal users that include this wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/posix-timers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/prio.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/prio.h

Purpose: defines scheduler priority and nice-value constants/conversion helpers.

Important APIs and types: `MAX_NICE`, `MIN_NICE`, `NICE_WIDTH`, `MAX_RT_PRIO`, `MAX_DL_PRIO`, `MAX_PRIO`, `DEFAULT_PRIO`, `NICE_TO_PRIO()`, `PRIO_TO_NICE()`, `nice_to_rlimit()`, and `rlimit_to_nice()` are the public symbols.

Control flow: scheduler policy code converts user nice values to internal static priorities, handles inverted priority ordering, and maps nice values to rlimit-style values.

State and persistence: no state is stored; these are constants and pure conversions.

Dependencies and integration points: used by scheduler classes, rlimit handling, proc/sys priority display, and nice/setpriority syscalls.

Risks and test signals: risks include off-by-one conversions, priority range ABI drift, and confusion between deadline/RT/fair ranges. Test nice/setpriority, RLIMIT_NICE, scheduler policy transitions, and boundary values -20/19.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/prio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/rseq_api.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/rseq_api.h

Purpose: compatibility include that exposes restartable-sequences APIs through the scheduler include namespace.

Important APIs and types: no new symbols are defined; it includes `linux/rseq.h`.

Control flow: scheduler code that needs rseq hooks can include this wrapper; runtime behavior belongs to rseq implementation and task `rseq` state.

State and persistence: no state is owned here.

Dependencies and integration points: connects scheduler headers with restartable sequence declarations.

Risks and test signals: risk is include layering drift or missing rseq declarations after refactors. Compile-test rseq/scheduler integration and run rseq selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/rseq_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/rt.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/rt.h

Purpose: declares realtime-priority classification helpers, RT mutex scheduler hooks, PI priority adjustment APIs, and RR timeslice constant.

Important APIs and types: `rt_prio()`, `rt_or_dl_prio()`, `rt_task()`, `rt_or_dl_task()`, `rt_or_dl_task_policy()`, `rt_mutex_pre_schedule()`, `rt_mutex_schedule()`, `rt_mutex_post_schedule()`, `rt_mutex_get_top_task()`, `rt_mutex_setprio()`, `rt_mutex_adjust_pi()`, `normalize_rt_tasks()`, and `RR_TIMESLICE` are key.

Control flow: scheduler and locking code classify tasks by current priority or policy, handle PI boosting through RT mutex hooks, and normalize RT tasks when needed. RR tasks use the default timeslice for replenishment.

State and persistence: state lives in task priority/policy fields and RT mutex PI fields. The header itself only declares accessors/hooks.

Dependencies and integration points: integrates scheduler classes with RT mutexes, priority inheritance, and realtime policy management.

Risks and test signals: risks include confusing PI-boosted priority with policy, stale `pi_top_task` locking assumptions, disabled RT_MUTEX stubs hiding bugs, and RR timeslice regressions. Test RT scheduling, RR quantum behavior, PI mutex chains, priority changes, and configs without RT mutexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/rt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/sd_flags.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/sd_flags.h

Purpose: X-macro list of scheduler-domain balancing/topology flags and their meta-properties.

Important APIs and types: `SDF_SHARED_CHILD`, `SDF_SHARED_PARENT`, `SDF_NEEDS_GROUPS`, and `SD_FLAG(...)` entries such as `SD_BALANCE_NEWIDLE`, `SD_BALANCE_EXEC`, `SD_BALANCE_FORK`, `SD_BALANCE_WAKE`, `SD_WAKE_AFFINE`, `SD_ASYM_CPUCAPACITY`, `SD_SHARE_CPUCAPACITY`, `SD_CLUSTER`, `SD_SHARE_LLC`, `SD_SERIALIZE`, `SD_ASYM_PACKING`, `SD_PREFER_SIBLING`, and `SD_NUMA` are the declarations.

Control flow: `sched/topology.h` includes this file with different `SD_FLAG` definitions to generate indexes, bit values, and debug metadata; topology construction applies meta-flags to propagate behavior through domain hierarchy.

State and persistence: no runtime state is stored here, but generated flag bits configure scheduler-domain runtime behavior.

Dependencies and integration points: depends on being included only with `SD_FLAG` defined. Integrates topology description with load balancing, wake affinity, NUMA, SMT/cache sharing, and asymmetric CPU capacity.

Risks and test signals: risks include incorrect import without `SD_FLAG`, wrong meta-flag propagation, bit-count overflow, and balancing regressions from flag semantics changes. Test sched-domain debug output, topology rebuilds, NUMA/SMT/asym-capacity machines, cpuset relax levels, and compile generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/sd_flags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/signal.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/signal.h

Purpose: defines signal-handling structures embedded in tasks and thread groups, plus helpers for signal pending state, wakeups, alternate stacks, process iteration, and rlimit access.

Important APIs and types: `struct sighand_struct`, `struct signal_struct`, `struct pacct_struct`, `struct thread_group_cputimer`, `struct core_state`, signal flags, `flush_signals()`, `dequeue_signal()`, `kernel_dequeue_signal()`, force/send/kill helpers, notify-signal helpers, signal-pending helpers, `fault_signal_pending()`, `signal_wake_up()`, restore-sigmask helpers, alternate signal stack helpers, process/thread iteration macros, pid accessors, `lock_task_sighand()`, and rlimit helpers are central.

Control flow: signal code dequeues pending signals under `siglock`, wakes tasks by setting thread flags and scheduler states, handles fatal/interruptible wait decisions, manages saved signal masks around interrupted syscalls, and iterates thread groups/process lists under RCU/tasklist constraints.

State and persistence: `sighand_struct` and `signal_struct` hold shared signal actions, pending signals, group exit/stop state, POSIX timers, process accounting, child/reaped stats, rlimits, tty/session IDs, OOM metadata, and exec credential locks. This state persists for thread-group lifetime.

Dependencies and integration points: integrates scheduler tasks with signals, ptrace/jobctl, POSIX timers, credentials, pid namespaces, coredump, OOM, procfs/rusage, cgroups, tty, and MM fault handling.

Risks and test signals: risks include locking mistakes around `siglock`, RCU-unsafe process iteration, missed `TIF_NOTIFY_SIGNAL` kicks, fatal signal checks in fault retry paths, alternate-stack boundary errors, and rlimit races. Test signal delivery, ptrace stops, group exit, exec under signals, POSIX CPU timers, signalfd, alternate stacks, wait/reparenting, and signal-heavy stress with lockdep/RCU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/smt.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/smt.h

Purpose: declares SMT scheduler activation state and architecture SMT update hook.

Important APIs and types: `sched_smt_present`, `sched_smt_active()`, and `arch_smt_update()` are the exported symbols.

Control flow: scheduler/topology code checks a static key to determine whether SMT scheduling behavior is active; architecture code can notify updates when SMT availability changes.

State and persistence: SMT presence is runtime static-key state, derived from CPU topology and hotplug/control policy.

Dependencies and integration points: depends on static keys and `CONFIG_SCHED_SMT`. Integrates scheduler topology and architecture SMT control.

Risks and test signals: risks include stale static-key state after SMT hotplug/control changes and disabled-config assumptions. Test SMT on/off toggles, CPU hotplug, sched-domain rebuilds, and non-SMT builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/smt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/stat.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/stat.h

Purpose: declares scheduler and fork counters exposed to proc/sys consumers and lightweight runtime queries.

Important APIs and types: `total_forks`, `nr_threads`, per-CPU `process_counts`, `nr_processes()`, `nr_running()`, `single_task_running()`, `nr_iowait()`, `nr_iowait_cpu()`, `sched_info_on()`, and optional `force_schedstat_enabled()` are key.

Control flow: scheduler/fork code updates counters; proc, sysinfo, drivers, and heuristics query approximate values without strict locking.

State and persistence: global and per-CPU counters track live processes, runnable tasks, iowait, forks, and optional schedstats. They are runtime diagnostic/accounting state.

Dependencies and integration points: depends on percpu and Kconfig. Integrates scheduler accounting with `/proc`, sysinfo, and optional schedstats.

Risks and test signals: risks include readers treating approximate unlocked counts as exact, schedstats enablement overhead, and per-CPU aggregation drift. Test proc/stat outputs, fork stress, iowait workloads, schedstats toggles, and CPU hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/sysctl.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/sysctl.h

Purpose: declares scheduler-related sysctl constants and tunable state.

Important APIs and types: `sysctl_hung_task_timeout_secs`, `enum sched_tunable_scaling`, `NUMA_BALANCING_*` mode bits, and `sysctl_numa_balancing_mode` are the main symbols.

Control flow: sysctl handlers and scheduler/MM code read these values to control hung-task timeout reporting, scheduler tunable scaling mode, and NUMA balancing modes. Disabled configs provide constants so callers avoid ifdefs.

State and persistence: state is runtime sysctl/global tunable data; persistence depends on userspace sysctl configuration, not the header.

Dependencies and integration points: integrates scheduler, hung-task detector, NUMA balancing, and sysctl infrastructure.

Risks and test signals: risks include disabled-config constants masking writes, invalid scaling mode handling, and NUMA mode bit confusion. Test sysctl reads/writes, hung-task detector config, NUMA balancing mode changes, and disabled feature builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/sysctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/task.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/task.h

Purpose: declares task lifetime, fork/clone, exit, wait, task reference, initial task, tasklist locking, and task allocation/stack interfaces.

Important APIs and types: `CLONE_LEGACY_FLAGS`, `struct kernel_clone_args`, `tasklist_lock`, `mmlist_lock`, `init_thread_union`, `init_task`, `schedule_tail()`, scheduler fork hooks, `do_task_dead()`, `make_task_dead()`, cache init, `release_task()`, `copy_thread()`, `do_group_exit()`, `kernel_clone()`, `copy_process()`, `create_io_thread()`, `fork_idle()`, `kernel_thread()`, `user_mode_thread()`, wait helpers, task refcount helpers, `release_thread()`, `task_stack_vm_area()`, and `task_lock()` are central.

Control flow: clone/fork code fills `kernel_clone_args`, creates/copies tasks, calls scheduler and architecture hooks, publishes tasks under tasklist locking, and releases resources on exit. References are acquired with `get_task_struct()` and dropped through RCU-delayed freeing when needed.

State and persistence: state includes task references, global task list, initial task, kernel stacks, task caches, and per-task resources protected by `alloc_lock`. It lasts for task lifetime and RCU grace periods after final put.

Dependencies and integration points: integrates scheduler with fork/exit, MM, files/fs, cgroups, architecture thread setup, wait/rusage, RCU, and procfs locking.

Risks and test signals: risks include clone flag ABI mistakes, task refcount underflow, freeing in atomic/RT contexts, tasklist lock nesting violations, and resource leaks on fork failure. Test fork/clone variants, io threads, kernel threads, wait4, exit races, RCU ref users, PREEMPT_RT, and lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/task.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/task_flags.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/task_flags.h

Purpose: compatibility include for task PF/PFA flag declarations.

Important APIs and types: no new symbols are declared here; it includes `linux/sched.h`, which defines PF flags and atomic PFA helper macros.

Control flow: callers include this wrapper to access task flags. Runtime behavior is in task flag operations from `sched.h`.

State and persistence: no state is owned here.

Dependencies and integration points: depends entirely on `linux/sched.h`; preserves header organization for task-flag users.

Risks and test signals: risk is include dependency drift. Compile-test users including only `sched/task_flags.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/task_flags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/task_stack.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/task_stack.h

Purpose: declares kernel stack access, reference, end-marker, stack-cache, and debug helpers for tasks.

Important APIs and types: `task_stack_page()`, `setup_thread_stack()`, `end_of_stack()`, `try_get_task_stack()`, `put_task_stack()`, `exit_task_stack_account()`, `task_stack_end_corrupted()`, `object_is_on_stack()`, `thread_stack_cache_init()`, `stack_not_used()`, `set_task_stack_end_magic()`, and `kstack_end()` are key.

Control flow: fork/setup code initializes thread stack metadata, stack readers pin non-current task stacks where refcounted, debug code checks magic/end corruption and unused stack, and object-on-stack tests compare against current stack bounds after KASAN tag reset.

State and persistence: state is each task’s kernel stack pointer, optional stack refcount, VMAP stack area, and stack-end magic. It lasts for task lifetime and stack RCU/freeing rules.

Dependencies and integration points: depends on `sched.h`, thread-info layout, magic constants, refcounts, KASAN, VMAP stack, and architecture stack growth direction.

Risks and test signals: risks include reading an exiting task stack without pinning, stack-growth boundary mistakes, missing magic initialization, and KASAN tag comparison errors. Test stack debugging, VMAP_STACK, THREAD_INFO_IN_TASK and legacy layouts, task exit races, and stack-usage diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/task_stack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/thread_info_api.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/thread_info_api.h

Purpose: compatibility include that exposes thread-info APIs through the scheduler namespace.

Important APIs and types: no new symbols are defined; it includes `linux/thread_info.h`.

Control flow: callers use this wrapper to access thread flags and current thread-info helpers.

State and persistence: no state is owned here.

Dependencies and integration points: bridges scheduler headers and architecture/generic thread-info declarations.

Risks and test signals: risk is include layering drift. Compile-test thread-info users after scheduler header refactors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/thread_info_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/topology.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/topology.h

Purpose: declares scheduler-domain topology structures, generated domain flags, domain partitioning APIs, topology-level callbacks, and CPU capacity helpers.

Important APIs and types: generated `SD_*` flag indexes/bits, `struct sd_flag_debug`, topology mask/flag functions, `struct sched_domain_attr`, `struct sched_domain_shared`, `struct sched_domain`, `sched_domain_span()`, `partition_sched_domains()`, domain allocation/free helpers, `cpus_equal_capacity()`, `cpus_share_cache()`, `cpus_share_resources()`, `struct sd_data`, `struct sched_domain_topology_level`, `set_sched_topology()`, `sched_update_asym_prefer_cpu()`, `SDTL_INIT()`, `rebuild_sched_domains_energy()`, arch capacity/pressure hooks, and `task_node()`.

Control flow: topology code generates domains from architecture topology levels, allocates per-CPU domain/group data, partitions domains for cpusets, and rebuilds energy-aware scheduling state when capacity/frequency models change.

State and persistence: scheduler domains and groups are runtime topology state, RCU-freed on rebuild. Shared domain counters track idle/busy information.

Dependencies and integration points: depends on topology, idle definitions, `sd_flags.h`, cpumasks, NUMA, SMT/cluster/mc/package topology, energy model, and cpufreq schedutil.

Risks and test signals: risks include span flexible-array layout assumptions, stale RCU domains after rebuild, wrong flag propagation, asymmetric capacity misclassification, and energy-domain rebuild omissions. Test topology debugfs/proc output, CPU hotplug, cpuset partitions, NUMA/SMT/cache topologies, EAS systems, and arch capacity hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/types.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/types.h

Purpose: defines common scheduler CPU-time aggregate types without pulling the full scheduler header.

Important APIs and types: `struct task_cputime` groups system time, user time, and total execution runtime in nanoseconds.

Control flow: accounting and timer code passes this structure between cputime collection, adjustment, POSIX CPU timers, and thread-group accounting.

State and persistence: the structure is a value container; persistent counters live in tasks or signal structs.

Dependencies and integration points: depends only on integer types. It is shared by scheduler, signal, POSIX timer, and accounting code.

Risks and test signals: risks include field-order assumptions, unit confusion, and overflow expectations for long-lived tasks. Test CPU accounting consumers and compile paths that need this type without full `sched.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/user.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/user.h

Purpose: declares per-UID resource accounting and lifetime management for `struct user_struct`.

Important APIs and types: `struct user_struct`, `uids_sysfs_init()`, `find_user()`, `root_user`, `INIT_USER`, `alloc_uid()`, `get_uid()`, and `free_uid()` are central. The structure tracks refcount, UID hash linkage, optional epoll watches, UNIX inflight files, pipe buffers, locked VM, watch count, and rate limiting.

Control flow: credential/user lookup code allocates or finds UID records, increments references when attached to credentials or resources, and frees when no longer used. Resource subsystems charge per-user counters through fields gated by config.

State and persistence: per-UID runtime accounting persists while references exist. It is not persistent across boot.

Dependencies and integration points: integrates credentials, sysfs UID exposure, epoll, UNIX sockets, pipes, perf/BPF/network/io_uring/VFIO/IOMMUFD locked memory, watch queues, and rate limiting.

Risks and test signals: risks include refcount leaks, per-user counter underflow, UID hash races, and config-dependent field users. Test UID creation/destruction, credential churn, epoll/pipe/UNIX socket limits, locked-memory accounting, and namespace/user stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/vhost_task.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/vhost_task.h

Purpose: declares the vhost task abstraction used to run vhost work in scheduler-managed task context.

Important APIs and types: opaque `struct vhost_task`, `vhost_task_create()`, `vhost_task_start()`, `vhost_task_stop()`, and `vhost_task_wake()` are the interface.

Control flow: vhost code creates a task with a work function and kill handler, starts it, wakes it when work is available, and stops it during teardown.

State and persistence: vhost task state is owned by the implementation and persists between create/start and stop/destruction.

Dependencies and integration points: integrates vhost drivers with task creation, scheduler wakeups, and signal/kill handling without exposing implementation details.

Risks and test signals: risks include wake after stop, kill-handler ordering, task lifetime leaks, and work function return semantics. Test vhost device start/stop, teardown under load, wake races, and signal/kill paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/vhost_task.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/wake_q.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/wake_q.h

Purpose: declares wake queues, a mechanism for batching task wakeups until after releasing contended locks.

Important APIs and types: `struct wake_q_head`, `WAKE_Q_TAIL`, `WAKE_Q_HEAD_INITIALIZER`, `DEFINE_WAKE_Q`, `wake_q_init()`, `wake_q_empty()`, `wake_q_add()`, `wake_q_add_safe()`, `wake_up_q()`, and raw spin unlock-and-wake helpers are central.

Control flow: lock or synchronization code marks tasks internally woken, appends them to a wake queue while holding references, releases the protecting lock, and then calls `wake_up_q()` to perform scheduler wakeups. Unlock helpers combine raw spin unlock with wakeup under preemption guard.

State and persistence: queue state is a transient singly-linked list using each task’s embedded `wake_q_node`; tasks cannot be abandoned in a wake queue and must be woken soon.

Dependencies and integration points: depends on `sched.h`, task refs, raw spinlocks, and preemption guards. It integrates futexes, mutex/rtmutex-like paths, and other synchronization primitives with scheduler wakeups.

Risks and test signals: risks include adding a task to two wake queues, failing to call `wake_up_q()`, spurious wakeups without condition loops, and waking before the task is ready. Test futex/mutex contention, PI paths, lock handoff races, wake queue reuse, and PREEMPT_RT spin unlock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/wake_q.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/xacct.h -->
# sources/distributed-fs/ceph-client/include/linux/sched/xacct.h

Purpose: declares optional extended task I/O accounting helpers.

Important APIs and types: `add_rchar()`, `add_wchar()`, `inc_syscr()`, and `inc_syscw()` update `task_struct.ioac` when `CONFIG_TASK_XACCT` is enabled, and compile to no-ops otherwise.

Control flow: read/write syscall and filesystem paths call these helpers to accumulate byte and syscall counters for the task.

State and persistence: accounting state lives in `task_struct.ioac` and is folded into process/task accounting outputs. It persists for task lifetime.

Dependencies and integration points: depends on `sched.h` and task I/O accounting fields. Integrates syscall/file I/O paths with taskstats/proc accounting.

Risks and test signals: risks include disabled-config no-op assumptions, counter overflow in long-lived tasks, and missing accounting at new I/O paths. Test taskstats/proc I/O counters, read/write workloads, and builds with and without TASK_XACCT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched/xacct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched_clock.h -->
# sources/distributed-fs/ceph-client/include/linux/sched_clock.h

Purpose: declares generic scheduler-clock registration and read-side data for extending hardware counters into 64-bit nanosecond scheduler time.

Important APIs and types: `struct clock_read_data`, `sched_clock_read_begin()`, `sched_clock_read_retry()`, `generic_sched_clock_init()`, and `sched_clock_register()` are exported under `CONFIG_GENERIC_SCHED_CLOCK`, with init/register no-ops otherwise.

Control flow: architecture or clocksource code registers a counter reader, bit width, and rate; generic scheduler clock code converts cycles using mult/shift and seqcount-protected epochs; readers retry if an update races.

State and persistence: `clock_read_data` holds runtime epoch, mask, reader function, multiplier, and shift. It is hot-path timekeeping state and not persistent across boot.

Dependencies and integration points: depends on generic sched clock config and integer types. Integrates architecture counters with scheduler clock users and `sched/clock.h`.

Risks and test signals: risks include wrong counter bit width/rate, seqcount update races, overflow in cycle-to-ns conversion, suspend dummy-reader handling, and cacheline hot-path regressions. Test sched_clock registration on arch platforms, wraparound, suspend/resume, seqcount retry behavior, and tracing timestamp sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sched_clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/scmi_imx_protocol.h -->
# sources/distributed-fs/ceph-client/include/linux/scmi_imx_protocol.h

Purpose: declares NXP i.MX vendor SCMI protocol IDs, notification payloads, and operation tables for BBM, MISC, LMM, and CPU extension protocols.

Important APIs and types: protocol IDs `SCMI_PROTOCOL_IMX_LMM`, `SCMI_PROTOCOL_IMX_BBM`, `SCMI_PROTOCOL_IMX_CPU`, `SCMI_PROTOCOL_IMX_MISC`, vendor strings, `struct scmi_imx_bbm_proto_ops`, notification event IDs, `struct scmi_imx_bbm_notif_report`, `struct scmi_imx_misc_ctrl_notify_report`, `struct scmi_imx_misc_proto_ops`, LMM constants/state enum/info struct, `struct scmi_imx_lmm_proto_ops`, and `struct scmi_imx_cpu_proto_ops` define the contract.

Control flow: SCMI protocol drivers expose operation tables through protocol handles; consumers set/get RTC time and alarms, read button state, control miscellaneous registers and notifications, fetch syslog data, control life-cycle manager power/reset/shutdown, and set/start/query CPU reset vectors.

State and persistence: persistent platform state is remote firmware-owned: RTC values, alarms, control settings, LMM state, reset vectors, and CPU started state. Kernel state is limited to reports and protocol handle dispatch.

Dependencies and integration points: depends on SCMI protocol framework, device/notifier infrastructure, bitfield helpers, and NXP i.MX firmware ABI documentation. It integrates platform drivers with vendor SCMI extensions.

Risks and test signals: risks include protocol ID collisions, firmware ABI mismatch, endian/width mistakes for 64-bit times/vectors, notification flag drift, and unsafe buffer sizing for syslog. Test with i.MX SCMI firmware, RTC/alarm/button notifications, MISC control get/set/notify, LMM boot/shutdown/reset-vector flows, CPU start/query, and absent-protocol error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/scmi_imx_protocol.h -->
