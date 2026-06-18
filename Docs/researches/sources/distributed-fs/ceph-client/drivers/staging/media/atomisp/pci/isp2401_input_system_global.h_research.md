# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2401_input_system_global.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2401_input_system_global.h` defines ISP2401 input-system global data models for stream2mmio, ibuf controller, DMA, CSI RX, metadata, pixel generator, stream configuration, and virtual stream state.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `input_system_channel_s`, `input_system_channel_cfg_s`, `input_system_input_port_s`, `input_system_input_port_cfg_s`, `isp2401_input_system_cfg_s`, `virtual_input_system_stream_s`, `virtual_input_system_stream_cfg_s`, `input_system_source_type_t`, `csi_rx`, `metadata`, `pixelgen`, `csi_rx_cfg`; `N_CSI_PORTS`, `INPUT_SYSTEM_N_STREAM_ID`, `ISP_INPUT_BUF_START_ADDR`, `NUM_OF_INPUT_BUF`, `NUM_OF_LINES_PER_BUF`, `LINES_OF_ISP_INPUT_BUF`, `ISP_INPUT_BUF_STRIDE`

Control flow: Configuration code maps an input port and stream into a CSI/pixelgen source, stream2mmio path, ibuf controller, DMA channel, optional metadata channel, and online/offline stream relation.

State and persistence behavior: State is hardware register state, accumulated in-memory configuration structs, input-buffer allocations, stream validity flags, and diagnostic snapshots. Nothing is persisted to disk.

Dependencies and integration points: These files depend on CSS receiver, acquisition/capture, input switch, stream2mmio, ibuf controller, isys DMA, CSI RX, pixel generator, device-access, and print/assert support headers.

Risks and edge cases: The virtual stream model carries validity, metadata, online, and linked-stream fields; inconsistent combinations can desynchronize main and metadata streams.

Test signals: Cover all CSI ports, virtual channels, MIPI formats, metadata enablement, online/offline paths, PRBS/TPG sources, register read/write helpers, IRQ status/clear paths, IB capacity accounting, and generation-specific 2400 versus 2401 format behavior.
