# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwxgmac2_dma.c

Purpose: Implements the XGMAC2 DMA callback table for reset, AXI/system-bus configuration, channel initialization, MTL FIFO thresholds, interrupt handling, feature discovery, ring pointer setup, TSO, SPH, and TBS.

Important APIs and flow: `dwxgmac210_dma_ops` exports all DMA callbacks. Initialization programs system bus mode, PBL settings, channel descriptor base addresses, default DMA interrupt masks, RX/TX queue modes, FIFO sizes, flow-control thresholds, and static queue-to-TC maps. Interrupt handling reads channel status and enable masks, maps abnormal/normal bits to stmmac action flags, updates per-CPU IRQ counters, and clears enabled pending bits.

Control flow and state: DMA state is stored in hardware registers and `priv->dma_cap`. `get_hw_feature()` decodes MAC feature registers into capabilities for checksum offload, EEE, timestamping, RSS, TSO, SPH, queue/channel counts, FIFO sizes, EST, FPE, safety, address width, and parser resources. Start/stop TX also toggles MAC TX enable; start RX enables MAC RX, while stop RX only stops the DMA channel.

Dependencies and integration: Uses `stmmac_dma_cfg`, platform AXI data, `stmmac_pcpu_stats`, and XGMAC register definitions. It is selected by `hwif.c` for XGMAC and XLGMAC entries and invoked through `hwif.h` wrappers by open, reinit, interrupt, ethtool, and queue-control paths.

Risks and test signals: Feature decoding drives many upper-layer decisions, so bit shifts and generation-specific rules need coverage. Test reset timeout, 32/40/48-bit addressing, channel counts, RX/TX interrupt masking by direction, FIFO threshold modes, RIWT watchdog, TSO/SPH/TBS enablement, queue AVB/DCB behavior, and fatal bus error recovery.
