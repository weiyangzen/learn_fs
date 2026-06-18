# sources/compression/zlib/uncompr.c

`uncompr.c` implements zlib's one-shot memory decompression helpers: `uncompress()`, `uncompress_z()`, `uncompress2()`, and `uncompress2_z()`. These wrap streaming inflate for callers that know the complete destination-buffer size.

`uncompress2_z()` is the core. It validates pointers, handles zero-length destination buffers with a non-null dummy output pointer, initializes a local `z_stream` with `inflateInit()`, feeds source and destination in `(uInt)-1` sized chunks, loops on `inflate(Z_NO_FLUSH)`, updates consumed/produced lengths, calls `inflateEnd()`, and normalizes `Z_STREAM_END`, `Z_NEED_DICT`, and selected `Z_BUF_ERROR` outcomes. The other functions adapt `uLong` versus `z_size_t` and pointer versus value source-length APIs.

State is stack-local except caller buffers and output length variables. Dependencies are `zlib.h` and the inflate implementation. Risks include caller-supplied destination capacity requirements, partial output on buffer exhaustion, careful accounting for lengths beyond `uInt`, and wrapper dereferences that assume valid length pointers. Test signals include `example.c` round trips plus negative tests for nulls, truncation, dictionaries, empty buffers, and consumed-byte reporting.
