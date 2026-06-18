# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2401_input_system_local.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2401_input_system_local.h` defines ISP2401 MIPI packet-format IDs and compressor context sizing.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `mipi_format_2401_t`; `__INPUT_SYSTEM_2401_LOCAL_H_INCLUDED__`, `N_MIPI_FORMAT_CUSTOM`, `N_MIPI_COMPRESSOR_CONTEXT`

Control flow: CSI RX backend configuration uses these numeric MIPI data type values when programming LUT entries for image and metadata packets.

State and persistence behavior: State is hardware register state, accumulated in-memory configuration structs, input-buffer allocations, stream validity flags, and diagnostic snapshots. Nothing is persisted to disk.

Dependencies and integration points: These files depend on CSS receiver, acquisition/capture, input switch, stream2mmio, ibuf controller, isys DMA, CSI RX, pixel generator, device-access, and print/assert support headers.

Risks and edge cases: The 2401 format list excludes RAW16/RAW18 support present in 2400, so cross-generation reuse can accept unsupported formats incorrectly.

Test signals: Cover all CSI ports, virtual channels, MIPI formats, metadata enablement, online/offline paths, PRBS/TPG sources, register read/write helpers, IRQ status/clear paths, IB capacity accounting, and generation-specific 2400 versus 2401 format behavior.
