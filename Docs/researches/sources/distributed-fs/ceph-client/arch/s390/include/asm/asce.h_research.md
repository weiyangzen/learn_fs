<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/asce.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/asce.h

Purpose: Defines address-space-control element flags and helpers for s390 dynamic address translation roots.

Important APIs/types/functions: `_ASCE_*` bit definitions and masks for region/table type, private-space, real-space, origin, and limit fields. Source-visible declarations include: #define _ASM_S390_ASCE_H; static inline bool enable_sacf_uaccess(void); unsigned long flags;; static inline void disable_sacf_uaccess(bool previous); unsigned long flags;.

Control flow: MM and low-level DAT code compose ASCE values and load them into control registers to select address translation roots.

State and persistence behavior: ASCE values persist in mm context, lowcore, and control-register state for active address spaces.

Dependencies and integration points: Direct includes are #include <linux/thread_info.h>, #include <linux/irqflags.h>, #include <asm/lowcore.h>, #include <asm/ctlreg.h>. Integrated with Integrates page table setup, KVM/SIE, lowcore, control-register management, and DAT bit definitions..

Risks: Bitfield mistakes are MMU-critical and can select the wrong table level, private-space mode, or address-space origin.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 36 lines, 754 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/asce.h -->
