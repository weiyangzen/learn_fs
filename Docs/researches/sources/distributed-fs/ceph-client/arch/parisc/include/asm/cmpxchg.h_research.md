# sources/distributed-fs/ceph-client/arch/parisc/include/asm/cmpxchg.h

Purpose: defines PA-RISC exchange and compare-exchange primitives for typed memory sizes and local fallbacks.

Important APIs/types/functions: declares `__xchg8`, `__xchg32`, optional `__xchg64`, `__cmpxchg_u8/u16/u32/u64`, `arch_xchg`, `arch_cmpxchg`, `arch_cmpxchg_local`, and `arch_cmpxchg64`.

Control flow: callers dispatch by operand size; unsupported sizes call bad-pointer sentinel functions so misuse fails at link or runtime. Local variants use generic helpers when full atomicity is not required.

State and persistence: mutates caller-owned shared memory; serialization details live in out-of-line assembly/C implementations. Dependencies and integration: fundamental to atomics, locking, refcounts, and lock-free kernel helpers.

Risks and test signals: size dispatch or sign extension mistakes break synchronization. Test with cmpxchg selftests, 64-bit-only coverage, and lock/refcount stress under SMP.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
