# sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_decompress_block.h

## Purpose
This header exposes the internal compressed-block decompression interface used by the Zstd decompressor implementation. It bridges public declarations in `<linux/zstd.h>` and private block-level helpers needed by frame and dictionary code.

## Important APIs, types, and functions
It defines `streaming_operation` with `not_streaming` and `is_streaming`, declares `ZSTD_decompressBlock_internal`, `ZSTD_buildFSETable`, and `ZSTD_decompressBlock_deprecated`, and relies on `ZSTD_DCtx`, `blockProperties_t`, and `ZSTD_seqSymbol` from included headers. The comments also identify related declarations published elsewhere: `ZSTD_decompressBlock`, `ZSTD_getcBlockSize`, and `ZSTD_decodeSeqHeaders`.

## Control flow
There is no executable control flow. Consumers include the header to call block decompression with explicit streaming context, construct sequence FSE tables from already validated normalized counts, or call the non-deprecated wrapper name without deprecation warnings inside the implementation.

## State and persistence
The header owns no state. Its `streaming_operation` flag influences how `zstd_decompress_block.c` stores literals in `ZSTD_DCtx`, especially whether destination-space literal storage is safe.

## Dependencies and integration points
It includes Zstd dependency, public API, internal constants, and decompression-internal definitions. It is part of the private interface between `zstd_decompress.c`, dictionary code, and the compressed-block decoder.

## Risks and test signals
Risks are ABI drift between public and private prototypes, misuse of `ZSTD_buildFSETable` with invalid or undersized workspace, and callers passing the wrong streaming mode. Test signals are build coverage of all decompressor translation units, static workspace-size assertions, and block decompression tests through both streaming and non-streaming APIs.
