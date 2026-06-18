# sources/distributed-fs/ceph-client/lib/lz4/lz4hc_compress.c

## Purpose
`lz4hc_compress.c` implements the high-compression LZ4 encoder for the kernel. It emits the same LZ4 block format as the fast compressor but spends more CPU on chain-table match search and multi-match selection to improve compression ratio. It supports one-shot and streaming HC compression with caller-managed work memory.

## Important APIs, types, and functions
Public exports are `LZ4_compress_HC()`, `LZ4_resetStreamHC()`, `LZ4_loadDictHC()`, `LZ4_compress_HC_continue()`, and `LZ4_saveDictHC()`. Important private routines are `LZ4HC_init()`, `LZ4HC_Insert()`, `LZ4HC_InsertAndFindBestMatch()`, `LZ4HC_InsertAndGetWiderMatch()`, `LZ4HC_encodeSequence()`, `LZ4HC_compress_generic()`, `LZ4HC_setExternalDict()`, and `LZ4_compressHC_continue_generic()`. The mutable context is `LZ4HC_CCtx_internal`, with `hashTable`, `chainTable`, `base`, `end`, `dictBase`, `dictLimit`, `lowLimit`, `nextToUpdate`, and `compressionLevel`.

## Control flow
One-shot compression checks work-memory alignment, initializes the HC context around the source buffer, chooses limited or unlimited output mode from `LZ4_compressBound()`, and enters `LZ4HC_compress_generic()`. The generic loop inserts positions into a hash table and a 64 KiB chain table, finds the best current match, searches for better second and third matches, adjusts overlaps with empirical rules, then emits one or two LZ4 sequences through `LZ4HC_encodeSequence()`. The last literal run is appended at the end. Streaming compression auto-initializes forgotten contexts, renormalizes huge histories by reloading the last dictionary, switches to external-dictionary mode when blocks are not contiguous, trims overlapping input/dictionary ranges, and then reuses the generic compressor.

## State and persistence
The HC stream context persists hash chains and dictionary boundaries across calls. Loaded dictionaries are capped to 64 KiB. `saveDictHC()` copies the active tail dictionary into caller-provided safe memory and rewrites `base`, `end`, `dictLimit`, `lowLimit`, and `nextToUpdate` so subsequent blocks can refer to the moved dictionary. As with the fast streaming compressor, previous blocks must remain readable unless saved.

## Dependencies and integration points
The file depends on `lz4defs.h`, `include/linux/lz4.h`, kernel `memset`/`memmove`, and module exports. It is built by `lib/lz4/Makefile` under `CONFIG_LZ4HC_COMPRESS` and is used by `crypto/lz4hc.c` and any kernel user that needs slower but denser LZ4 output while preserving compatibility with `LZ4_decompress_*()`.

## Risks and test signals
Risks include chain-table underflow or stale indexes, match references crossing `dictLimit`/`lowLimit`, output-limit checks before sequence emission, context alignment, and compression-level extremes changing search attempts exponentially. Streaming edge cases include source buffers overlapping the retained dictionary and contexts whose indexed distance grows past 2 GiB. Test signals should include round trips at levels below, within, and above supported levels; output-limit failure returning zero without treating `dst` as valid; dictionary load/save/continue cases; contiguous and external dictionary streams; and compression compatibility with the normal LZ4 safe decompressor.
