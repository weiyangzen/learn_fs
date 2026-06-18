# sources/distributed-fs/ceph-client/lib/decompress_unlzma.c

## Purpose
Implements a compact LZMA decompressor for kernel preboot and initramfs use.

## APIs, Types, and Functions
The main function is `unlzma()`, with preboot `__decompress()`. Key types are `struct rc` for the range coder, `struct lzma_header` for properties/dictionary/output size, `struct writer` for dictionary/output state, and `struct cstate` for the LZMA state machine and repeated distances. Helpers include range-coder primitives, bit-tree decode, literal handling `process_bit0()`, match/repetition handling `process_bit1()`, and writer copy functions.

## Control Flow
`unlzma()` reads the LZMA header, validates property byte ranges, decodes `lc`, `lp`, and `pb`, endian-converts dictionary and output sizes, allocates the dictionary/output buffer and probability model, initializes all probabilities, then loops until the declared output size is reached or an end marker is decoded. Each iteration chooses literal or match processing using probability tables indexed by state and position. Output is written directly or through a circular dictionary flushed in chunks. Cleanup releases probability, output, and input buffers.

## State and Persistence
All state is per decompression call: range-coder position/code/range, probability arrays, dictionary buffer, output cursor, previous byte, and match distances. No data persists globally.

## Dependencies and Integration Points
Depends on `linux/decompress/mm.h`, compiler attributes, static/preboot inclusion conventions, and the generic decompressor ABI. It is dispatched by `decompress.c` for LZMA magic and used in early boot paths with limited library support.

## Risks and Test Signals
Risks include corrupt header properties, dictionary-size edge cases, invalid back references, output flush failures, range-coder EOF behavior, and memory pressure for large dictionaries or probability tables. Test signals include LZMA known-answer streams, truncated/corrupted match-distance cases, end-marker cases, streaming flush tests, and boot tests with LZMA-compressed images.
