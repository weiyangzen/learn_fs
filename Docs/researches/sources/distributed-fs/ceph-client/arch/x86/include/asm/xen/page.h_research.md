<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/page.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/page.h

Purpose: Provides x86 Xen page, frame, and address-translation helpers. It converts between pseudo-physical, machine, guest, bus, virtual, PFN, MFN, and GFN address spaces and exposes p2m/m2p state used by Xen PV guests.

Important APIs/types/functions: `xmaddr_t`, `xpaddr_t`, `XEN_PHYSICAL_MASK`, `XEN_PTE_MFN_MASK`, `INVALID_P2M_ENTRY`, `FOREIGN_FRAME`, `IDENTITY_FRAME`, globals `machine_to_phys_mapping`, `machine_to_phys_nr`, `xen_p2m_addr`, `xen_p2m_size`, `xen_max_p2m_pfn`; helpers `xen_alloc_p2m_entry`, `get_phys_to_machine`, `set_phys_to_machine`, `set_phys_range_identity`, `set_foreign_p2m_mapping`, `clear_foreign_p2m_mapping`, `xen_safe_read_ulong`, `xen_safe_write_ulong`, `__pfn_to_mfn`, `pfn_to_mfn`, `mfn_to_pfn`, `phys_to_machine`, `machine_to_phys`, `pfn_to_gfn`, `gfn_to_pfn`, `bfn_to_local_pfn`, `virt_to_machine`, `mfn_pte`, and `xen_arch_need_swiotlb`.

Control flow: Translation helpers first short-circuit non-PV domains to identity mappings. PV paths consult the p2m array, fall back to extended lookup for sparse/out-of-range entries, mask indicator bits for public conversions, and verify m2p round trips before returning local PFNs. Safe read/write helpers use exception-table fixups for potentially faulting m2p accesses.

State and persistence behavior: Persistent state is the p2m table, m2p mapping window, max p2m bounds, and special indicator bits for invalid, foreign, and identity frames. Foreign mappings must be marked with `FOREIGN_FRAME()` so generic PFN validation does not mistake them for local pages.

Dependencies and integration points: Depends on Linux MM, PFN, device, exception table, page-table, Xen grant-table, and Xen domain helpers. Integrates with PV MMU, grant mapping, SWIOTLB/DMA decisions, page-table construction, and memory hotplug/sparse p2m handling.

Risks and test signals: Risks include mfn/pfn confusion, foreign-page aliasing, faulting m2p reads, SME physical mask mistakes, and wrong behavior outside PV. Test Xen PV boot, grant map/unmap, ballooning, sparse memory hotplug, p2m identity ranges, DMA on PV/HVM, page-table creation, and fault injection on m2p windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/page.h -->
