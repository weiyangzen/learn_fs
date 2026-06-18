# sources/compression/zlib/examples/zran.c

## Purpose
`zran.c` demonstrates indexed random access into zlib, gzip, or raw deflate streams. It builds access points at deflate block boundaries and later resumes raw inflation from the closest point before a requested uncompressed offset.

## Important APIs, Types, and Functions
Public functions are `deflate_index_build()`, `deflate_index_extract()`, and `deflate_index_free()`, declared in `zran.h`. Internal helpers include `add_point()`, optional `inflatePreface()` when `NOPRIME` replaces `inflatePrime()`, and the `TEST` main program. The implementation uses `point_t`, `struct deflate_index`, `inflateInit2()`, `inflateReset2()`, `inflateSetDictionary()`, `inflatePrime()`, and `inflate(..., Z_BLOCK)`.

## Control Flow, State, and Persistence
Index building auto-detects raw/zlib/gzip input, inflates one block at a time, and records compressed offset, bit offset, uncompressed offset, and a copied 32 KiB history window whenever the span threshold is met. Extraction binary-searches the point list, seeks the input file, primes any saved prefix bits, installs the saved dictionary, skips forward to the requested offset, and writes up to the requested length. The index owns heap-allocated point windows and a reusable inflate stream, and gzip multi-member boundaries reset history.

## Dependencies and Integration Points
It depends on `zlib.h`, `zran.h`, standard file APIs, `off_t`, `fseeko()`, and optional `inflatePrime()` support. Applications can save/load the exposed point data because access points avoid opaque inflate-state pointers.

## Risks and Test Signals
Risks include memory cost of roughly 32 KiB per point, index invalidation if the compressed file changes, subtle bit-offset handling, and multi-member gzip trailer/header transitions. Strong signals are successful extraction at offsets before, at, and after access points; raw/zlib/gzip detection; crossing gzip members; and clean `Z_BUF_ERROR`, `Z_DATA_ERROR`, or `Z_ERRNO` on damaged inputs.
