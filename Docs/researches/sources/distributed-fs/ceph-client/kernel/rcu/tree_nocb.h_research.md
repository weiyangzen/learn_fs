# sources/distributed-fs/ceph-client/kernel/rcu/tree_nocb.h

## Purpose
`tree_nocb.h` implements the tree-RCU no-callbacks (NOCB) path used when CPUs offload RCU callback processing to per-CPU callback kthreads and per-group grace-period kthreads. It covers boot-time selection of NOCB CPUs, callback enqueue bypassing, lazy callback flushing, deferred wakeups, runtime offload/deoffload of offline CPUs, kthread creation, and diagnostic dumps. When `CONFIG_RCU_NOCB_CPU` is disabled, the file supplies stubs so the rest of tree RCU can call the same helpers without conditional code.

## Important APIs, Types, and Functions
- Boot/module controls: `rcu_nocb_setup()`, `parse_rcu_nocb_poll()`, `nocb_nobypass_lim_per_jiffy`, and `rcu_nocb_gp_stride` configure offloaded CPUs, polling mode, bypass thresholds, and GP-kthread grouping.
- Lock helpers: `rcu_nocb_lock()`, `rcu_nocb_unlock()`, `rcu_nocb_unlock_irqrestore()`, `rcu_nocb_bypass_lock()`, and `rcu_lockdep_assert_cblist_protected()` centralize NOCB locking rules around `rdp->nocb_lock` and `rdp->nocb_bypass_lock`.
- Enqueue/bypass path: `rcu_nocb_try_bypass()`, `rcu_nocb_flush_bypass()`, `rcu_nocb_do_flush_bypass()`, `nocb_bypass_needs_flush()`, `call_rcu_nocb()`, and `__call_rcu_nocb_wake()` decide whether callbacks go directly to `rdp->cblist` or through `rdp->nocb_bypass`.
- Worker paths: `nocb_gp_wait()`, `rcu_nocb_gp_kthread()`, `nocb_cb_wait()`, and `rcu_nocb_cb_kthread()` drive grace-period waiting and callback invocation for offloaded CPUs.
- Runtime toggling: `rcu_nocb_cpu_offload()`, `rcu_nocb_cpu_deoffload()`, `rcu_nocb_cpu_toggle_offload()`, `rcu_nocb_rdp_offload()`, and `rcu_nocb_rdp_deoffload()` change NOCB state for offline CPUs.
- Lazy RCU hooks: `rcu_set_jiffies_lazy_flush()`, `rcu_get_jiffies_lazy_flush()`, `lazy_rcu_shrink_count()`, and `lazy_rcu_shrink_scan()` expose testable lazy flush timing and memory-pressure flushing.
- Initialization/diagnostics: `rcu_init_nohz()`, `rcu_boot_init_nocb_percpu_data()`, `rcu_spawn_cpu_nocb_kthread()`, `rcu_organize_nocb_kthreads()`, `rcu_bind_current_to_nocb()`, and `show_rcu_nocb_state()`.

## Control Flow
At boot, `rcu_nocbs=`, `rcu_nocb_poll`, `CONFIG_RCU_NOCB_CPU_DEFAULT_ALL`, and `nohz_full` determine `rcu_nocb_mask`. `rcu_init_nohz()` allocates or merges masks, registers the lazy shrinker when enabled, marks selected per-CPU segmented callback lists as `SEGCBLIST_OFFLOADED`, and calls `rcu_organize_nocb_kthreads()` to assign each CPU to a GP representative.

On `call_rcu()`, the NOCB caller enters `call_rcu_nocb()`. `rcu_nocb_try_bypass()` first handles non-offloaded and early-boot cases, then rate-limits direct `cblist` enqueues. High-rate or lazy callbacks use `nocb_bypass`; old or full bypass queues are flushed into `cblist`. If a formerly empty queue receives work, `__call_rcu_nocb_wake()` wakes the GP kthread immediately or schedules a deferred wakeup timer depending on IRQ state, polling mode, and whether callbacks are lazy-only.

The GP kthread loops in `nocb_gp_wait()`. It scans the NOCB group list, flushes bypass lists when age/size thresholds require, advances segmented callback lists when grace periods complete, wakes per-CPU callback kthreads when callbacks are ready, waits for the earliest needed grace period, and processes pending offload/deoffload toggles. The callback kthread waits on `nocb_cb_wq`, invokes `rcu_do_batch()`, advances callbacks again if possible, and sleeps when no ready callbacks remain.

Runtime offload/deoffload requires the target CPU to be offline. Deoffload performs `rcu_barrier()`, parks the callback kthread, verifies empty lists, asks the GP kthread to remove the `rdp` from the group list, and clears `SEGCBLIST_OFFLOADED`. Offload performs the reverse list/flag transition and unparks the callback kthread.

## State and Persistence
State is in per-CPU `struct rcu_data`: `cblist`, `nocb_bypass`, `lazy_len`, `nocb_*_kthread`, `nocb_gp_rdp`, wait queues, wakeup timers, sleep flags, group list nodes, and bypass rate counters. Global state includes `rcu_nocb_mask`, `rcu_nocb_poll`, `rcu_state.nocb_is_setup`, `rcu_state.nocb_mutex`, and lazy shrinker registration. There is no filesystem persistence; configuration persists only through boot parameters, module parameters, and in-memory kernel state.

## Dependencies and Integration Points
The file is included by the tree-RCU implementation and depends on RCU segmented callback lists, per-CPU `rcu_data`, `rcu_node` grace-period sequencing, kthreads, timers, swait queues, CPU hotplug locking, cpumasks, `NO_HZ_FULL`, shrinkers, tracepoints, and lockdep. It integrates with `tree_plugin.h` through `rcu_rdp_is_offloaded()`, with stall diagnostics through `show_rcu_nocb_state()`, with memory reclaim through the lazy shrinker, and with callback enqueue/core GP code through `call_rcu_nocb()` and deferred wakeup flushing.

## Risks
The central risks are ordering and wakeup races. Bypass callbacks must not be stranded when `cblist` is empty, `cblist.len` must continue to account for bypass entries, lazy and non-lazy callbacks must retain ordering, and deferred timer wakeups must not leave GP kthreads asleep. Runtime toggling is sensitive to offline CPU preconditions, `rcu_barrier()` completion, parked kthreads, and stable `SEGCBLIST_OFFLOADED` reads. Locking is split across `nocb_lock`, `nocb_bypass_lock`, `nocb_gp_lock`, CPU hotplug state, and `rcu_state.nocb_mutex`, so incorrect call context can create deadlocks or lockdep splats.

## Test Signals
Useful signals include boot logs showing NOCB CPU masks, `rcu_nocb_poll`, and GP stride grouping; tracepoints from `trace_rcu_nocb_wake()`; `show_rcu_nocb_state()` output in stall dumps; rcutorture NOCB/lazy scenarios; hotplug tests that offload and deoffload offline CPUs; memory pressure that triggers lazy shrinker scans; and lockdep warnings from unsafe offloaded-state reads or unprotected callback-list access.
