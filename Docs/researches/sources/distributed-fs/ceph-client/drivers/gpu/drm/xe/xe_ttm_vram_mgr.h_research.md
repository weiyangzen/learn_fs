# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_vram_mgr.h

Purpose: Declares the VRAM manager API and inline converters between TTM base structures and Xe VRAM manager/resource structures.

Important APIs/types/functions: Declares initialization, SG allocation/free, visible/used/available query functions, and inline `to_xe_ttm_vram_mgr_resource` plus `to_xe_ttm_vram_mgr`.

Control flow: Setup code calls init functions; memory accounting/debug code calls query functions; DMA-buf or external mapping paths call SG helpers; TTM callbacks and consumers use inline converters for container access.

State and persistence behavior: Header has no storage but exposes access to manager/resource state defined in `xe_ttm_vram_mgr_types.h`.

Dependencies and integration points: Includes `xe_ttm_vram_mgr_types.h`; forward-declares DMA direction, device, tile, and VRAM region types. Shared by regular VRAM and stolen-memory manager code.

Risks: Container helpers assume the passed base pointer really belongs to Xe VRAM manager/resource types. Misuse with non-VRAM TTM resources will corrupt interpretation.

Test signals: Compile coverage for all consumers, SG export tests, and memory-manager init paths for both `XE_PL_VRAM*` and `XE_PL_STOLEN`.
