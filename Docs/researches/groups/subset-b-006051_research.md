# subset-b-006051 Research

Grouped source research for the Ceph-client kernel scheduler files in subset B. Each section preserves the source path in its title and is marker-delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/core_sched.c -->
# sources/distributed-fs/ceph-client/kernel/sched/core_sched.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/core_sched.c` implements the task-facing parts of Linux core scheduling. It manages per-task core-scheduling cookies exposed through `PR_SCHED_CORE`, propagates cookies across fork/free, and accounts SMT forced-idle time when schedstats are enabled. The file was read as a complete 302-line source.

## Important APIs, Types, and Functions

`struct sched_core_cookie` wraps a `refcount_t`; the cookie value stored in `task_struct::core_cookie` is the allocated object's address. `sched_core_alloc_cookie()`, `sched_core_get_cookie()`, and `sched_core_put_cookie()` allocate, refcount, free, and toggle global core-scheduling enablement through `sched_core_get()`/`sched_core_put()`. `sched_core_update_cookie()` is the central mutation routine: it locks the task rq, dequeues any core-scheduler rb-node, swaps `p->core_cookie`, re-enqueues when needed, and reschedules a running task whose compatibility changed. Public integration points are `sched_core_fork()`, `sched_core_free()`, `sched_core_share_pid()`, `__sched_core_account_forceidle()`, and `__sched_core_tick()`.

## Control Flow

The prctl path enters `sched_core_share_pid()`, validates SMT support, command, pid type, and user pointer shape, resolves the target task under RCU, then applies ptrace-style access checks. `PR_SCHED_CORE_GET` hashes the target cookie and writes it to user space. `CREATE` allocates a fresh cookie, `SHARE_TO` clones the current task cookie, and `SHARE_FROM` clones the target thread cookie into the current task. For thread-group or process-group scopes, it first verifies access to every member under `tasklist_lock`, then applies the cookie to every thread. Cookie lifetimes are balanced by the final `sched_core_put_cookie(cookie)`.

The schedstats path is driven by rq ticks and scheduling edges. `__sched_core_tick()` updates the core rq clock if called on a sibling rq and delegates to `__sched_core_account_forceidle()`, which computes elapsed forced-idle time, scales it across SMT siblings and occupied cookied tasks, then charges the selected running/core-picked tasks with `__account_forceidle_time()`.

## State and Persistence Behavior

State is entirely in memory: allocated cookie objects, task `core_cookie` fields, per-rq core state, and per-task schedstats. Forked tasks inherit the current cookie by refcounting it; task exit drops it. There is no on-disk persistence. Forced-idle accounting persists only in runtime scheduler statistics.

## Dependencies and Integration Points

The file depends on `sched.h`, rq locking, tasklist traversal, RCU, ptrace permission checks, `PR_SCHED_CORE_*` ABI constants, rb-node helpers, SMT masks, and schedstats. It integrates with core-scheduler enqueue/dequeue logic implemented elsewhere, cputime accounting through `__account_forceidle_time()`, and user space through `prctl(PR_SCHED_CORE, ...)`.

## Risks and Edge Cases

Cookie changes while a task is queued or running must preserve rq/core rb-tree invariants and trigger rescheduling when compatibility changes. Group operations can partially fail only before mutation because the code performs a preflight permission pass. User-pointer alignment and command/scope validation are strict. Forced-idle accounting depends on recent core rq clocks and can mischarge if core force-idle counters are inconsistent, guarded by warnings.

## Test Signals

Useful signals are kernel selftests or targeted prctl tests for get/create/share-to/share-from across thread, thread-group, and process-group scopes; permission-denial tests across credentials; fork/exit stress with cookie refcount validation; SMT scheduling tests that confirm incompatible cookies force idle siblings; and schedstat checks for `core_forceidle_sum` when core scheduling is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/core_sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/cpuacct.c -->
# sources/distributed-fs/ceph-client/kernel/sched/cpuacct.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/cpuacct.c` implements the legacy CPU accounting cgroup controller. It tracks aggregate and per-CPU CPU usage for each accounting cgroup, exposes legacy cgroup files such as `cpuacct.usage`, `cpuacct.usage_percpu`, `cpuacct.usage_all`, and `cpuacct.stat`, and receives charge callbacks from scheduler/cputime code. The file was read as a complete 365-line source.

## Important APIs, Types, and Functions

