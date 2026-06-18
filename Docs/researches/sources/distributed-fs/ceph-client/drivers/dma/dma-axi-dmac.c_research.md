# sources/distributed-fs/ceph-client/drivers/dma/dma-axi-dmac.c

Purpose: DMAengine driver for Analog Devices AXI-DMAC soft IP. It supports one configured channel with slave SG, peripheral DMA vectors, cyclic/repeated transfers, interleaved 2D transfers, optional hardware scatter-gather, partial-transfer reporting, and hardware capability discovery.

Important APIs/types/functions: `struct axi_dmac` wraps MMIO, clock, IRQ, DMA device, and channel. `struct axi_dmac_chan` stores bus types/widths, direction, alignment/length limits, feature flags, active descriptors, and `virt_dma_chan`. `struct axi_dmac_desc` owns SG hardware descriptors and cyclic/partial state. Key functions include `axi_dmac_start_transfer`, `axi_dmac_transfer_done`, `axi_dmac_interrupt_handler`, `axi_dmac_prep_slave_sg`, `axi_dmac_prep_peripheral_dma_vec`, `axi_dmac_prep_dma_cyclic`, `axi_dmac_prep_interleaved`, `axi_dmac_detect_caps`, and `axi_dmac_probe`.

Control flow: probe maps MMIO, enables clock, reads IP version, obtains interface configuration from registers or legacy DT, initializes one virt channel, detects capabilities by probing registers, validates coherent-DMA support if requested, registers DMAengine and OF DMA controller, then requests IRQ. Prep paths allocate coherent hardware descriptors, validate direction/address/length alignment, fill linear or 2D SG descriptors, and optionally chain cyclic lists. Issue-pending enables the core and SG mode, then starts queued transfers. The IRQ acknowledges pending bits, handles EOT completion and SOT queue-space events, records partial transfer lengths, completes or cycles descriptors, and starts more work.

State and persistence: Active descriptor lists, `next_desc`, submitted/completed counters, hardware descriptor IDs, partial lengths, and MMIO control registers form volatile state. No persistent storage.

Dependencies/integration: DMAengine, `virt-dma`, OF DMA helpers, ADI AXI common version macros, DT bus-type bindings, regmap for debug/register access, clk, IRQ, coherent DMA allocation.

Risks: Capability probing writes to live registers and must occur before traffic. Cyclic termination differs between SG and non-SG hardware; older non-SG cores require a disable/enable hotfix to flush prefetch. Error paths in vector prep must free coherent descriptors consistently. Direction is fixed by IP instantiation.

Test signals: probe across old/new IP versions, SG and non-SG transfers, cyclic callback and `DMA_PREP_LOAD_EOT` behavior, partial-transfer residue, 2D interleaved limits, coherent-DMA DT validation, terminate-all, and IRQ sharing behavior.
