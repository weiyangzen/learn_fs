## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-v0-core.c

Purpose: Register back end for eDMA v0, covering legacy viewport and unrolled register maps, interrupt handling, linked-list writing, channel configuration, doorbell start, debugfs enablement, and emulated interrupt acknowledgement.

Important APIs/types/functions: registers ops through `dw_edma_v0_core_register()`. Key functions are `dw_edma_v0_core_off()`, `dw_edma_v0_core_ch_count()`, `dw_edma_v0_core_ch_status()`, `dw_edma_v0_core_handle_int()`, `dw_edma_v0_core_start()`, `dw_edma_v0_core_ch_config()`, `dw_edma_v0_core_ack_emulated_irq()`, and helpers for viewport-safe channel register reads/writes.

Control flow: common core calls `start()` with a chunk; this back end writes LLI entries and the loopback LLP, enables engine and interrupts on first chunk, writes MSI target/data registers, sets channel LLP, synchronizes remote LL memory with a dummy read when needed, and rings the direction-specific doorbell. IRQ handling reads done/abort status, masks by assigned IRQ channel mask, clears per-channel bits, and calls common done/abort callbacks.

State and persistence: hardware state includes engine enable, interrupt masks/clears/status, per-channel context, MSI programming, and LL memory contents. Legacy channel access is serialized by `dw->lock` because all channels share a viewport selector.

Dependencies and integration: uses `dw-edma-v0-regs.h`, `dw-edma-v0-debugfs.h`, `bitfield`, 64-bit MMIO helpers, and `dw_edma_core_ops`.

Risks and test signals: legacy viewport races, CB/TCB toggling, remote LL write ordering, MSI data packing, and HDMA-compatible power-enable special cases are sensitive. Test with legacy and unroll map formats, done/abort IRQs, remote engine mode, multiple channels, and debugfs register reads.
