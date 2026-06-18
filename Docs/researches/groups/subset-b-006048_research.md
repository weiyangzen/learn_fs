# subset-b-006048 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/resource.c -->
# sources/distributed-fs/ceph-client/kernel/resource.c

## Purpose
`resource.c` is the kernel's generic I/O port and physical memory resource-tree manager. It owns the exported root resources `ioport_resource`, `iomem_resource`, and `soft_reserve_resource`, exposes `/proc/ioports` and `/proc/iomem`, arbitrates insert/request/release/adjust operations on resource trees, and supplies helper walks used by memory hotplug, `/dev/mem`, CXL/device-private memory, and driver resource reservation paths. The implementation is generic kernel infrastructure rather than Ceph-specific code.

## Important APIs, Types, And Functions
The central type is `struct resource`, with `start`, `end`, `flags`, `desc`, `parent`, `child`, and `sibling` representing ordered nested ranges. `resource_lock` is a global `rwlock_t` protecting tree topology and range metadata. Exported APIs include `request_resource()`, `request_resource_conflict()`, `release_resource()`, `allocate_resource()`, `find_resource_space()`, `insert_resource()`, `insert_resource_conflict()`, `insert_resource_expand_to_fit()`, `remove_resource()`, `adjust_resource()`, `__request_region()`, `__release_region()`, `devm_request_resource()`, `devm_release_resource()`, `__devm_request_region()`, `__devm_release_region()`, `walk_iomem_res_desc()`, `walk_system_ram_res()`, `walk_system_ram_range()`, `walk_mem_res()`, `region_intersects()`, `region_intersects_soft_reserve()`, `resource_is_exclusive()`, `iomem_is_exclusive()`, and optional `alloc_free_mem_region()` / `request_free_mem_region()` helpers under `CONFIG_GET_FREE_REGION`.

Private helpers implement the mechanics: `next_resource()` and `for_each_resource()` do preorder traversal, `__request_resource()` inserts non-overlapping children, `__release_resource()` removes a node while either dropping or lifting children, `find_next_res()` finds clipped matching ranges, `__region_intersects()` classifies a query as disjoint/intersecting/mixed, and `__find_resource_space()` scans holes under alignment and min/max constraints.

## Control Flow
Request paths acquire `resource_lock` for write, validate that the new range fits the root, walk sorted siblings, and either link the node or return the first conflict. Insert paths are more complex: `__insert_resource()` can wrap existing fully-contained conflicts under the new resource, enabling firmware or bus windows to become parents of previously discovered children. Release and remove paths unlink a resource and either release or reparent children depending on caller intent.

Range-walk APIs repeatedly call `find_next_res()` and advance to `res.end + 1`, passing clipped ranges to callbacks. Allocation scans gaps between sibling resources, clips against constraints, lets architecture code remove reservations via `arch_remove_reservations()`, applies alignment or a custom `alignf`, then installs the selected range. `/proc` display uses seq_file traversal under the read lock and hides addresses from readers lacking `CAP_SYS_ADMIN`.

Memory hotremove uses `release_mem_region_adjustable()` to remove, shrink, or split a busy memory resource. If splitting, it allocates a new high resource and reparents children above the split. Memory hotplug can mark System RAM resources mergeable and merge adjacent childless resources with identical flags, names, and descriptors.

## State And Persistence
Resource trees are in-memory global kernel state. The root resources live for the lifetime of the kernel; dynamically allocated resources are freed only if they came from slab, while early memblock-allocated descriptors may intentionally leak when released. `/proc/ioports`, `/proc/iomem`, debug messages, and `/dev/mem` mapping revocation reflect that state but do not persist it across boot. Boot parameters `reserve=` and `iomem=` mutate initial reservations or strictness policy.

## Dependencies And Integration Points
This file depends on `linux/ioport.h`, procfs, seq_file, devres, memory hotplug, Kconfig-conditioned strict devmem checks, pseudo filesystem inode support, and architecture hooks such as `sched_clock` is unrelated but `arch_remove_reservations()` and `devmem_is_allowed()` are important. Integration points include PCI/firmware resource discovery, driver `request_region()` APIs, CXL namespace resource allocation, ZONE_DEVICE/private memory, memory hotplug/hotremove, `/dev/mem`, and System RAM walkers used by memory management.

