<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_dsd.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_dsd.h

## Purpose

`qla_dsd.h` defines the qla2xxx data segment descriptor helpers used when building firmware IOCBs from Linux scatter-gather lists. It provides the two wire formats the firmware consumes: 32-bit descriptors and 64-bit descriptors.

## Important APIs, Types, And Functions

- `struct dsd32` is an 8-byte descriptor containing little-endian 32-bit DMA address and little-endian 32-bit length.
- `append_dsd32()` writes `sg_dma_address()` and `sg_dma_len()` into the current descriptor with unaligned little-endian stores, then advances the descriptor pointer.
- `struct dsd64` is a packed 12-byte descriptor containing little-endian 64-bit DMA address and little-endian 32-bit length.
- `append_dsd64()` performs the equivalent operation for 64-bit DMA addresses.

## Control Flow

The header has no standalone runtime flow. IOCB builders include it, allocate or point at an array of DSD slots in a request or continuation IOCB, then repeatedly call `append_dsd32()` or `append_dsd64()` while walking a mapped scatterlist. The caller owns DMA mapping, descriptor capacity, IOCB continuation allocation, and final doorbell submission.

## State And Persistence Behavior

There is no global or persistent software state. The helpers mutate only the caller-provided descriptor pointer and the memory backing the firmware request. The written descriptor contents persist in the request ring or DMA buffer until firmware consumes them or the driver reuses the buffer.

## Dependencies And Integration Points

The header includes `<linux/unaligned.h>` and depends on Linux scatterlist DMA accessors. `qla_fw.h` includes this header and embeds `struct dsd64` in many firmware request definitions, including SCSI command, CT, ELS, verify-chip, and access-chip IOCBs. The helpers are part of the low-level contract between qla IOCB builders and firmware.

## Risks And Edge Cases

- `append_dsd32()` truncates `sg_dma_address()` to 32 bits by design. Callers must use it only for hardware/IOCB paths that support 32-bit DMA addresses.
- The helpers do not validate descriptor array capacity. IOCB builders must correctly calculate continuation entries before appending.
- The helpers assume `sg_dma_address()`/`sg_dma_len()` are valid, so callers must map the scatterlist first and unwind DMA mappings on later failures.
- `struct dsd64` is packed because the firmware layout is 12 bytes; removing packing or using normal structure assignment could change layout or alignment assumptions.

## Test Signals

Build-time checks should cover all qla IOCB builders that include `qla_fw.h`. Targeted unit or instrumentation checks can validate `sizeof(struct dsd32) == 8`, `sizeof(struct dsd64) == 12`, descriptor pointer advancement, little-endian encoding, and correct behavior with unaligned descriptor addresses. Runtime I/O tests with multi-segment scatterlists and DMA addresses above 4 GiB exercise the 64-bit path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_dsd.h -->
