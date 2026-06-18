# sources/distributed-fs/ceph-client/drivers/char/agp/ati-agp.c

## Purpose
This file implements AGPGART support for ATI Radeon IGP host bridges using a two-level GATT and ATI GART MMIO registers.

## Important APIs, Types, and Functions
Key functions include `ati_create_page_map()`, `ati_free_page_map()`, `ati_create_gatt_pages()`, `is_r200()`, `ati_fetch_size()`, `ati_tlbflush()`, `ati_cleanup()`, `ati_configure()`, `ati_insert_memory()`, `ati_remove_memory()`, `ati_create_gatt_table()`, `ati_free_gatt_table()`, `agp_ati_probe()`, and `agp_ati_remove()`. The bridge callback table is `ati_generic_bridge`.

## Control Flow
Probe matches ATI host bridges, verifies AGP capability, checks the device against a supported chipset table, allocates a bridge, attaches ATI callbacks, reads mode, and calls `agp_add_bridge()`. GATT creation allocates an uncached AGP-mapped page directory and second-level pages, programs aperture size in RS100 or RS300 registers, records the aperture bus address, fills directory entries, and initializes PTEs to the scratch page. Configure ioremaps GART MMIO, sets AGP mode, enables the GART feature, sets a PCI command/status-related bit, and writes the GATT base.

## State and Persistence Behavior
State is held in `ati_generic_private.registers`, second-level `gatt_pages`, and generic bridge fields. Page-table pages are mapped into AGP-visible memory and changed to uncached, then restored on free. Cleanup restores the previous aperture size and unmaps MMIO.

## Dependencies and Integration Points
It depends on PCI, generic AGP backend, architecture AGP page mapping helpers `map_page_into_agp()`/`unmap_page_from_agp()`, x86 memory attribute helpers, and ATI PCI IDs.

## Risks
Correctly distinguishing RS100/RS200-style registers from RS300-style registers is essential. GATT page allocation has multi-level cleanup requirements. Insert/remove only support mask type 0 and must catch occupied entries before writes. The code does not explicitly bounds-check removal range against aperture size, relying on callers. Cacheability and AGP page mapping mistakes can produce stale or inaccessible GATT entries.

## Test Signals
Test supported ATI IGP variants, aperture size read/write, GATT allocation failure unwind, insert/remove occupancy checks, TLB flush register writes, resume reconfiguration, and module unload after active AGP mappings are released.
