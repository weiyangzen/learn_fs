# sources/distributed-fs/ceph-client/drivers/nvmem/mtk-efuse.c

Purpose: MediaTek eFuse NVMEM provider with optional post-processing for GPU speed-bin cells.

Important APIs/types/functions: `mtk_reg_read()` byte-copies MMIO eFuse data. `mtk_efuse_fixup_dt_cell_info()` attaches `mtk_efuse_gpu_speedbin_pp()` to small `gpu-speedbin` cells on SoCs needing conversion from numeric bin to bitmask. Probe registers NVMEM and creates a child `mtk-socinfo` platform device.

Control flow: probe maps the eFuse resource, chooses compatible match data, fills a byte-granular read-only NVMEM config sized from the resource, optionally installs the fixup callback, registers NVMEM, then registers `mtk-socinfo`. Remove unregisters that child device.

State/persistence: eFuse data is persistent hardware state. The driver persists only the MMIO base and optional child platform device pointer.

Dependencies/integration: OF compatibles include `mediatek,mt8173-efuse`, `mediatek,mt8186-efuse`, and generic `mediatek,efuse`; integrates with NVMEM fixed cells and MediaTek SoC information driver.

Risks: `pdata` is assumed non-NULL from match data. The prefix comparison for `gpu-speedbin` uses the shorter of actual and expected lengths, so very short names that prefix-match could be post-processed. SoC info registration failure is informational, not fatal.

Test signals: raw byte reads, MT8186 speed-bin cell conversion, child device registration/unregistration, and missing match-data probe behavior.
