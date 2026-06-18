# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mamoiada_params.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mamoiada_params.h` describes the Mamoiada ISP hardware profile: vector width, memory depths, register-file sizes, feature switches, cache parameters, immediate sizes, FIFO depths, shielding, and streaming port presence.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: No named structs or enums are introduced here.; `RTL_VERSION`, `ISP_BRANCHDELAY`, `ISP_BUS_WIDTH`, `ISP_BUS_ADDR_WIDTH`, `ISP_BUS_BURST_SIZE`, `ISP_SCALAR_WIDTH`, `ISP_SLICE_NELEMS`, `ISP_VEC_NELEMS`, `ISP_VEC_ELEMBITS`, `ISP_VEC_ELEM8BITS`

Control flow: Generated ISP code and host-side build logic use these compile-time constants to size memories, align vectors, and expose capabilities such as IRQ, soft reset, LUT, histogram, VALSU, and streaming ports.

State and persistence behavior: These files provide compile-time hardware contracts only. Runtime state lives in device registers, token FIFOs, memory regions, or generated firmware structures.

Dependencies and integration points: They integrate with input-system configuration, capture/acquisition hardware, MMU register programming, generated ISP code, and CSS firmware ABI assumptions.

Risks and edge cases: This is a hardware contract rather than executable code; any mismatch with firmware or silicon invalidates many derived buffer and parameter sizes.

Test signals: Mechanically verify bitfield widths/indexes, reset values, MIPI data type values, token pack/unpack paths, MMIO register offsets, and build-time consistency against firmware-generated headers.
