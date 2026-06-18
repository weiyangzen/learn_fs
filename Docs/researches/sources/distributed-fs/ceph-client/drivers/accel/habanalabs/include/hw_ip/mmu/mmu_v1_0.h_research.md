## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/hw_ip/mmu/mmu_v1_0.h

### Purpose
`mmu_v1_0.h` provides address-bit masks, shifts, and root/busy register offsets for the first HabanaLabs MMU generation.

### Important APIs, Types, And Functions
It defines HOP0 through HOP4 masks/shifts for a five-level 4 KiB-style walk and register offsets `MMU_HOP0_PA43_12`, `MMU_HOP0_PA49_44`, and `MMU_ASID_BUSY`.

### Control Flow
The header has no functions. MMU v1.0 code extracts hop indexes from virtual addresses using these masks/shifts, writes the split HOP0 physical address registers, and polls ASID busy state.

### State, Persistence, And Dependencies
State persists in MMU registers and page tables. This file depends on v1.0 hardware using the documented virtual-address layout and register addresses.

### Integration Points
It integrates with HabanaLabs MMU setup and map/unmap operations for devices using MMU v1.0.

### Risks
A wrong mask shifts the page-table walk to the wrong PTE. Root-address split fields are especially sensitive because an invalid HOP0 base breaks all translations for the ASID.

### Test Signals
Validate virtual-address-to-hop index calculations, root register programming for low/high physical bits, ASID busy polling, and translation of mappings that exercise each hop boundary.
