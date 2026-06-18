# sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-main.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-main.c -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-main.c

### Purpose
`fsl-edma-main.c` is the platform driver for Freescale/NXP eDMA controllers across Vybrid, Layerscape, i.MX, and S32G variants. It handles device-tree matching, resource mapping, clocks, DMAMUX resources, channel creation, IRQ topology, power domains, OF DMA translation, DMAengine registration, and system suspend/resume.

### Important APIs, Types, And Functions
Probe and lifecycle functions are `fsl_edma_probe()`, `fsl_edma_remove()`, `fsl_edma_init()`, and `fsl_edma_exit()`. IRQ paths include `fsl_edma_tx_handler()`, `fsl_edma_err_handler()`, `fsl_edma_irq_handler()`, `fsl_edma2_tx_handler()`, `fsl_edma3_tx_handler()`, `fsl_edma3_err_handler_per_chan()`, `fsl_edma3_err_handler_shared()`, `fsl_edma3_or_tx_handler()`, and `fsl_edma3_or_err_handler()`. OF translation is done by `fsl_edma_xlate()` and `fsl_edma3_xlate()`. Variant-specific IRQ setup is selected through `struct fsl_edma_drvdata` entries such as `vf610_data`, `ls1028a_data`, `imx7ulp_data`, `imx8qm_data`, `imx8ulp_data`, `imx93_data3`, `imx93_data4`, `imx95_data5`, and `s32g2_data`.

### Control Flow, State, And Persistence
Probe reads `dma-channels`, allocates a flexible engine object, maps the controller, initializes register pointers for non-split layouts, enables block and DMAMUX clocks, reads optional channel masks and endianness, attaches per-channel power domains when needed, creates each unmasked virtual channel, computes channel TCD and mux addresses, clears initial CSR state, initializes IRQ routing through the variant callback, registers DMAengine operations from the common layer, registers the OF DMA controller, and enables round-robin arbitration on older layouts. OF translation assigns source IDs, channel priority, RX/remote/multi-FIFO flags, and DMAMUX routing while avoiding duplicate source IDs. Suspend late disables active channels and marks them suspended; resume early restores channel state, remuxes source IDs, and re-enables arbitration.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on device tree properties, platform IRQ/resource APIs, clocks, runtime PM domains, device links, DMAengine registration, OF DMA controller registration, and common eDMA operations. Integration points include many SoC compatible strings, DMAMUX resources, split and non-split eDMA register layouts, shared or per-channel IRQs, and client DMA specifier formats. Risks include variant flag mismatch, channel-mask bit handling above 32 channels, source-ID uniqueness false positives, missing optional error IRQs, autosuspend and device-link ordering, IRQ registration cleanup, and suspend while clients still have in-flight transfers. Test signals include probe for each compatible, masked-channel configurations, all IRQ topologies, OF xlate argument validation, duplicate srcid rejection, per-channel clocks, power-domain attach/detach, suspend/resume with idle and active channels, and memcpy/slave/cyclic operation through the common layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-main.c -->
