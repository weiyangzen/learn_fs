<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ctlreg.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/ctlreg.h

Purpose: Provides typed helpers for reading, writing, setting, and clearing s390 control registers.

Important APIs/types/functions: `__ctl_load()`, `__ctl_store()`, `local_ctl_*`, `system_ctl_*`, and bit operation wrappers around control register fields. Source-visible declarations include: #define __ASM_S390_CTLREG_H; #define CR0_TRANSACTIONAL_EXECUTION_BIT (63 - 8); #define CR0_CLOCK_COMPARATOR_SIGN_BIT (63 - 10); #define CR0_CRYPTOGRAPHY_COUNTER_BIT (63 - 13); #define CR0_PAI_EXTENSION_BIT (63 - 14); #define CR0_CPUMF_EXTRACTION_AUTH_BIT (63 - 15); #define CR0_WARNING_TRACK_BIT (63 - 30); #define CR0_LOW_ADDRESS_PROTECTION_BIT (63 - 35); #define CR0_FETCH_PROTECTION_OVERRIDE_BIT (63 - 38); #define CR0_STORAGE_PROTECTION_OVERRIDE_BIT (63 - 39).

Control flow: Inline assembly stores or loads control registers, while system-wide helpers coordinate updates across CPUs where implemented.

State and persistence behavior: State is CPU control-register contents and any global synchronization around system updates.

Dependencies and integration points: Direct includes are #include <linux/bits.h>, #include <linux/bug.h>. Integrated with Integrates MMU/DAT, interrupt subclasses, lowcore, SMP, and feature control paths..

Risks: Control-register changes are privileged and CPU-local unless explicitly broadcast; incorrect masks can break address translation or interrupt delivery.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 256 lines, 8004 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ctlreg.h -->
