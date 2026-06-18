# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/extents_types.h

## Role

`extents_types.h` defines runtime-only types shared by extent read, update, movement, and failure-handling code.

## Main Types

- `struct bch_extent_crc_unpacked`: normalized checksum/compression metadata with compressed size, uncompressed size, live size, checksum type, compression type, offset, nonce, and checksum value.
- `struct extent_ptr_decoded`: decoded view of one readable pointer plus its active CRC and optional EC stripe pointer.
- `struct bch_io_failures`: per-read failure accumulator containing per-device error state and an EC diagnostic print buffer.

## Read Flags

`BCH_READ_FLAGS()` defines read behavior modifiers:
- stale-pointer retry behavior
- promotion permission
- user-mapped buffer handling
- soft/hard required read device
- last-fragment completion
- forced bounce/clone
- retry state
- poison-check bypass

These flags are used heavily by `read.c`, movement code, scrub, and self-healing.
