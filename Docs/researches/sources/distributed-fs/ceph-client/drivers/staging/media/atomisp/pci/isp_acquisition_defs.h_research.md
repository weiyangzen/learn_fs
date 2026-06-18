# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp_acquisition_defs.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp_acquisition_defs.h` defines the acquisition-unit register map, reset values, token fields, command/ack token IDs, MIPI packet metadata fields, and packet data type constants.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: No named structs or enums are introduced here.; `_isp_acquisition_defs_h`, `_ISP_ACQUISITION_REG_ALIGN`, `_ISP_ACQUISITION_BYTES_PER_ELEM`, `NOF_ACQ_IRQS`, `MEM2STREAM_FSM_STATE_BITS`, `ACQ_SYNCHRONIZER_FSM_STATE_BITS`, `NOF_ACQ_REGS`, `ACQ_START_ADDR_REG_ID`, `ACQ_MEM_REGION_SIZE_REG_ID`, `ACQ_NUM_MEM_REGIONS_REG_ID`

Control flow: The acquisition unit reads memory regions into a stream and reports packet/region acknowledgements using the encoded token layout documented here.

State and persistence behavior: These files provide compile-time hardware contracts only. Runtime state lives in device registers, token FIFOs, memory regions, or generated firmware structures.

Dependencies and integration points: They integrate with input-system configuration, capture/acquisition hardware, MMU register programming, generated ISP code, and CSS firmware ABI assumptions.

Risks and edge cases: Bitfield indexes for packet length, data type, channel, and memory-region ID overlap by token type; using the wrong token interpretation corrupts control flow.

Test signals: Mechanically verify bitfield widths/indexes, reset values, MIPI data type values, token pack/unpack paths, MMIO register offsets, and build-time consistency against firmware-generated headers.
