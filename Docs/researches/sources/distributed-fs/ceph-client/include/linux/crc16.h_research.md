<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc16.h -->
# sources/distributed-fs/ceph-client/include/linux/crc16.h

## Purpose

`crc16.h` declares the standard CRC-16 helper using polynomial `0x8005` and initial value 0. The source was read as a complete 21-line file.

## Important APIs, Types, and Functions

It declares `u16 crc16(u16 crc, const u8 *p, size_t len)`.

## Control Flow

Callers pass a seed or previous CRC and a buffer. The implementation returns the updated CRC, supporting one-shot and incremental use.

## State and Persistence Behavior

No state is stored by the header. Implementation lookup tables, if any, are shared read-only.

## Dependencies and Integration Points

It depends on `linux/types.h` and integrates with drivers and protocols requiring this CRC-16 variant.

## Risks and Edge Cases

Protocols often differ in bit order, initial value, and final inversion; using this helper for a different CRC-16 variant will silently produce wrong checksums.

## Test Signals

Signals include known-vector checks, incremental equivalence tests, zero-length input, and protocol-level checksum validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc16.h -->