`enum cpuacct_stat_index` distinguishes user and system accounting buckets. `struct cpuacct` embeds `cgroup_subsys_state` plus per-CPU `cpuusage` and `kernel_cpustat` storage. `cpuacct_css_alloc()` and `cpuacct_css_free()` create and free controller state. `cpuacct_cpuusage_read()` and `cpuacct_cpuusage_write()` are the low-level per-CPU readers/resetters, with rq locking on 32-bit platforms for safe 64-bit access. User-visible cftype handlers include `cpuusage_read()`, `cpuusage_write()`, `cpuacct_percpu_seq_show()`, `cpuacct_all_seq_show()`, and `cpuacct_stats_show()`. Runtime entry points are `cpuacct_charge()` for elapsed execution time and `cpuacct_account_field()` for user/system/irq/softirq cpustat fields.

## Control Flow

At cgroup creation, the root cgroup reuses global `kernel_cpustat` and a static per-CPU root usage counter; children allocate separate per-CPU usage and cpustat arrays. Reads iterate all possible CPUs and sum or print per-CPU values. `cpuacct.stat` builds `task_cputime`, adjusts it through `cputime_adjust()`, and reports clock ticks. Writes only accept `0` and reset all per-CPU counters except the root cgroup.

At runtime, `cpuacct_charge()` is called with the target CPU rq locked and walks from the task's cpuacct cgroup to the root, adding nanoseconds to each ancestor's per-CPU `cpuusage`. `cpuacct_account_field()` adds a specific cpustat field to each non-root ancestor; the root is updated by the caller.

## State and Persistence Behavior

All state is in per-CPU kernel memory associated with cgroup lifetime. Counters are monotonically increasing unless reset through `cpuacct.usage` write on non-root cgroups. There is no persistence across reboot or cgroup destruction.

## Dependencies and Integration Points

The controller depends on cgroup core APIs, per-CPU allocation, `kernel_cpustat`, scheduler rq locking, task CSS lookup, and cputime adjustment helpers from `cputime.c`. It integrates with legacy cgroup v1 cpuacct files and with scheduler accounting hooks reached through `cgroup_account_cputime*()`.

## Risks and Edge Cases

32-bit platforms require rq locking around 64-bit per-CPU reads/writes. Root cgroup reset is explicitly rejected to protect global kernel cpustat. Reads cover possible CPUs rather than online CPUs, so offline CPU historical counters remain visible. Hierarchical charging assumes parent links remain valid during accounting. `cpuacct.stat` uses adjusted cputime, so it may differ from raw nanosecond usage files.

## Test Signals

Signals include cgroup v1 cpuacct smoke tests for every exposed file; reset tests that accept only zero and do not reset root; parent-child hierarchy charge tests; CPU hotplug/offline counter visibility checks; 32-bit or KCSAN-style race coverage around concurrent read/update; and workload comparisons against `/proc/stat` and task cputime totals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/cpuacct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/cpudeadline.c -->
# sources/distributed-fs/ceph-client/kernel/sched/cpudeadline.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/cpudeadline.c` maintains the root-domain CPU deadline heap used by `SCHED_DEADLINE` load balancing. It lets the deadline class find CPUs whose current earliest deadline is later than a waking or pushable task's deadline, and separately tracks CPUs with no deadline tasks as free candidates. The file was read as a complete 278-line source.

## Important APIs, Types, and Functions

The implementation uses `struct cpudl` and `struct cpudl_item` declared in `cpudeadline.h`. The heap helpers `parent()`, `left_child()`, `right_child()`, `cpudl_heapify_down()`, `cpudl_heapify_up()`, and `cpudl_heapify()` maintain a max-heap ordered by latest earliest-deadline. `cpudl_find()` is the lookup API. `cpudl_set()` inserts or updates a CPU's deadline and removes it from `free_cpus`. `cpudl_clear()` removes a CPU from the heap and marks it free or unavailable depending on the runqueue online state. `cpudl_init()` and `cpudl_cleanup()` allocate and release heap and cpumask storage.

## Control Flow

When a deadline task becomes runnable or the earliest deadline on an rq changes, `cpudl_set()` records the CPU in the max-heap and heapifies it upward or downward. When the last deadline task leaves an rq or the CPU goes offline, `cpudl_clear()` removes its heap item by replacing it with the tail and heapifying, then updates `free_cpus`. `cpudl_find()` first prefers CPUs in `free_cpus` intersected with the task affinity mask. On asymmetric-capacity systems it filters that mask through `dl_task_fits_capacity()`, falling back to the highest-capacity CPU if none fit. If no free CPU is usable, it checks the heap root: if the root CPU is allowed and its current earliest deadline is later than the task deadline, that CPU can be preempted.

## State and Persistence Behavior

State is per root domain in memory: a raw spinlock, heap size, `free_cpus` cpumask, and one `elements` array that stores both heap positions and per-CPU reverse indices. `IDX_INVALID` means the CPU is not currently in the heap. State is rebuilt through scheduler root-domain initialization and updated under rq/root-domain scheduling events.

