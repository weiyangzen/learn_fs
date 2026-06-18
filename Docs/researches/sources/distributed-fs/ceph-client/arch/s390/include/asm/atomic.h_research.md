<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/atomic.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/atomic.h

Purpose: Implements the s390 `atomic_t` and `atomic64_t` architecture API.

Important APIs/types/functions: `arch_atomic_*`, `arch_atomic64_*`, fetch/add/sub/test/bitwise operations, exchange, compare-exchange, and try-cmpxchg wrappers. Source-visible declarations include: #define __ARCH_S390_ATOMIC__; static __always_inline int arch_atomic_read(const atomic_t *v); #define arch_atomic_read arch_atomic_read; static __always_inline void arch_atomic_set(atomic_t *v, int i); #define arch_atomic_set arch_atomic_set; static __always_inline int arch_atomic_add_return(int i, atomic_t *v); #define arch_atomic_add_return arch_atomic_add_return; static __always_inline int arch_atomic_fetch_add(int i, atomic_t *v); #define arch_atomic_fetch_add arch_atomic_fetch_add; static __always_inline void arch_atomic_add(int i, atomic_t *v).

Control flow: Public atomic helpers delegate to `atomic_ops.h` load-and-op instructions or compare-and-swap loops and add barriers on return/fetch/test variants.

State and persistence behavior: State is caller-owned atomic counters; this header defines their concurrency semantics.

Dependencies and integration points: Direct includes are #include <linux/compiler.h>, #include <linux/types.h>, #include <asm/atomic_ops.h>, #include <asm/barrier.h>, #include <asm/cmpxchg.h>. Integrated with Integrates generic atomic API, locking, refcounts, scheduler, memory model barriers, and cmpxchg primitives..

Risks: Barrier choice and old/new return semantics are concurrency ABI; mismatches cause rare SMP bugs.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 230 lines, 6770 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/atomic.h -->
