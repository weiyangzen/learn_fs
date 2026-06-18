# sources/compression/xz/tests/test_index.c

Purpose: comprehensive tests for `lzma_index` data structures, accounting, iteration, concatenation, duplication, encoding, decoding, and buffer APIs.

Important helpers and state: `MEMLIMIT`, optional global `decode_buffer`, `decode_buffer_size`, and `decode_test_index`; `generate_index_decode_buffer()` builds a reference encoded Index; `index_is_equal()` compares stream/block offsets and sizes; `verify_index_buffer()` validates raw Index bytes; `my_alloc()` simulates allocation failure for `lzma_index_dup()`.

Control flow: early tests cover memory usage estimates, actual memory used, appending records, stream flags/check masks, stream padding, stream/block counts, index size, stream size, total compressed size, file size, and uncompressed size. Iterator tests validate init, rewind, block/stream/any/nonempty iteration modes, offsets, empty streams, padding, and locating uncompressed offsets across large allocation group boundaries. Concatenation and duplication tests check overflow and historical empty-stream/memory-leak regressions. Encoder/decoder tests cover streaming and buffer APIs, NULL arguments, memlimits, corrupt indicators, corrupt middle bytes, CRC errors, nonzero padding, too-short input, extra input, and appending after decoding an empty Index.

State and persistence: all state is in heap-allocated `lzma_index` objects and in-memory buffers. No files are used. Ownership transfer matters: `lzma_index_cat(dest, src)` consumes `src` on success.

Dependencies and integration: includes internal `common/index.h` for constants and `vli_ceil4()`, plus public liblzma Index APIs, VLI, CRC, stream coders, and the tuktest harness.

Risks: this file guards size arithmetic and offset accounting, a high-risk area for overflows and out-of-bounds access. Feature-disabled encoder/decoder builds skip serialization tests. The simulated allocator has static count state, so it is suitable only for the one failure scenario.

Test signals: broad regression coverage, including named historical fixes for append overflow, duplication of empty streams, decoder NULL-output cleanup, and appending to decoded empty indexes.
