# sources/distributed-fs/ceph-client/arch/x86/xen/Kconfig

Purpose: Defines x86 Xen guest configuration options and feature dependencies for PV, PVHVM, PVH, Dom0, debugfs, and PV MSR behavior.

Important entries: `XEN` enables base Xen guest support and selects paravirt clock, callback vector, and hibernate callbacks. `XEN_PV` adds 64-bit PV support with XXL paravirt ops, PV MMU, VPMU, and guest perf. `XEN_512GB` limits PV domain memory by default. `XEN_PVHVM`, `XEN_PVHVM_GUEST`, and `XEN_PVH` cover HVM/PVH modes. `XEN_DOM0` selects Dom0 support with ACPI/PCI/IOAPIC constraints. `XEN_DEBUG_FS` enables debug/tuning files. `XEN_PV_MSR_SAFE` defaults PV MSR access to safe variants.

Control flow and state: Kconfig choices determine which objects are built and which paravirt, MMU, interrupt, grant-table, and boot paths are available. There is no runtime state in this file, but options such as `XEN_PV_MSR_SAFE` and `XEN_512GB` feed boot-time defaults in the source files.

Dependencies and integration points: The file depends on x86 paravirt, APIC, TSC, ACPI, PCI, SWIOTLB_XEN, and architecture mode constraints. It directly drives `arch/x86/xen/Makefile` object inclusion.

Risks and test signals: Misstated dependencies can build unusable guest modes or omit required runtime pieces. Build matrix signals include PV-only, HVM/PVHVM, PVH Dom0, debugfs, SMP/non-SMP, and safe-MSR combinations.
