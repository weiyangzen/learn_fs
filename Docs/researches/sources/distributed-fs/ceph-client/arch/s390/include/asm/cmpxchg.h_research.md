<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cmpxchg.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cmpxchg.h

Purpose: Implements s390 compare-exchange, exchange, try-cmpxchg, and 128-bit cmpxchg primitives.

Important APIs/types/functions: `arch_cmpxchg()`, `arch_try_cmpxchg()`, `arch_xchg()`, byte/halfword emulation using containing-word CAS, and `arch_cmpxchg128()`/`arch_try_cmpxchg128()`. Source-visible declarations include: #define __ASM_CMPXCHG_H; void __cmpxchg_called_with_bad_pointer(void);; static __always_inline u32 __cs_asm(u64 ptr, u32 old, u32 new); static __always_inline u64 __csg_asm(u64 ptr, u64 old, u64 new); static inline u8 __arch_cmpxchg1(u64 ptr, u8 old, u8 new); union {; int i;; static inline u16 __arch_cmpxchg2(u64 ptr, u16 old, u16 new); union {; int i;.

Control flow: 1/2-byte operations align to containing words and retry with shifted masks; 4/8-byte operations use `cs`/`csg`; 16-byte operations use `cdsg` on aligned `u128` data.

State and persistence behavior: State is caller-owned memory modified atomically.

Dependencies and integration points: Direct includes are #include <linux/mmdebug.h>, #include <linux/types.h>, #include <linux/bug.h>, #include <asm/asm.h>. Integrated with Integrates atomics, locking, qspinlocks, refcounts, lockless data structures, and generic cmpxchg API..

Risks: Alignment, endian shifts, and retry updates to `oldp` are subtle; wrong handling breaks lockless algorithms.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 273 lines, 6171 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cmpxchg.h -->
