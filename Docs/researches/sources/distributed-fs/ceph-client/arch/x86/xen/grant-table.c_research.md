# sources/distributed-fs/ceph-client/arch/x86/xen/grant-table.c

Purpose: Implements x86-specific grant table mapping support, allocating virtual areas for PV grant shared/status frames and setting/removing PTEs that map Xen-provided grant MFNs.

Important APIs/types/functions: `arch_gnttab_map_shared()` and `arch_gnttab_map_status()` map grant frame MFNs into preallocated vmalloc areas. `arch_gnttab_unmap()` clears those PTEs. `arch_gnttab_init()` allocates shared/status virtual areas for PV guests. `xen_pvh_gnttab_setup()` preallocates translated grant frames for PVH.

Control flow and state: Static `gnttab_shared_vm_area` and `gnttab_status_vm_area` hold vmalloc areas, captured PTE pointers, and an index filled by `apply_to_page_range()`. PV guests allocate both shared and status spaces; status is allocated even before V2 is active to survive migration to V2-capable hosts. PVH setup initializes auto-translated grant frame storage before generic grant-table init.

Dependencies and integration points: It depends on Xen grant-table core, vmalloc/page-table helpers, Xen page macros, PV/PVH predicates, ballooned page translation helpers, and event setup headers.

Risks and test signals: PTE arrays must match virtual area size and lifetime; status-frame preallocation affects migration compatibility. Test signals include grant table v1/v2 operation, migration between hosts, map/unmap leak checks, PVH grant mappings, and frontend/backend I/O through granted pages.
