# sources/compression/zstd/tests/fuzz/sequence_compression_api.c

## Purpose

`sequence_compression_api.c` is the most comprehensive target in this group for zstd's experimental sequence-ingestion APIs. It generates arbitrary but valid `ZSTD_Sequence` arrays, synthesizes the corresponding source buffer, compresses through `ZSTD_compressSequences()` and sometimes `ZSTD_compressSequencesAndLiterals()`, then verifies decompression restores the generated source.

## Important APIs, Types, And Helpers

The entry point is `LLVMFuzzerTestOneInput()`. Helper functions include `FUZZ_RDG_rand()` and `generatePseudoRandomString()` for deterministic literal data, `generateRandomSequences()` for valid sequence arrays, `decodeSequences()` for reconstructing source bytes from sequences/literals/dictionary, `transferLiterals()` for extracting literal bytes, `roundTripTest_compressSequencesAndLiterals()`, and `roundTripTest()`.

Core zstd APIs include `ZSTD_compressSequences()`, `ZSTD_compressSequencesAndLiterals()`, `ZSTD_decompressDCtx()`, `ZSTD_CCtx_setParameter()`, `ZSTD_CCtx_getParameter()`, `ZSTD_createCDict_advanced()`, `ZSTD_createDDict_advanced()`, `ZSTD_CCtx_refCDict()`, and `ZSTD_DCtx_refDDict()`. It uses `ZSTD_SequenceFormat_e` to choose `ZSTD_sf_noBlockDelimiters` or `ZSTD_sf_explicitBlockDelimiters`.

## Control Flow

The fuzzer creates or reuses compression/decompression contexts, chooses window log, compression level, and sequence format, resets and configures the compression context for deterministic single-threaded sequence validation, and lazily initializes global literal, dictionary, sequence, and source buffers.

`generateRandomSequences()` emits sequences bounded by generated source size, maximum match length, current window size, optional dictionary size, and explicit-block constraints. In explicit delimiter mode it inserts zero-offset delimiter sequences when a block would exceed `min(ZSTD_BLOCKSIZE_MAX, windowSize)`, may split literals into delimiter sequences, and always appends a final delimiter.

`decodeSequences()` reconstructs a generated source buffer by copying literals from the fixed literal buffer and matches from either the dictionary or previously written output. In no-delimiter mode, it appends remaining literal bytes after all sequences. The resulting source and sequence array are passed to `roundTripTest()`, which optionally references global CDict/DDict objects and tests both `compressSequencesAndLiterals()` under its supported parameter combination and `compressSequences()`.

## State And Persistence

Several large static allocations persist under `STATEFUL_FUZZING`: compression/decompression contexts, the literal buffer, generated source buffer, generated sequence array, dictionary buffer, CDict, and DDict. Without `STATEFUL_FUZZING`, most are freed at the end of each input, but the dictionary buffer and CDict/DDict are not released in this file's non-stateful cleanup path, making process lifetime cleanup rely on fuzzer process exit.

The dictionary buffer is a zero-filled raw-content dictionary of size `1 << ZSTD_WINDOWLOG_MAX_32`, with CDict/DDict created by reference. The generator uses this large dictionary when the fuzzer-selected `hasDict` flag is set.

## Dependencies And Integration Points

The target depends on zstd static-linking-only APIs, `zstd_errors.h`, fuzz helpers, random parameter infrastructure, and optional third-party sequence producer setup macros. It directly tests sequence APIs that sit between external sequence producers and zstd frame emission.

## Risks And Edge Cases

This target deliberately explores hard boundaries: huge numbers of sequences, tiny explicit blocks, dictionary offsets that reach before generated output, maximum window-size constraints, `dstSize_tooSmall` in explicit delimiter mode, and `cannotProduce_uncompressedBlock` from `compressSequencesAndLiterals()`. The manual source decoder is itself security-sensitive test code; bugs there could mask or falsely report compressor behavior.

Memory pressure is nontrivial because the dictionary maximum can be large and several 1 MiB buffers are retained. `transferLiterals()` uses assertions about destination slack and source consumption, so malformed generated sequences should be caught before zstd ingestion.

## Test Signals

Round-trip decompressed size and byte equality are the main success conditions. Expected non-round-trip outcomes are limited to documented `dstSize_tooSmall` in explicit delimiter mode and `cannotProduce_uncompressedBlock` for `compressSequencesAndLiterals()`. Valuable corpus cases cover explicit delimiter splits, dictionary-backed matches, window-bound offsets, many small blocks, and toggling validation mode.
