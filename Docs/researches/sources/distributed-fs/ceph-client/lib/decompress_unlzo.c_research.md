# sources/distributed-fs/ceph-client/lib/decompress_unlzo.c

## Purpose
Wraps LZO decompression for lzop-framed kernel, initramfs, and initrd payloads.

## APIs, Types, and Functions
The linked/preboot decompressor is `unlzo()`, with preboot `__decompress()`. `parse_header()` validates and skips the lzop header. Constants define lzop magic, maximum block size, header flags, and minimum/maximum header lengths.

## Control Flow
`unlzo()` validates that input comes from either a pointer or `fill`, allocates input/output buffers as needed, reads and parses the lzop header, then iterates over blocks. Each block starts with uncompressed size, a zero terminator, compressed size, and checksum fields. The function rejects oversized or inconsistent sizes, fills enough compressed input, copies uncompressed blocks directly when sizes match, otherwise calls `lzo1x_decompress_safe()`, flushes or advances output, updates `posp`, and compacts unused streaming input without relying on `memmove()`.

## State and Persistence
State is per-call: input buffer, output buffer, current lzop cursor, and `posp`. No global state is kept.

## Dependencies and Integration Points
Depends on the Linux LZO API, unaligned big-endian reads, decompressor allocation helpers, and optional static inclusion of the LZO source. It is selected by magic dispatch and supports early environments where standard library helpers may be unavailable.

## Risks and Test Signals
Risks include malformed lzop header parsing, block size validation bugs, ignored checksum fields, short streaming reads, and flush failures. Test signals include lzop-compatible streams, uncompressed-block cases, corrupt size/header cases, streaming input tests, and boot/initramfs tests with LZO compression.
