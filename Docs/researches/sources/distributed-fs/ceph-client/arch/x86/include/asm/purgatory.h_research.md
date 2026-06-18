<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/purgatory.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/purgatory.h

Purpose: declares the x86 kexec purgatory entry point. Important API is `purgatory()` plus the generic purgatory include.

Control flow: kexec/crash-kexec code transfers through purgatory to verify and prepare the next kernel before final jump. This header has no executable logic; it only gives C users the assembly symbol. State is maintained by generic kexec/purgatory code. Risks are symbol/prototype mismatches or assembly-only include misuse. Test signals include normal `kexec -e`, crash kernel boot, and purgatory checksum validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/purgatory.h -->
