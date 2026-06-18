# sources/distributed-fs/ceph-client/arch/sparc/lib/atomic32.c

Purpose: Implements atomic and cmpxchg/xchg helpers for SPARC32 using spinlock serialization.

Important APIs/functions: Exports `arch_atomic_add_return`, `arch_atomic_fetch_add/and/or/xor`, `arch_atomic_xchg`, `arch_atomic_cmpxchg`, `arch_atomic_fetch_add_unless`, `arch_atomic_set`, `sp32___set_bit`, `sp32___clear_bit`, `sp32___change_bit`, `__cmpxchg_u8/u16/u32/u64`, and `__xchg_u32`.

Control flow: Hashes target addresses to a small spinlock array when SMP or uses a dummy lock otherwise. Each operation locks, reads/modifies/writes the target, unlocks, and returns old or new values per API contract.

State and persistence: Maintains static spinlocks. Mutates atomic variables and bit words.

Dependencies/integration: Includes `linux/atomic.h`, `linux/spinlock.h`, and `linux/module.h`; built for `CONFIG_SPARC32`.

Risks/test signals: Lock hashing affects contention and correctness. Test atomic API litmus cases, cmpxchg sizes, SMP stress, interrupt context assumptions, and bit operation return values.
