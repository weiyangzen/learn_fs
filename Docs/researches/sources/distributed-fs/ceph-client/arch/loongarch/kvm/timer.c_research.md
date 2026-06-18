# sources/distributed-fs/ceph-client/arch/loongarch/kvm/timer.c

Purpose: virtualizes the LoongArch stable timer for KVM guests, switching between hardware guest timer state while running and hrtimer-backed software state while blocked/outside guest.

Important APIs, types, and functions: `kvm_init_timer()`, `kvm_restore_timer()`, `kvm_save_timer()`, `kvm_swtimer_wakeup()`, and helpers `ktime_to_tick()`, `tick_to_ns()`, `_kvm_save_timer()`.

Control flow: timer init records a MHz-scale frequency and clears TVAL. Restore disables the hardware timer, restores ESTAT/TCFG, handles disabled timers, oneshot fired state, blocked vCPU soft timer cancellation, and recalculates remaining ticks or periodic expiry. Save reads TCFG/TVAL/ESTAT, computes a future hrtimer expiry, and starts a pinned hard hrtimer if the vCPU is blocking. The hrtimer callback queues `INT_TI` and wakes the vCPU waitqueue.

State and persistence: per-vCPU timer fields include `timer_mhz`, `expire`, `swtimer`, and saved timer CSRs in `vcpu->arch.csr`. Pending timer interrupts are represented in `irq_pending` and guest ESTAT.

Dependencies and integration points: called by vCPU create/load/put paths; uses CSR timer helpers, hrtimer, rcuwait, delay loops for hardware interrupt settling, and interrupt delivery.

Risks: oneshot fired handling and TVAL `-1` semantics are subtle. Frequency conversion uses `timer_hz >> 20`; precision and zero risks should be considered for unusual clocks. PREEMPT_RT expectations drive hard pinned timer mode.

Test signals: guest clocksource/timer tests, vCPU halt/wakeup, periodic and oneshot timers, migration/save-restore timer state, and blocked vCPU timer expiry.
