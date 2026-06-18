<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/arch-stackprotector.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/arch-stackprotector.h

Purpose: Declares s390 stack protector guard patching for early and regular kernel code.

Important APIs/types/functions: `__stack_chk_guard`, `stack_protector_debug`, `__stack_protector_apply_early()`, `__stack_protector_apply()`, and inline wrappers. Source-visible declarations include: #define _ASM_S390_ARCH_STACKPROTECTOR_H; extern unsigned long __stack_chk_guard;; extern int stack_protector_debug;; void __stack_protector_apply_early(unsigned long kernel_start);; int __stack_protector_apply(unsigned long *start, unsigned long *end, unsigned long kernel_start);; static inline void stack_protector_apply_early(unsigned long kernel_start); static inline int stack_protector_apply(unsigned long *start, unsigned long *end).

Control flow: Early setup applies the guard using the kernel start address; the later helper patches a supplied memory range with the runtime kernel base.

State and persistence behavior: The global canary and patched instruction/data references persist for the booted kernel.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates compiler stack protector output, early boot relocation, alternatives/text patching, and per-build security configuration..

Risks: Incorrect kernel-start offsets or range bounds can leave stale canaries or corrupt text/data during early boot.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 25 lines, 759 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/arch-stackprotector.h -->