## Dependencies and Integration Points

The file depends on scheduler deadline time comparison (`dl_time_before()`), task affinity, CPU present/online state, capacity-awareness helpers, and raw spinlocks. It is updated from `deadline.c` through `inc_dl_deadline()`, `dec_dl_deadline()`, `rq_online_dl()`, and `rq_offline_dl()`, and queried by deadline wakeup, push, and pull balancing.

## Risks and Edge Cases

Heap reverse-index correctness is critical: every move updates `elements[cpu].idx`. `cpudl_maximum()` assumes a non-empty heap when no free CPU path succeeds, so callers rely on valid root-domain state. `cpudl_find()` may return a CPU that races with concurrent updates; deadline balancing revalidates under rq locks. Capacity fallback intentionally favors running the task over perfect fit when all allowed CPUs fail the fit test.

## Test Signals

Signals include heap invariant tests under random set/clear/update sequences; deadline migration tests where later-deadline CPUs are selected; free-CPU preference tests; CPU hotplug transitions checking `online` behavior; asymmetric-capacity deadline placement tests; and scheduler stress with concurrent wakeups and migrations under lockdep/KCSAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/cpudeadline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/cpudeadline.h -->
# sources/distributed-fs/ceph-client/kernel/sched/cpudeadline.h

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/cpudeadline.h` declares the CPU-deadline heap data structures and APIs used by the deadline scheduler class. The header was read as a complete 24-line source.

## Important APIs, Types, and Functions

`IDX_INVALID` marks CPUs not present in the heap. `struct cpudl_item` stores a CPU id, that CPU's current earliest deadline, and the heap index for reverse lookup. `struct cpudl` owns the raw spinlock, heap size, free-CPU cpumask, and dynamically allocated item array. The exported declarations are `cpudl_find()`, `cpudl_set()`, `cpudl_clear()`, `cpudl_init()`, and `cpudl_cleanup()`.

## Control Flow

This header has no runtime control flow. It defines the contract consumed by root-domain initialization and by `deadline.c`: initialize a `cpudl`, update it when an rq's deadline state changes, query it when a deadline task needs a later-deadline CPU, and clean it up with the root domain.

## State and Persistence Behavior

The declared state is heap and cpumask memory owned by a scheduler root domain. It persists for the root domain lifetime and is not file-backed.

## Dependencies and Integration Points

The header includes Linux scalar types and spinlock declarations and assumes scheduler definitions for `task_struct` and `cpumask` are visible to users. It is tightly paired with `cpudeadline.c` and integrated by `deadline.c`.

## Risks and Edge Cases

Because the header exposes raw structures, layout changes affect every root-domain user. `IDX_INVALID` must remain distinct from valid heap indices. Callers must hold the appropriate rq/root-domain locks around update operations as documented in the implementation.

## Test Signals

Compile coverage with `deadline.c`, root-domain init/teardown coverage, and lockdep-enabled scheduler tests that exercise `cpudl_set()`, `cpudl_clear()`, and `cpudl_find()` through deadline task migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/cpudeadline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/cpufreq.c -->
# sources/distributed-fs/ceph-client/kernel/sched/cpufreq.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/cpufreq.c` provides the scheduler-to-cpufreq callback hook used by governors such as `schedutil`. It stores per-CPU `update_util_data` pointers and exposes helpers to install, remove, and validate scheduler utilization update callbacks. The file was read as a complete 75-line source.

## Important APIs, Types, and Functions

`DEFINE_PER_CPU(struct update_util_data __rcu *, cpufreq_update_util_data)` is the central per-CPU hook pointer. `cpufreq_add_update_util_hook()` sets the callback function in caller-provided data and publishes it with RCU. `cpufreq_remove_update_util_hook()` clears the pointer. `cpufreq_this_cpu_can_update()` checks whether the current CPU can update a policy directly or, for drivers with `dvfs_possible_from_any_cpu`, through a still-installed local scheduler hook.

## Control Flow

Governor startup calls `cpufreq_add_update_util_hook()` for each CPU in a policy after ensuring no hook is already installed. Scheduler hot paths later call `cpufreq_update_util()` from RCU-sched read-side critical sections, which dereference this pointer and invoke `data->func`. Governor stop clears hooks and must synchronize RCU before freeing hook storage. `cpufreq_this_cpu_can_update()` is used by schedutil before calculating or committing frequency changes to avoid stale remote/offline CPU requests.

## State and Persistence Behavior

State is one RCU-protected callback pointer per CPU. The pointed-to storage is governor-owned, usually per-CPU schedutil state. No data persists beyond governor policy lifetime.

## Dependencies and Integration Points

