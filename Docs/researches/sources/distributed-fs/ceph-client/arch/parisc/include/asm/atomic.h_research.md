# sources/distributed-fs/ceph-client/arch/parisc/include/asm/atomic.h

Purpose: implements PA-RISC atomic integer operations. Because PA-RISC lacks broad in-memory atomic RMW primitives, operations are serialized through hashed spinlocks around aligned values.

Important APIs/types/functions: declares `__atomic_hash[ATOMIC_HASH_SIZE]`, lock/unlock helpers, `arch_atomic_read`, `arch_atomic_set`, add/sub/and/or/xor operations, return/fetch variants, and 64-bit `atomic64_t` equivalents.

Control flow: each modifying operation chooses a hash lock from the target address, disables/restores IRQ state, updates the underlying counter, and releases the lock. Reads and sets use barriers where required.

State and persistence: atomic values persist in caller-owned memory; the global hash-lock table is shared serialization state. Dependencies and integration: depends on `cmpxchg.h`, `barrier.h`, `spinlock.h`, and cache-line alignment.

Risks and test signals: incorrect locking or alignment can lose updates under IRQ/SMP concurrency. Test with atomic selftests, lockdep, SMP stress, and 32-bit/64-bit builds.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
