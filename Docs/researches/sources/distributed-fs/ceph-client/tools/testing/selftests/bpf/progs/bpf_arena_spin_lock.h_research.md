<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_arena_spin_lock.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_arena_spin_lock.h

## Purpose

Header-only BPF arena spinlock implementation that tests low-level atomic locking, IRQ/preemption helpers, and verifier range constraints.

## Important APIs, Types, and Functions

- Important functions/callbacks: `encode_tail`, `xchg_tail`, `clear_pending`, `clear_pending_set_locked`, `set_locked`, `arena_fetch_set_pending_acquire`, `arena_spin_trylock`, `arena_spin_lock_slowpath`, `arena_spin_lock`, `arena_spin_unlock`
- BPF helpers/kfunc-like calls: `bpf_assert_range`, `bpf_get_smp_processor_id`, `bpf_local_irq_restore`, `bpf_local_irq_save`, `bpf_preempt_disable`, `bpf_preempt_enable`, `bpf_printk`

## Control Flow and Data Flow

Lock acquisition first tries an atomic fast path, then sets pending state, exchanges queue tail, disables preemption/IRQs where required, waits through a queued slow path, and releases by clearing lock/pending state or handing off to the next waiter.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf_atomic.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_assert_range`, `bpf_get_smp_processor_id`, `bpf_local_irq_restore`, `bpf_local_irq_save`, `bpf_preempt_disable`, `bpf_preempt_enable`, `bpf_printk`.

## Test Signals

Load/attach success and verifier log expectations are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_arena_spin_lock.h -->
