# Group Research: group_306_dragonflybsd_sources_os_bsd_dragonflybsd_sys_kern_usched_bsd4_c_sour_63a540b2772d

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/dragonflybsd`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/usched_bsd4.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/usched_bsd4.c

## Purpose

`usched_bsd4.c` implements DragonFly BSD's original BSD4 user scheduler. It registers `usched_bsd4`, manages runnable user LWPs separately from the LWKT kernel-thread scheduler, maps real-time/normal/idle/thread priorities onto scheduler queues, tracks per-CPU current user-thread ownership, and uses helper threads plus IPIs to place runnable user threads on CPUs.

## Main Responsibilities

- Registers the `bsd4` scheduler through `struct usched usched_bsd4`.
- Maintains global run queues for realtime/FIFO, normal, and idle classes.
- Acquires and releases the per-CPU current user LWP when threads enter or leave userland.
- Computes dynamic user priorities from `rtprio`, `nice`, estimated CPU use, and batch behavior.
- Implements round-robin preemption and scheduler-clock CPU accounting.
- Selects CPUs for newly runnable LWPs using ready/current CPU masks, affinity masks, SMT hints, and optional cache-coherent topology heuristics.
- Starts per-CPU scheduler helper threads and exposes `kern.usched_bsd4.*` sysctls.

## Scheduling Model

The file defines `MAXPRI` as 128 and uses `NQS == 32`, so each scheduler queue covers four priority values. Normal LWPs use `lwp_usdata.bsd4` fields for `priority`, `rqindex`, `estcpu`, `batch`, and `rqtype`.

There are three global queue arrays:

- `bsd4_rtqueues[NQS]` for realtime/FIFO priorities.
- `bsd4_queues[NQS]` for normal priorities.
- `bsd4_idqueues[NQS]` for idle priorities.

Each queue class has a bitmask (`bsd4_rtqueuebits`, `bsd4_queuebits`, `bsd4_idqueuebits`) so the scheduler can find the first non-empty queue with bit scan operations. `bsd4_runqcount` tracks total queued LWPs, `bsd4_curprocmask` tracks CPUs with a designated current user LWP, and `bsd4_rdyprocmask` tracks CPUs ready to accept work.

## Core Control Flow

`bsd4_acquire_curproc()` is called before returning to userland. It removes the thread from sleep queues if needed, recalculates `estcpu`, handles pending user reschedule requests, and loops until the calling LWP becomes the per-CPU `uschedcp`. If it cannot run on the current CPU or loses to a better current LWP, it deschedules itself, queues itself through `bsd4_setrunqueue()`, and switches away. This function is explicitly allowed to migrate the thread.

`bsd4_release_curproc()` detaches the current LWP from the CPU's user scheduler slot, clears the current-CPU mask bit, sets `upri` to `PRIBASE_NULL`, and calls `bsd4_select_curproc()` to choose a replacement.

`bsd4_select_curproc()` chooses the next LWP from the global queues, optionally using the cache-coherent chooser. If it finds one, it marks the CPU as having a current user LWP, stores `uschedcp`, resets round-robin state, acquires the target LWKT thread, and schedules it.

`bsd4_setrunqueue()` validates the LWP state, gives away LWKT ownership, inserts the LWP into the global scheduler queue, then searches for a CPU to notify. It first prefers CPUs that are ready but not currently running a user thread, then CPUs running worse-priority user threads, and finally falls back to a rotating CPU. Remote CPUs are kicked with either an IPI reschedule or helper-thread wakeup.

## Priority and Accounting

`bsd4_schedulerclock()` runs at `ESTCPUFREQ` on each CPU. It requests user reschedule after `usched_bsd4_rrinterval`, increments `lwp_estcpu` toward `ESTCPUMAX`, asserts no active spinlocks, and calls `bsd4_resetpriority()`.

`bsd4_recalculate_estcpu()` decays or recomputes estimated CPU use based on elapsed scheduler ticks, the LWP's measured CPU ticks, system runnable pressure, and `usched_bsd4_decay`. It also updates `lwp_batch`: sustained CPU use makes a thread more batch-like, while low CPU use reduces batchiness.

`bsd4_resetpriority()` maps scheduling class to queue priority. Realtime/FIFO, idle, and thread classes use explicit `rtprio` values. Normal class combines `nice`, `estcpu`, and the batch adjustment, then moves an on-runqueue LWP between queues if its bucket changes. It also updates `td_upri` for LWKT's view of user threads running in the kernel and may trigger a reschedule if the LWP became more important than a CPU's current user LWP.

`bsd4_forking()` initializes child `estcpu` above the parent to make the child less desirable, starts child batch state at midpoint, and docks the parent slightly to limit fork-heavy workloads.

## CPU Selection and Topology

The default chooser, `bsd4_chooseproc_locked()`, scans realtime, normal, then idle queues for the best runnable LWP whose CPU mask includes the current CPU. It avoids replacing `chklp` unless the queued thread is meaningfully better and prefers a same-CPU candidate at equal queue priority when available.

`bsd4_chooseproc_locked_cache_coherent()` adds topology-aware behavior. It tries to keep threads near their home CPU/topology level, defers batch-like threads that would harm cache locality, records a "best of the worst" candidate when it must give up, and uses `bsd4_kick_helper()` to wake the LWP's preferred CPU instead of stealing unnecessarily.

The SMT path in `bsd4_setrunqueue()` prefers an idle physical core and uses sibling information from `cpu_topology` to avoid loading sibling logical CPUs when a better core exists.

## Initialization and Tunables

`bsd4_rqinit()` initializes the global queues and spinlock and enables CPU 0 for scheduling. `sched_thread_cpu_init()` creates per-CPU helper threads, records CPU topology nodes, enables ready/current masks, and creates `kern.usched_bsd4` sysctls.

Important tunables include `rrinterval`, `decay`, `batch_time`, `kicks`, `smt`, `cache_coherent`, `upri_affinity`, `queue_checks`, and `stick_to_level`. Debug state is exposed under `debug.bsd4_*`, and KTR events trace acquisition, release, runqueue placement, choosing, and helper behavior.

## Concurrency and Risk Notes

The scheduler depends on carefully paired critical sections, `bsd4_spin`, atomic CPU-mask updates, `LWP_MP_ONRUNQ`, LWKT deschedule/acquire/schedule operations, and IPI callbacks. The comments repeatedly identify migration-sensitive paths: `bsd4_acquire_curproc()` can migrate a thread even though most kernel code assumes stable CPU locality. Runqueue insertion loses ownership of the LWP once the spinlock is released, so priority changes, exits, or remote CPU selection can race unless state flags and locks are correct.

The global runqueue design creates contention around `bsd4_spin`, while the topology/cache-coherent logic adds heuristic complexity. CPU-mask edge cases are partly handled, including fallback behavior when `usched_global_cpumask` does not cover an LWP's allowed CPU mask.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/usched_bsd4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/usched_dfly.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/usched_dfly.c

## Purpose

`usched_dfly.c` implements DragonFly BSD's `dfly` user scheduler. It is a topology-aware evolution of the older BSD4 scheduler: instead of one global runqueue set, it maintains per-CPU runqueues, per-CPU aggregate load, CPU topology metadata, helper threads, and tunable heuristics for locality, IPC pairing, NUMA memory weighting, priority fairness, idle pulling, proactive pushing, and periodic rebalancing.

## Main Responsibilities

- Registers `struct usched usched_dfly`.
- Acquires and releases per-CPU current user LWP ownership for userland returns.
- Maintains per-CPU realtime, normal, and idle run queues.
- Tracks each LWP's queue CPU (`lwp_qcpu`), priority, estimated CPU, load contribution, fork state, and round-robin count through `lwp_usdata.dfly`.
- Chooses target CPUs by traversing the CPU topology tree and applying weighted load calculations.
- Updates per-CPU `uload` and `ucount` as LWPs become runnable, sleep, migrate queues, or exit.
- Implements scheduler-clock preemption, priority recalculation, and periodic balancing.
- Creates helper threads and exposes `kern.usched_dfly.*` sysctls.

## Data Model

Most scheduler constants and structures are defined in `sys/usched_dfly.h`, included by this file. Priorities use `MAXPRI == 128`, `NQS == 32`, and `PPQ == 4`. Normal priorities combine nice contribution (`NICE_QS` queues) and estimated CPU contribution (`EST_QS` queues). `ESTCPUMAX` is capped by `EST_QS`.

Each `struct usched_dfly_pcpu` contains:

- A per-CPU scheduler spinlock.
- A helper thread and `globaldata` pointer.
- Current user priority and current user LWP.
- Per-CPU aggregate `uload` and runnable/running `ucount`.
- Three queue arrays: normal, realtime/FIFO, and idle.
- Bitmaps for non-empty queues.
- Queue count, CPU id, CPU mask, and CPU topology node.

Global masks publish CPU availability: `dfly_curprocmask` for CPUs with current user LWPs and `dfly_rdyprocmask` for CPUs ready to accept work. Per-CPU flags mirror those masks to reduce global cache-line traffic.

## Core Control Flow

`dfly_acquire_curproc()` is called when a thread is about to return to userland. It has a fast path for the common case where the thread is not on a sleep queue, no scheduler action is pending, and it is already the CPU's `uschedcp`. The slow path removes sleep-queue state, recalculates CPU usage, handles pending reschedule requests, then loops until the LWP owns the current CPU's user scheduler slot.

During that loop it can:

- Move an outcast LWP to a CPU allowed by its CPU mask.
- Proactively push a rescheduled LWP to a better queue.
- Claim an idle `uschedcp` slot.
- Steal a slot from a much worse current user LWP.
- Requeue after an explicit yield.
- Move to another CPU under proactive push features.
- Fall back to descheduling itself, queueing, and switching.

`dfly_release_curproc()` clears `uschedcp` when the current LWP leaves user scheduling, updates the current mask unless the thread yielded, and calls `dfly_select_curproc()` to choose a replacement.

`dfly_select_curproc()` chooses the best LWP from the local CPU queue, marks the CPU current if needed, installs `uschedcp`, and schedules the target LWKT thread.

`dfly_setrunqueue()` chooses a target per-CPU queue for a runnable LWP. Forked LWPs get special placement according to feature flags: best CPU, same CPU, random/simple CPU, or current CPU when no local queue pressure exists. Non-forked LWPs normally use `dfly_choose_best_queue()`.

`dfly_setrunqueue_dd()` inserts the LWP into the chosen CPU queue and decides whether to interrupt the current user thread immediately, defer until the next scheduler tick, wake a local helper, or send a remote reschedule IPI.

## Priority, Load, and Accounting

`dfly_schedulerclock()` runs from the per-CPU scheduler timer. It handles contended idle-thread cases, increments per-LWP round-robin counts, triggers reschedule at `usched_dfly_rrinterval`, optionally respects `TDF_MP_BATCH_DEMARC`, increments `lwp_estcpu`, and calls `dfly_resetpriority()`.

`dfly_recalculate_estcpu()` recomputes estimated CPU use after enough scheduler ticks have elapsed. Sleeping LWPs decay by half and clear fast estimate state. Running LWPs update per-CPU accounting through `updatepcpu()`, compute instant CPU fraction from `lwp_cpticks / ttlticks`, and fold it into `lwp_estcpu`.

`dfly_resetpriority()` locks the LWP's queue CPU, maps `rtprio` plus nice/estcpu into `lwp_priority`, moves an on-runqueue LWP between buckets when its queue index changes, updates `td_upri`, recomputes `lwp_uload` with `lptouload()`, adjusts per-CPU aggregate load if the LWP is counted, and may request local or remote reschedule.

`dfly_uload_update()` adds an LWP's load to its queue CPU while its LWKT thread is runnable and removes it after the LWP sleeps. `dfly_exiting()` clears any remaining load contribution during LWP exit. `dfly_changeqcpu_locked()` changes queue CPU and moves load accounting when an LWP migrates between per-CPU queues.

`dfly_forking()` gives a child a worse initial `estcpu` according to `usched_dfly_forkbias`, marks it as forked for first placement, initializes `lwp_qcpu` from the parent subject to CPU mask, and docks the parent slightly to dampen fork-heavy workloads.

## Queue Selection and Rebalancing

`dfly_chooseproc_locked()` selects either the best or worst LWP from a CPU's queues. Best mode scans realtime, normal, then idle queues from lowest queue index. Worst mode scans idle, normal, then realtime from highest queue index. It respects `chklp` priority to avoid bouncing, checks CPU masks when pulling from another CPU, removes the chosen LWP, clears `LWP_MP_ONRUNQ`, and transfers queue/load ownership if the LWP is being stolen from another CPU.

`dfly_choose_best_queue()` is the main push heuristic. It walks from `root_cpu_node` down the topology tree, scoring child CPU groups by average weighted load. The score includes aggregate `uload`, `ucount * weight3`, priority availability (`weight4`), current CPU stickiness (`weight1`), NUMA memory advantage (`weight5`), and wake-from CPU pairing (`weight2`). IPC pairing can prefer or avoid SMT siblings or the same logical CPU depending on `ipc_smt`, `ipc_same`, and load average. The selected CPU is forced back into the LWP's allowed CPU mask if needed.

`dfly_choose_worst_queue()` is the pull heuristic. It walks the topology tree looking for the most overloaded nearby queue with runnable work, avoids returning the current CPU, and can ignore some stickiness when called by the periodic rebalancer.

`dfly_choose_queue_simple()` is the fallback when topology is unavailable. It scans ready CPUs from a rotating base, first preferring CPUs without current user LWPs, then CPUs with worse current priorities, and finally falls back to an allowed CPU.

`dfly_schedulerclock()` also contains the rover rebalancer for feature `0x04`. Every eight ticks, a rotating CPU can pull the worst LWP from the worst queue if the load difference justifies it, then either schedule it immediately or enqueue it locally.

`dfly_helper_thread()` runs per CPU at low priority. It marks the CPU ready, clears reschedule requests, schedules local queued work when available, and, under feature `0x01`, can steal a worst LWP from another overloaded CPU. It sleeps with a configurable poll timeout.

## Initialization and Tunables

`usched_dfly_cpu_init()` initializes the sysctl context, records highest NUMA node memory, locks configuration while per-CPU structures are initialized, creates helper threads, initializes queues, records CPU topology nodes, sets ready/current masks, and registers sysctls.

Key tunables include:

- `rrinterval`, `decay`, `poll_ticks`.
- `ipc_smt` and `ipc_same` for wake-from pairing.
- `weight1` through `weight7` for locality, IPC, queue count, priority availability, NUMA memory, and transfer hysteresis.
- `fast_resched`, `features`, and `swmask`.
- Debug sysctls `debug.dfly_scdebug`, `debug.dfly_pid_debug`, `debug.dfly_chooser`, and `debug.dfly_forkbias`.

Feature bits control idle pulling, proactive pushing, rebalancing rover, more proactive pushing, and fork placement mode.

## Concurrency and Risk Notes

This scheduler has many concurrent state transitions across per-CPU spinlocks, `lwp_spin`, atomic CPU masks, IPI callbacks, helper threads, and LWKT scheduling operations. Correctness depends on `lwp_qcpu`, `LWP_MP_ONRUNQ`, and `LWP_MP_ULOAD` staying synchronized with queue membership and per-CPU load counters. Several paths intentionally avoid global locks and accept benign races around current priorities or reschedule requests.

The topology heuristics are performance-sensitive and heavily tunable. Incorrect weights can cause thread migration instability, poor IPC locality, NUMA imbalance, or underuse of idle CPUs. The comments explicitly warn that fork bias and IPC/locality weights can strongly affect build workloads and multi-socket behavior.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/usched_dfly.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/usched_dummy.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/usched_dummy.c

## Purpose

`usched_dummy.c` implements a simple example DragonFly user scheduler named `dummy`. It provides the same `struct usched` interface as the real schedulers but uses one global FIFO run queue, minimal priority logic, basic per-CPU current-user-LWP state, and helper threads. It is useful as a reference implementation for scheduler mechanics rather than as a sophisticated production scheduler.

## Main Responsibilities

- Registers `struct usched usched_dummy`.
- Maintains a single global `TAILQ` of runnable user LWPs.
- Tracks each CPU's current user LWP in `dummy_pcpu[]`.
- Uses `dummy_curprocmask` and `dummy_rdyprocmask` to publish CPUs with current user LWPs and CPUs ready to accept work.
- Handles acquire/release, runqueue insertion, selection, yield, priority reset, fork initialization, and helper-thread wakeup.
- Exposes `kern.usched_dummy_rrinterval`.

## Scheduling Model

The scheduler defines the same priority base ranges used by BSD4-style user schedulers, but it does not maintain per-priority queues. `lwp_priority` and `lwp_estcpu` reuse the `lwp_usdata.bsd4` fields. All runnable LWPs that cannot immediately become a CPU's `uschedcp` are inserted at the tail of `dummy_runq`.

`dummy_runqcount` tracks the global queue length. `dummy_spin` protects the queue and cross-CPU helper decisions. Each CPU has only `rrcount`, `helper_thread`, and `uschedcp`.

## Core Control Flow

`dummy_acquire_curproc()` is called before userland return. It handles pending reschedule requests through `dummy_select_curproc()`. If the CPU has no current LWP and the global runqueue is empty, the caller becomes `uschedcp`. Otherwise the caller runs any passive release hook, deschedules itself, enqueues itself with `dummy_setrunqueue()`, switches away, and loops until some CPU selects it as current. The loop can migrate the thread.

`dummy_release_curproc()` checks that the LWP is not on a runqueue and, if it is the CPU's current user LWP, calls `dummy_select_curproc()`.

`dummy_select_curproc()` clears the reschedule request, pops the first LWP from `dummy_runq`, clears `LWP_MP_ONRUNQ`, installs it as `uschedcp`, marks the CPU current, acquires the LWKT thread, and schedules it. If the runqueue is empty, it clears the CPU's current-user bit.

`dummy_setrunqueue()` immediately assigns the LWP to the local CPU if that CPU has no current user LWP. Otherwise it inserts the LWP at the global queue tail, marks `LWP_MP_ONRUNQ`, gives away LWKT ownership, and wakes another ready helper CPU if one is available.

## Priority and Timer Behavior

`dummy_schedulerclock()` only implements round-robin timing. If an LWP is running and the per-CPU `rrcount` reaches `usched_dummy_rrinterval`, it resets the counter and requests user reschedule.

`dummy_recalculate_estcpu()` is empty. `dummy_forking()` copies the parent's `estcpu` to the child. `dummy_resetpriority()` maps `lwp_rtprio.type` and `prio` into broad priority bases and updates `td_upri` for normal priority. It does not reposition queued LWPs by priority because the runqueue is FIFO.

`dummy_yield()` simply requests user reschedule. `dummy_changedcpu()`, `dummy_exiting()`, and `dummy_uload_update()` are no-ops.

## Helper Threads and Initialization

`dummyinit()` initializes the global queue and spinlock and enables CPU 0 for dummy scheduling. `dummy_sched_thread_cpu_init()` creates one helper thread per active CPU, enables that CPU in the ready mask, and clears current-mask bits for CPUs other than CPU 0.

`dummy_sched_thread()` uses LWKT deschedule interlocking. Each helper marks itself ready, then either forwards the wakeup to another ready CPU if it already has `uschedcp`, pulls the first LWP from the global queue if it is idle, or goes back to sleep.

## Concurrency and Risk Notes

This file intentionally avoids advanced priority and affinity behavior. The global FIFO queue is simple but can contend on `dummy_spin`, does not preserve priority ordering, and only does minimal CPU-affinity handling. It still exercises sensitive scheduler mechanics: LWKT descheduling, `LWP_MP_ONRUNQ`, helper wakeups, current/ready CPU masks, and acquire paths that can migrate the thread.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/usched_dummy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_aio.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_aio.c

## Purpose

`vfs_aio.c` is a stub implementation for the POSIX 1003.1B AIO/LIO facility in DragonFly BSD. It provides syscall entry points and a kqueue filterops symbol, but no asynchronous I/O functionality.

## Main Responsibilities

- Defines syscall handlers for AIO/LIO-related system calls.
- Returns `ENOSYS` from every AIO syscall stub.
- Provides `aio_filtops` for event-filter integration.
- Rejects AIO filter attachment with `ENXIO`.

## Implemented Entry Points

The following syscall handlers all immediately return `ENOSYS`:

- `sys_aio_return()`
- `sys_aio_suspend()`
- `sys_aio_cancel()`
- `sys_aio_error()`
- `sys_aio_read()`
- `sys_aio_write()`
- `sys_lio_listio()`
- `sys_aio_waitcomplete()`

The source tree's syscall table references these handlers for AIO syscall numbers, so userland can call the symbols but receives "function not implemented" behavior.

## Event Filter Behavior

`filt_aioattach()` always returns `ENXIO`, indicating that an AIO knote cannot be attached. `aio_filtops` is exported with `FILTEROP_MPSAFE`, the attach function, and null detach/event callbacks.

## Integration and Risk Notes

This file deliberately contains no VFS, vnode, buffer, credential, request queue, signal, completion, cancellation, or timeout logic. Its behavior is stable and small: AIO is unavailable through these interfaces. Compatibility-sensitive callers must handle `ENOSYS` for syscalls and `ENXIO` for kqueue AIO filter attachment.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_aio.c -->