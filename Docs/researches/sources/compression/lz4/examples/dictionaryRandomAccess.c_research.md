# sources/compression/lz4/examples/dictionaryRandomAccess.c

## Purpose
This example shows how to compress independently addressable blocks with a fixed dictionary and then decompress an arbitrary byte range by using a tail jump table of block offsets.

## Important APIs, Types, and Functions
It uses `LZ4_initStream()`, `LZ4_loadDict()`, `LZ4_compress_fast_continue()`, `LZ4_setStreamDecode()`, and `LZ4_decompress_safe_continue()`. Constants define `BLOCK_BYTES`, `DICTIONARY_BYTES`, `MAX_BLOCKS`, and `kTestMagic`. Helpers perform checked binary I/O and seeking.

## Control Flow
`test_compress()` writes a magic header, then for each 1 KiB input block reloads the dictionary, compresses the block independently, writes compressed bytes, and stores cumulative offsets. It appends the offset table and count at EOF. `test_decompress()` validates magic, reads enough offsets from the tail table to cover the requested range, seeks to the first needed block, reloads the dictionary for each block, decodes, and writes only the requested slice. `main()` loads the dictionary file, compresses, decompresses the requested range, and verifies against the original input at the requested offset.

## State and Persistence
Persistent output is a custom block file `<input>.lz4s-1024` containing magic, compressed block payloads, offsets, and offset count. The decoded slice is written to `<input>.lz4s-1024.dec`.

## Dependencies and Integration Points
It integrates with `examples/Makefile` and the block streaming dictionary API. The test target runs it twice with the same file as input and dictionary, including a tiny `.gitignore` case.

## Risks
`MAX_BLOCKS` caps the number of source blocks and the offset table uses host-endian `int`. Negative offsets, negative lengths, and integer overflow are not fully defended beyond asserts and simple checks. The magic string is deliberately weak and only demonstrates versioning, not robust file identification.

## Test Signals
Expected output is `verify : OK`. Stronger tests should cover zero-length ranges, ranges ending inside a block, ranges spanning multiple blocks, small dictionary files, and malformed offset tables.
