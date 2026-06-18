# sources/distributed-fs/ceph-client/arch/x86/xen/enlighten_pvh.c

Purpose: Handles Xen PVH-specific boot setup, especially PVH Dom0 firmware/memory quirks, GSI setup, EFI probing, VGA console import, and e820 map acquisition.

Important APIs/types/functions: `xen_pvh` records PVH mode. Dom0 builds can export `xen_pvh_setup_gsi()`. `pvh_reserve_extra_memory()` turns selected UNUSABLE e820 ranges into reserved RAM for foreign mappings/ballooning. `pvh_arch_setup()` applies PVH arch policy. `xen_pvh_init()` marks PVH mode and installs arch setup/banner hooks. `mem_map_via_hcall()` gets the memory map from `XENMEM_memory_map`.

Control flow and state: PVH init sets `xen_domain_type` to HVM, records `pvh_start_info.flags`, installs PVH arch hooks, calls Xen EFI init, and for initial domains imports Xen's Dom0 console into `boot_params`. Arch setup reserves extra memory and, for Dom0, adds Xen consoles and disables native cpuidle/cpufreq because Xen owns those power states.

Dependencies and integration points: It uses Xen memory and platform hypercalls, ACPI GSI semantics, x86 boot params, hvc console, IO-APIC, EFI, cpuidle/cpufreq controls, and common Xen extra-memory handling.

Risks and test signals: PVH Dom0 maps host-like memory with unavailable holes; mishandling UNUSABLE conversion can collide with MMIO or foreign mappings. GSI setup errors affect device interrupts. Test signals include PVH Dom0 boot, ACPI interrupt setup, memory balloon headroom, disabled native power drivers, EFI table discovery, and correct e820 population from the hypervisor.