The file depends on scheduler internals, RCU, per-CPU storage, `struct cpufreq_policy`, and cpufreq driver policy masks. It is exported GPL-only for governors and integrates directly with `cpufreq_schedutil.c`.

## Risks and Edge Cases

Installing over an existing hook or installing a null callback is rejected by warnings and no-op returns. Removal does not wait for readers; callers must use `synchronize_rcu()` or RCU callbacks before freeing. Remote DVFS updates must be suppressed when the local CPU is going offline and has no scheduler hook.

## Test Signals

Signals include governor start/stop tests that verify hook install/remove and RCU synchronization; CPU hotplug tests for remote DVFS policies; WARN coverage for duplicate/null hooks; and schedutil workloads proving `cpufreq_update_util()` still receives callbacks after policy transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/cpufreq_schedutil.c -->
# sources/distributed-fs/ceph-client/kernel/sched/cpufreq_schedutil.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/cpufreq_schedutil.c` implements the `schedutil` cpufreq governor, which selects CPU frequency or performance levels from scheduler utilization, utilization clamps, IO-wait boosts, deadline bandwidth, and scheduler-class extension performance targets. The file was read as a complete 938-line source.

## Important APIs, Types, and Functions

`struct sugov_policy` stores policy-level state: cpufreq policy, tunables, update lock, rate-limit timing, cached/next frequency, slow-switch irq work/kthread state, and limit-change flags. `struct sugov_cpu` stores per-CPU hook data, IO-wait boost state, last utilization, and bandwidth minimum. Main update paths are `sugov_update_single_freq()`, `sugov_update_single_perf()`, and `sugov_update_shared()`. Frequency computation flows through `sugov_get_util()`, `sugov_effective_cpu_perf()`, `get_capacity_ref_freq()`, and `get_next_freq()`. IO boosting is managed by `sugov_iowait_boost()`, `sugov_iowait_apply()`, and `sugov_iowait_reset()`. Governor lifecycle functions are `sugov_init()`, `sugov_exit()`, `sugov_start()`, `sugov_stop()`, and `sugov_limits()`.

## Control Flow

Governor init enables fast switching if possible, allocates policy state, creates a deadline-scheduled kthread for slow-switch drivers, creates or shares sysfs tunables, and rebuilds sched domains for energy-aware scheduling. Start chooses the update callback by policy shape and driver support: shared policies use `sugov_update_shared()`, fast-switch adjust-perf policies use `sugov_update_single_perf()`, and others use `sugov_update_single_freq()`. Each CPU gets a scheduler utilization hook through `cpufreq_add_update_util_hook()`.

On scheduler updates, the governor first updates IO-wait boost and deadline-bandwidth signals. `sugov_should_update_freq()` rejects unsupported remote updates, handles policy limit changes with barriers, honors forced update requests, and enforces `rate_limit_us`. Single-frequency mode computes one CPU's util and calls fast-switch directly or queues deferred irq/kthread work. Single-performance mode calls `cpufreq_driver_adjust_perf()` when frequency invariance exists. Shared mode locks the policy, updates the triggering CPU, scans all policy CPUs, chooses max util, then fast-switches or defers. Slow-switch work reads `next_freq` under `update_lock`, clears `work_in_progress`, and invokes `__cpufreq_driver_target()` under `work_lock`.

## State and Persistence Behavior

State persists while the cpufreq policy uses schedutil. Tunables may be global or per-policy depending on governor configuration. Per-CPU `sugov_cpu` state is zeroed on start. Cached raw frequency avoids redundant driver resolution. `limits_changed` and `need_freq_update` coordinate policy limit updates across cpufreq and scheduler contexts.

## Dependencies and Integration Points

The file depends on scheduler utilization APIs (`effective_cpu_util()`, `cpu_util_cfs_boost()`, deadline bandwidth, uclamp), architecture frequency/capacity scaling, cpufreq governor and driver operations, kthreads, irq work, sysfs governor attributes, energy model sched-domain rebuilds, and optional sched-ext hooks (`scx_cpuperf_target()`, `scx_switched_all()`). It integrates with `cpufreq.c` hook installation and with `deadline.c` through deadline bandwidth signals and SCHED_DEADLINE sugov kthreads.

## Risks and Edge Cases

Fast-switch callbacks run under rq lock and must not sleep. Slow-switch work must not miss updates while `work_in_progress` is being cleared, hence the policy lock. Memory barriers between `sugov_limits()` and `sugov_should_update_freq()` protect policy limit visibility. IO-wait boost decays by tick timing and can overboost or underboost bursty IO. Shared-policy util uses max policy CPU util, so stale per-CPU state can matter after hotplug if hooks are not stopped cleanly. Deadline-bandwidth increases bypass rate limiting through `need_freq_update`.

## Test Signals

