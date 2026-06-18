# sources/compression/zlib/compress.c

Purpose: implements convenience APIs for compressing an entire memory buffer and computing a conservative compression bound.

Important APIs/functions: exports `compress2_z`, `compress2`, `compress_z`, `compress`, `compressBound_z`, and `compressBound`. Uses `z_stream`, `deflateInit`, `deflate`, and `deflateEnd`.

Control flow: `compress2_z` validates pointer/length combinations, zeroes the destination length, initializes deflate with the requested level, feeds input and output in chunks no larger than `uInt` max, loops until `deflate` stops returning `Z_OK`, finalizes the stream, and maps `Z_STREAM_END` to `Z_OK`. Wrapper functions adapt `uLong`/`uLongf` arguments and default compression level. `compressBound_z` computes the documented upper bound and returns `(z_size_t)-1` on overflow.

State and persistence: stack-local stream state only; output is written into caller-provided memory and `*destLen` is updated.

Dependencies and integration: includes `zlib.h` with `ZLIB_INTERNAL`. This is the simple-buffer API layered on the streaming deflate implementation in `deflate.c`.

Risks: callers must provide a large enough destination buffer or receive `Z_BUF_ERROR`. `compress2` casts `z_size_t` back to `uLong`, so very large sizes are constrained by the legacy API width. Pointer validation permits zero-length null buffers but rejects nonzero lengths with null pointers.

Test signals: exercised by zlib examples, minigzip-related tests indirectly, and C standard CI across many compilers.
