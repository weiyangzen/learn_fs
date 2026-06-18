# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_global.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_global.h` defines ISP2400 input-system global enums and configuration structs for CSI ports, channels, sources, buffering modes, IB memory regions, TPG/PRBS/gpfifo sources, and configuration flags.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `isp2400_input_system_cfg_s`, `sync_generator_cfg_s`, `tpg_cfg_s`, `prbs_cfg_s`, `gpfifo_cfg_s`, `ib_buffer_s`, `csi_cfg_s`, `mipi_lane_cfg_t`, `input_system_source_t`, `input_system_connection_t`, `input_system_multiplex_t`, `input_system_sink_t`; `N_CSI_PORTS`, `N_CHANNELS`, `IB_CAPACITY_IN_WORDS`

Control flow: Higher-level input-system setup accumulates these structs, then commits them into receiver/backend/acquisition/input-buffer hardware programming.

State and persistence behavior: State is hardware register state, accumulated in-memory configuration structs, input-buffer allocations, stream validity flags, and diagnostic snapshots. Nothing is persisted to disk.

Dependencies and integration points: These files depend on CSS receiver, acquisition/capture, input switch, stream2mmio, ibuf controller, isys DMA, CSI RX, pixel generator, device-access, and print/assert support headers.

Risks and edge cases: Configuration flags can express set, blocked, required, and conflict states; bad reconciliation can over-allocate the 384-word input-buffer capacity or route streams incorrectly.

Test signals: Cover all CSI ports, virtual channels, MIPI formats, metadata enablement, online/offline paths, PRBS/TPG sources, register read/write helpers, IRQ status/clear paths, IB capacity accounting, and generation-specific 2400 versus 2401 format behavior.