## Risks
The main risks are off-by-one and overflow errors in inclusive ranges, stale `struct resource *` pointers after merge/free, lock ordering around callbacks and devres cleanup, and subtle child reparenting mistakes when splitting/removing nested ranges. `walk_res_desc()` and related loops must handle `res.end + 1` carefully near address-space limits. `__request_region_locked()` can sleep for muxed resources after dropping the write lock, so callers must tolerate retries. Strict devmem revocation relies on correct inode publication barriers and on resource busy/exclusive flags being set before mappings are revoked.

## Test Signals
`resource_kunit.c` directly tests resource union/intersection helpers and `region_intersects()` over nested System RAM/CXL-style windows. Additional signals should come from kernel selftests and boot tests that exercise `/proc/iomem`, `reserve=`, `iomem=strict/relaxed`, hotplug/hotremove, driver request/release paths, and CXL/device-private memory allocation. Lockdep, KASAN, KCSAN, and memory hotplug stress runs are useful for catching topology and lifetime mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/resource_kunit.c -->
# sources/distributed-fs/ceph-client/kernel/resource_kunit.c

## Purpose
`resource_kunit.c` is a KUnit test suite for resource range helpers and `resource.c` tree behavior. It validates `resource_union()`, `resource_intersection()`, and a realistic `region_intersects()` scenario involving System RAM ranges, memory holes, and nested CXL-window-like parent resources.

## Important APIs, Types, And Functions
The file defines static test resources `r0` through `r4`, `struct result` expectation rows, `results_for_union[]`, and `results_for_intersection[]`. Helpers `resource_do_test()`, `resource_do_union_test()`, and `resource_do_intersection_test()` run symmetric checks against expected boolean return values and range outputs. `resource_test_region_intersects()` builds a temporary resource subtree using `alloc_free_mem_region()`, `__request_region()`, and `insert_resource()`. Cleanup is registered with `kunit_add_action_or_reset()` via `remove_free_resource()` and `kfree_wrapper()`.

## Control Flow
The union and intersection tests iterate through table-driven cases and test both argument orders. The region-intersection test first allocates a free parent area under `iomem_resource`, then adds several ranges: top-level System RAM, a hole, a CXL window, another System RAM range, a larger CXL window, nested System RAM, nested code, and another nested System RAM range. It then probes offsets around boundaries to verify `REGION_INTERSECTS`, `REGION_DISJOINT`, and `REGION_MIXED` behavior.

## State And Persistence
The suite temporarily mutates the global `iomem_resource` tree while the KUnit case runs. It relies on KUnit cleanup actions to remove inserted/requested resources and free allocations. There is no persistent state beyond KUnit result reporting.

## Dependencies And Integration Points
The test depends on KUnit, `linux/ioport.h`, page-size constants, `alloc_free_mem_region()` from `resource.c`, and live resource-tree insertion/request APIs. It integrates with the kernel's KUnit runner through `kunit_test_suite(resource_test_suite)`.

## Risks
Because the region test uses the global iomem tree, cleanup ordering matters. Missing cleanup could leave artificial resources behind and poison later tests. The test assumes enough free address space exists for a 7 MiB aligned test parent. It also deliberately models nested non-RAM windows, so changes in `region_intersects()` semantics may require expectation updates rather than indicating simple breakage.

## Test Signals
Passing KUnit cases named `resource_test_union`, `resource_test_intersection`, and `resource_test_region_intersects` are the primary signal. Failures identify incorrect range endpoints, wrong boolean results, cleanup/add-action failures, inability to allocate a test window, or incorrect mixed/disjoint/intersects classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/resource_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rseq.c -->
# sources/distributed-fs/ceph-client/kernel/rseq.c

