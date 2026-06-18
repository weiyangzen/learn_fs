## sources/distributed-fs/ceph-client/drivers/dma/dw-axi-dmac/dw-axi-dmac.h

Purpose: Private definitions for the DesignWare AXI DMAC platform driver, including hardware config structures, channel/descriptor types, LLI layout, register offsets, and bit definitions.

Important APIs/types/functions: defines `struct dw_axi_dma_hcfg`, `struct axi_dma_chip`, `struct dw_axi_dma`, `struct axi_dma_chan`, `struct axi_dma_desc`, `struct axi_dma_hw_desc`, `struct axi_dma_lli`, and `struct axi_dma_chan_config`. Inline helpers convert `dma_chan`/`virt_dma_chan`/`virt_dma_desc` to AXI driver types. Enums define AXI burst lengths, transfer widths, multiblock modes, flow-control modes, handshake selection, and interrupt bits.

Control flow: no executable flow beyond type conversion helpers. The platform source uses these offsets and masks to program common registers, channel registers, APB handshake controls, interrupt masks, and LLIs.

State and persistence: documents the in-memory and hardware-backed state shape. Persistent behavior is limited to hardware register/descriptor semantics while the driver is loaded.

Dependencies and integration: includes Linux DMAengine, device, clock, and `virt-dma` headers. The LLI layout is packed to match hardware fetch format, so structure field order is an ABI with the controller.

Risks and test signals: incorrect bit definitions can corrupt transfers or interrupt handling across all platform code. Test signals are successful descriptor fetches, correct IRQ decoding, compatible behavior on <=8 and >=16 channel register maps, and validation across 32/64-bit register accesses.
