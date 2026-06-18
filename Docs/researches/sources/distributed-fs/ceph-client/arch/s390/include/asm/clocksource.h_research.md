<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/clocksource.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/clocksource.h

Purpose: Provides the s390 architecture clocksource include point.

Important APIs/types/functions: Include guard only in this snapshot, relying on implementation elsewhere. Source-visible declarations include: #define _ASM_S390_CLOCKSOURCE_H.

Control flow: Generic clocksource code can include it for architecture-specific hooks without adding declarations here.

State and persistence behavior: No state.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates timekeeping and s390 clocksource implementation files..

Risks: Minimal wrapper; adding declarations must stay compatible with generic clocksource expectations.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 7 lines, 184 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/clocksource.h -->
