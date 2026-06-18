# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/qspinlock.h

Purpose: This header implements the PowerPC front end for queued spinlocks, including fast-path trylock/unlock assembly, owner encoding, contention checks, and architecture spinlock macro bindings.

Important APIs/types/functions: Tunables include `_Q_SPIN_EH_HINT`, `_Q_SPIN_TRY_LOCK_STEAL`, `_Q_SPIN_SPEC_BARRIER`, `_Q_SPIN_MISO`, `_Q_SPIN_MISO_UNLOCK`, and `_Q_SPIN_PREFETCH_NEXT`. Helpers include `queued_spin_is_locked`, `queued_spin_value_unlocked`, `queued_spin_is_contended`, `queued_spin_encode_locked_val`, `__queued_spin_trylock_nosteal`, `__queued_spin_trylock_steal`, `queued_spin_trylock`, `queued_spin_lock`, `queued_spin_unlock`, and external `queued_spin_lock_slowpath`. It maps `arch_spin_*` operations to queued spinlock helpers and declares/stubs `pv_spinlocks_init`.

Control flow: Lock acquisition first attempts the inline trylock. The no-steal path succeeds only if the whole word is zero; the steal path may acquire when the locked bits are clear even if a tail exists, preserving the tail bits. Both use `lwarx/stwcx.` with acquire barriers. Failure falls into `queued_spin_lock_slowpath`. Unlock performs a release store to the `locked` byte and optionally emits `miso`.

State and persistence: `struct qspinlock` contains a 32-bit value with locked, owner CPU, and tail fields as defined by `qspinlock_types.h`. The owner CPU is encoded from `smp_processor_id`. Contention is inferred from `_Q_TAIL_CPU_MASK`.

Dependencies and integration points: It depends on compiler helpers, PowerPC qspinlock layout, paravirt spinlocks, PowerPC acquire barrier macros, and SMP CPU IDs. It integrates with generic locking, paravirtual spinlock initialization, slowpath queueing code, and architecture lock API macros.

Risks and test signals: Inline assembly must preserve reservation semantics and memory ordering. Trylock stealing changes fairness and can interact with slowpath queue assumptions. Owner CPU encoding depends on mask widths. Tests include locktorture/lockstorm, queued-spinlock selftests, paravirt spinlock builds, 32/64-bit SMP builds, contention/fairness measurements, and memory-order litmus tests around unlock release.
