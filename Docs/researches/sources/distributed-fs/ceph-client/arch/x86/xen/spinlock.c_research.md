<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/spinlock.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/spinlock.c

## Purpose
Provides Xen PV queued-spinlock hooks. It lets a vCPU blocked on a queued spinlock yield to Xen and wait for a disabled per-CPU event-channel IRQ, and lets unlock paths kick the target vCPU through a Xen synthetic IPI.

## Important APIs, Types, And Functions
State is `lock_kicker_irq`, `irq_name`, and `xen_qlock_wait_nest`. Main functions are `xen_qlock_kick`, `xen_qlock_wait`, `xen_init_lock_cpu`, `xen_uninit_lock_cpu`, and `xen_init_spinlocks`. It installs `pv_ops_lock.queued_spin_lock_slowpath`, `queued_spin_unlock`, `wait`, `kick`, and `vcpu_is_preempted`.

## Control Flow
`xen_init_spinlocks` disables PV spinlocks for one-vCPU or `nopvspin` configurations; otherwise it initializes the lock hash and patches PV qspinlock hooks. For each CPU, `xen_init_lock_cpu` binds `XEN_SPIN_UNLOCK_VECTOR`, disables the Linux IRQ so it is used as a pollable Xen event, and records its IRQ. Waiters clear a pending event on first-level entry or poll the IRQ if the lock byte still matches the expected value. Unlockers kick the owner CPU if its kicker IRQ exists.

## State And Persistence
Persistent state is per-CPU disabled IRQ bindings and names, plus global paravirt lock hook replacement. It has no durable persistence.

## Dependencies And Integration Points
Depends on Xen events, x86 qspinlock paravirt support, `virt_spin_lock_key`, `nopvspin`, and stolen-vCPU detection.

## Risks And Edge Cases
Waiting is skipped in NMI or before IRQ initialization, so paths fall back to spinning. Nested waits must avoid consuming another waiter's event. The dummy handler should never run because IRQs are disabled; delivery would trigger `BUG()`. CPU hotplug must unbind initialized IRQs only.

## Test Signals
Use lock-stress workloads on multi-vCPU Xen, CPU hotplug, boot with `mitigations=auto,nosmt`, `nopvspin`/single-vCPU configurations, and IRQ leak checks after offline/online.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/spinlock.c -->
