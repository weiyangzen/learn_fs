<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pmmu_hbw_stlb_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pmmu_hbw_stlb_masks.h

## Purpose
`pmmu_hbw_stlb_masks.h` defines field masks and shifts for the high-bandwidth PMMU shared TLB block. It is paired with `pmmu_hbw_stlb_regs.h`, guarded by `ASIC_REG_PMMU_HBW_STLB_MASKS_H_`, and exports 193 macros covering STLB lookup, invalidation, cache configuration, page-table-hop configuration, thresholding, interrupts, range invalidation, and ASID scrambling.

## Important APIs, Types, And Functions
No functions or types are present. Key field groups include:

- `BUSY`, `ASID`, and HOP0 physical address fields.
- `CACHE_INV` producer index and index mask, plus invalidation base address fields.
- `STLB_FEATURE_EN` for multi-page-size mode, lookup enable, bypass, bank stop, trace, follower, caching, and follower limit.
- `STLB_AXI_CACHE` and `HOP_CONFIGURATION` fields used for memory access behavior and page-table walk topology.
- `INV_ALL_*`, `INV_PS`, consumer index, hit count, set selection, SRAM init busy flags.
- `MEM_CACHE_*`, `SET_THRESHOLD_HOP0..5`, multi-hit interrupt mask/clear, L0 cache config, ARPROT, range invalidation start/end/asid, and ASID scrambler polynomial matrix entries.

## Control Flow
The header itself is declarative. Driver MMU initialization composes `HOP_CONFIGURATION` with these shifts/masks, configures STLB features and memory cache behavior, and invalidates STLB/cache entries by programming invalidation registers then polling status. In `gaudi2.c`, HBW STLB cache invalidation writes and polls `MEM_CACHE_INVALIDATION` and `MEM_CACHE_INV_STATUS`, and STLB setup uses the HOP configuration field macros.

## State And Persistence
The fields describe MMU translation-cache state and configuration. Translation roots, cache enable/bypass state, invalidation indices, hit counters, thresholds, and ASID scrambling configuration persist in hardware until reset or reconfiguration. Invalidation status is transient and must be polled carefully.

## Dependencies
The masks depend on matching addresses in `pmmu_hbw_stlb_regs.h`, Gaudi2 MMU helper code, and kernel bitfield operations. Correctness also depends on page-table format and ASID allocation policy in the driver/firmware stack.

## Integration Points
The file integrates directly with Gaudi2 MMU initialization and invalidation paths. `gaudi2.c` uses `mmPMMU_HBW_STLB_BASE` and these masks to configure hop layout and invalidate HBW STLB caches. Security code includes the PMMU HBW STLB base region in protected-range handling.

## Risks
MMU mask errors are severe: wrong hop configuration can break address translation; wrong invalidation fields can leave stale translations; wrong ASID scrambling or range invalidation fields can cause cross-context leakage or spurious faults. Polling code must respect status bits and timeouts because invalidation is asynchronous.

## Test Signals
Signals include MMU initialization success, page-table walk correctness for small and large pages, range and full invalidation tests, stale-translation stress under map/unmap churn, ASID isolation, and absence of multi-hit interrupts or PMMU cache timeout errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pmmu_hbw_stlb_masks.h -->
