<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/access-regs.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/access-regs.h

Purpose: Provides helpers for saving and restoring s390 access registers.

Important APIs/types/functions: `struct access_regs`, `save_access_regs()`, and `restore_access_regs()` using `stam` and `lam` instructions. Source-visible declarations include: #define __ASM_S390_ACCESS_REGS_H; struct access_regs {; unsigned int regs[NUM_ACRS];; static inline void save_access_regs(unsigned int *acrs); struct access_regs *regs = (struct access_regs *)acrs;; static inline void restore_access_regs(unsigned int *acrs); struct access_regs *regs = (struct access_regs *)acrs;.

Control flow: Inline assembly stores or loads access registers 0 through 15 to caller-provided memory.

State and persistence behavior: No header-owned state; it serializes register state into caller storage.

Dependencies and integration points: Direct includes are #include <linux/instrumented.h>, #include <asm/sigcontext.h>. Integrated with Used by low-level context switch, signal, ptrace, and address-space-control code that needs access-register preservation..

Risks: The memory layout must match hardware register order; wrong buffers or missing clobbers corrupt task address-space state.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 38 lines, 806 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/access-regs.h -->
