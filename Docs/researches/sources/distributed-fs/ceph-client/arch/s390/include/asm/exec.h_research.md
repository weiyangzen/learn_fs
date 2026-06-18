<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/exec.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/exec.h

Purpose: Declares s390 exec stack alignment policy.

Important APIs/types/functions: `arch_align_stack(unsigned long sp)`. Source-visible declarations include: #define __ASM_EXEC_H; extern unsigned long arch_align_stack(unsigned long sp);.

Control flow: Exec and stack setup call the arch helper to perturb or align the initial user stack pointer.

State and persistence behavior: State is the computed user stack pointer in a new process image.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates binfmt loaders, ASLR, and process setup..

Risks: Stack alignment is user ABI and affects libc/startup assumptions.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 13 lines, 269 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/exec.h -->
