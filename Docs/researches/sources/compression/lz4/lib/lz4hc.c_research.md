# sources/compression/lz4/lib/lz4hc.c

## Purpose
`lz4hc.c` implements LZ4 high-compression block and streaming compression. It is not an independent module: it includes or depends on shared `lz4.c` internals for byte access, match counting, wild copies, constants, memory allocation hooks, debug logging, and low-level format encoding.

## Important APIs, Types, And Functions
The public entry points are `LZ4_compress_HC`, `LZ4_compress_HC_extStateHC`, `LZ4_compress_HC_extStateHC_fastReset`, `LZ4_compress_HC_destSize`, `LZ4_createStreamHC`, `LZ4_freeStreamHC`, `LZ4_initStreamHC`, `LZ4_resetStreamHC`, `LZ4_resetStreamHC_fast`, `LZ4_setCompressionLevel`, `LZ4_favorDecompressionSpeed`, `LZ4_loadDictHC`, `LZ4_attach_HC_dictionary`, `LZ4_compress_HC_continue`, `LZ4_compress_HC_continue_destSize`, and `LZ4_saveDictHC`. Internally, `cParams_t` maps compression levels to strategies: `lz4mid` for level 2, hash-chain HC for levels 3-9, and optimal parsing for levels 10-12. `LZ4HC_match_t` carries match offset, length, and negative backtracking.

## Control Flow
The main dispatcher is `LZ4HC_compress_generic_internal()`: it validates sizes, advances `ctx->end`, selects the strategy, and marks the state dirty if compression fails. `LZ4MID_compress()` keeps 4-byte and 8-byte hash tables for a faster medium mode. `LZ4HC_compress_hashChain()` repeatedly finds best, second, and third matches and emits sequences through `LZ4HC_encodeSequence()`. `LZ4HC_compress_optimal()` builds a bounded dynamic-programming price table (`LZ4_OPT_NUM`) and reverse-walks it to encode the cheapest path.

## State, Persistence, And Dependencies
All persistent compression state is in `LZ4HC_CCtx_internal`: hash table, chain table, prefix bounds, external dictionary bounds, `nextToUpdate`, compression level, decompression-speed preference, dirty flag, and optional attached dictionary context. Streaming moves prior input from prefix to external dictionary when blocks are non-contiguous, trims history to the 64 KB LZ4 window, and rejects simultaneous ext-dict and dict-context use. There is no file persistence.

## Integration Points
The file backs the HC API declared by `lz4hc.h`, is linked into liblz4, is exercised by the CLI benchmark, and is heavily targeted by OSS-Fuzz HC and streaming harnesses. It integrates with regular LZ4 decompression because it emits standard LZ4 block sequences.

## Risks
The implementation is pointer- and integer-boundary sensitive: dictionary rollover, 2 GB index limits, 64 KB offsets, `fillOutput` truncation, and output-capacity rollback are key risk areas. Fast reset is only safe for coherent states; failures set `dirty` so the next reset must rebuild state. Compile-time memory access modes can trade portability for speed.

## Test Signals
Useful signals are round-trip tests across all compression levels, `destSize` partial-input behavior, streaming continuation with prefix and external dictionaries, attached dictionaries, tiny output buffers, large inputs near limits, failed compression followed by fast reset, and sanitizer builds with portable memory access.
