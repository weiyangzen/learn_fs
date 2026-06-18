<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/archrandom.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/archrandom.h

Purpose: Declares s390 architecture random-number support using CPACF PRNO/TRNG capabilities.

Important APIs/types/functions: `s390_arch_random_available()`, `s390_arch_get_random_*()`, and `s390_arch_get_seed_*()` style hooks for random core integration. Source-visible declarations include: #define _ASM_S390_ARCHRANDOM_H; extern atomic64_t s390_arch_random_counter;; static inline size_t __must_check arch_get_random_longs(unsigned long *v, size_t max_longs); static inline size_t __must_check arch_get_random_seed_longs(unsigned long *v, size_t max_longs).

Control flow: The random core probes availability and uses CPACF-backed helpers to fill caller-provided words or seed buffers.

State and persistence behavior: State is CPACF hardware RNG/DRNG state and any implementation-side reseed state, not this header.

Dependencies and integration points: Direct includes are #include <linux/static_key.h>, #include <linux/preempt.h>, #include <linux/atomic.h>, #include <asm/cpacf.h>. Integrated with Integrates with `random.h`, CPACF PRNO/TRNG, CPU facility detection, and kernel entropy seeding..

Risks: Availability and blocking semantics must be conservative; exposing weak or unavailable hardware randomness would affect system entropy.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 38 lines, 947 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/archrandom.h -->
