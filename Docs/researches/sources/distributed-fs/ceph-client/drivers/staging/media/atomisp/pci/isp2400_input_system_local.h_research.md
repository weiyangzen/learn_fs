# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_local.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_local.h` maps ISP2400 input-system register aliases, offsets, MIPI formats, IRQ-info bits, receiver port offsets, subsystem offsets, and complete channel/session configuration structs.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `target_cfg2400_s`, `channel_cfg_s`, `input_system_cfg2400_s`, `mipi_format_2400_t`, `rx_irq_info_t`; `__INPUT_SYSTEM_2400_LOCAL_H_INCLUDED__`, `_HRT_CSS_RECEIVER_DEVICE_READY_REG_IDX`, `_HRT_CSS_RECEIVER_IRQ_STATUS_REG_IDX`, `_HRT_CSS_RECEIVER_IRQ_ENABLE_REG_IDX`, `_HRT_CSS_RECEIVER_TIMEOUT_COUNT_REG_IDX`, `_HRT_CSS_RECEIVER_INIT_COUNT_REG_IDX`, `_HRT_CSS_RECEIVER_RAW16_18_DATAID_REG_IDX`, `_HRT_CSS_RECEIVER_SYNC_COUNT_REG_IDX`, `_HRT_CSS_RECEIVER_RX_COUNT_REG_IDX`, `_HRT_CSS_RECEIVER_FS_TO_LS_DELAY_REG_IDX`

Control flow: Implementation code uses these aliases to program receiver ports/backends, input switch, target ISP/SP/stream2mem blocks, and multicast/multiplexer routing.

State and persistence behavior: State is hardware register state, accumulated in-memory configuration structs, input-buffer allocations, stream validity flags, and diagnostic snapshots. Nothing is persisted to disk.

Dependencies and integration points: These files depend on CSS receiver, acquisition/capture, input switch, stream2mmio, ibuf controller, isys DMA, CSI RX, pixel generator, device-access, and print/assert support headers.

Risks and edge cases: Many macros alias hardware register indexes; a wrong offset or generation mismatch writes a valid value to the wrong register.

Test signals: Cover all CSI ports, virtual channels, MIPI formats, metadata enablement, online/offline paths, PRBS/TPG sources, register read/write helpers, IRQ status/clear paths, IB capacity accounting, and generation-specific 2400 versus 2401 format behavior.
