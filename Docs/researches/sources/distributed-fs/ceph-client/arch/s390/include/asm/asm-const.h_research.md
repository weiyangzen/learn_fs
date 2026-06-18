<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/asm-const.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/asm-const.h

Purpose: Provides assembly-friendly constant emission wrappers for s390 headers.

Important APIs/types/functions: `__ASM_CONST`, `_AC`, and related include support inherited from generic constant headers. Source-visible declarations include: #define _ASM_S390_ASM_CONST_H.

Control flow: Assembly and C preprocessing use these macros to form correctly typed constants in mixed C/asm headers.

State and persistence behavior: No runtime state.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates with low-level assembly headers and generated offsets..

Risks: Changing constant typing can break assembly parsing or sign/width assumptions.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 12 lines, 377 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/asm-const.h -->
