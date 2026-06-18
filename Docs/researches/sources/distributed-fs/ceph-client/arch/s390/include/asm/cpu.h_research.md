<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpu.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cpu.h

Purpose: Declares s390 CPU identification data and static CPU feature keys.

Important APIs/types/functions: `struct cpuid` and `DECLARE_STATIC_KEY_FALSE(cpu_has_bear)`. Source-visible declarations include: #define _ASM_S390_CPU_H; struct cpuid; unsigned int version : 8;; unsigned int ident : 24;; unsigned int machine : 16;; unsigned int unused : 16;.

Control flow: CPU detection fills CPUID/facility data and static keys allow hot paths to branch on CPU features.

State and persistence behavior: Persistent state is CPU identity and static-key patching state.

Dependencies and integration points: Direct includes are #include <linux/types.h>, #include <linux/jump_label.h>. Integrated with Integrates CPU setup, facility detection, alternatives/static branches, and feature users such as BEAR support..

Risks: Static-key default and feature discovery must align or hot paths execute unsupported instructions.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 28 lines, 622 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpu.h -->
