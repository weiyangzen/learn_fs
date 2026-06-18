# sources/distributed-fs/ceph-client/lib/lzo/lzodefs.h

## Purpose
`lzodefs.h` is the private constants and architecture helper header for the kernel LZO implementation. It defines copy primitives, architecture feature switches, match-class constants, RLE versioning, and dictionary sizing shared by the compressor and decompressor.

## Important APIs, types, and functions
The header defines `LZO_VERSION` as `1` for the RLE-capable stream format, `COPY4()` and `COPY8()` unaligned copy helpers, `LZO_USE_CTZ32`, `LZO_USE_CTZ64`, and `LZO_FAST_64BIT_MEMORY_ACCESS` feature macros based on architecture configuration. It declares match offset and length ranges for M1, M2, M3, and M4, marker values for each match class, RLE zero-run limits, `lzo_dict_t`, and dictionary hash parameters `D_BITS`, `D_SIZE`, `D_MASK`, and `D_HIGH`.

## Control flow
The header has no standalone control flow. Its macros select compressor and decompressor fast paths at compile time. For example, `COPY8()` uses one 64-bit unaligned copy on x86_64 and arm64, but falls back to two 32-bit copies elsewhere. The ctz/clz feature macros determine how the compressor scans equal bytes and zero runs.

## State and persistence
There is no mutable state. The persistent effect is the binary format contract encoded by match markers, maximum offsets, and the LZO-RLE version. `D_SIZE` determines the compressor work-memory dictionary layout and must remain consistent with `LZO1X_1_MEM_COMPRESS` in `include/linux/lzo.h`.

## Dependencies and integration points
The file relies on kernel unaligned helpers and architecture configuration macros. It is included by `lzo1x_compress.c` and `lzo1x_decompress_safe.c` and aligns with the public LZO API in `include/linux/lzo.h`. The RLE constants also align with `Documentation/staging/lzo.rst` and crypto LZO-RLE test vectors.

## Risks and test signals
Risks include changing marker or offset constants in a way that breaks on-disk or wire compatibility, choosing unsafe copy behavior on strict-alignment architectures, and mismatching dictionary size with caller-allocated work memory. Test signals are cross-architecture builds, byte-for-byte decode of historical LZO streams, RLE stream tests with version marker `1`, compressor memory-size assertions, and sanitizer/fuzz coverage of match classes around every maximum offset and length boundary.
