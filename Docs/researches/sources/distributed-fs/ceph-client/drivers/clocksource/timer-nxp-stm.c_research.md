# sources/distributed-fs/ceph-client/drivers/clocksource/timer-nxp-stm.c

Purpose: NXP System Timer Module platform driver for S32G2, registering one STM instance per possible CPU as both a clocksource and a CPU-affine clockevent.

Important APIs/types/functions: `struct stm_timer` embeds base, rate, delta, saved counter, clockevent, clocksource, and module refcount. Clocksource callbacks use module get/put and suspend/resume counter save. Clockevent callbacks program channel 0 compare and update compare in ISR. `nxp_stm_timer_probe()` is a devm platform-driver probe guarded by `stm_instances_lock`.

Control flow: probe serializes instance assignment, ignores extra nodes beyond possible CPUs, maps MMIO, gets IRQ and enabled clock, allocates state, requests IRQ, registers clocksource/sched_clock, initializes per-CPU clockevent for current instance number, increments instances, and installs CPU hotplug when all possible CPUs have an instance. CPU startup forces IRQ affinity and registers clockevent with a 2 us minimum delta.

State/persistence: global `stm_instances`, per-CPU `stm_timers`, `stm_sched_clock`, and per-instance atomic module refcounts. Suspend stores counter and resumes restores it.

Dependencies/integration: platform compatible `nxp,s32g2-stm`, devm resources, CPU hotplug, IRQ affinity, CCF clock, module metadata.

Risks: each instance registers a clocksource and overwrites sched_clock pointer; hotplug only installs after all CPUs’ instances probed; periodic mode uses `rate` as delta, which is one second rather than `rate/HZ`; compare race returns `-ETIME`. Test signals include multi-node async probing, CPU hotplug, IRQ affinity, suspend/resume counter restore, and clockevent periodic correctness.
