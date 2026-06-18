# sources/distributed-fs/ceph-client/lib/crc/crc16.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/crc16.c` implements a table-driven CRC-16 using polynomial 0x8005.

## Important APIs, Types, and Functions

The exported API is `crc16(u16 crc, const u8 *p, size_t len)`. The file owns a static `crc16_table[256]`.

## Control Flow

The function iterates through each byte, indexes the table with `(crc & 0xff) ^ *p`, shifts the CRC right by 8, xors the table value, and returns the final CRC.

## State and Persistence Behavior

The table is read-only static data. CRC state is caller-provided and returned by value.

## Dependencies and Integration Points

Dependencies include `linux/crc16.h`, module metadata, and export support. Kernel modules select `CRC16` to use this helper.

## Risks and Edge Cases

CRC16 variants differ by polynomial reflection, seed, and final xor; callers must use the matching convention. The buffer pointer must be valid for `len`.

## Test Signals

Signals include known CRC16 vectors, zero-length behavior, incremental equivalence, and module export coverage.

## Read Coverage

Source read size: 65 lines, 2768 bytes.
