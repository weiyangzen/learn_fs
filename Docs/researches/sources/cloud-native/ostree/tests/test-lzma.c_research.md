<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-lzma.c -->
# sources/cloud-native/ostree/tests/test-lzma.c

## Purpose
`test-lzma.c` unit-tests OSTree's LZMA compressor and decompressor GConverter implementations.

## Important APIs, Types, And Functions
The core helper is `helper_test_compress_decompress`, which uses `_ostree_lzma_compressor_new`, `_ostree_lzma_decompressor_new`, `g_converter_input_stream_new`, `g_memory_input_stream_new_from_data`, `g_memory_output_stream_new_resizable`, and `g_output_stream_splice`.

## Control Flow
The helper compresses an input byte buffer into a memory output stream, converts the compressed data back through the decompressor, and compares the resulting bytes with the original input. Registered tests cover representative data sizes/content including empty or small data depending on compiled test cases.

## State And Persistence
All state is in-memory GLib streams and buffers. No files are written.

## Dependencies And Integration Points
It validates OSTree's LZMA stream wrappers used for archive/repository compression paths, plus GLib's converter stream integration.

## Risks And Test Signals
The important risk is converter state handling across splice boundaries and close flags. Passing signals include positive compressed byte counts, no GLib errors, and exact byte-for-byte decompression.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-lzma.c -->
