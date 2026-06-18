<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc64.h -->
# sources/distributed-fs/ceph-client/include/linux/crc64.h

## Purpose

`crc64.h` declares CRC64 helpers for big-endian ECMA-182 and CRC64-NVME. The source was read as a complete 28-line file.

## Important APIs, Types, and Functions

It declares `crc64_be(u64 crc, const void *p, size_t len)` and `crc64_nvme(u64 crc, const void *p, size_t len)`. The NVMe helper includes bitwise inversion at the beginning and end.

## Control Flow

Callers pass a seed or previous CRC and a buffer. `crc64_be()` supports ECMA-182 semantics; `crc64_nvme()` follows NVMe NVM Command Set CRC64 behavior including inversion.

## State and Persistence Behavior

No mutable state is owned by the header. Implementations may use constant tables or architecture acceleration.

## Dependencies and Integration Points

It depends on `linux/types.h` and integrates with storage, NVMe protection, and protocols requiring 64-bit CRCs.

## Risks and Edge Cases

The two helpers have different variant semantics, especially NVMe inversion. Seed values must match the protocol, and incremental use must preserve the correct intermediate value.

## Test Signals

Signals include ECMA-182 and NVMe known vectors, one-shot versus incremental equivalence, zero-length input, and storage metadata validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc64.h -->
