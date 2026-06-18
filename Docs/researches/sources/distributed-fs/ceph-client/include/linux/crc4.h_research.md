<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc4.h -->
# sources/distributed-fs/ceph-client/include/linux/crc4.h

## Purpose

`crc4.h` declares a small CRC-4 helper for bit-length bounded inputs. The source was read as a complete 9-line file.

## Important APIs, Types, and Functions

It declares `uint8_t crc4(uint8_t c, uint64_t x, int bits)`.

## Control Flow

Callers pass a current CRC nibble, input bits packed into a 64-bit value, and the number of bits to process. The implementation returns the updated 4-bit CRC in an 8-bit container.

## State and Persistence Behavior

No state is owned.

## Dependencies and Integration Points

It depends on `linux/types.h` and integrates with compact hardware/protocol fields using CRC-4 checks.

## Risks and Edge Cases

The `bits` argument must match the meaningful bits in `x`; excessive or negative values would be implementation-sensitive. Callers must mask or interpret only the low CRC bits as required by their protocol.

## Test Signals

Signals include known-vector CRC-4 tests, boundary tests for 0, 1, and maximum expected bit counts, and protocol field validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc4.h -->