Signals include cpufreq governor selftests across fast-switch, adjust-perf, and slow-switch drivers; sysfs `rate_limit_us` read/write tests; policy min/max limit-change tests; CPU hotplug and shared-policy stress; IO-wait wakeup benchmarks checking boost and decay; deadline workload tests confirming rate-limit bypass; uclamp/EAS frequency selection tests; and lockdep coverage for rq-lock and slow-switch sleeping boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/cpufreq_schedutil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/cpupri.c -->
# sources/distributed-fs/ceph-client/kernel/sched/cpupri.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/cpupri.c` maintains a root-domain priority-to-CPU index for real-time and deadline scheduling decisions. It lets the RT scheduler find CPUs running lower-priority work in near-constant time, while supporting affinity masks and optional fitness filters. The file was read as a complete 317-line source.

## Important APIs, Types, and Functions

`convert_prio()` maps scheduler priorities into `CPUPRI_INVALID`, `CPUPRI_NORMAL`, RT priority buckets 1-99, and `CPUPRI_HIGHER`. `__cpupri_find()` checks one priority vector's atomic count and cpumask with memory barriers. `cpupri_find()` is the basic lookup wrapper. `cpupri_find_fitness()` applies an optional per-CPU fitness function, currently used for capacity awareness. `cpupri_set()` moves a CPU between priority vectors. `cpupri_init()` allocates vector cpumasks and `cpu_to_pri`; `cpupri_cleanup()` frees them.

## Control Flow

Writers call `cpupri_set()` with the CPU rq lock held when a runqueue's highest RT-like priority changes. The function converts the incoming priority, adds the CPU to the new vector before removing it from the old vector, and uses atomic/memory-barrier ordering so racing readers see the CPU in at least one valid bucket. Readers call `cpupri_find_fitness()` with a task and optional destination mask. It iterates from lowest priority up to just below the task's priority, checks vector count/mask, intersects with task affinity and active CPUs, filters by fitness when requested, and falls back to a priority-only search if every fitted CPU failed.

## State and Persistence Behavior

State is per root domain in memory: an array of `struct cpupri_vec` buckets and a per-CPU current bucket array. It persists for root-domain lifetime and changes as rq priorities, CPU active state, and scheduler classes change.

## Dependencies and Integration Points

The file depends on cpumasks, atomic counters, memory barriers, RT priority definitions, and scheduler task affinity. It is used by RT balancing and by deadline code when deadline rq state changes map a CPU to `CPUPRI_HIGHER` or back to its RT highest priority.

## Risks and Edge Cases

The data structure is intentionally racy for readers, so correctness relies on scheduler rebalancing to repair stale choices. Barrier ordering in `cpupri_set()` is essential: adding before removing prevents missed CPUs, and decrement-before-mask-clear handles removal races. Fitness fallback favors priority correctness over CPU capacity fit. Initialization cleanup must free only successfully allocated masks on partial failure.

## Test Signals

Signals include RT migration tests with affinity-restricted tasks; priority raise/lower stress under lockdep; capacity-awareness tests with fitness rejection and fallback; CPU active/offline mask tests; randomized bucket invariant checks; and KCSAN-style coverage for reader/writer races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/cpupri.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/cpupri.h -->
# sources/distributed-fs/ceph-client/kernel/sched/cpupri.h

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/cpupri.h` declares the CPU-priority data structures and APIs used by real-time scheduler balancing. The header was read as a complete 30-line source.

## Important APIs, Types, and Functions

`CPUPRI_NR_PRIORITIES` is `MAX_RT_PRIO + 1`. Priority constants define invalid, normal, RT buckets, and a higher-than-RT bucket. `struct cpupri_vec` contains an atomic CPU count and cpumask for one priority bucket. `struct cpupri` contains the bucket array and `cpu_to_pri` reverse map. Declared APIs are `cpupri_find()`, `cpupri_find_fitness()`, `cpupri_set()`, `cpupri_init()`, and `cpupri_cleanup()`.

## Control Flow

The header has no executable flow. It provides the contract for root-domain setup, rq priority updates, and RT/deadline balancing lookups.

## State and Persistence Behavior

The declared state is root-domain memory and persists until root-domain teardown. It is not persistent across boot.

## Dependencies and Integration Points

The header depends on atomic operations, cpumasks, and RT priority definitions. It is implemented by `cpupri.c` and consumed by RT and deadline scheduler classes.

## Risks and Edge Cases

The constants must remain aligned with `convert_prio()` and RT priority ranges. Callers must treat lookup results as recommendations because concurrent rq priority changes can race with reads.

## Test Signals

Compile coverage with RT/deadline classes, root-domain allocation tests, and migration workloads that exercise priority lookup and update APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/cpupri.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/cputime.c -->
# sources/distributed-fs/ceph-client/kernel/sched/cputime.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/cputime.c` implements scheduler CPU-time accounting for user, system, guest, IRQ, softirq, steal, idle, force-idle, tick-based accounting, and virtual CPU accounting modes. It also provides adjusted task and thread-group cputime readers. The file was read as a complete 1100-line source.

