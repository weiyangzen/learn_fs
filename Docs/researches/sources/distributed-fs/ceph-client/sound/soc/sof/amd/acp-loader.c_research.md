# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-loader.c

Purpose: ACP firmware block staging, PTE programming, DMA/SHA transfer setup, DSP run control, and signed-firmware loading support.

Important APIs/types/functions: `acp_dsp_block_write()` stages IRAM/DRAM/SRAM firmware blocks in coherent DMA buffers. `acp_dsp_block_read()` reads SRAM blocks from scratch. `configure_pte_for_fw_loading()` builds ATU PTEs for firmware buffers. `acp_dsp_pre_fw_run()` runs SHA DMA for code and plain DMA for DRAM/SRAM blocks, configures cache windows, and frees staging buffers. `acp_sof_dsp_run()` clears runstall. `acp_sof_load_signed_firmware()` requests separate code/data binaries for quirked signed firmware.

Control flow: block writes allocate buffers lazily by block type, copy firmware data, and record sizes/use flags. Pre-run computes code page count, programs PTEs, validates/transfers code through SHA DMA, optionally transfers DRAM and SRAM images, enables cache window for newer ACP revisions, and frees coherent buffers. Run writes `ACP_DSP0_RUNSTALL` and optional fusion DSP runstall when firmware debug is enabled.

State and persistence: transient DMA buffers and sizes live in `acp_dev_data` during firmware load. `is_dram_in_use`, `is_sram_in_use`, page counts, and quirk flags affect later pre-run behavior.

Dependencies and integration points: used through `sof_acp_common_ops`. Depends on PCI DMA APIs, SOF generic firmware loader, ACP DMA helpers in `acp.c`, register offsets, and firmware naming from PCI descriptors/quirks.

Risks: buffer size constants (`ACP_DEFAULT_DRAM_LENGTH`, `ACP_DEFAULT_SRAM_LENGTH`) must match firmware expectations. Signed firmware subtracts `ACP_FIRMWARE_SIGNATURE` from transfer size; incorrect quirking breaks validation. Error paths after allocations rely on later cleanup; repeated firmware load failures should be checked for leaks.

Test signals: firmware boot on normal and signed-image platforms, SHA DMA validation status, DRAM/SRAM section transfer completion, and runstall register traces.
