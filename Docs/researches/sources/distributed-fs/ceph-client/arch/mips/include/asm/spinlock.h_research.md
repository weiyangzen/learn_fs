<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/spinlock.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/spinlock.h

Purpose: Provides the MIPS queued spinlock hook and includes generic queued spinlock/read-write lock implementations.

Important APIs/types/functions: `queued_spin_unlock(struct qspinlock *lock)` when configured, the `queued_spin_unlock` macro override, and includes `asm/qspinlock.h` and `asm/qrwlock.h`.

Control flow: Unlock uses `smp_store_release` to store zero into the lock value, providing release ordering before generic queued lock code handles later acquisitions.

State and persistence: State is the `qspinlock` word embedded in caller-owned locks. The header does not allocate lock state.

Dependencies and integration points: Depends on MIPS processor barriers and generic qspinlock/qspinlock types. Integrated by all kernel spinlock users on MIPS.

Risks: Memory ordering is subtle; weakening `smp_store_release` breaks lock release semantics. Struct layout must match generic qspinlock types.

Test signals: Locking selftests, SMP stress, lockdep, qspinlock build coverage, and MIPS SMP boot under contention are relevant.

Source read size: 31 lines, 822 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/spinlock.h -->
