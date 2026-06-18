# sources/compression/zstd/lib/compress/zstd_compress_sequences.h

## Purpose
Declares the private sequence-section entropy API for zstd compression. It exposes FSE encoding-type selection, CTable construction, sequence bitstream encoding, and cost-estimation helpers to the block and superblock compression paths.

## Important APIs, Types, And Functions
`ZSTD_DefaultPolicy_e` controls whether default FSE tables are allowed. Declared functions are `ZSTD_selectEncodingType()`, `ZSTD_buildCTable()`, `ZSTD_encodeSequences()`, `ZSTD_fseBitCost()`, and `ZSTD_crossEntropyCost()`. The signatures make repeat-mode state, previous/new FSE tables, default normalized distributions, code tables, workspace, strategy, and BMI2 control explicit.

## Control Flow
The header defines a two-stage sequence entropy contract: callers first choose and build tables for each symbol stream, then call `ZSTD_encodeSequences()` with the selected CTables and per-sequence code tables to produce the body bitstream. Cost helpers support more careful decisions in stronger strategies and in superblock sizing estimates.

## State And Persistence
No direct state is owned. Repeat modes and CTables are passed by pointer, so callers own persistence across blocks. The workspace pointer is caller-owned scratch.

## Dependencies And Integration Points
It includes compression internals for `SeqDef`, common `fse.h` for `FSE_repeat` and `FSE_CTable`, and common zstd internals for symbol encoding types and strategy. It is used by entropy-stat builders and `zstd_compress_superblock.c`.

## Risks And Edge Cases
Callers must keep counts, maxima, code tables, default norms, and table sizes consistent. Mismatched `prevCTableSize`, unsupported symbols, or undersized entropy workspaces can cause errors or invalid output. The API is private, so compile-time integration is the main guard against signature drift.

## Test Signals
Build tests across all compression strategies, plus round-trip tests that force every sequence encoding type and long-offset mode, provide meaningful coverage for this header's contract.
