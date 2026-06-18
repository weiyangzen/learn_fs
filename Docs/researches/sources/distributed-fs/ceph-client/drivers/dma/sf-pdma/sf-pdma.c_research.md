# sources/distributed-fs/ceph-client/drivers/dma/sf-pdma/sf-pdma.c

Purpose: SiFive FU540/Microchip MPFS Platform DMAEngine memcpy driver. It exposes memory-to-memory DMA channels, programs per-channel PDMA registers, handles done/error IRQ pairs, and integrates with OF DMA by channel ID.

Important APIs/types/functions: `struct sf_pdma`, `struct sf_pdma_chan`, `struct sf_pdma_desc`, and `struct pdma_regs` are defined in `sf-pdma.h`. DMAEngine hooks are `sf_pdma_alloc_chan_resources`, `sf_pdma_free_chan_resources`, `sf_pdma_tx_status`, `sf_pdma_prep_dma_memcpy`, `sf_pdma_slave_config`, `sf_pdma_terminate_all`, and `sf_pdma_issue_pending`. IRQ/tasklet flow uses `sf_pdma_done_isr`, `sf_pdma_err_isr`, `sf_pdma_donebh_tasklet`, and `sf_pdma_errbh_tasklet`.

Control flow: probe reads `dma-channels` or defaults to four, applies platform quirks to transfer type, maps registers, requests two IRQs per channel, initializes channel register pointers and tasklets, sets DMAEngine memcpy capabilities, sets a 64-bit DMA mask when possible, registers DMAEngine, and registers OF DMA. Prep allocates one descriptor, validates nonzero len/src/dest, fills transfer type/size/src/dst, and prepares it with virt-dma. Issue pending starts the first issued descriptor if no descriptor is active. Transfer programming writes type, size, destination, source, marks status in progress, and sets claim/run/interrupt bits. Done IRQ clears done status and either schedules completion if residue is zero or adjusts descriptor addresses/size and restarts for remaining bytes. Error IRQ clears error status and schedules retry/failure tasklet.

State/persistence: each channel keeps one active `desc`, current status, retry/error flags, register pointers, IRQ numbers, and a copied slave config. Descriptors are dynamically allocated and freed by virt-dma. No persistent storage.

Dependencies/integration: depends on OF DMA, platform IRQ resources, MMIO, virt-dma, DMAEngine, and optional match-data quirk `PDMA_QUIRK_NO_STRICT_ORDERING` for MPFS.

Risks: error tasklet invokes callback directly on final failure without completing/freeing the virt-dma descriptor in the same path, so changes should inspect error lifecycle carefully. `sf_pdma_desc_residue` scans `desc_submitted` and may not report active descriptors as expected. Done path mutates active descriptor for partial residue. `descriptor_reuse = true` should be checked against descriptor freeing semantics.

Test signals: DMA memcpy selftests across all channels, partial completion/residue restart, injected error IRQ with retry exhaustion, OF DMA channel selection, MPFS strict-ordering quirk, terminate/free while active, and module remove after queued work.
