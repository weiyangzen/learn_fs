# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_mmu.c

Purpose: `sh_css_mmu.c` connects the CSS driver to the hardware MMU and SP TLB invalidation path. It invalidates SP-side DMA proxy translation state when the SP is running and updates all MMU devices with a new page table base index.

Important APIs/types/functions: `ia_css_mmu_invalidate_cache()` checks `sh_css_sp_is_running()`, obtains the SP firmware `invalidate_tlb` address from `sh_css_sp_fw`, and stores `true` to the SP DMEM symbol `ia_css_dmaproxy_sp_invalidate_tlb`. `sh_css_mmu_set_page_table_base_index(hrt_data base_index)` loops over `N_MMU_ID`, calls `mmu_set_page_table_base_index()`, and invalidates each MMU cache.

Control flow and state: the cache invalidation path is conditional on SP running so DMEM is not touched before SP initialization. The page-table update path is synchronous and iterates all MMU IDs without storing additional state in this file.

Dependencies and integration: it depends on `ia_css_mmu` APIs, SP running state from `sh_css_sp.h`, loaded SP firmware offsets from `sh_css_firmware.h`, SP DMEM accessors, and `mmu_device.h`. It is part of memory mapping setup and invalidation after HMM/page table changes.

Risks: if firmware offset metadata is wrong or the SP firmware is not loaded, the invalidate flag can target the wrong DMEM address. `sh_css_mmu_set_page_table_base_index()` assumes all MMU IDs accept the same base index and always invalidates immediately; failures are not reported. The local `HIVE_ADDR_...` variable is assigned but not directly used except to silence warnings, so the actual symbol address comes from `sp_address_of()`.

Test signals: integration tests should update page table bases and verify DMA translations change only after invalidation. SP-running and SP-not-running cases should be covered. Firmware load tests should verify `sh_css_sp_fw.info.sp.invalidate_tlb` is populated before invalidation paths are used.
