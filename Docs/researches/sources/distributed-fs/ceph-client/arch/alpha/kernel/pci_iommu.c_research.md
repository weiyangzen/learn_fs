# sources/distributed-fs/ceph-client/arch/alpha/kernel/pci_iommu.c

## Purpose
`pci_iommu.c` implements Alpha PCI DMA mapping operations. It chooses among direct-map DMA windows, DAC addressing, and scatter-gather IOMMU arenas; maintains arena PTE allocation; maps and unmaps streaming and coherent buffers; maps scatterlists; and exposes AGP GART reservation/bind APIs. Its public output is `alpha_pci_ops`, the `dma_map_ops` table used by devices on Alpha PCI systems.

## Important APIs, Types, And Functions
- `mk_iommu_pte()` builds a valid Alpha IOMMU PTE from a physical address.
- `size_for_memory()` returns a power-of-two window size no larger than a cap and at least large enough for low memory.
- `iommu_arena_new_node()` and `iommu_arena_new()` allocate boot-time IOMMU arena structures and PTE arrays with `memblock_alloc_or_panic()`.
- `iommu_arena_find_pages()`, `iommu_arena_alloc()`, and `iommu_arena_free()` implement locked bitmap-like PTE allocation by scanning the PTE table for zero entries, honoring segment-boundary constraints and alignment.
- `pci_dac_dma_supported()` checks whether a PCI device and machine vector can use DAC addressing via `alpha_mv.pci_dac_offset`.
- `pci_map_single_1()` is the central single-buffer mapper. It first tries the direct window, then DAC when allowed, then host-bridge SG/ISA IOMMU arenas.
- `alpha_gendev_to_pci()` maps generic `struct device` pointers to PCI devices, ISA bridge pseudo-devices, or NULL for ISA bus masters.
- `alpha_pci_map_phys()`, `alpha_pci_unmap_phys()`, `alpha_pci_alloc_coherent()`, and `alpha_pci_free_coherent()` implement DMA map/unmap and coherent allocation hooks.
- `sg_classify()`, `sg_fill()`, `alpha_pci_map_sg()`, and `alpha_pci_unmap_sg()` merge scatterlist entries, choose direct/DAC/IOMMU mappings, and release mappings.
- `alpha_pci_supported()` answers `dma_supported`.
- `iommu_reserve()`, `iommu_release()`, `iommu_bind()`, and `iommu_unbind()` are AGP/GART-style arena reservation helpers.
- `alpha_pci_ops` wires these functions into the DMA mapping layer and reuses common mmap/sgtable/page allocation helpers.

## Control Flow
Single-buffer mapping starts in `alpha_pci_map_phys()`, rejects `DMA_ATTR_MMIO`, converts generic devices, checks DAC eligibility, and delegates to `pci_map_single_1()`. `pci_map_single_1()` returns immediately for direct-map or DAC-capable addresses. If those fail, it requires `alpha_mv.mv_pci_tbi`, selects `hose->sg_pci` unless it exceeds the device mask, falls back to `hose->sg_isa`, allocates PTEs, writes PTEs for each page, and returns the DMA window address plus original offset. Unmapping reverses this by recognizing direct/DAC addresses, otherwise freeing arena PTEs and flushing the IOMMU TLB if freed entries lie beyond the next allocation pointer.

Scatter-gather mapping classifies entries into physical or virtual runs, chooses an arena if the platform has a TBI function, and emits compact DMA segments. `sg_fill()` uses direct/DAC for physically contiguous leaders and IOMMU mappings for virtual contiguity. If IOMMU allocation fails for a virtually contiguous run, it reclassifies without virtual merging and retries. Unmap walks the mapped output entries until a zero `dma_length` marker and frees only IOMMU-backed ranges.

AGP helpers reserve PTE ranges as `IOMMU_RESERVED_PTE`, later bind them to page arrays, and unbind them back to reserved state rather than free state.

## State And Persistence
Persistent in-kernel state lives in each `pci_iommu_arena`: a PTE array, spinlock, allocation cursor, base, size, and alignment. PTE values track free (`0`), invalid in-use, reserved AGP ranges, or valid physical mappings. Coherent allocations allocate kernel pages and map them through the same DMA path. There is no disk persistence, but incorrect arena state persists until reboot and can corrupt future DMA mappings.

## Dependencies And Integration Points
The code depends on Alpha machine-vector fields (`alpha_mv.mv_pci_tbi`, `alpha_mv.pci_dac_offset`), PCI hose fields (`sg_pci`, `sg_isa`), global direct-map exports (`__direct_map_base`, `__direct_map_size`), `isa_bridge`, Linux DMA/IOMMU helpers, scatterlist APIs, and memblock boot allocation. It is integrated through `alpha_pci_ops`, which architecture setup assigns to devices.

## Risks
- The arena allocator is linear and cursor-based; fragmentation or repeated large mappings can cause allocation failures until wrap and TLB flush.
- `alpha_gendev_to_pci()` uses `BUG_ON(!isa_bridge)` for non-PCI devices, so unexpected device classes can crash the kernel.
- Some error paths assume `pdev` is non-NULL when unmapping via generic DMA APIs; ISA/NULL handling should be treated carefully.
- SG code temporarily overloads `dma_address` and `dma_length` for classification markers, so changes must preserve marker interpretation.
- Incorrect TLB flush boundaries can leave stale DMA translations visible to hardware.

## Test Signals
- Boot on Alpha systems with and without `mv_pci_tbi`.
- DMA API tests covering streaming map/unmap, coherent allocation, SG mapping, direct window, DAC, and ISA-mask-limited devices.
- Stress with small/large scatterlists to exercise coalescing and allocation fallback.
- AGP/GART reservation tests verifying reserve-bind-unbind-release state transitions.
- Kernel warnings `pci_map_single failed`, `Bogus pci_unmap_single`, and SG allocation failures should be absent under normal device workloads.
