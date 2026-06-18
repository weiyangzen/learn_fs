# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/stlb_regs.h

Purpose: maps the Goya STLB register block with 16 addresses. The block drives TLB invalidation, feature enablement, AXI cache attributes, hop configuration, linked-list lookup masks, invalidate-all/set/page-size controls, hit/consumer status, and SRAM initialization state.

Important APIs/types/functions: macro-only `mmSTLB_*` addresses from `mmSTLB_CACHE_INV` at `0x490010` to `mmSTLB_SRAM_INIT` at `0x49004C`.

Control flow: MMU invalidation code programs invalidation base high/low, sets page size and set selection, writes a producer index to `CACHE_INV`, then waits for consumer/index/page-size status to indicate completion. Initialization code can check SRAM init busy bits.

State and persistence: STLB feature, invalidation, linked-list, and SRAM init status are persistent device state. They directly affect MMU correctness.

Dependencies and integration: included by `goya_regs.h`; field masks are in `stlb_masks.h`. Goya/Gaudi driver code uses equivalent macros in MMU prepare and cache invalidation functions.

Risks: address mismatches can make invalidations no-ops, causing stale translations and memory corruption. The Goya STLB base differs from Gaudi's equivalent block, so cross-device headers must not be mixed.

Test signals: MMU cache invalidation under map/unmap churn, consumer-index progression, page-size coverage, translation fault/retry tests, and boot-time SRAM init polling.
