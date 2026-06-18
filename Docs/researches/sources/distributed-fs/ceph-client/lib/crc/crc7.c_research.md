# sources/distributed-fs/ceph-client/lib/crc/crc7.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/crc7.c` implements big-endian CRC7, commonly used by MMC/SD style protocols.

## Important APIs, Types, and Functions

The exported API is `crc7_be(u8 crc, const u8 *buffer, size_t len)`. The file owns `crc7_be_syndrome_table[256]`.

## Control Flow

The function iterates through the input bytes and updates the left-aligned CRC with `crc7_be_syndrome_table[crc ^ *buffer++]`.

## State and Persistence Behavior

The table is read-only static data. CRC state is caller-supplied and returned in left-aligned byte form with the low bit unused.

## Dependencies and Integration Points

Dependencies include `linux/crc7.h`, module metadata, and export support. Protocol code selects `CRC7` to use this helper.

## Risks and Edge Cases

The CRC is left-aligned in the returned byte; callers expecting right-aligned CRC7 must shift appropriately. Variant seed/final bit handling remains caller-owned.

## Test Signals

Signals include known CRC7 command vectors, zero-length return, chunked update equivalence, left-alignment checks, and module export coverage.

## Read Coverage

Source read size: 73 lines, 2566 bytes.