## Important APIs, Types, and Functions

IRQ-time accounting is controlled by `sched_clock_irqtime`, `cpu_irqtime`, `enable_sched_clock_irqtime()`, `disable_sched_clock_irqtime()`, `irqtime_account_irq()`, and `irqtime_tick_accounted()`. Core charge APIs are `account_user_time()`, `account_guest_time()`, `account_system_index_time()`, `account_system_time()`, `account_steal_time()`, `account_idle_time()`, and `__account_forceidle_time()`. Tick paths include `account_process_tick()` and `account_idle_ticks()`. Readers/adjusters include `thread_group_cputime()`, `cputime_adjust()`, `task_cputime_adjusted()`, and `thread_group_cputime_adjusted()`. Generic virtual accounting adds `vtime_user_enter/exit()`, `vtime_guest_enter/exit()`, `vtime_task_switch_generic()`, `task_gtime()`, `task_cputime()`, `kcpustat_field()`, and `kcpustat_cpu_fetch()`.

## Control Flow

Runtime accounting classifies elapsed time by execution context. User and guest paths increment task `utime`, group user time, guest time where relevant, and cpustat fields. System time distinguishes hardirq, softirq, normal kernel, and guest VCPU contexts. Tick accounting first subtracts steal and IRQ/softirq time, then charges remaining tick time to user, idle, guest, or system. `thread_group_cputime()` combines dead-thread signal totals with live thread values under RCU and a seqcount-style signal stats lock, refreshing current runtime when querying its own group.

When native virtual accounting is enabled, adjusted readers return raw precise fields. Otherwise `cputime_adjust()` scales tick-derived user/system time to match `sum_exec_runtime` while preserving monotonicity under `prev_cputime::lock`. Generic vtime mode tracks a task state machine (`VTIME_SYS`, `VTIME_USER`, `VTIME_GUEST`, `VTIME_IDLE`, `VTIME_INACTIVE`) using seqcounts and `sched_clock()`, flushing deltas on user/guest transitions and context switches. Kernel cpustat readers fetch pending vtime from the current task on a CPU, retrying if they race with context switch state.

## State and Persistence Behavior

State lives in task fields (`utime`, `stime`, `gtime`, `vtime`, `prev_cputime`), signal/thread-group aggregates, per-CPU `kernel_cpustat`, per-CPU `irqtime`, rq steal-time snapshots, cgroup CPU accounting, and optional schedstats. Counters are in-memory runtime state and monotonic except for task/cgroup lifetime resets.

## Dependencies and Integration Points

The file depends on scheduler clocks, rq state, preempt/IRQ context, paravirt steal clock static calls, cgroup CPU accounting, process accounting, taskstats, seqcounts, RCU, and architecture vtime hooks. It integrates with `cpuacct.c`, `/proc/stat` and task `/proc` readers through `kcpustat_*`, core scheduling through force-idle accounting, and virtualization through guest/steal APIs.

## Risks and Edge Cases

IRQ-time accounting intentionally permits remote readers to race with local IRQ writers, accepting small misattribution to avoid IRQ locks. Tick accounting can account more time than the nominal caller elapsed due to delayed guest/steal clocks. `cputime_adjust()` must preserve monotonic user/system values even when raw tick ratios fluctuate. Vtime readers must retry around context-switch states to avoid double-counting or missing pending time. Nice changes during nohz vtime can make user-vs-nice split approximate.

## Test Signals

Signals include `/proc/stat` and task cputime consistency tests under user/system/guest/irq/softirq/idle workloads; nohz/full-dynticks tests for vtime transitions; KVM guest enter/exit accounting checks; steal-time simulation; cgroup cpuacct hierarchy tests; monotonicity tests for adjusted cputime; and lockdep/KCSAN coverage around seqcount and rq locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/cputime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/deadline.c -->
# sources/distributed-fs/ceph-client/kernel/sched/deadline.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/deadline.c` implements the `SCHED_DEADLINE` scheduling class: earliest-deadline-first selection, Constant Bandwidth Server enforcement, GRUB reclaiming, deadline bandwidth admission control, push/pull migration, CPU hotplug handling, cpuset/root-domain accounting, and deadline-server support for fair and sched-ext classes. The file was read as a complete 3879-line source.

## Important APIs, Types, and Functions

