# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2401_input_system_private.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2401_input_system_private.h` implements ISP2401 private inline diagnostics for the ibuf controller, including register load/store, per-process state capture, full controller state capture, and formatted dump output.

Important APIs, types, and functions: Important local symbols: `ibuf_ctrl_reg_load`, `ibuf_ctrl_reg_store`, `ibuf_ctrl_get_proc_state`, `ibuf_ctrl_get_state`, `ibuf_ctrl_dump_state` Types and constants: No named structs or enums are introduced here.; `__INPUT_SYSTEM_2401_PRIVATE_H_INCLUDED__`

Control flow: `ibuf_ctrl_get_proc_state()` reads every process register bank, `ibuf_ctrl_get_state()` loops over processes, and `ibuf_ctrl_dump_state()` prints the snapshot.

State and persistence behavior: State is hardware register state, accumulated in-memory configuration structs, input-buffer allocations, stream validity flags, and diagnostic snapshots. Nothing is persisted to disk.

Dependencies and integration points: These files depend on CSS receiver, acquisition/capture, input switch, stream2mmio, ibuf controller, isys DMA, CSI RX, pixel generator, device-access, and print/assert support headers.

Risks and edge cases: This diagnostic code trusts process counts and register definitions from platform headers; stale definitions make dumps misleading.

Test signals: Cover all CSI ports, virtual channels, MIPI formats, metadata enablement, online/offline paths, PRBS/TPG sources, register read/write helpers, IRQ status/clear paths, IB capacity accounting, and generation-specific 2400 versus 2401 format behavior.
