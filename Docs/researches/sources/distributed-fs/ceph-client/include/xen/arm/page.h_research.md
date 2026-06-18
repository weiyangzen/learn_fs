<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/page.h -->
# sources/distributed-fs/ceph-client/include/xen/arm/page.h

## Purpose
This header defines ARM Xen address translation helpers for pseudo-physical, guest, bus, and machine addresses, plus foreign grant mapping hooks and SWIOTLB decision support.

## Important APIs, Types, And Functions
- `xmaddr_t` and `xpaddr_t` wrap Xen machine and pseudo-physical addresses; `XMADDR()` and `XPADDR()` build them.
- `phys_to_machine_mapping_valid()` is always true and `INVALID_P2M_ENTRY` marks missing mappings.
- `pfn_to_gfn()` and `gfn_to_pfn()` are identity mappings on ARM.
- `pfn_to_bfn()` consults `phys_to_mach`/`__pfn_to_mfn()` when a non-empty mapping exists, otherwise falls back to identity.
- `virt_to_gfn()`, `gfn_to_virt()`, and `percpu_to_gfn()` convert kernel/percpu addresses to Xen page granularity.
- `arbitrary_virt_to_machine()` `BUG()`s because ARM guests are HVM for this path.
- Foreign mapping functions manage grant table map/unmap P2M entries.
- `__set_phys_to_machine*`, `set_phys_to_machine()`, and `xen_arch_need_swiotlb()` expose P2M updates and DMA bounce decisions.

## Control Flow
Grant mapping code calls `set_foreign_p2m_mapping()` after map hypercalls and `clear_foreign_p2m_mapping()` during unmap. DMA setup calls `xen_arch_need_swiotlb()` to decide whether a device address needs Xen SWIOTLB bouncing. Address helpers are inline conversion paths used by grant and DMA code.

## State And Persistence
Persistent state is the `phys_to_mach` red-black tree for non-identity bus mappings and architecture-maintained P2M entries. The header does not allocate state itself.

## Dependencies And Integration Points
It depends on ARM page and pgtable headers, Linux PFN/DMA/device types, Xen core detection, and grant-table structures. It integrates with Xen SWIOTLB, grant mapping, DMA APIs, and page conversion helpers.

## Risks And Edge Cases
Linux pages may span multiple non-contiguous 4 KiB Xen pages, so callers must not treat Linux pages and Xen frames as interchangeable. Direct PV-only helpers call `BUG()` on ARM. `pfn_to_bfn()` fallback to identity is correct only when no override mapping exists.

## Test Signals
Signals include correct grant map/unmap P2M updates, DMA bouncing decisions for non-direct mappings, valid conversions for normal/percpu addresses, and no PV-only helper use on ARM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/page.h -->
