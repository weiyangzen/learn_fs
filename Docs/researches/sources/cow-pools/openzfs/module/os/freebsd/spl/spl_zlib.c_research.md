# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_zlib.c

## Scope

FreeBSD SPL zlib wrapper for OpenZFS compression/decompression callers. It adapts kernel allocation callbacks to FreeBSD malloc/free and provides ZFS-style `z_compress_level()` and `z_uncompress()`.

## Main Interfaces

- Internal zlib wrappers: `zlib_deflateInit()`, `zlib_deflate()`, `zlib_deflateEnd()`, `zlib_inflateInit()`, `zlib_inflate()`, and `zlib_inflateEnd()`.
- Public compression API: `z_compress_level(dest, destLen, source, sourceLen, level)`.
- Public decompression API: `z_uncompress(dest, destLen, source, sourceLen)`.

## State And Control Flow

`zcalloc()` and `zcfree()` route zlib allocation through `M_SOLARIS`. The workspace allocator stubs currently return `NULL`; disabled `#if 0` checks mean the zlib paths rely on the zlib stream allocation callbacks rather than an active workspace cache.

`z_compress_level()` initializes a `z_stream`, validates output size fits in `uInt`, calls deflate with `Z_FINISH`, maps incomplete output to `Z_BUF_ERROR`, stores `stream.total_out`, and tears down the stream. `z_uncompress()` mirrors this with inflate and maps missing dictionary or truncated input conditions to `Z_DATA_ERROR`.

## Dependencies

Uses FreeBSD kernel zlib from `contrib/zlib/zlib.h`, SPL `kmem`/`M_SOLARIS`, and ZFS zmod API expectations.

## Correctness Notes

The output-size truncation guard is important because zlib uses `uInt` lengths while ZFS passes `size_t`. Workspace caching is documented but not active in this FreeBSD implementation. Error conversion in `z_uncompress()` preserves expected zlib API semantics for corrupted/truncated inputs.
