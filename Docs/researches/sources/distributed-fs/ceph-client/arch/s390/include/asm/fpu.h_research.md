<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu.h

Purpose: Implements the high-level s390 in-kernel FPU/vector state management API.

Important APIs/types/functions: `KERNEL_FPC`, `KERNEL_VXR_*`, `KERNEL_FPR`, save/load helpers, `load_user_fpu_regs()`, `save_user_fpu_regs()`, `kernel_fpu_begin/end()`, and FP/VX conversion helpers. Source-visible declarations include: #define _ASM_S390_FPU_H; enum {; #define KERNEL_FPC BIT(KERNEL_FPC_BIT); #define KERNEL_VXR_V0V7 BIT(KERNEL_VXR_V0V7_BIT); #define KERNEL_VXR_V8V15 BIT(KERNEL_VXR_V8V15_BIT); #define KERNEL_VXR_V16V23 BIT(KERNEL_VXR_V16V23_BIT); #define KERNEL_VXR_V24V31 BIT(KERNEL_VXR_V24V31_BIT); #define KERNEL_VXR_LOW (KERNEL_VXR_V0V7 | KERNEL_VXR_V8V15); #define KERNEL_VXR_MID (KERNEL_VXR_V8V15 | KERNEL_VXR_V16V23); #define KERNEL_VXR_HIGH (KERNEL_VXR_V16V23 | KERNEL_VXR_V24V31).

Control flow: The API marks kernel-owned register ranges in thread flags, saves user state for ranges about to be used, optionally saves nested kernel ranges, and restores previous ownership on end.

State and persistence behavior: Persistent state lives in `thread_struct` user/kernel FPU save areas plus `ufpu_flags` and `kfpu_flags`; stack save areas hold nested kernel state.

Dependencies and integration points: Direct includes are #include <linux/cpufeature.h>, #include <linux/processor.h>, #include <linux/preempt.h>, #include <linux/string.h>, #include <linux/sched.h>, #include <asm/sigcontext.h>, #include <asm/fpu-types.h>, #include <asm/fpu-insn.h>. Integrated with Integrates scheduler context switch, signal/ptrace FP register ABI, vector crypto/checksum users, preemption assumptions, and low-level instruction wrappers..

Risks: Kernel FPU sections must use matching flags and save-area sizes. Nested or interrupt-context use depends on disjoint vector ranges to avoid unnecessary or missing saves.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 290 lines, 8301 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu.h -->
