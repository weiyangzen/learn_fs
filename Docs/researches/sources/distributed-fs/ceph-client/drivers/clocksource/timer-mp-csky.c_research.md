# sources/distributed-fs/ceph-client/drivers/clocksource/timer-mp-csky.c

Purpose: C-SKY SMP private timer driver using CPU control registers for per-CPU clockevents and a CPU-register clocksource/sched_clock.

Important APIs/types/functions: per-CPU `struct timer_of csky_to` requests only the clock. `mtcr()` and `mfcr()` access private timer control, load, current value, and status registers. `csky_mptimer_starting_cpu()` registers each CPU clockevent; `csky_timer_interrupt()` clears status and dispatches; `csky_clocksource` reads `PTIM_CCVR`.

Control flow: init maps one common private IRQ from DT, requests it as percpu, calls `timer_of_init()` for each possible CPU to acquire clock metadata, registers clocksource/sched_clock at the timer rate, then installs CPU hotplug callbacks. CPU startup sets cpumask, enables percpu IRQ, and registers oneshot clockevent; CPU dying disables IRQ.

State/persistence: `csky_mptimer_irq` is global, and `csky_to` is per-CPU static state. No MMIO base is used; control register state is CPU-local.

Dependencies/integration: compatible `csky,mptimer`, DT IRQ and clock, arch `asm/reg_ops.h`, CPU hotplug, percpu IRQ infrastructure, `timer-of`.

Risks: rollback cleans timer_of resources but not percpu IRQ on all failures; clocksource rate uses last initialized CPU’s timer metadata; hardware must provide synchronized per-core counters. Test signals include CPU hotplug on/off, percpu IRQ affinity, one-shot event delivery, and stable cross-CPU time.
