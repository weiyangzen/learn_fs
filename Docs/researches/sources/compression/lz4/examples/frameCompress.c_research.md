# sources/compression/lz4/examples/frameCompress.c

## Purpose
This example demonstrates direct use of the LZ4 frame API for bounded-memory streaming compression and decompression. It also demonstrates injecting uncompressed data into a frame via `LZ4F_uncompressedUpdate()`.

## Important APIs, Types, and Functions
It defines `kPrefs` as `LZ4F_preferences_t` with 256 KiB linked blocks and no checksums. Compression uses `LZ4F_createCompressionContext()`, `LZ4F_compressBegin()`, `LZ4F_compressUpdate()`, `LZ4F_uncompressedUpdate()`, `LZ4F_compressEnd()`, and `LZ4F_freeCompressionContext()`. Decompression uses `LZ4F_createDecompressionContext()`, `LZ4F_getFrameInfo()`, `LZ4F_decompress()`, and `LZ4F_freeDecompressionContext()`. Important local functions are `safe_fwrite()`, `compress_file_internal()`, `compress_file()`, `get_block_size()`, `decompress_file_internal()`, `decompress_file_allocDst()`, `decompress_file()`, and `compareFiles()`.

## Control Flow
`main()` parses `<input file> [-o <offset> -d <file>]`, compresses input to `<input>.lz4`, decompresses to `<input>.lz4.dec`, then compares output. Compression writes the frame header, loops over input chunks, optionally switches to an uncompressed source file once `uncOffset` is reached, writes each compressed or uncompressed update, and ends the frame. Decompression reads enough input for the header, derives the block-size output buffer, then loops through `LZ4F_decompress()` until the frame ends and rejects trailing data.

## State and Persistence
Frame contexts hold streaming compression/decompression state. Persistent outputs are a `.lz4` frame and decoded `.lz4.dec` file. Optional uncompressed injection reads from a second file but still produces one LZ4 frame.

## Dependencies and Integration Points
It includes both `lz4frame.h` and `lz4frame_static.h`, uses `getopt()`, and is built by the examples Makefile. CLI validation of the generated frame is performed by `lz4 -vt`.

## Risks
The optional injection path has subtle offset accounting and accepts `-o 0` differently from positive offsets in user messages. Several file opens are not checked before use. Decompression intentionally supports only a single frame and treats trailing data as an error, which is stricter than concatenated-frame use cases.

## Test Signals
Successful normal execution prints frame write sizes, `decompress : done`, and `verify : OK`. Additional test signals include CLI validation, injection mode comparison against the alternate uncompressed file at the requested offset, and rejection of trailing data.
