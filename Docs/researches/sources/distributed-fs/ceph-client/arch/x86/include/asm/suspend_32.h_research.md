<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/suspend_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/suspend_32.h

Purpose: defines 32-bit x86 saved CPU context for suspend/hibernate. Important type is the architecture saved-context structure containing control registers, segment descriptors/selectors, GDT/IDT, LDT/TR, and general resume state.

Control flow: suspend code saves processor state before low-power transition or image creation and restores it during resume. State is memory-resident saved CPU context. Dependencies include 32-bit descriptor tables, paging, ACPI/hibernate assembly, and CPU feature restoration.

Risks include stale descriptor pointers, CR3/CR4 mismatches, and resume crashes on CPUs with changed state. Test signals include i386 suspend-to-RAM/hibernate, resume after CPU hotplug, and descriptor-table validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/suspend_32.h -->
