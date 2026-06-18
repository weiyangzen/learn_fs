# sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_decompress_block.c

## Purpose
`zstd_decompress_block.c` implements the compressed-block decoder for the in-kernel Zstandard library. It parses block and sequence headers, decodes literal sections, builds or reuses entropy tables, reconstructs literal/match sequences, and maintains history-window continuity across blocks and standalone block calls.

## Important APIs, types, and functions
Key exported or externally consumed entry points are `ZSTD_getcBlockSize`, `ZSTD_decodeSeqHeaders`, `ZSTD_buildFSETable`, `ZSTD_decompressBlock_internal`, `ZSTD_checkContinuity`, `ZSTD_decompressBlock_deprecated`, and `ZSTD_decompressBlock`. Internal machinery includes `ZSTD_decodeLiteralsBlock`, `ZSTD_allocateLiteralsBuffer`, `ZSTD_buildSeqTable`, `ZSTD_decodeSequence`, `ZSTD_execSequence`, `ZSTD_execSequenceEnd`, split-literal variants, and long-offset prefetch variants. Important transient types are `seq_t`, `ZSTD_fseState`, `seqState_t`, `ZSTD_OffsetInfo`, and `ZSTD_longOffset_e`.

## Control flow
Compressed block decoding first rejects overlarge blocks, decodes the literal section, then decodes sequence headers and FSE tables for literal length, offset, and match length. Literal buffers are placed either after the output, in `litExtraBuffer`, or split between both depending on streaming mode, block size, and destination capacity. Sequence decoding initializes FSE states from the bitstream, regenerates each sequence, copies literals, resolves repeat offsets and external dictionary references, copies matches, and finally appends remaining literals. Runtime dispatch chooses normal, split-literal, or long-offset/prefetch loops, with BMI2-specialized wrappers when enabled.

## State and persistence
Persistent decompression state lives in `ZSTD_DCtx`: entropy tables, repeat offsets, literal buffer metadata, prefix and external-dictionary pointers, frame parameters, checksum state, and cold-dictionary hints. `ZSTD_checkContinuity` updates `prefixStart`, `virtualStart`, `dictEnd`, and `previousDstEnd` when output is not contiguous. Sequence execution updates repeat offsets for later blocks, and table pointers may continue to reference default, dictionary, repeated, or freshly built tables.

## Dependencies and integration points
The file depends on Zstd common helpers for memory, bits, FSE, Huffman, CPU feature dispatch, and internal frame constants. It integrates with higher-level frame decompression in `zstd_decompress.c`, dictionary loading through `zstd_ddict.h`, the public block API in `<linux/zstd.h>`, and the decompressor aggregation path in `decompress_sources.h`.

## Risks and test signals
Risks cluster around malformed headers, unchecked assumptions after FSE/Huffman validation, destination/literal-buffer overlap, 32-bit pointer overflow, repeat-offset underflow, external dictionary boundary math, and streaming writes that could overwrite history. Test signals include fuzzed compressed blocks, empty and zero-sequence blocks, all literal encodings, repeated entropy tables with and without dictionaries, split-literal streaming blocks, offsets crossing prefix/ext-dict boundaries, 32-bit long offsets, BMI2 and non-BMI2 builds, and standalone `ZSTD_decompressBlock()` continuity tests.
