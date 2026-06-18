<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/cpuid.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/cpuid.h

Purpose: Documents and defines Xen CPUID leaves for x86 guests, including Xen signature discovery, Xen version reporting, hypercall page count/MSR base, time-source details, HVM feature bits, and PV machine-address width reporting.

Important APIs/types/functions: Macros `XEN_CPUID_FIRST_LEAF`, `XEN_CPUID_LEAF`, signature constants, `XEN_CPUID_FEAT1_MMU_PT_UPDATE_PRESERVE_AD`, TSC feature and mode constants, HVM feature flags such as `XEN_HVM_CPUID_IOMMU_MAPPINGS`, `XEN_HVM_CPUID_EXT_DEST_ID`, `XEN_HVM_CPUID_UPCALL_VECTOR`, `XEN_CPUID_MACHINE_ADDRESS_WIDTH_MASK`, and `XEN_CPUID_MAX_NUM_LEAVES`.

Control flow: This header owns no executable flow; Xen-aware detection code issues CPUID at the Xen leaf base and branches on the returned signature and feature bits.

State and persistence behavior: No kernel state is stored here. Values are ABI constants whose meaning persists across guest boot, migration, and userspace/tooling expectations.

Dependencies and integration points: Integrated with Xen guest discovery, clocksource/TSC setup, HVM interrupt routing, IOMMU mapping assumptions, and hypercall page setup. Consumers also pair it with `xen_cpuid_base()` in `hypervisor.h`.

Risks and test signals: ABI drift is the primary risk. Test by booting PV, HVM, and PVH guests on Xen hosts with and without Viridian leaves, checking Xen signature discovery, TSC mode handling, event upcall vector support, high APIC/MSI destination IDs, and migration-time TSC incarnation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/cpuid.h -->
