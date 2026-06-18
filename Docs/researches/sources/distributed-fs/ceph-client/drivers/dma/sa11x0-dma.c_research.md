# sources/distributed-fs/ceph-client/drivers/dma/sa11x0-dma.c

Purpose: DMAEngine slave/cyclic driver for SA-11x0 DMA hardware. It maps 16 named virtual peripheral directions onto six physical DMA channels and uses double-buffer hardware registers to stream SG and cyclic transfers.

Important APIs/types/functions: `struct sa11x0_dma_sg`, `struct sa11x0_dma_desc`, `struct sa11x0_dma_chan`, `struct sa11x0_dma_phy`, and `struct sa11x0_dma_dev` model split SG fragments, virtual channels, physical channels, and controller state. DMAEngine hooks include `sa11x0_dma_prep_slave_sg`, `sa11x0_dma_prep_dma_cyclic`, `sa11x0_dma_device_config`, `sa11x0_dma_issue_pending`, `sa11x0_dma_tx_status`, `sa11x0_dma_device_pause`, `sa11x0_dma_device_resume`, and `sa11x0_dma_device_terminate_all`.

Control flow: probe ioremaps the register block, initializes six physical channels and IRQs, clears hardware, registers DMAEngine channels from static peripheral descriptors, and advertises filter-map entries for IR and SSP clients. Prep validates native channel direction, alignment, bus width, burst, and nonzero length, splits large SG/cyclic periods into hardware-sized fragments, and creates virt-dma descriptors. `issue_pending` moves submitted descriptors to issued and queues virtual channels needing a physical channel. A controller tasklet assigns free physical channels to pending virtual channels, starts descriptors, and releases physical channels when no more compatible work remains. IRQs clear DONE/ERROR bits and, under the virtual channel lock, complete fragment A/B events, complete cookies or cyclic callbacks, and load more fragments.

State/persistence: virtual channel state includes assigned physical channel and status. Physical channel state tracks active/load descriptors, fragment indices, saved suspend registers, and register base. Pending virtual channels live on a controller list protected by `d->lock`.

Dependencies/integration: depends on legacy platform resources/IRQs, DMAEngine filter maps, virt-dma, tasklets, and SA-11x0 DDAR/DCSR hardware semantics.

Risks: manual physical-channel multiplexing and double-buffer state are concurrency-sensitive. Residue calculation reads active hardware address and walks split fragments, so it is best-effort during races. System suspend saves buffer register order depending on BIU state and resumes only if descriptors remain. Only 1- or 2-byte widths and bursts 4/8 are accepted.

Test signals: slave SG and cyclic audio-style transfers, all named channel filters, physical-channel contention among more than six virtual channels, pause/resume/terminate, suspend/resume mid-transfer, error IRQ logging, residue before/during/after transfer, and alignment rejection.