## Purpose
`rseq.c` implements the restartable sequences syscall and kernel slow paths. Rseq lets user space execute short per-CPU critical sections without heavyweight atomics, with the kernel aborting the sequence on migration, preemption, or signal delivery by fixing the user instruction pointer to an abort address. This file also provides debugfs controls/statistics and, when configured, time-slice extension support for rseq v2.

## Important APIs, Types, And Functions
Key exported or externally used entry points are `SYSCALL_DEFINE4(rseq)`, `__rseq_handle_slowpath()`, `__rseq_signal_deliver()`, `__rseq_debug_syscall_return()`, trace helpers `__rseq_trace_update()` and `__rseq_trace_ip_fixup()`, optional `rseq_syscall_enter_work()`, `rseq_slice_extension_prctl()`, and `SYSCALL_DEFINE0(rseq_slice_yield)`. Important internal helpers include `rseq_register()`, `rseq_unregister()`, `rseq_reregister()`, `rseq_length_valid()`, `rseq_handle_cs()`, `rseq_slowpath_update_usr()`, and `rseq_reset_ids()`. Optional statistics use per-CPU `struct rseq_stats` and debugfs files under `rseq/`.

## Control Flow
Registration validates user memory, structure size, and alignment; determines ABI version; initializes user fields such as `rseq_cs`, `flags`, `cpu_id_start`, `cpu_id`, `node_id`, and `mm_cid`; then records the userspace pointer, length, signature, and event version in `current->rseq`. Unregistration verifies pointer, length, flags, and signature, resets user IDs, then clears task rseq state. Re-registration of the same area returns `-EBUSY`; mismatches return `-EINVAL` or `-EPERM`.

On return-to-user slow paths, `rseq_slowpath_update_usr()` reads and clears scheduler event state with interrupts disabled, samples CPU/MMCID IDs, and updates user ABI fields or sends `SIGSEGV` on unrecoverable faults. Signal delivery calls `rseq_handle_cs()` to abort any active critical section before the signal handler IP is used. Debug syscall-return validation detects syscalls issued inside a critical section and kills the task under debug policy.

The optional slice extension path uses per-CPU hrtimers to bound granted extensions, syscall work to revoke grants on kernel entry, prctl controls to enable/disable per task, and debugfs to tune the nanosecond grant window.

## State And Persistence
Per-task state lives in `task_struct::rseq`, including the registered userspace pointer, ABI length, signature, event flags, and optional slice state. User-visible state is written into the registered TLS `struct rseq`. Per-CPU stats are volatile and exposed through debugfs. Static keys control debug and slice-extension availability. Boot parameters `rseq_debug=` and `rseq_slice_ext=` set initial feature behavior.

## Dependencies And Integration Points
The file integrates with scheduler migration/preemption events, signal delivery, syscall entry/exit work, tracepoints, debugfs, hrtimers, prctl, `uaccess` helpers, `task_mm_cid()`, `cpu_to_node()`, and architecture `pt_regs` IP manipulation through rseq API helpers declared in headers. User-space ABI compatibility depends on ELF auxiliary vector feature/align values and libc registration behavior.

## Risks
The highest-risk areas are user memory access fault handling, ABI-size/version compatibility, alignment validation, clearing or preserving event bits correctly, and avoiding stale critical-section state on signal or syscall transitions. Slice extension adds latency-sensitive timer and rescheduling behavior; incorrect revocation can either overrun scheduling latency or falsely abort user sequences. Debug and stats paths must not perturb hot exit-to-user paths excessively.

## Test Signals
Relevant tests include rseq selftests for registration, unregister, migration aborts, signal aborts, mm_cid/node/cpu ID updates, and critical-section IP fixups. Debugfs stats should increment in expected paths when `CONFIG_RSEQ_STATS` is enabled. Slice-extension tests should cover prctl enable/disable, `rseq_slice_yield`, syscall aborts, expiration, and disabled static-key behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/scftorture.c -->
# sources/distributed-fs/ceph-client/kernel/scftorture.c

