<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/extmem.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/extmem.h

Purpose: Declares z/VM DCSS/extmem segment management APIs.

Important APIs/types/functions: Segment type/sharing constants, `segment_load()`, `segment_unload()`, `segment_save()`, `segment_type()`, `segment_modify_shared()`, and `segment_warning()`. Source-visible declarations include: #define _ASM_S390X_DCSS_H; #define MAX_DCSS_ADDR (512UL * SZ_1G); #define SEG_TYPE_SW 0; #define SEG_TYPE_EW 1; #define SEG_TYPE_SR 2; #define SEG_TYPE_ER 3; #define SEG_TYPE_SN 4; #define SEG_TYPE_EN 5; #define SEG_TYPE_SC 6; #define SEG_TYPE_EWEN 7.

Control flow: Callers load named DCSS segments with requested sharing/type, receive address/length, and later save, unload, or change sharing.

State and persistence behavior: Persistent state is hypervisor segment mapping and kernel mappings of loaded segments.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates z/VM DCSS, xip/extmem drivers, module-like shared segment users, and VM-specific diagnostics..

Risks: Segment names/types are hypervisor ABI; incorrect sharing changes can affect other guests or mappings.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 39 lines, 1066 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/extmem.h -->
