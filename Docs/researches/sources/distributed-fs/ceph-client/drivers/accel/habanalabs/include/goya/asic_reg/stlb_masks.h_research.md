# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/stlb_masks.h

Purpose: defines 63 field shift/mask constants for the shared TLB block. It covers cache invalidation producer/index masks, invalidation base physical address bits, feature enables, AXI cache attributes, page-table hop configuration, linked-list masks, invalidate-all/set/page-size controls, hit/consumer counters, and SRAM init busy bits.

Important APIs/types/functions: no functions or types. Key macros include `STLB_CACHE_INV_PRODUCER_INDEX_MASK`, `STLB_CACHE_INV_BASE_49_40_PA_MASK`, `STLB_STLB_FEATURE_EN_LOOKUP_EN_MASK`, `STLB_STLB_FEATURE_EN_BYPASS_MASK`, `STLB_HOP_CONFIGURATION_*`, `STLB_INV_PS_R_MASK`, and `STLB_SRAM_INIT_BUSY_*`.

Control flow: MMU code prepares invalidation base registers, writes invalidate page-size/set/producer-index values, then polls invalidation progress or hit counters. Equivalent Gaudi code writes `mmSTLB_CACHE_INV_BASE_*`, toggles `mmSTLB_CACHE_INV`, and polls `mmSTLB_INV_PS`.

State and persistence: STLB configuration and invalidation producer/consumer state live in hardware. The producer index often acts as a monotonic software-managed sequence value.

Dependencies and integration: included by `goya_regs.h`, paired with `stlb_regs.h`, and consumed by MMU/cache invalidation flows. Some STLB mask definitions are duplicated in higher-level device mask headers for convenience.

Risks: invalidation fields are correctness-critical for address translation. A bad base mask or page-size field can leave stale translations active. Producer-index wrap and consumer synchronization must match hardware expectations.

Test signals: MMU map/unmap tests, page-size variants, cache invalidation completion polling, translation fault tests after unmap, and SRAM init status checks.