## Purpose
`scftorture.c` is a torture-test module for `smp_call_function()` and related IPI primitives. It repeatedly invokes reschedule, single-CPU, many-CPU, all-CPU, wait, no-wait, and RPC-like variants under randomized load, optional CPU hotplug, stutter, long waits, and shutdown control.

## Important APIs, Types, And Functions
Module parameters control holdoff, long waits, thread count, CPU hotplug cadence, shutdown, stats interval, stutter, hotplug locking mode, verbosity, and operation weights. `struct scf_statistics` records per-thread counts. `struct scf_selector` stores weighted primitive choices. `struct scf_check` is passed to IPI handlers to validate memory ordering, target CPU, completion, and wait/no-wait ownership. Main functions include `scf_sel_add()`, `scf_sel_rand()`, `scf_handler()`, `scf_handler_1()`, `scftorture_invoke_one()`, `scftorture_invoker()`, `scf_torture_stats_print()`, `scf_torture_init()`, and `scf_torture_cleanup()`.

## Control Flow
Initialization computes default weights when all weights are unset, rejects an all-zero workload, initializes optional hotplug/shutdown/stutter torture services, allocates per-thread statistics, starts invoker kthreads, and optionally starts a stats printer thread. Each invoker pins itself to a CPU, waits for all invokers to start, drains its per-CPU no-wait free list, selects a primitive randomly by cumulative weight, and invokes the chosen SMP call-function primitive. Wait calls validate that handlers observed input state and set output state; no-wait calls return `scf_check` objects later through a lockless per-CPU free pool.

Cleanup stops invokers, issues one final synchronous `smp_call_function()` to flush in-flight no-wait handlers, stops the stats thread, prints final counters, frees stats/free-pool objects, and reports success/failure based on atomic error counters and hotplug failures.

## State And Persistence
State is module-global and volatile: selection arrays, stats, task pointers, per-CPU invoked counts, per-CPU lockless free pools, atomic error counters, and `scfdone`. Module parameters are runtime configuration. The test produces printk output but no persistent artifacts.

## Dependencies And Integration Points
The file depends on torture framework helpers, kthreads, completions, lockless lists, CPU hotplug APIs, SRCU/RCU headers, SMP call-function APIs, scheduler preemption controls, and optional built-in-only `resched_cpu()`. It integrates with kernel module init/exit or built-in torture boot flows.

## Risks
Because this is stress code, risks include false positives under CPU hotplug races, leaked `scf_check` allocations when no-wait handlers are delayed, unsafe assumptions about CPU availability, and long-wait configurations that create extreme latency. The code deliberately uses `GFP_ATOMIC` and tolerates allocation failure, but allocation failure counts differ under KASAN. Memory-ordering checks depend on barriers and handler/caller conventions.

## Test Signals
Healthy runs print periodic and final `scf_invoked_count` statistics without `!!!`, with zero `ste`, `stnmie`, and `stnmoe` counters. `LOCK_HOTPLUG` signals hotplug torture failures. Workload coverage is visible through per-primitive counters and overflow counts. Boot/module unload should complete without leaks, hung kthreads, or WARN splats except expected stress warnings under injected failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/scftorture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/Makefile -->
# sources/distributed-fs/ceph-client/kernel/sched/Makefile

## Purpose
This Makefile defines how the scheduler subsystem is compiled. It sets instrumentation policy, compiler flags, and the main object layout for scheduler compilation units.

## Important APIs, Types, And Functions
There are no C APIs here. Important build variables are `CONTEXT_ANALYSIS_core.o`, `CONTEXT_ANALYSIS_fair.o`, `ccflags-y`, `KCOV_INSTRUMENT`, `KCSAN_SANITIZE`, `KCSAN_INSTRUMENT_BARRIERS`, `CFLAGS_core.o`, `CFLAGS_build_policy.o`, `CFLAGS_build_utility.o`, and `obj-y`.

## Control Flow
Kbuild evaluates warning suppression first, disables KCOV for scheduler files, disables KCSAN sanitization while keeping barrier instrumentation, conditionally adds frame-pointer flags for `core.o`, disables branch profiling for aggregate build files when branch profiling is enabled, then builds `core.o`, `fair.o`, `build_policy.o`, and `build_utility.o`.

