# sources/compression/zstd/zlibWrapper/examples/example_original.c

## Purpose
`example_original.c` is the baseline upstream zlib example retained beside the wrapper-modified copy. It demonstrates zlib's one-shot, gzip-file, streaming, flush/sync recovery, dynamic parameter, and preset dictionary APIs without zstd wrapper changes.

## Important APIs, Types, and Functions
It defines the same example test surface as the adapted copy: `test_compress()`, `test_gzio()`, `test_deflate()`, `test_inflate()`, `test_large_deflate()`, `test_large_inflate()`, `test_flush()`, `test_sync()`, `test_dict_deflate()`, `test_dict_inflate()`, and `main()`. It includes `zlib.h` directly and uses `compress()`, `uncompress()`, `gz*` APIs, `deflate*`/`inflate*` streaming APIs, `deflateParams()`, `deflateSetDictionary()`, `inflateSetDictionary()`, and `inflateSync()`.

## Control Flow, State, and Persistence
`main()` validates the zlib runtime version, allocates cleared buffers, runs one-shot and gzip-file tests in non-`Z_SOLO` builds, then exercises small-buffer streaming, large-buffer streaming with parameter changes, flush/sync recovery, and preset dictionary round trips. The original test string is shorter (`"hello, hello!"`) and the dictionary is `"hello"`, so gzip seek offsets and expected line lengths differ from the wrapper-modified copy. `test_sync()` intentionally corrupts a full-flush stream and expects `inflate()` after `inflateSync()` to report `Z_DATA_ERROR` because the adler checksum is wrong.

## Dependencies and Integration Points
It depends only on zlib headers/library and standard C library facilities, with optional `Z_SOLO` allocator hooks. In this repository it functions as a comparison/reference for the wrapper-specific `example.c`, not as the Makefile's primary built source.

## Risks and Test Signals
Risks are mostly portability and example assumptions: fixed buffer sizes, direct process exits on failures, generated `foo.gz` state, and strict expectations for zlib checksum/sync behavior that wrapper mode may not support. Strong signals are exact string output, successful gzip seek/read/unget/gets behavior, `Z_STREAM_END` on normal stream completion, `Z_DATA_ERROR` after damaged full-flush recovery, and dictionary adler matching before `inflateSetDictionary()`.
