## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-hdma-v0-debugfs.c

Purpose: Optional debugfs register exposure for native HDMA v0 channels.

Important APIs/types/functions: exports `dw_hdma_v0_debugfs_on()`. Builds read-only files for per-channel write/read register blocks via `dw_hdma_debugfs_regs_ch()`, `dw_hdma_debugfs_regs_wr()`, and `dw_hdma_debugfs_regs_rd()`.

Control flow: when debugfs is initialized, creates `mf`, `wr_ch_cnt`, `rd_ch_cnt`, then a `registers/write/channel:N` and `registers/read/channel:N` tree. Each file reads a live 32-bit MMIO register such as `ch_en`, `doorbell`, `llp`, `sar`, `dar`, `ch_stat`, `int_stat`, MSI registers, and control fields.

State and persistence: debugfs entries are devm-allocated views onto live hardware registers. They do not persist data or modify device state.

Dependencies and integration: compiled under `CONFIG_DEBUG_FS`; depends on `dw-hdma-v0-regs.h` and the common eDMA debug root.

Risks and test signals: read-only MMIO is low-impact but still tied to correct offsets and live device lifetime. Test with debugfs enabled, native HDMA probe, register file reads during idle and active transfers, and disabled debugfs builds.