## State And Persistence
The file affects build outputs only. Its state is Kbuild configuration derived from Kconfig symbols and make variables; nothing persists at runtime.

## Dependencies And Integration Points
It integrates with Kbuild, compiler feature probing via `cc-disable-warning`, sanitizer/instrumentation infrastructure, profiling flags, architecture frame-pointer expectations, and the aggregate scheduler source files.

## Risks
Instrumentation choices are correctness-sensitive because scheduler code runs in contexts where tracing, KCOV, KCSAN, or branch profiling can add recursion, noise, or noinstr violations. Changing object partitioning can significantly affect build parallelism and compile memory use.

## Test Signals
The key signal is successful kernel build across configurations with and without frame pointers, trace branch profiling, KCOV, and KCSAN. Runtime scheduler tests mainly validate source files included by this build layout rather than the Makefile directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/autogroup.c -->
# sources/distributed-fs/ceph-client/kernel/sched/autogroup.c

## Purpose
`autogroup.c` implements scheduler autogrouping, which automatically places tasks from the same session/signal group into scheduler task groups under the root group. It improves interactive fairness without requiring explicit cgroup configuration and provides proc/sysctl controls for enabling and adjusting group nice values.

## Important APIs, Types, And Functions
Global state includes `sysctl_sched_autogroup_enabled`, `autogroup_default`, and `autogroup_seq_nr`. Core functions are `autogroup_init()`, `autogroup_create()`, `autogroup_destroy()`, `autogroup_free()`, `task_wants_autogroup()`, `sched_autogroup_create_attach()`, `sched_autogroup_detach()`, `sched_autogroup_fork()`, `sched_autogroup_exit()`, `sched_autogroup_exit_task()`, `proc_sched_autogroup_set_nice()`, `proc_sched_autogroup_show_task()`, and `autogroup_path()`. Reference management uses `struct kref`; group updates use `signal->siglock` and the autogroup `rw_semaphore`.

## Control Flow
Boot initialization attaches the init task's signal to `autogroup_default`, points it at `root_task_group`, initializes locking and reference state, and registers the sysctl when enabled. Creating an autogroup allocates `struct autogroup`, creates a scheduler `task_group`, optionally redirects RT scheduling entities to the root group, stores the backpointer, and online-links it under root. Attaching a process takes the target signal lock, swaps `signal->autogroup`, moves all threads with `sched_move_task()`, releases the lock, and drops the previous reference.

Fork copies a reference from the current task's autogroup into the new signal. Exit drops that reference. The proc nice setter checks range, LSM permission, `can_nice()`, admin throttling, converts nice to scheduler shares, updates group shares under write lock, and records the nice value. Display takes a read lock and emits `/autogroup-ID nice N`.

## State And Persistence
Autogroup state is in memory and tied to `signal_struct` lifetime. References count potential users rather than current thread membership. `sysctl_sched_autogroup_enabled` is mutable at runtime and can be disabled at boot with `noautogroup`. Per-autogroup nice values and IDs persist only while the autogroup exists.

## Dependencies And Integration Points
The file integrates with CFS task groups, root task group, scheduler migration via `sched_move_task()`, fork/exit paths, procfs task status output, sysctl, security hooks, nice permission checks, and optional RT group scheduling. It is included by `build_utility.c` under `CONFIG_SCHED_AUTOGROUP`.

## Risks
The main risks are lifetime and locking mistakes around `signal->autogroup`, races with cgroup attachment, exiting threads, and task-group destruction. RT group redirection is subtle because RT tasks use root RT bandwidth while the autogroup remains a CFS grouping concept. Proc nice updates take heavy scheduler locks and are rate-limited for non-admin callers to reduce abuse.

