# sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-common.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-common.c -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-common.c

### Purpose
`fsl-edma-common.c` contains shared DMAengine operations and transfer-control-descriptor handling for Freescale/NXP eDMA variants. It prepares cyclic, slave scatter-gather, and memcpy transfers, manages TCD pools, handles virtual-channel completion, controls request enable/disable, configures DMAMUX slots, computes residue, and provides common resource cleanup.

### Important APIs, Types, And Functions
Important exported-to-driver functions include `fsl_edma_tx_chan_handler()`, `fsl_edma_disable_request()`, `fsl_edma_chan_mux()`, `fsl_edma_free_desc()`, `fsl_edma_terminate_all()`, `fsl_edma_pause()`, `fsl_edma_resume()`, `fsl_edma_slave_config()`, `fsl_edma_tx_status()`, `fsl_edma_prep_dma_cyclic()`, `fsl_edma_prep_slave_sg()`, `fsl_edma_prep_memcpy()`, `fsl_edma_xfer_desc()`, `fsl_edma_issue_pending()`, `fsl_edma_alloc_chan_resources()`, `fsl_edma_free_chan_resources()`, `fsl_edma_cleanup_vchan()`, and `fsl_edma_setup_regs()`. Core helpers include `fsl_edma_enable_request()`, `fsl_edma3_enable_request()`, `fsl_edma_fill_tcd()`, `fsl_edma_set_tcd_regs()`, `fsl_edma_alloc_desc()`, and `fsl_edma_desc_residue()`.

### Control Flow, State, And Persistence
Prepared transfers allocate a flexible `struct fsl_edma_desc` plus one DMA-pool TCD per segment or period. TCDs are filled in little-endian memory format for hardware scatter-gather, then copied into endian-aware MMIO registers when a descriptor is started. `fsl_edma_issue_pending()` refuses submission while suspended, otherwise starts the next virtual descriptor when no descriptor is active. TX IRQ handling calls `fsl_edma_tx_chan_handler()`, which completes non-cyclic descriptors or invokes cyclic callbacks, then starts the next descriptor. Terminate/pause/resume disable or re-enable hardware requests under the vchan lock. Slave peripheral resources are mapped with `dma_map_resource()` and cached until configuration changes or resources are freed.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on `virt-dma`, DMA pools, DMA mapping, runtime PM, clocks, endian-aware accessors and tracepoints from `fsl-edma-common.h`, and variant flags supplied by `fsl-edma-main.c`. Integration points include DMAMUX programming, eDMA v2/v3/v4 split-register layouts, 32-bit and 64-bit TCD formats, power domains, and DMAengine clients. Risks include TCD endian/layout mistakes, 64-bit address residue reads racing with non-atomic MMIO, minor-loop offset programming for multi-FIFO or port windows, pause/terminate races with IRQ completion, and mismatched `dma_map_resource()` direction naming. Test signals include cyclic audio transfers, SG chains, memcpy with alignment constraints, residue during in-progress transfers, suspend refusal, pause/resume, resource-free unmapping, DMAMUX enable/disable, TCD64 operation, and dynamic tracepoint output for TCD fills.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-common.c -->
