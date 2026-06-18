# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_private.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_private.h` implements inline register load/store helpers for ISP2400 input-system, receiver, receiver-port, and subsystem MMIO windows.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: No named structs or enums are introduced here.; `__INPUT_SYSTEM_2400_PRIVATE_H_INCLUDED__`

Control flow: Each helper asserts ID and base validity, computes base plus optional port/subsystem offset plus register stride, and calls `ia_css_device_load_uint32()` or `ia_css_device_store_uint32()`.

State and persistence behavior: State is hardware register state, accumulated in-memory configuration structs, input-buffer allocations, stream validity flags, and diagnostic snapshots. Nothing is persisted to disk.

Dependencies and integration points: These files depend on CSS receiver, acquisition/capture, input switch, stream2mmio, ibuf controller, isys DMA, CSI RX, pixel generator, device-access, and print/assert support headers.

Risks and edge cases: Assertions may disappear in production builds, leaving invalid IDs or `-1` bases to produce bad MMIO addresses.

Test signals: Cover all CSI ports, virtual channels, MIPI formats, metadata enablement, online/offline paths, PRBS/TPG sources, register read/write helpers, IRQ status/clear paths, IB capacity accounting, and generation-specific 2400 versus 2401 format behavior.
