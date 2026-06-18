<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/suspend.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/suspend.h

Purpose: selects x86 suspend state definitions for 32-bit or 64-bit builds. It includes `suspend_32.h` or `suspend_64.h` and exposes common suspend/resume interfaces.

Control flow: hibernation and ACPI suspend save CPU state using architecture-specific structures, then restore it on resume. State is saved processor/register context. Dependencies include ACPI sleep, hibernation, CPU state save/restore assembly, and page-table state.

Risks include incomplete register restoration, wrong CR/segment state, and resume failures after CPU feature changes. Test signals include suspend-to-RAM, hibernation, CPU hotplug plus suspend, and 32/64-bit resume paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/suspend.h -->
