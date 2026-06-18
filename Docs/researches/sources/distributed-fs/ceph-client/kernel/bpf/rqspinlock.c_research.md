# sources/distributed-fs/ceph-client/kernel/bpf/rqspinlock.c

## Purpose
`rqspinlock.c` implements resilient queued spinlocks for BPF-facing lock kfuncs. It adapts the kernel queued spinlock/MCS slow path with bounded waits, timeout reporting, and AA/ABBA deadlock detection so BPF programs using `struct bpf_res_spin_lock` can fail lock acquisition instead of spinning forever. It also exposes BTF kfuncs for normal and IRQ-save lock/unlock pairs and emits diagnostic stream output when a lock violation is detected.

## Important APIs, Types, and Functions
The file defines `struct rqspinlock_timeout` for timeout bookkeeping and exports the per-CPU `rqspinlock_held_locks` array of `struct rqspinlock_held`. `is_lock_released()` tests masked lock-word state with acquire ordering. `check_deadlock_AA()` detects attempts to reacquire a lock already held by the current CPU, while `check_deadlock_ABBA()` scans other CPUs' held-lock tables to catch common lock-order inversions. `check_timeout()` combines the timeout deadline with periodic deadlock checks.

`resilient_tas_spin_lock()` is the fallback test-and-set implementation for architectures without queued spinlocks. Under `CONFIG_QUEUED_SPINLOCKS`, `resilient_queued_spin_lock_slowpath()` is the main slow path: it handles pending-bit acquisition, MCS queueing, timeout unwind, queue destruction, and handoff to the next waiter. The BPF kfuncs are `bpf_res_spin_lock()`, `bpf_res_spin_unlock()`, `bpf_res_spin_lock_irqsave()`, and `bpf_res_spin_unlock_irqrestore()`. `rqspinlock_register_kfuncs()` registers them for `BPF_PROG_TYPE_UNSPEC` at `late_initcall`.

## Control Flow
Fast-path acquisition happens outside this file through `res_spin_lock()`. Once slow path is entered, the caller has already reserved a held-lock tracking entry. The fallback TAS path repeatedly reads `lock->val`, attempts `atomic_try_cmpxchg()`, and calls `RES_CHECK_TIMEOUT()` while spinning; on failure it releases the held-lock entry before returning `-EDEADLK` or `-ETIMEDOUT`.

The queued path first handles a transient `_Q_PENDING_VAL`, tries to become the pending waiter, and waits for the locked bit to clear using `res_smp_cond_load_acquire()`. If pending acquisition times out, it clears the pending bit and releases the tracking entry. If contention remains, it enters the MCS queue: allocates a per-CPU qnode, encodes the tail, publishes it with `xchg_tail()`, links to any previous node, waits for predecessor handoff, then waits for locked/pending bits to clear. Deadlock findings avoid destructive queue teardown where possible; timeout findings try to clear the tail or signal the next node with `RES_TIMEOUT_VAL` so queued waiters can unwind. Successful queue-head acquisition either atomically clears the tail and sets locked or sets the lock bit and wakes the next waiter.

The kfunc wrappers disable preemption, optionally save/disable local IRQs, call `res_spin_lock()`, and restore preemption/IRQs on failure. Unlock kfuncs call `res_spin_unlock()` and restore the corresponding execution state.

## State and Persistence Behavior
All state is kernel runtime state. The lock word lives in the caller-provided `rqspinlock_t`/`bpf_res_spin_lock`. Per-CPU held-lock state records the locks held or being acquired and is used for diagnostics and deadlock detection. Per-CPU `rqnodes` store nested MCS queue nodes, bounded by `_Q_MAX_NODES`. Timeout state is stack-local per acquisition attempt. No state is persisted across program unload, reboot, or map serialization.

## Dependencies and Integration Points
The implementation depends on qspinlock internals (`../locking/qspinlock.h`, `mcs_spinlock.h`, `lock_events.h`), architecture support from `asm/rqspinlock.h`, BPF kfunc/BTF registration, trace lock contention events, preemption/IRQ primitives, and BPF stream diagnostics from `bpf_stream_stage`. It integrates with verifier-side lock reference tracking through the BPF resilient spin-lock kfunc ABI and with BPF program lookup/file-line reporting through `bpf_prog_find_from_stack()` and stream stack dumps.

## Risks and Test Signals
The highest risks are queue unwind races on timeout, stale or incomplete per-CPU held-lock tables causing false positive or missed deadlock reports, mismatched preemption/IRQ restore paths, architecture-specific qspinlock assumptions, and fairness loss when qnode allocation falls back to trylock. Test signals include BPF selftests for successful lock/unlock, AA deadlock, ABBA deadlock, timeout under a stuck holder, nested NMI/IRQ contexts, IRQ-save flag restore, stream diagnostics, lockdep/trace contention events, and builds with and without `CONFIG_QUEUED_SPINLOCKS`.
