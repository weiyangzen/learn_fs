<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu-types.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu-types.h

Purpose: Defines s390 FPU and kernel-FPU save-area structures.

Important APIs/types/functions: `struct fpu`, `struct kernel_fpu_hdr`, `struct kernel_fpu`, `KERNEL_FPU_STRUCT()`, and stack declaration macros for 8/16/32 vector registers. Source-visible declarations include: #define _ASM_S390_FPU_TYPES_H; struct fpu {; struct kernel_fpu_hdr {; struct kernel_fpu {; struct kernel_fpu_hdr hdr;; #define KERNEL_FPU_STRUCT(vxr_size) \; struct kernel_fpu_##vxr_size { \; struct kernel_fpu_hdr hdr; \; #define DECLARE_KERNEL_FPU_ONSTACK(vxr_size, name) \; struct kernel_fpu_##vxr_size name __uninitialized.

Control flow: Kernel code declares save areas sized for the vector ranges it will use; `fpu.h` checks those sizes before saving/restoring.

State and persistence behavior: Persistent state is task user-FPU and kernel-FPU save areas embedded in thread structures or caller stacks.

Dependencies and integration points: Direct includes are #include <asm/sigcontext.h>. Integrated with Integrates thread state, signal/ptrace FPU formats, in-kernel vector users, and compile-time size checking..

Risks: Save-area sizing must match flag ranges; too-small stack structures would corrupt memory during FPU nesting.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 51 lines, 1085 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu-types.h -->
