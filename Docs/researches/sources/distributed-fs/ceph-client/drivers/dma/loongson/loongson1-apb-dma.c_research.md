
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/loongson/loongson1-apb-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/loongson/loongson1-apb-dma.c

Purpose: implements the Loongson-1 APB DMAEngine driver for up to three APB DMA channels used by peripherals such as NAND and audio. It supports slave scatter-gather, cyclic transfers, pause/resume, termination, residue reporting, and OF channel translation by channel ID.

Important APIs and control flow: `ls1x_dma_probe()` counts IRQs to determine channels, allocates the controller with a flexible channel array, fills DMAEngine capabilities, initializes each channel in `ls1x_dma_chan_probe()`, registers DMAEngine, and registers `of_dma_xlate_by_chan_id`. `ls1x_dma_alloc_chan_resources()` requests a per-channel IRQ, creates an LLI DMA pool, and allocates a coherent query descriptor. `ls1x_dma_prep_lli()` builds hardware LLI lists from scatterlists, chooses RAM-to-device or device-to-RAM command bits, checks copy alignment, links entries, and loops the list for cyclic transfers. `ls1x_dma_issue_pending()` starts the first issued LLI; `ls1x_dma_irq_handler()` completes or cyclic-callbacks the active virt-dma descriptor. Pause/resume query the current LLI, stop hardware, then restart from the saved physical address. `ls1x_dma_tx_status()` queries current LLI state and sums remaining descriptor lengths for residue.

State and persistence behavior: each channel owns an IRQ, register base, LLI pool, coherent current-LLI query buffer, source/destination slave config, bus width, cyclic flag, and current LLI pointer. Descriptors own lists of DMA-pool LLIs freed by virt-dma cleanup. Hardware state is driven through a shared control register with channel ID bits.

Dependencies and integration points: depends on platform resources, per-channel named IRQs `ch0`.., DMAEngine/virt-dma, OF DMA, DMA pools, and the compatible `loongson,ls1b-apbdma`. Clients pass peripheral addresses and bus widths through `dma_slave_config`.

Risks and test signals: risks include `ls1x_dma_prep_dma_cyclic()` leaking `desc` if scatterlist allocation fails, freeing `curr_lli` without checking allocation state, `is_cyclic` not obviously cleared for non-cyclic descriptors, 32-bit address truncation in LLI fields, residue list search assumptions, and shared control register operations across channels. Test signals include per-channel IRQ acquisition, SG and cyclic audio/NAND transfers, pause/resume from queried LLI, correct residue after partial transfer, rejection of unaligned buffers and unsupported directions, and clean removal/freeing of LLI pools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/loongson/loongson1-apb-dma.c -->
