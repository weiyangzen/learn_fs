# sources/distributed-fs/ceph-client/lib/crc/crc-itu-t.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/crc-itu-t.c` implements table-driven CRC ITU-T V.41 using polynomial 0x1021.

## Important APIs, Types, and Functions

The exported symbols are `crc_itu_t_table[256]` and `crc_itu_t(u16 crc, const u8 *buffer, size_t len)`.

## Control Flow

The function loops over bytes and updates the running CRC through `crc_itu_t_byte()`, which uses the exported table.

## State and Persistence Behavior

The lookup table is read-only data. The running CRC is provided and returned by value.

## Dependencies and Integration Points

Dependencies include `linux/crc-itu-t.h`, module metadata, and export support. Kernel users select `CRC_ITU_T` when they need this V.41 polynomial.

## Risks and Edge Cases

This implementation is a specific polynomial/orientation variant; callers must not substitute it for other 16-bit CRCs. Seed/finalization conventions remain caller-owned.

## Test Signals

Signals include ITU-T known vectors, zero-length return of the input CRC, chunked-update equivalence, and exported table visibility.

## Read Coverage

Source read size: 68 lines, 2829 bytes.
