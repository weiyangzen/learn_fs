# sources/compression/zstd/lib/decompress/zstd_decompress_block.c

## Purpose
`zstd_decompress_block.c` implements decoding for compressed zstd blocks. It parses compressed block headers and literal sections, builds or reuses FSE sequence tables, decodes literal-length/match-length/offset sequences from the bitstream, executes matches against current prefix or external dictionary history, and updates block-to-block entropy and repcode state.

## Important APIs, Types, And Functions
Public/internal entry points are `ZSTD_getcBlockSize()`, `ZSTD_decodeSeqHeaders()`, `ZSTD_buildFSETable()`, `ZSTD_decompressBlock_internal()`, `ZSTD_checkContinuity()`, `ZSTD_decompressBlock_deprecated()`, and `ZSTD_decompressBlock()`. Important internal helpers include `ZSTD_decodeLiteralsBlock()`, `ZSTD_allocateLiteralsBuffer()`, `ZSTD_buildSeqTable()`, `ZSTD_decodeSequence()`, `ZSTD_execSequence()`, `ZSTD_execSequenceEnd()`, split-literal-buffer variants, long-offset/prefetch sequence decoders, and `ZSTD_getOffsetInfo()`. Local state types include `seq_t`, `ZSTD_fseState`, `seqState_t`, and `ZSTD_OffsetInfo`.

## Control Flow
`ZSTD_decompressBlock_internal()` first rejects compressed block sizes above the active max block size, decodes the literals section, then decodes sequence headers and FSE tables. Literal decoding handles `set_basic`, `set_rle`, `set_compressed`, and `set_repeat`, placing literals either in the destination tail, in `litExtraBuffer`, or split across both to avoid overwriting history during streaming. Sequence-header decoding reads the sequence count, parses table encoding modes for LL/OF/ML, and builds or points to default/repeated/RLE FSE tables. The block entry point then determines whether 32-bit long-offset handling or prefetch decoding is needed and dispatches to the regular, split-literal, or long/prefetch sequence loop. Sequence loops decode symbols, copy literals, copy matches from prefix or extDict, flush remaining literals, verify bitstream completion, and save repcodes back to the context.

## State And Persistence
The block decoder mutates the caller's `ZSTD_DCtx`: literal buffer pointers and location, `litEntropy`, `fseEntropy`, HUF/FSE table pointers, entropy tables, `entropy.rep`, `ddictIsCold`, and history pointers through `ZSTD_checkContinuity()`. It persists no external state. Default FSE tables are static constants. Repeated literal and sequence tables depend on prior blocks or dictionaries; therefore caller ordering and context reuse are semantically significant.

## Dependencies And Integration Points
This module depends on common memory, compiler, FSE, HUF, bit, and zstd internal helpers plus `zstd_decompress_internal.h`. It is called by frame-level code for `bt_compressed` blocks and by the deprecated block API. It shares literal-buffer allocation policy with streaming frame decompression and consumes dictionary-loaded entropy tables from `ZSTD_loadDEntropy()` in `zstd_decompress.c`.

## Risks
The main risks are pointer arithmetic near buffer ends, 32-bit address-space overflow, wildcopy overread/overwrite assumptions, split literal-buffer transitions, validating offsets against prefix plus external dictionary history, repeated-table use before initialization, last-sequence FSE state handling, and differences between 32-bit long-offset decoding and 64-bit decoding. Performance-sensitive alignment and prefetch code should be changed carefully because it can alter decoder speed without changing behavior.

## Test Signals
Important signals are successful decode of blocks using all literal encodings and sequence table encodings, repeat-table behavior across block boundaries and dictionaries, corrupt headers producing zstd errors rather than overreads, offsets that cross from extDict into prefix, near-end literals and matches, small-offset overlap copies, long-distance matches on 32-bit-sensitive configurations, cold-DDict prefetch path coverage, and block API continuity across consecutive `ZSTD_decompressBlock()` calls.
