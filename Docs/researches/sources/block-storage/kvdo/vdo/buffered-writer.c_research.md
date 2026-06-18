# File Research: sources/block-storage/kvdo/vdo/buffered-writer.c

## Purpose

Implements a sequential buffered writer over a `dm_bufio_client` region.

## Main Responsibilities

- Owns references to an IO factory and dm-bufio client.
- Allocates writable bufio blocks with `dm_bufio_new()`.
- Appends arbitrary-length data across block boundaries.
- Writes zero bytes efficiently.
- Zero-fills unused tail space before releasing a dirty block.
- Flushes dirty buffers on destruction.
- Records sticky write errors.

## Important Functions

- `make_buffered_writer()` allocates and initializes writer state and retains the IO factory.
- `free_buffered_writer()` flushes current buffer, writes dirty buffers, destroys client/factory references, and frees writer.
- `prepare_next_buffer()` allocates the next block unless block limit is exceeded.
- `flush_previous_buffer()` zero-fills remaining bytes, marks dirty, releases the buffer, and advances block number.
- `write_to_buffered_writer()` appends caller data.
- `write_zeros_to_buffered_writer()` appends zeros.
- `flush_buffered_writer()` flushes current buffer if no sticky error exists.

## Behavior Details

Once an error is stored in `writer->error`, future write/flush attempts return it. Partial block writes are padded with zeros on flush.

## Dependencies

Uses device-mapper bufio, IO factory reference management, and UDS error/logging helpers.
