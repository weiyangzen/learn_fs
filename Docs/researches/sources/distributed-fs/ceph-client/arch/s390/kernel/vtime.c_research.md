## sources/distributed-fs/ceph-client/arch/s390/kernel/vtime.c

Purpose: Implements s390 virtual CPU timer accounting, steal-time calculation, multi-threading scaling, and exported virtual timer list APIs.

Important APIs and functions: `vtime_task_switch()`, `vtime_flush()`, `vtime_account_kernel()`, `vtime_account_softirq()`, `vtime_account_hardirq()`, `init_virt_timer()`, `add_virt_timer()`, `add_virt_timer_periodic()`, `mod_virt_timer()`, `mod_virt_timer_periodic()`, `del_virt_timer()`, and `vtime_init()`.

Control flow: Low-level timer reads update lowcore last-update fields, classify elapsed CPU-timer deltas into user, guest, system, hardirq, softirq, and steal buckets, scale user/system times for SMT utilization when needed, and push accounting to generic kernel time accounting. `vtime_flush()` also expires virtual timers when accumulated elapsed CPU time reaches the current virtual timer deadline. Virtual timers are kept in a sorted list protected by `virt_timer_lock`; expired callbacks run outside the lock and periodic timers are reinserted.

State and persistence: Owns global virtual timer list/lock, atomic current and elapsed virtual timer counters, per-CPU MT cycle arrays/scaling factors, and lowcore timer fields mirrored in task thread timer fields during context switch.

Dependencies and integration: Integrates with entry code lowcore timer updates, generic CPU/accounting APIs, CPU measurement facility `stcctm`, SMP SMT metadata, lowcore CPU timer instructions, and exported vtimer users.

Risks and test signals: Risks include accounting drift, steal-time underflow/overflow, timer-list races, callbacks modifying timers, and SMT scaling arithmetic. Test signals include `/proc/stat` user/system/irq/softirq/steal accounting, guest time for `PF_VCPU`, vtimer add/mod/del behavior, CPU hotplug vtime initialization, and SMT utilization scaling changes.