Core helpers map deadline entities to runqueues (`rq_of_dl_se()`, `dl_rq_of_se()`), manage root-domain bandwidth (`init_dl_bw()`, `__dl_add()`, `__dl_sub()`, `sched_dl_overflow()`), and update rq bandwidth (`add_rq_bw()`, `add_running_bw()`, `dl_rq_change_utilization()`). CBS and timers are handled by `setup_new_dl_entity()`, `replenish_dl_entity()`, `update_dl_entity()`, `start_dl_timer()`, `dl_task_timer()`, `inactive_task_timer()`, and `update_curr_dl_se()`. Deadline servers use `dl_server_start()`, `dl_server_stop()`, `dl_server_init()`, `sched_init_dl_servers()`, and `dl_server_apply_params()`. Scheduler-class methods are collected in `DEFINE_SCHED_CLASS(dl)`: enqueue/dequeue/yield, wakeup preemption, pick/set/put task, balance, migration, rq online/offline, tick, priority changes, and class switches. Admission and ABI helpers include `sched_dl_global_validate()`, `sched_dl_do_global()`, `__setparam_dl()`, `__getparam_dl()`, `__checkparam_dl()`, `dl_cpuset_cpumask_can_shrink()`, `dl_bw_alloc()`, `dl_bw_free()`, and `dl_bw_deactivate()`.

## Control Flow

Enqueueing a deadline entity updates sleeper stats, handles constrained-deadline activation, adds bandwidth on restore/migration, handles throttled entities, applies CBS wakeup/replenishment rules, then inserts the entity in an rb-tree ordered by absolute deadline. `inc_dl_deadline()` updates the rq's earliest deadline, `cpudl`, and `cpupri`. Dequeue removes the rb-node, updates counts and deadline indices, and on sleep starts the inactive/0-lag path via `task_non_contending()`. Picking chooses the leftmost rb-node; if it is a deadline server, the server asks its client class for a task and stops itself if none is available.

Runtime accounting flows through `update_curr_dl()`, which uses scheduler execution delta, scales by GRUB reclaim or CPU/frequency capacity, subtracts from runtime, throttles overrun or yielded entities, dequeues them, and starts replenishment timers. `dl_task_timer()` replenishes throttled tasks, migrates them if their rq went offline, re-enqueues them, and reschedules if needed. `inactive_task_timer()` removes active bandwidth after 0-lag or clears bandwidth for dead/non-deadline tasks.

Migration is split into wakeup placement (`select_task_rq_dl()`), push (`push_dl_task()`), and pull (`pull_dl_task()`). `find_later_rq()` queries `cpudl`, honors affinity/topology, and `find_lock_later_rq()` revalidates under double rq locks. Pushable tasks are kept in an rb-tree ordered by deadline. Pulling scans overloaded rqs, moves earlier-deadline pushable tasks, or uses stopper work for migration-disabled tasks.

Admission control calculates bandwidth ratios per root domain and CPU capacity. `sched_dl_overflow()` reserves or updates bandwidth on policy changes; cpuset/hotplug helpers allocate, free, deactivate, and rebuild bandwidth across root domains. Global RT runtime settings also set the deadline bandwidth cap because deadline and RT bandwidth remain linked in parts of the scheduler.

## State and Persistence Behavior

State is in `sched_dl_entity`, per-rq `dl_rq`, root-domain `dl_bw`, `cpudl`, `cpupri`, pushable rb-trees, hrtimers, and cpuset task counts. Deadline task parameters persist in task_struct until policy changes or the entity is cleared. Runtime, absolute deadline, throttling, yielding, non-contending, and server-defer flags are transient in-memory scheduler state. There is no file-backed persistence.

## Dependencies and Integration Points

The file depends on scheduler core locks/classes, hrtimers, cpusets, housekeeping masks, root domains, `cpudeadline.c`, `cpupri.c`, cpufreq utilization updates, PELT load updates, RT bandwidth, uclamp/capacity scaling, schedstats, tracepoints, and optional RT mutex PI and sched-ext support. User ABI integration comes through `sched_setattr()`/`sched_getattr()`, sysctl deadline period limits, and debugfs server tuning implemented in `debug.c`.

## Risks and Edge Cases

Deadline correctness depends on maintaining rb-tree order, rq bandwidth invariants, and root-domain bandwidth under many races. Timer callbacks hold task references and must balance `get_task_struct()`/`put_task_struct()` even when cancellation races. Constrained-deadline tasks after deadline but before next period need special throttling to avoid admission-test violations. PI boosting can temporarily override throttling. Offline migration must preserve running and reserved bandwidth across rqs and root domains. Shared RT/deadline bandwidth and asymmetric capacity admission are particularly sensitive to overflow, CPU hotplug, and cpuset partition changes.

