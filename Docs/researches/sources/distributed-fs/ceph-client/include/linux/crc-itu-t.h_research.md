<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc-itu-t.h -->
# sources/distributed-fs/ceph-client/include/linux/crc-itu-t.h

## Purpose

`crc-itu-t.h` declares CRC ITU-T V.41 helpers for a 16-bit `0x1021` polynomial with initial value 0. The source was read as a complete 26-line file.

## Important APIs, Types, and Functions

It exposes `crc_itu_t_table[256]`, `crc_itu_t(u16 crc, const u8 *buffer, size_t len)`, and inline `crc_itu_t_byte(u16 crc, const u8 data)`, which advances the CRC with `(crc << 8) ^ table[((crc >> 8) ^ data) & 0xff]`.

## Control Flow

Callers compute a full-buffer CRC or update one byte at a time, supplying either the initial seed or previous CRC for incremental operation.

## State and Persistence Behavior

Only the constant lookup table is shared. No mutable state is maintained.

## Dependencies and Integration Points

It depends on `linux/types.h` and integrates with kernel protocol implementations that require ITU-T V.41 CRC semantics.

## Risks and Edge Cases

CRC variants are easy to confuse: seed, bit direction, polynomial representation, and final XOR must match the protocol. Byte helper users must preserve the returned CRC between chunks.

## Test Signals

Signals include protocol known vectors, byte-at-a-time versus buffer equivalence, zero-length input, and cross-checks against documented ITU-T V.41 examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc-itu-t.h -->
