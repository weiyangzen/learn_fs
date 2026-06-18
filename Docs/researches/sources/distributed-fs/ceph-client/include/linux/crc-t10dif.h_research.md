<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc-t10dif.h -->
# sources/distributed-fs/ceph-client/include/linux/crc-t10dif.h

## Purpose

`crc-t10dif.h` declares the T10 DIF CRC helper used for storage data integrity fields. The source was read as a complete 14-line file.

## Important APIs, Types, and Functions

It declares `crc_t10dif_update(u16 crc, const u8 *p, size_t len)` and inline `crc_t10dif(const u8 *p, size_t len)`, which computes from seed 0 by calling the update helper.

## Control Flow

Storage code can compute a one-shot T10 DIF CRC with `crc_t10dif()` or continue an existing CRC with `crc_t10dif_update()`.

## State and Persistence Behavior

The header owns no state. Any table or optimized state lives in the implementation.

## Dependencies and Integration Points

It depends on `linux/types.h` and integrates with block/SCSI/NVMe integrity paths and protection information code.

## Risks and Edge Cases

Seed choice must match the storage protocol. Incremental boundaries must preserve the intermediate CRC exactly. Hardware-offload paths should match this software helper.

## Test Signals

Signals include T10 DIF known vectors, block integrity metadata validation, hardware/software CRC equivalence, incremental chunking tests, and zero-length buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc-t10dif.h -->