## Test Signals
Signals include booting with and without `noautogroup`, toggling `/proc/sys/kernel/sched_autogroup_enabled`, observing `/proc/<pid>/autogroup`, changing autogroup nice values, running fork/session workloads, and testing interaction with cgroups, RT policy changes, and task exit under lockdep/KASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/autogroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/autogroup.h -->
# sources/distributed-fs/ceph-client/kernel/sched/autogroup.h

## Purpose
`autogroup.h` declares the scheduler autogroup interface and provides no-op fallbacks when `CONFIG_SCHED_AUTOGROUP` is disabled.

## Important APIs, Types, And Functions
When enabled, it defines `struct autogroup` with `kref`, `task_group *tg`, `rw_semaphore lock`, `id`, and `nice`. It declares `autogroup_init()`, `autogroup_free()`, `task_group_is_autogroup()`, `task_wants_autogroup()`, `autogroup_task_group()`, and `autogroup_path()`. The key inline `autogroup_task_group()` reads `sysctl_sched_autogroup_enabled` and redirects eligible root-group tasks to `p->signal->autogroup->tg`.

## Control Flow
Scheduler code calls `autogroup_task_group(p, tg)` when resolving a task's effective task group. If autogrouping is enabled and `task_wants_autogroup()` accepts the task/root group combination, the inline returns the signal's autogroup task group; otherwise it returns the original group. Disabled builds return original groups and empty helpers.

## State And Persistence
The header itself has no state. It exposes the runtime state managed by `autogroup.c`: autogroup references, task-group pointers, nice values, and sysctl enablement.

## Dependencies And Integration Points
It includes `sched.h` and is consumed by scheduler core/fair/debug paths that need task-group selection or path formatting. It is also included by `autogroup.c` for the concrete implementation.

## Risks
Because this header contains inline task-group selection, changes can affect hot scheduler paths. It dereferences `p->signal->autogroup` only when the implementation says the task wants autogrouping, so caller locking and signal lifetime assumptions must remain valid.

## Test Signals
Build coverage with `CONFIG_SCHED_AUTOGROUP=y` and `n` validates the enabled declarations and disabled stubs. Runtime task-group selection can be observed through scheduler debug/proc output and autogroup behavior under fork/session/cgroup tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/autogroup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/build_policy.c -->
# sources/distributed-fs/ceph-client/kernel/sched/build_policy.c

## Purpose
`build_policy.c` is an aggregate compilation unit for scheduling policy code. It coalesces headers and source modules related to idle, RT, deadline, PELT, CPU deadline, scheduler syscalls, and optional sched_ext policy support for build efficiency.

## Important APIs, Types, And Functions
The file exports no independent APIs. Its important content is the include list: scheduler/user API headers, internal `sched.h`, `smp.h`, `autogroup.h`, `stats.h`, `pelt.h`, and source inclusions for `idle.c`, `rt.c`, `cpudeadline.c`, `pelt.c`, `cputime.c`, `deadline.c`, optional `ext_internal.h`, `ext.c`, `ext_idle.c`, and `syscalls.c`.

## Control Flow
At build time the preprocessor combines the listed policy modules into one translation unit. Kconfig controls the sched_ext include block. Runtime control flow is provided by the included source files, not by wrapper logic here.

## State And Persistence
No runtime state is defined by this wrapper itself. It affects symbol visibility, compile-time optimization scope, and generated object contents.

## Dependencies And Integration Points
It depends on Kbuild selecting `build_policy.o` and on all included scheduler policy modules being valid when compiled together. The Makefile can add branch-profiling suppression for this object because scheduler policy code may include noinstr-sensitive paths.

## Risks
Aggregate builds can hide missing includes between individual source files, create macro/order coupling, and increase rebuild cost when any included module changes. Source inclusion order matters if included files rely on prior definitions.

## Test Signals
Successful scheduler builds across configurations, especially with `CONFIG_SCHED_CLASS_EXT`, RT, deadline, and branch profiling options, are the main signals. Runtime validation comes from scheduler policy tests for the included modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/build_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/build_utility.c -->
# sources/distributed-fs/ceph-client/kernel/sched/build_utility.c

