# sources/distributed-fs/ceph-client/lib/decompress_bunzip2.c

## Purpose
Implements a small bzip2 decompressor adapted for Linux kernel preboot and initramfs use.

## APIs, Types, and Functions
The callable decompressor is `bunzip2()` in linked builds and `__decompress()` in preboot builds. Internal types include `struct group_data` for Huffman decoding tables and `struct bunzip_data` for input buffering, bit-buffer state, CRCs, block workspace, selectors, MTF tables, and output-resume state. Important helpers are `get_bits()`, `get_next_block()`, `read_bunzip()`, `start_bunzip()`, and `nofill()`.

## Control Flow
`start_bunzip()` allocates and initializes `bunzip_data`, validates the `BZh1` through `BZh9` header, builds the big-endian CRC table, and allocates the block workspace based on the block-size digit. `get_next_block()` parses block headers, validates signatures, builds selector and Huffman tables, decodes Huffman/MTF/RLE symbols into `dbuf`, and prepares the inverse Burrows-Wheeler traversal. `read_bunzip()` emits bytes, handles repeat runs, updates per-block and total CRCs, and requests the next block when needed. `bunzip2()` loops over `read_bunzip()`, flushing or writing into the caller's buffer, then verifies final CRC and frees all allocations.

## State and Persistence
All decompression state is in `struct bunzip_data` and temporary buffers allocated per call. With streaming output, `write*` fields persist between `read_bunzip()` calls. There is no cross-call global state.

## Dependencies and Integration Points
Depends on `linux/decompress/mm.h` allocation helpers, CRC32 polynomial constants, optional static inclusion for preboot, and the generic decompressor callback contract: `fill`, `flush`, `outbuf`, `pos`, and `error`. It integrates with compressed kernel and initramfs paths.

## Risks and Test Signals
Risks include malformed Huffman tables, invalid selectors, block-size overflows, CRC mismatches, short input/output callbacks, and memory pressure for `dbuf`. Test signals include bzip2 known-good streams, corrupted header/block/CRC cases, streaming `fill`/`flush` tests, block sizes 1-9, truncated input, and boot tests using bzip2-compressed initramfs or kernel images.
