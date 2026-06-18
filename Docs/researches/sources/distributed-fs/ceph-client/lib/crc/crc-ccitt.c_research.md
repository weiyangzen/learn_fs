# sources/distributed-fs/ceph-client/lib/crc/crc-ccitt.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/crc-ccitt.c` implements the table-driven CRC-CCITT variant used by kernel users of `<linux/crc-ccitt.h>`.

## Important APIs, Types, and Functions

The exported symbols are `crc_ccitt_table[256]` and `crc_ccitt(u16 crc, u8 const *buffer, size_t len)`.

## Control Flow

The function iterates over the buffer and updates the running CRC with `crc_ccitt_byte()`, which indexes the exported table. The table represents the reflected 0x8408 form of the CRC-CCITT polynomial.

## State and Persistence Behavior

The table is read-only module/kernel data. CRC state is caller-supplied and returned; no global mutable state exists.

## Dependencies and Integration Points

Dependencies include `linux/crc-ccitt.h`, module metadata, and export support. Drivers and protocols use the exported function or table for incremental checksums.

## Risks and Edge Cases

Variant naming is easy to confuse with ITU-T/X.25 forms; callers must supply the correct seed and final xor convention. The function assumes `buffer` is valid for `len`.

## Test Signals

Signals include known CRC-CCITT vectors, incremental update equivalence, zero-length behavior, exported table access, and module build/load coverage.

## Read Coverage

Source read size: 66 lines, 2984 bytes.
