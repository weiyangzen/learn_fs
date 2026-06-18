# sources/compression/zlib/examples/gznorm.c

## Purpose
Normalizes a gzip stream from stdin to stdout into a single gzip member with a canonical header. It removes original names, timestamps, comments, extra fields, and per-member headers/trailers while preserving compressed deflate blocks without recompressing. It also makes repeated normalization idempotent by excising an existing final empty fixed block when present.

## APIs, Types, And Functions
Uses public zlib APIs `inflateInit2(15 + 16)`, `inflate(..., Z_BLOCK)`, `inflateReset()`, `inflateEnd()`, and `crc32_combine()`. `aprintf()` allocates formatted error strings, `BYE` centralizes cleanup/error return, and `gzip_normalize()` performs all transformation. `main()` sets binary mode where needed and calls `gzip_normalize(stdin, stdout, &err)`.

## Control Flow
`gzip_normalize()` writes a fixed ten-byte gzip header, then drives `inflate()` in `Z_BLOCK` mode over chunks of input. A small state machine moves through `BETWEEN`, `HEAD`, `BLOCK`, and `TAIL`. Headers are discarded. In `BLOCK`, consumed compressed bytes are copied to output while a bit buffer clears last-block bits, aligns stored-block headers to byte boundaries, strips final empty fixed blocks, and carries trailing bits between members. In `TAIL`, the member CRC and length are accumulated; CRCs are combined with `crc32_combine()` using the actual uncompressed member length. At EOF it verifies state, writes a terminating empty fixed block, writes the combined trailer, flushes output, and reports I/O errors.

## State And Persistence
State is streaming and local: inflate state, gzip state enum, accumulated CRC/length, bit buffer (`buf`/`num`), per-member uncompressed length, and partial trailer state. The utility persists only stdout output. It handles empty input by emitting an empty canonical gzip stream.

## Dependencies And Integration
Depends on libc I/O/allocation/error reporting and zlib gzip-aware inflate. On DOS/Windows-style platforms it switches stdin/stdout to binary mode. It operates on gzip and deflate bitstream internals directly rather than using `gzFile`; the output is intended to be accepted by standard gzip decompressors.

## Risks And Test Signals
Risks include subtle bit-buffer bugs across member boundaries, incorrect `data_type` interpretation, CRC combination overflow checks, partial trailer handling across input chunks, and I/O error reporting after buffered writes. Test signals include normalizing empty input, one-member and multi-member gzip streams, streams with all optional header fields, every deflate block type, members ending at varied bit offsets, idempotence (`gznorm | gznorm` unchanged), corrupt/truncated inputs, and binary-mode smoke tests on Windows-like platforms.
