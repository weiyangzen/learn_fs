<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_stlb_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_stlb_masks.h

## Purpose
`dcore0_hmmu0_stlb_masks.h` is the generated bitfield map for the DCORE0 HMMU0 STLB register bank. It defines 192 shift/mask macros for STLB busy/ASID/root-hop setup, cache invalidation, feature and AXI-cache controls, hop configuration, invalidation status, SRAM init, memory-cache configuration, per-hop thresholds, multi-hit interrupts, range invalidation, and ASID scrambler polynomial matrix fields.

## Important APIs, types, and functions
Key fields include `BUSY`, `ASID`, `HOP0_PA43_12` and `HOP0_PA63_44`, cache invalidation producer/index/mask and base address fields, feature-enable bits for multi-page-size, lookup, bypass, bank stop, trace, follower, caching, and follower limits, STLB AXI cache attributes, hop configuration fields for first/last/follower/large-page behavior, lookup masks, invalidate-all start/set/page-size/consumer-index/hit-count/set fields, SRAM init busy bits, memory-cache invalidation done/idle, memory-cache base/config fields, threshold min/max/mask for hops 0-5, multi-hit interrupt mask, L0 cache config, memory read ARPROT, range invalidation enable/ASID/start/end fields, ASID scrambler enable, and H3 polynomial matrix rows 0-18.

## Control flow
The header is declarative. MMU/STLB initialization programs ASID and root-hop physical addresses, feature/hop/cache configuration, cache thresholds, scrambler fields, and interrupt masks. Invalidation flows write cache/range/all invalidation registers, poll busy/done/consumer/hit-count fields, and coordinate with MMU page-table updates.

## State and persistence behavior
STLB configuration is persistent translation-cache state. Root table address, ASID, feature, cache, hop, threshold, range invalidation, and scrambler values stay active until reset or reprogramming. Invalidation status and hit counts are transient but important for synchronization with page-table changes.

## Dependencies and integration points
This file integrates with `dcore0_hmmu0_stlb_regs.h`, HMMU MMU control, page-table management, TLB/cache invalidation code, ASID allocation, and memory fault handling. It shares address and ASID semantics with AXUSER/MMU programming elsewhere in Gaudi2.

## Risks and edge cases
Risks include stale translations after incomplete invalidation, wrong root-hop physical address halves, ASID mismatch with AXUSER traffic, bypass or bank-stop left enabled, threshold values that reduce cache correctness/performance, and scrambler matrix programming errors. Invalidation flows are synchronization-sensitive and should not ignore busy/done fields.

## Test signals
Test signals include STLB initialization, page-table walk success, range and full invalidations, ASID-specific invalidation, cache idle/done polling, multi-hit interrupt handling, page remap/unmap stress, and fault tests proving stale translations are not reused.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_stlb_masks.h -->
