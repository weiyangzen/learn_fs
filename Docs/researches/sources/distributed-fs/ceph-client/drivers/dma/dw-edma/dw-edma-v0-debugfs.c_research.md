## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-v0-debugfs.c

Purpose: Optional debugfs register exposure for eDMA v0 legacy/unroll/compatible hardware.

Important APIs/types/functions: exports `dw_edma_v0_debugfs_on()`. Defines debugfs entry descriptors, `dw_edma_debugfs_u32_get()`, register array builders for global write/read registers, per-channel context registers, and legacy viewport-aware access.

Control flow: when debugfs is initialized, the function creates `mf`, `wr_ch_cnt`, `rd_ch_cnt`, and a `registers` tree under the DMAengine debug root. It creates write/read subdirectories and channel directories, with read-only files that return MMIO register values. Legacy channel register reads program the viewport selector under `dw->lock`.

State and persistence: debugfs entries are devm-allocated and mirror live MMIO state; they do not store values independently.

Dependencies and integration: compiled only when `CONFIG_DEBUG_FS` through the Makefile. Integrates with DMAengine debug roots and eDMA v0 register layouts.

Risks and test signals: unsafe debugfs files expose live register reads; legacy viewport must remain locked to avoid racing hardware access. Test by mounting debugfs, probing eDMA v0, reading global and channel files in legacy and unroll formats, and verifying no probe failure when debugfs is disabled.
