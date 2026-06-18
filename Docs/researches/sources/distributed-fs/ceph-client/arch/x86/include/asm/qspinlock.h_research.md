<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/qspinlock.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/qspinlock.h

Purpose: provides x86 queued spinlock customization, especially the pending-bit fast path and paravirtual lock integration. Important APIs/macros are `_Q_PENDING_LOOPS`, `queued_fetch_set_pending_acquire()`, `native_pv_lock_init()`, and inclusion of generic qspinlock logic.

Control flow: lock acquisition uses `GEN_BINARY_RMWcc()` with a locked `btsl` to atomically set the pending bit and reconstruct the observed lock word, then falls through to generic queued spinlock paths. Paravirt builds route through paravirt spinlock hooks.

State and persistence: lock state resides in `struct qspinlock`; this header owns no global state. Dependencies include jump labels, CPU features, paravirt, `rmwcc`, and generic qspinlock types. Risks include incorrect condition-code read-modify-write semantics, pending-bit races, and paravirt/native divergence. Test signals include SMP spinlock stress, locktorture, paravirt guests, and queued lock fairness under contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/qspinlock.h -->
