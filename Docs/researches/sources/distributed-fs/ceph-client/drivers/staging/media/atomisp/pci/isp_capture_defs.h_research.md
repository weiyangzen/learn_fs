# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp_capture_defs.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp_capture_defs.h` defines the capture-unit register map, command and acknowledgement tokens, packet metadata layout, MIPI data type constants, and capture FSM state IDs.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: No named structs or enums are introduced here.; `_isp_capture_defs_h`, `_ISP_CAPTURE_REG_ALIGN`, `_ISP_CAPTURE_BITS_PER_ELEM`, `_ISP_CAPTURE_BYTES_PER_ELEM`, `_ISP_CAPTURE_BYTES_PER_WORD`, `_ISP_CAPTURE_ELEM_PER_WORD`, `NOF_IRQS`, `CAPT_NOF_REGS`, `CAPT_START_MODE_REG_ID`, `CAPT_START_ADDR_REG_ID`

Control flow: Capture programming writes start/init/stop and memory-region registers, then hardware reports packet received/written, region written, flush, SOP, and stop acknowledgements.

State and persistence behavior: These files provide compile-time hardware contracts only. Runtime state lives in device registers, token FIFOs, memory regions, or generated firmware structures.

Dependencies and integration points: They integrate with input-system configuration, capture/acquisition hardware, MMU register programming, generated ISP code, and CSS firmware ABI assumptions.

Risks and edge cases: Start/stop/freeze/resume/init tokens share low bits and require exact packing; bad memory region sizes or restart addresses can overrun capture buffers.

Test signals: Mechanically verify bitfield widths/indexes, reset values, MIPI data type values, token pack/unpack paths, MMIO register offsets, and build-time consistency against firmware-generated headers.
