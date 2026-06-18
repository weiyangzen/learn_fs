# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_mem.c

Purpose: manages IPA local/shared memory definitions, validation, mapping, canary setup, DMA zero buffer, IMEM/SMEM IOMMU mappings, and immediate-command initialization/zeroing of AP/modem memory regions.

Important APIs/functions: `ipa_mem_find()` locates configured local-memory regions. `ipa_mem_init()` validates memory data, maps `"ipa-shared"`, maps optional SRAM/IMEM and SMEM through the IOMMU, and sets DMA mask. `ipa_mem_config()` reads `SHARED_MEM_SIZE`, bounds configured regions, allocates a coherent zero buffer, writes canaries, and checks UC event-ring alignment. `ipa_mem_setup()` uses immediate commands to initialize header memory and zero processing/modem memory, then programs `LOCAL_PKT_PROC_CNTXT`. `ipa_mem_zero_modem()` re-zeroes modem-owned regions after SSR.

Control flow: early init validates all config-table regions for version applicability, required presence, size/alignment, duplicate IDs, and table memory consistency. Config, under power, reconciles hardware-advertised shared memory with mapped resources and prepares DMA zeroing. Setup, after command endpoint is enabled, performs hardware memory initialization via GSI immediate commands.

State/persistence: `ipa->mem`, `mem_count`, `mem_virt`, `mem_addr`, `mem_size`, `mem_offset`, `zero_virt/addr/size`, `imem_iova/size`, and `smem_iova/size` persist until exit/deconfig. SMEM allocation itself is persistent until AP reboot and cannot be freed.

Dependencies/integration: depends on `ipa_data` memory tables, IPA table validation, immediate command DMA helpers, Linux DMA/IOMMU/memremap APIs, Device Tree resources, Qualcomm SMEM, and register field helpers.

Risks: memory offsets are hardware-visible and also sent to the modem via QMI; off-by-one or size-unit mistakes can corrupt shared tables. `ipa_mem_valid()` logs missing required regions but returns true, so required-region enforcement may be weaker than intended. IOMMU direct mappings assume physical-address IOVA layout. Canary writes do not appear to be checked later in this file.

Test signals: probe validates memory tables, `ipa_mem_config()` accepts hardware shared memory size, QMI init-driver request contains expected offsets, modem SSR zeroing succeeds, and no IOMMU unmap size warnings occur on exit.