## Test Signals

Signals include `sched_setattr()` parameter validation and admission tests; runtime overrun/yield CBS replenishment tests; constrained-deadline self-suspension tests; GRUB reclaim and frequency/capacity scaling benchmarks; push/pull migration tests across affinity, topology, and overloaded rqs; CPU hotplug and cpuset partition stress; PI boosting with throttled deadline tasks; deadline server debugfs tuning tests; and tracepoint/schedstat validation for throttle, replenish, and migration events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/deadline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/debug.c -->
# sources/distributed-fs/ceph-client/kernel/sched/debug.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/debug.c` implements scheduler observability and debugfs/proc reporting. It exposes scheduler feature toggles, tunable scaling, dynamic preemption mode, verbose scheduler-domain debug trees, deadline-server controls, `/sys/kernel/debug/sched/debug`, SysRq scheduler dumps, per-runqueue printers, and `/proc/<pid>/sched` task output. The file was read as a complete 1403-line source.

## Important APIs, Types, and Functions

Formatting helpers include `SEQ_printf()`, `nsec_high()`, `nsec_low()`, and `SPLIT_NS()`. Feature control uses `sched_feat_names`, optional `sched_feat_keys`, `sched_feat_show()`, `sched_feat_set()`, and `sched_feat_write()`. Debugfs initialization is in `sched_init_debug()`, with file operations for `features`, `verbose`, `preempt`, `tunable_scaling`, `debug`, and fair/ext deadline-server `runtime` and `period`. Scheduler-domain debug is handled by `update_sched_domain_debugfs()`, `dirty_sched_domain_sysctl()`, and `register_sd()`. Printing APIs include `print_cfs_rq()`, `print_rt_rq()`, `print_dl_rq()`, `print_cpu()`, `sched_debug_header()`, `sched_debug_show()`, `sysrq_sched_debug_show()`, `proc_sched_show_task()`, `proc_sched_set_task()`, and `resched_latency_warn()`.

## Control Flow

At late init, `sched_init_debug()` creates the top-level `sched` debugfs directory and registers control/report files. Feature writes copy a small user buffer, strip it, serialize with CPU hotplug read lock and inode lock, then update `sysctl_sched_features` and static keys. Scaling writes parse an integer and call `sched_update_scaling()`. Dynamic preempt writes parse a mode string and call `sched_dynamic_update()`.

Verbose scheduler-domain debug is lazy and CPU-aware: enabling `verbose` calls `update_sched_domain_debugfs()`, which allocates `sd_sysctl_cpus`, creates a `domains` tree, and creates per-CPU/per-domain files for domain tunables and flags. Dirty CPUs are marked for later rebuild.

The main sched debug seq iterator emits a header at position 0 and one online CPU per later position. Each CPU dump prints rq clocks/counters, CFS/RT/DL rq stats, and a task table. `/proc/<pid>/sched` prints task execution, wait, sleep, block, migration, PELT, uclamp, policy, deadline, NUMA, and sched-ext fields depending on config. Deadline-server debugfs writes stop the server, apply validated runtime/period parameters through `dl_server_apply_params()`, restart it, and log enable/disable transitions.

## State and Persistence Behavior

State includes debugfs dentries, `sched_debug_verbose`, optional static keys for scheduler features, `sd_sysctl_cpus`, server runtime/period fields stored in per-rq deadline-server entities, and task schedstats reset by `proc_sched_set_task()`. Debugfs settings are runtime-only and do not persist across reboot.

## Dependencies and Integration Points

The file depends on debugfs, seq_file, scheduler core data structures, sched domains, cgroups/autogroups, NUMA balancing, schedstats, uclamp, sched-ext, dynamic preemption, static branches, and deadline-server APIs from `deadline.c`. It integrates with `/proc`, SysRq, debugfs, and scheduler sysctl-style global tunables.

## Risks and Edge Cases

Debug code reads many live scheduler fields and must avoid sleeping or lock inversions on hot paths. Feature static-key changes require CPU hotplug serialization. Scheduler-domain debugfs rebuild can be called before debugfs init and must no-op safely. Group path printing uses a trylock and fallback buffer to avoid global buffer contention. Deadline-server runtime/period writes can disable servers and risk starvation; validation enforces runtime <= period and period bounds, but operational impact remains large.

## Test Signals

Signals include mounting debugfs and reading every sched file; writing valid/invalid `features`, `tunable_scaling`, and dynamic preempt modes; enabling/disabling verbose domains across CPU hotplug; writing fair/ext server runtime and period and checking error paths; reading `/proc/<pid>/sched` for fair, RT, and deadline tasks; SysRq scheduler dump smoke tests; and lockdep coverage while dumping under scheduler stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/debug.c -->
