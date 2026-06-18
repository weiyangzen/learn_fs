# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_public.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_public.h` declares the ISP2400 input-system public API for receiver compression/port/IRQ control, raw register access, configuration reset/commit, and user-level CSI/FIFO/SRAM/XMEM/PRBS/GPFIFO channel configuration.

Important APIs, types, and functions: Important local symbols: `receiver_set_compression`, `receiver_port_enable`, `is_receiver_port_enabled`, `receiver_irq_enable`, `receiver_irq_clear` Types and constants: No named structs or enums are introduced here.; `__INPUT_SYSTEM_2400_PUBLIC_H_INCLUDED__`

Control flow: Callers build a session by invoking channel-configuration functions, then commit the accumulated configuration to hardware; register helpers expose low-level diagnostics and control.

State and persistence behavior: State is hardware register state, accumulated in-memory configuration structs, input-buffer allocations, stream validity flags, and diagnostic snapshots. Nothing is persisted to disk.

Dependencies and integration points: These files depend on CSS receiver, acquisition/capture, input switch, stream2mmio, ibuf controller, isys DMA, CSI RX, pixel generator, device-access, and print/assert support headers.

Risks and edge cases: The API comments acknowledge minimal checking in user functions, so callers must supply coherent channel IDs, port modes, region sizes, target configs, and frame counts.

Test signals: Cover all CSI ports, virtual channels, MIPI formats, metadata enablement, online/offline paths, PRBS/TPG sources, register read/write helpers, IRQ status/clear paths, IB capacity accounting, and generation-specific 2400 versus 2401 format behavior.
