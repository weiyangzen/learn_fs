# sources/distributed-fs/ceph-client/arch/x86/xen/p2m.c

Purpose: Maintains Xen PV physical-to-machine mapping state. It builds the guest-visible linear p2m table, Xen toolstack MFN list tree, sparse missing/identity mappings, dynamic p2m allocation, foreign grant mappings, non-RAM remap support, and optional debugfs p2m dumps.

Important APIs/types/functions: Global exported state includes `xen_p2m_addr`, `xen_p2m_size`, and `xen_max_p2m_pfn`. Key functions include `xen_build_dynamic_phys_to_machine()`, `xen_vmalloc_p2m_tree()`, `xen_build_mfn_list_list()`, `xen_setup_mfn_list_list()`, `get_phys_to_machine()`, `xen_alloc_p2m_entry()`, `set_phys_range_identity()`, `set_phys_to_machine()`, `set_foreign_p2m_mapping()`, `clear_foreign_p2m_mapping()`, `xen_do_remap_nonram()`, `xen_add_remap_nonram()`, and debugfs `p2m_dump_show()`.

Control flow: Boot starts with the domain-builder MFN list in `start_info`, pads invalid entries, then vmallocs a larger sparse p2m area. `xen_rebuild_p2m_list()` maps full p2m pages, shared missing pages, shared identity pages, or shared PMD-level pages depending on contiguous element type. The parallel MFN tree is built for Xen/toolstack access unless `SIF_VIRT_P2M_4TOOLS` is set. Runtime updates allocate missing PMD/PTE/leaf levels under `p2m_update_lock`, bump shared-info `p2m_generation` around visible changes, and update max PFN hints.

State and persistence behavior: Persistent state is split between the linear p2m mapping, `p2m_top_mfn`, `p2m_top_mfn_p`, missing/identity leaf pages, `p2m_generation`, `xen_p2m_last_pfn`, and a small `xen_nonram_remap` table. Foreign grant mappings store `FOREIGN_FRAME` entries and must be cleared on unmap. Identity entries are marked with `IDENTITY_FRAME_BIT` to disambiguate true PFN==MFN mappings.

Dependencies and integration points: It integrates with Xen shared info, grant tables, balloon/unpopulated pages, ACPI ioremap overrides, memblock/vmalloc, page-table population helpers, debugfs root creation, and PV MMU PFN/MFN conversion.

Risks and test signals: Sparse p2m changes are visible to external tools, so generation barriers matter. Foreign mapping failure paths must unmap grants immediately. Non-RAM remap capacity is tiny and fatal on overflow. Test signals include PV boot with sparse/identity p2m, memory hotplug limit sizing, grant map/unmap stress, migration/suspend p2m rebuild, ACPI non-RAM ioremap remap boundaries, debugfs p2m ranges, and toolstack p2m scanning correctness.