## Purpose
`build_utility.c` is the aggregate compilation unit for scheduler utility code. It bundles scheduler clock, debug, load average, completion/wait primitives, topology, CPU priority, stop task, and optional subsystem integrations into one object for build efficiency.

## Important APIs, Types, And Functions
It exports no standalone runtime API, but it includes many source modules: `clock.c`, optional `cpuacct.c`, `cpufreq.c`, `cpufreq_schedutil.c`, `debug.c`, optional `stats.c`, `loadavg.c`, `completion.c`, `swait.c`, `wait_bit.c`, `wait.c`, `cpupri.c`, `stop_task.c`, `topology.c`, optional `core_sched.c`, `psi.c`, `membarrier.c`, `isolation.c`, and optional `autogroup.c`. Headers include scheduler clock, debug, isolation, loadavg, nohz, rseq API, task stack, cpufreq, cpuset, debugfs, energy model, membarrier, procfs, PSI, security, swait/wait APIs, and architecture `switch_to`.

## Control Flow
Kbuild compiles this file as a single translation unit. Conditional include blocks select optional modules based on Kconfig. Runtime behavior is the behavior of the included files.

## State And Persistence
The wrapper itself declares no persistent runtime state. It shapes object composition and compile-time coupling between scheduler utility modules.

## Dependencies And Integration Points
It is integrated by `kernel/sched/Makefile` as `build_utility.o`. Because it includes core utility primitives like completion and wait queues, it indirectly supplies symbols used throughout the kernel. Optional integrations connect scheduler utility code to cgroups, cpufreq, schedutil, PSI, membarrier, CPU isolation, core scheduling, and autogroup.

## Risks
As an aggregate source file, it can mask missing local includes and create ordering dependencies. Instrumentation and branch profiling flags must be compatible with all included modules. A compile failure in any included utility source breaks the whole object, and changes can cause broad recompilation.

## Test Signals
Builds across broad scheduler Kconfig matrices are the primary signal. Runtime signals are covered by tests for the included primitives, such as completion/wait tests, scheduler debugfs/proc output, topology scheduling, cpufreq schedutil behavior, PSI, membarrier, and autogroup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/build_utility.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/clock.c -->
# sources/distributed-fs/ceph-client/kernel/sched/clock.c

## Purpose
`clock.c` implements scheduler clock helpers, especially for architectures with unstable per-CPU clocks. It provides `sched_clock()`, `local_clock()`, `sched_clock_cpu()`, idle sleep/wakeup hooks, stability transitions, and a weak `running_clock()` implementation.

## Important APIs, Types, And Functions
Important functions include weak `sched_clock()`, `sched_clock_init()`, `sched_clock_cpu()`, `local_clock_noinstr()`, `local_clock()`, `sched_clock_tick()`, `sched_clock_tick_stable()`, `sched_clock_idle_sleep_event()`, `sched_clock_idle_wakeup_event()`, `clear_sched_clock_stable()`, and weak `running_clock()`. Under `CONFIG_HAVE_UNSTABLE_SCHED_CLOCK`, `struct sched_clock_data` stores `tick_raw`, `tick_gtod`, and `clock`; per-CPU instances are shared-aligned. Static keys track `sched_clock_running` and `__sched_clock_stable`.

## Control Flow
On stable-clock systems, scheduler clock reads mostly forward to architecture `sched_clock()`. On unstable-clock systems, initialization computes offsets between GTOD (`ktime_get_ns()`) and raw `sched_clock()`, later marks the clock stable if no instability is detected, or schedules work to clone a safe timestamp to all CPUs and mark it unstable if instability is detected after boot.

When unstable, `sched_clock_local()` reads raw time, clamps negative deltas to zero, combines GTOD base plus raw deltas, clamps within a tick-sized window, and atomically updates the per-CPU clock monotonically. `sched_clock_remote()` couples local and remote per-CPU clocks by taking the larger value, with special atomic read handling for 32-bit. Tick and idle hooks stamp GTOD/raw samples and resync after idle wakeups unless timekeeping is suspended.

