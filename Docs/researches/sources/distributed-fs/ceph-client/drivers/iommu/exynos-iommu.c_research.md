# sources/distributed-fs/ceph-client/drivers/iommu/exynos-iommu.c

## Purpose
Samsung Exynos SYSMMU IOMMU driver. It manages one or more SYSMMU controllers per master device, implements Exynos-specific two-level 32-bit IOVA page tables, handles hardware version differences from v1 through v7, controls clocks/runtime PM, reports faults, and registers generic IOMMU domain operations.

## Important APIs, Types, And Functions
`struct sysmmu_drvdata` holds one controller's registers, clocks, active state, version, variant ops, master link, and domain list nodes. `struct exynos_iommu_owner` is per-master state with controller list, current domain, and RPM mutex. `struct exynos_iommu_domain` owns the level-1 table, level-2 free-entry counters, attached controller list, and locks. `struct sysmmu_variant` abstracts register offsets and fault decoding for v1, v5, v7, and v7 VM layouts. Key functions cover version detection, block/unblock, TLB invalidation, enable/disable, IRQ fault handling, platform probe, PM suspend/resume, page-table allocation/free, identity and translated attach, map/unmap, iova-to-phys, device probe/release, OF xlate, and `exynos_iommu_init()`.

## Control Flow
Core init creates an aligned kmem cache and zero L2 table, then registers the SYSMMU platform driver if matching DT nodes exist. Controller probe maps registers, requests IRQ, gets clocks, detects hardware version and variant, initializes global page-entry shift/protection tables on first probe, sets DMA mask for v5+, chooses a DMA device for page-table cache syncs, enables runtime PM, and registers the IOMMU. OF xlate builds per-master owner state and links controllers. Attach first returns the old domain to identity, then assigns the new page-table physical address to each controller and enables active controllers. Map writes section, large page, or small page PTEs with cache sync; unmap clears entries, updates counters, and invalidates attached controllers. Fault IRQ decodes variant-specific status, reports to IOMMU core, panics if unrecovered, clears interrupt, and unblocks the SYSMMU.

## State And Persistence
Runtime state includes global `PG_ENT_SHIFT`, protection tables, `dma_dev`, `lv2table_kmem_cache`, `zero_lv2_table`, per-controller active/version/domain fields, per-owner controller lists, and per-domain page tables/counters. There is no disk persistence. Page tables are DMA-synced through the selected `dma_dev` because hardware walks them directly.

## Dependencies And Integration Points
It integrates with platform/OF probing, IOMMU core, DMA-IOMMU reserved regions, runtime PM and device links, clock framework, DMA mapping/cache sync, kmem caches, iommu-pages allocation, fault reporting, and generic device grouping. Client devices reference SYSMMU phandles through DT.

## Risks
Global `PG_ENT_SHIFT` assumes all controllers share address format. Page-table updates depend on `dma == phys` for the page table DMA mapping and use BUG_ON for violations. Faults panic if not handled by a client. Hardware v3.x FLPD cache workarounds require holes/alignment and explicit invalidation; missing them can cause false faults. Attach/detach and PM use multiple locks across owner/domain/controller state. Lack of driver remove cleanup for global caches is normal for core init but matters for test isolation.

## Test Signals
Boot Exynos platforms with v1/v3/v5/v7 SYSMMUs, one and multiple controllers per master, runtime suspend/resume while attached, identity attach/detach, 1 MiB/64 KiB/4 KiB map/unmap, FLPD cache workaround paths, fault injection and client fault handlers, DMA mask setup, page-table cache sync validation, and CONFIG_EXYNOS_IOMMU_DEBUG logging.
