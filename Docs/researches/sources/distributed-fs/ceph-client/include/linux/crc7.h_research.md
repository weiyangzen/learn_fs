<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc7.h -->
# sources/distributed-fs/ceph-client/include/linux/crc7.h

## Purpose

`crc7.h` declares a big-endian CRC-7 helper. The source was read as a complete 8-line file.

## Important APIs, Types, and Functions

It declares `u8 crc7_be(u8 crc, const u8 *buffer, size_t len)`.

## Control Flow

Callers seed the CRC, process a buffer, and receive the updated CRC-7 in an 8-bit container.

## State and Persistence Behavior

No state is owned by the header.

## Dependencies and Integration Points

It depends on `linux/types.h` and integrates with protocols such as MMC/SD-style command CRC checks that use CRC-7 variants.

## Risks and Edge Cases

Callers must match the protocol's seed and final bit placement. Only the relevant seven bits should be interpreted.

## Test Signals

Signals include known command-vector tests, incremental equivalence, zero-length input, and protocol frame validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc7.h -->
