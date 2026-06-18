<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu-insn.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu-insn.h

Purpose: Provides C-callable wrappers around individual s390 floating-point and vector instructions.

Important APIs/types/functions: `fpu_ld/std`, FPC load/store helpers, safe `fpu_lfpc_safe()`, vector load/store/multiple/permute/GF/logic/arithmetic helpers, and KASAN/KMSAN instrumentation hooks. Source-visible declarations include: #define __ASM_S390_FPU_INSN_H; static __always_inline void fpu_cefbr(u8 f1, s32 val); static __always_inline unsigned long fpu_cgebr(u8 f2, u8 mode); unsigned long val;; static __always_inline void fpu_debr(u8 f1, u8 f2); static __always_inline void fpu_ld(unsigned short fpr, freg_t *reg); static __always_inline void fpu_ldgr(u8 f1, u32 val); static __always_inline void fpu_lfpc(unsigned int *fpc); static inline void fpu_lfpc_safe(unsigned int *fpc); static __always_inline void fpu_std(unsigned short fpr, freg_t *reg).

Control flow: Each inline emits exactly the targeted FP/vector instruction with memory barriers; memory operands call instrumentation helpers, and fault-prone FPC loading uses exception-table recovery.

State and persistence behavior: State is FP/vector registers, FPC, and caller-provided save/load buffers.

Dependencies and integration points: Direct includes are #include <asm/fpu-insn-asm.h>, #include <linux/instrumented.h>, #include <linux/kmsan.h>, #include <asm/asm-extable.h>. Integrated with Integrates kernel FPU sections, crypto vector code, checksum/vector helpers, KASAN/KMSAN, and `fpu-insn-asm.h` macro encodings..

Risks: Callers must be inside `kernel_fpu_begin/end`; otherwise user FP/vector state can be corrupted. Partial vector length helpers must unpoison exactly written bytes.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 482 lines, 11681 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu-insn.h -->
