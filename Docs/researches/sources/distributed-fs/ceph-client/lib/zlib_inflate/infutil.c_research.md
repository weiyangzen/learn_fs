# sources/distributed-fs/ceph-client/lib/zlib_inflate/infutil.c

Purpose: Provides `zlib_inflate_blob()`, a convenience helper to inflate a raw deflate blob into a caller-provided buffer using temporary stream/workspace allocation.

Important APIs/functions:
- `zlib_inflate_blob(void *gunzip_buf, unsigned int sz, const void *buf, unsigned int len)` returns decompressed byte count or negative errno-style errors.

Control flow:
- Allocates a `z_stream_s` and inflate workspace with `kmalloc`.
- Sets input/output pointers and calls `zlib_inflateInit2(strm, -MAX_WBITS)` because the gzip header is expected to be stripped.
- Calls `zlib_inflate(strm, Z_FINISH)` once and treats only `Z_STREAM_END` as success.
- Calls `zlib_inflateEnd()` then frees workspace and stream.

State and persistence:
- All state is temporary and freed before return.
- Does not persist decompressor state across calls.

Dependencies and integration:
- Includes `<linux/zutil.h>`, errno, slab, and vmalloc headers.
- Exported by `inflate_syms.c`.
- Useful for firmware/init data style one-shot raw deflate decompression.

Risks:
- Single-shot `Z_FINISH` requires provided input and output buffers to be complete and sized correctly.
- It returns `-EINVAL` for any zlib failure, losing detailed zlib error type.
- Comment says returns `Z_OK` if successful, but implementation returns decompressed length on success.

Test signals:
- One-shot raw deflate blob success, too-small output buffer, truncated input, malformed input, and allocation failure injection.
