<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc-ccitt.h -->
# sources/distributed-fs/ceph-client/include/linux/crc-ccitt.h

## Purpose

`crc-ccitt.h` declares the kernel's table-driven CRC-CCITT helper. The source was read as a complete 16-line file.

## Important APIs, Types, and Functions

It exposes `crc_ccitt_table[256]`, `crc_ccitt(u16 crc, const u8 *buffer, size_t len)`, and inline `crc_ccitt_byte(u16 crc, const u8 c)`, which advances the CRC by one byte using `(crc >> 8) ^ table[(crc ^ c) & 0xff]`.

## Control Flow

Callers seed a CRC, process buffers through `crc_ccitt()`, or process single bytes through the inline helper. Incremental callers feed the previous returned CRC back into the next call.

## State and Persistence Behavior

The only shared state is the constant lookup table. No mutable state or persistence is owned.

## Dependencies and Integration Points

It depends on `linux/types.h` and integrates with drivers/protocols that require CCITT-style 16-bit CRCs.

## Risks and Edge Cases

Correctness depends on matching the expected seed, byte order, and final XOR convention of the protocol. The helper does not validate buffer pointers or lengths beyond normal C behavior.

## Test Signals

Signals include known-vector CRC tests, incremental versus one-shot comparisons, zero-length input, and protocol driver checksum validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc-ccitt.h -->
