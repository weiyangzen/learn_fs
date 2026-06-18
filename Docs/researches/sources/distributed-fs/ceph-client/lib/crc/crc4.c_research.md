# sources/distributed-fs/ceph-client/lib/crc/crc4.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/crc4.c` computes a 4-bit CRC over a caller-supplied integer value using polynomial `0b10111`.

## Important APIs, Types, and Functions

The exported GPL API is `crc4(uint8_t c, uint64_t x, int bits)`. The file owns a 16-entry nibble table `crc4_tab`.

## Control Flow

The function masks bits above the requested width, rounds the bit count up to a nibble boundary, then processes four-bit nibbles from most significant to least significant by xoring the current CRC with the nibble and indexing `crc4_tab`.

## State and Persistence Behavior

The nibble table is read-only. CRC state is carried in the input/output byte.

## Dependencies and Integration Points

Dependencies include `linux/crc4.h`, module metadata, and export support. Callers use it for compact hardware/protocol fields rather than byte buffers.

## Risks and Edge Cases

`(1ull << bits)` is undefined for `bits >= 64`, so callers must constrain bit counts. Left-aligned interpretation must match protocol expectations. The returned CRC is only four bits wide but stored in a byte.

## Test Signals

Signals include known polynomial vectors, bit widths not divisible by four, zero bits, maximum safe bit width, initial CRC variation, and caller validation for 64-bit widths.

## Read Coverage

Source read size: 45 lines, 1029 bytes.
