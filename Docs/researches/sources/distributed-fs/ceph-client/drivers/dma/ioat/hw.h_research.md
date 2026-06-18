
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/hw.h -->
# sources/distributed-fs/ceph-client/drivers/dma/ioat/hw.h

Purpose: declares IOAT hardware-facing constants and descriptor structures: supported Intel PCI device IDs, IOAT version values, fixed descriptor size, operation opcodes, and packed descriptor layouts for copy, XOR, PQ, PQ update, raw, and super-extended descriptors.

Important APIs and control flow: the main structures are `ioat_dma_descriptor`, `ioat_xor_descriptor`, `ioat_xor_ext_descriptor`, `ioat_pq_descriptor`, `ioat_pq_ext_descriptor`, `ioat_pq_update_descriptor`, and `ioat_sed_raw_descriptor`. Bitfield unions expose control bits such as interrupt enable, snoop controls, completion write, fence, null descriptor, source count, PQ disable flags, writeback-error status, and the operation opcode. PQ16 helper structures define the two 64-byte SED halves used for 9-16 source RAID operations.

State and persistence behavior: hardware descriptor state persists in DMA-coherent memory allocated by the runtime driver and consumed by the IOAT engine. The file itself has no mutable software state, but its layout is a binary ABI with hardware and must remain 64-byte aligned/compatible with `IOAT_DESC_SZ` and `SED_SIZE`.

Dependencies and integration points: included by all IOAT source files and paired with `registers.h` for MMIO access. `prep.c` fills these descriptors, `dma.c` interprets `op`, extension requirements, and writeback error status during cleanup, and `init.c` uses PCI IDs and versions to select capabilities and quirks.

Risks and test signals: risks include implementation-defined C bitfield layout assumptions, endian sensitivity of descriptor control fields, stale or missing PCI IDs preventing probe, operation-code mismatches, and descriptor-size regressions corrupting ring linking. Test signals include `sizeof`/alignment sanity for descriptor formats, successful memcpy/XOR/PQ/PQ16 self-tests on capable hardware, correct interpretation of DWBES validation bits, and no hardware descriptor errors from alignment or next-pointer encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/hw.h -->
