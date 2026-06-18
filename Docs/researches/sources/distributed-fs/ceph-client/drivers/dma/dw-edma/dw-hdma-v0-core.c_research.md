## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-hdma-v0-core.c

Purpose: Register back end for native DesignWare HDMA v0 hardware, supporting linked-list and non-linked-list modes.

Important APIs/types/functions: registers ops through `dw_hdma_v0_core_register()`. Key functions are `dw_hdma_v0_core_off()`, `dw_hdma_v0_core_ch_count()`, `dw_hdma_v0_core_ch_status()`, `dw_hdma_v0_core_handle_int()`, `dw_hdma_v0_core_start()`, `dw_hdma_v0_core_ll_start()`, `dw_hdma_v0_core_non_ll_start()`, and `dw_hdma_v0_core_ch_config()`.

Control flow: `off()` masks/clears stop and abort interrupts and disables all channels. Start writes LL entries and a looping LLP, or in non-LL mode directly programs SAR/DAR/transfer size for a single burst. It enables channel interrupts, programs LL pointer/cycle bits for LL mode, and rings the per-channel doorbell. IRQ handling iterates channels in the assigned mask and invokes common done/abort callbacks based on per-channel interrupt status.

State and persistence: per-channel MMIO holds enable, doorbell, LLP, cycle sync, transfer registers, MSI addresses, status, and interrupt setup. Non-LL mode uses only the first burst in a chunk. No persistent state beyond hardware while loaded.

Dependencies and integration: uses `dw-hdma-v0-regs.h`, `dw-hdma-v0-debugfs.h`, and common eDMA core ops. It is selected when `dw_edma_chip.mf == EDMA_MF_HDMA_NATIVE`.

Risks and test signals: risks include swapped argument order in register helper calls, non-LL single-burst assumptions, interrupt mask polarity, remote LL ordering, and unknown doorbell offset reporting. Test native HDMA with SG/cyclic/interleaved paths, non-LL fallback, abort/stop IRQs, local and remote modes, and debugfs reads.
