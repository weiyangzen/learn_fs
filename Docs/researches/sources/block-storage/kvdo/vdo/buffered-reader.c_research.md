# File Research: sources/block-storage/kvdo/vdo/buffered-reader.c

## Purpose

Implements a sequential buffered reader over a `dm_bufio_client` region.

## Main Responsibilities

- Owns references to an IO factory and dm-bufio client.
- Reads aligned blocks through `dm_bufio_read()`.
- Releases prior buffer when moving to a new block.
- Prefetches up to four blocks ahead.
- Copies arbitrary-length reads across block boundaries.
- Verifies expected byte sequences without consuming on failure.

## Important Functions

- `make_buffered_reader()` allocates a reader, stores block limit, prefetches block 0, and retains the IO factory.
- `free_buffered_reader()` releases active buffer, destroys client, releases factory, and frees reader.
- `position_reader()` positions to a block/offset and reads the block if necessary.
- `read_from_buffered_reader()` copies requested bytes, crossing blocks as needed.
- `verify_buffered_data()` compares expected data and rewinds to starting position on mismatch/error.

## Behavior Details

`reset_reader()` advances to the next block only when no bytes remain in the current buffer. Partial reads that hit out-of-range/EOF after reading some bytes return `UDS_SHORT_READ`.

## Dependencies

Uses Linux device-mapper bufio, `io-factory`, UDS memory/log/status helpers, and `UDS_BLOCK_SIZE`.