## State And Persistence
State is volatile per-CPU scheduler clock data plus global offsets/static keys. It persists only for the running boot. Stability transitions affect tick dependency state and irqtime accounting. There is no disk persistence.

## Dependencies And Integration Points
The file depends on timekeeping (`ktime_get_ns()`), raw architecture `sched_clock()`, static keys, tick dependencies, workqueues, irq/preemption controls, CPU IDs, and optional `generic_sched_clock_init()`. Scheduler, tracing, irqtime, idle, and accounting code consume these clock APIs.

## Risks
Clock code is high risk because it runs in NMI/noinstr-sensitive contexts and must preserve monotonicity without heavy locking. Incorrect offset/stability transitions can create time jumps, bad runtime accounting, scheduler latency artifacts, or tracing anomalies. Remote clock coupling must be atomic on 32-bit and safe against concurrent NMI updates.

## Test Signals
Signals include boot logs marking sched_clock stable/unstable, successful operation with `tsc=unstable`, scheduler accounting sanity, tracing timestamps without backward local movement, idle wakeup tests, and lockdep/noinstr validation. Cross-CPU comparisons may go backward by design and should not be tested as globally monotonic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/completion.c -->
# sources/distributed-fs/ceph-client/kernel/sched/completion.c

## Purpose
`completion.c` implements the kernel completion primitive: a synchronization point where one or more waiters block until another context signals completion. Unlike semaphores, completions document event synchronization rather than mutual exclusion and support single or all-waiter wakeups.

## Important APIs, Types, And Functions
The key object is `struct completion`, with `done` and an `swait_queue_head`. Exported APIs include `complete()`, `complete_on_current_cpu()`, `complete_all()`, `wait_for_completion()`, `wait_for_completion_timeout()`, `wait_for_completion_io()`, `wait_for_completion_io_timeout()`, `wait_for_completion_interruptible()`, `wait_for_completion_interruptible_timeout()`, `wait_for_completion_killable()`, `wait_for_completion_state()`, `wait_for_completion_killable_timeout()`, `try_wait_for_completion()`, and `completion_done()`. Internal helpers include `complete_with_flags()`, `do_wait_for_common()`, `__wait_for_common()`, `wait_for_common()`, and `wait_for_common_io()`.

## Control Flow
`complete()` and `complete_on_current_cpu()` lock the swait queue, increment `done` unless saturated at `UINT_MAX`, and wake one waiter with optional wake flags. `complete_all()` sets `done` to `UINT_MAX` and wakes all waiters; callers must reinitialize before reuse. Wait paths call `might_sleep()`, annotate acquire/release, lock the wait queue, enqueue an swait entry if `done` is zero, set the requested task state, drop the lock while scheduling, reacquire, and repeat until signaled, interrupted, or timed out. On success, single completions decrement `done` unless saturated.

## State And Persistence
Completion state is entirely in memory and owned by the embedding subsystem. `done` is a counter for single completions or saturated `UINT_MAX` after `complete_all()`. Waiters are transient swait queue entries. No state persists outside the object lifetime.

## Dependencies And Integration Points
The implementation depends on scheduler task states, `schedule_timeout()`, `io_schedule_timeout()`, raw spinlocks with IRQ save/restore, swait queues, lockdep, and completion memory-order annotations. Completions are used throughout the kernel for task startup/shutdown, async work, device operations, RPC-like waits, and module teardown.

## Risks
Misuse risks include calling blocking waits from atomic context, reinitializing too soon after `complete_all()`, freeing a completion while `complete()` still references it, ignoring interruptible return codes, or expecting `completion_done()` to indicate absence of waiters after `complete_all()`. Implementation risks are memory ordering, lost wakeups, timeout semantics, and PREEMPT_RT locking constraints.

## Test Signals
Signals include unit or subsystem tests covering single waiter, multiple waiter, timeout, interruptible/killable waits, IO waits, `try_wait_for_completion()`, `completion_done()`, and `complete_all()` reinitialization discipline. Lockdep should catch atomic-context waits or invalid RT contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/completion.c -->
