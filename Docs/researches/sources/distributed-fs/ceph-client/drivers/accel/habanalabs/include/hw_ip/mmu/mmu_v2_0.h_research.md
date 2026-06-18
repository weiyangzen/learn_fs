## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/hw_ip/mmu/mmu_v2_0.h

### Purpose
`mmu_v2_0.h` defines HabanaLabs MMU v2.0 hop masks and shifts for 4 KiB and 64 KiB page modes, plus a compact DMA-hop layout.

### Important APIs, Types, And Functions
It exports `HOP0_MASK_4K` through `HOP5_MASK_4K`, `HOP0_MASK_64K` through `HOP5_MASK_64K`, matching shift macros, and DMA aliases `DHOP0_MASK` through `DHOP4_MASK`/`DHOP*_SHIFT`.

### Control Flow
The file has no functions. MMU v2 code chooses the appropriate mask/shift set based on page size and extracts indexes for up to six hops; DMA mappings use the DHOP layout.

### State, Persistence, And Dependencies
State persists in page tables programmed by users of these constants. The header depends on hardware supporting distinct 4 KiB, 64 KiB, and DMA walk encodings.

### Integration Points
It integrates with v2 MMU map/unmap, contiguous-page optimization, and DMA address-space mapping logic in the HabanaLabs driver.

### Risks
Mixed page-size modes can be error-prone because HOP indexes shift by different amounts. DHOP4 uses a nonstandard mask/shift, so generic six-hop code must not accidentally reuse full 4 KiB HOP4 constants.

### Test Signals
Verify 4 KiB and 64 KiB mappings at each hop boundary, DMA-hop translations, large/contiguous mapping paths, and fault reports that decode the same virtual address indexes used during mapping.
