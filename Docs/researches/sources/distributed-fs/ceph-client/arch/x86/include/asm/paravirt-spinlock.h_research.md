# sources/distributed-fs/ceph-client/arch/x86/include/asm/paravirt-spinlock.h

Purpose: defines the paravirtualized queued-spinlock interface and the fallback virtual spinlock shortcut for x86 guests. It lets hypervisors replace queued spinlock slow paths, unlock, wait/kick, and vCPU-preemption checks with PV-aware operations.

Important APIs, types, and functions: `struct pv_lock_ops` contains `queued_spin_lock_slowpath`, callee-save `queued_spin_unlock`, `wait`, `kick`, and callee-save `vcpu_is_preempted`. It declares global `pv_ops_lock`, native/PV slowpath and unlock symbols, `nopvspin`, `native_pv_lock_init()`, native test helpers, and `virt_spin_lock_key`. Inline wrappers include `pv_queued_spin_lock_slowpath()`, `pv_queued_spin_unlock()`, `pv_vcpu_is_preempted()`, `pv_wait()`, `pv_kick()`, `queued_spin_lock_slowpath()`, `queued_spin_unlock()`, `vcpu_is_preempted()`, `native_queued_spin_unlock()`, and `virt_spin_lock()`.

Control flow: under `CONFIG_PARAVIRT_SPINLOCKS`, queued spinlock calls dispatch through `PVOP_*` macros and can be patched to native byte-store unlock or no-preemption behavior when features are absent. `virt_spin_lock()` uses a static key to optionally replace fair queueing with test-and-set spinning in guests without PV spinlock support.

State and persistence: global PV ops and static key state are runtime-only. Lock state lives in each `qspinlock`.

Dependencies and integration points: depends on qspinlock layout, `paravirt_types.h`, static keys, KCSAN release annotation, CPU feature alternatives, KVM/Xen PV spinlock setup, and scheduler vCPU preemption reporting.

Risks: unlock uses a callee-save paravirt calling convention and must preserve release semantics on the low byte. Enabling `virt_spin_lock_key` trades fairness for avoiding holder-preemption stalls; incorrect use can regress native scalability or guest latency.

Test signals: qspinlock stress on native, KVM, and Xen; lock holder preemption tests; `nopvspin` boot option; static-key transitions during PV setup; KCSAN/lockdep validation; and CPU-hotplug with `vcpu_is_preempted()`.
