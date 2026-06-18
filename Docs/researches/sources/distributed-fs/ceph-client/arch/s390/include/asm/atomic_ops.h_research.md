<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/atomic_ops.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/atomic_ops.h

Purpose: Contains low-level s390 atomic instruction implementations.

Important APIs/types/functions: `__atomic_read/set`, 32/64-bit add/and/or/xor helpers, constant add helpers, and add-and-test variants. Source-visible declarations include: #define __ARCH_S390_ATOMIC_OPS__; static __always_inline int __atomic_read(const int *ptr); int val;; static __always_inline void __atomic_set(int *ptr, int val); static __always_inline long __atomic64_read(const long *ptr); long val;; static __always_inline void __atomic64_set(long *ptr, long val); #define __ATOMIC_OP(op_name, op_type, op_string, op_barrier) \; static __always_inline op_type op_name(op_type val, op_type *ptr) \; #define __ATOMIC_OPS(op_name, op_type, op_string) \.

Control flow: On z196-capable builds it uses load-and-op instructions; older builds use `cs`/`csg` retry loops. Optional flag-output paths derive zero/nonzero results directly from condition codes.

State and persistence behavior: No owned state; it mutates caller memory atomically.

Dependencies and integration points: Direct includes are #include <linux/limits.h>, #include <asm/march.h>, #include <asm/asm.h>. Integrated with Used by `atomic.h`, FPU state flags, refcount-like users, and low-level synchronization..

Risks: Instruction constraints, memory clobbers, and fallback loops must preserve atomicity across supported march levels.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 245 lines, 7302 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/atomic_ops.h -->
