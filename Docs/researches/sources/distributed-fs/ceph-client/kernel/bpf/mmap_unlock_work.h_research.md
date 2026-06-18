# sources/distributed-fs/ceph-client/kernel/bpf/mmap_unlock_work.h

Purpose: provides a small helper abstraction for deferring `mmap_read_unlock()` from IRQ-disabled BPF lookup paths into `irq_work` when directly unlocking the mmap semaphore could deadlock. The source was read as a complete 65-line file.

Important APIs/types: `struct mmap_unlock_irq_work`, per-CPU declaration `mmap_unlock_work`, `bpf_mmap_unlock_get_irq_work`, and `bpf_mmap_unlock_mm`.

Control flow: callers ask `bpf_mmap_unlock_get_irq_work` whether the current context requires deferred unlock. In IRQ-disabled non-RT context it returns the current CPU work item unless that work is already busy; in PREEMPT_RT it forces fallback because trying the mmap semaphore in IRQ-disabled context is not allowed. `bpf_mmap_unlock_mm` either unlocks immediately or records the mm, releases lockdep ownership, and queues irq_work to perform the actual unlock later.

State and persistence: uses one per-CPU work object, so only one deferred mmap unlock per CPU can be outstanding. The `mm` pointer is transient until the queued work runs.

Dependencies/integration: depends on `irq_work`, `mm_struct`, `mmap_read_unlock`, lockdep `rwsem_release`, IRQ state helpers, and PREEMPT_RT configuration. It is included by BPF memory/VMA lookup code that can run with IRQs disabled.

Risks and edge cases: if per-CPU irq_work is already busy, callers must take a fallback path or risk losing an unlock. Lockdep state is manually adjusted before the real unlock, so misuse can hide or create lockdep anomalies. PREEMPT_RT behavior intentionally differs.

Test signals: BPF helpers that inspect user memory/VMA under IRQ-disabled contexts, PREEMPT_RT build/runtime coverage, lockdep runs, and stress that forces concurrent per-CPU deferred unlock attempts.
