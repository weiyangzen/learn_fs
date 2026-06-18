<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/suspend_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/suspend_64.h

Purpose: defines 64-bit x86 saved CPU context for suspend and hibernation. Important fields include saved CR registers, MSRs such as EFER/FS/GS/KERNEL_GS, descriptor table pointers, segment selectors, and restore entry data.

Control flow: suspend saves long-mode CPU state, switches through low-level resume code, restores control registers/MSRs/descriptors, and resumes normal kernel execution. State is saved per-CPU processor context in memory.

Dependencies include long-mode paging, MSR helpers, percpu GS base, ACPI sleep, hibernate image restore, and CPU feature reinitialization. Risks include GS/FS base corruption, EFER/CR4 mismatch, broken KASLR/percpu assumptions, and resume failure under virtualization. Test signals include x86-64 S3, hibernation, FSGSBASE/CET/PCID configurations, and resume on multiple CPU vendors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/suspend_64.h -->
