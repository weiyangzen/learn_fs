# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/sched.c

Purpose: implements the SPU scheduler, binding saved contexts to physical SPUs, timeslicing, priority queues, NUMA/CPU-mask filtering, affinity gangs, load average accounting, and `/proc/spu_loadavg`.

Important APIs: `spu_set_timeslice`, `__spu_update_sched_info`, `spu_update_sched_info`, `do_notify_spus_active`, `spu_activate`, `spu_deactivate`, `spu_yield`, `spuctx_switch_state`, `spu_sched_init`, and `spu_sched_exit`. Internal helpers include `spu_bind_context`, `spu_unbind_context`, affinity placement functions, `find_victim`, `grab_runnable_context`, and `spusched_tick`.

Control flow: activation tries an idle SPU matching CPU/NUMA and affinity constraints; RT contexts can preempt lower-priority contexts. Binding associates the owner mm, installs callbacks, switches `ctx->ops` to hardware ops, restores CSA to hardware, and wakes run waiters. Unbinding saves hardware state back to the CSA, switches ops to backing ops, clears callbacks, updates statistics, and wakes stopped waiters. A scheduler kthread wakes on a timer and ticks each active SPU context, preempting non-FIFO contexts whose slice expired when a higher-priority queued context exists.

State and dependencies: global `spu_prio` holds runqueue bitmap/lists; `cbe_spu_info` provides physical SPU lists and counters; gang affinity fields are mutated under gang locks. Risks include lock ordering between context, node list, and runqueue locks; starvation during victim retry; affinity placement edge cases; and accounting drift. Test signals include priority preemption, NOSCHED reservation accounting, CPU affinity changes, gang affinity placement, loadavg output, and clean scheduler exit.
