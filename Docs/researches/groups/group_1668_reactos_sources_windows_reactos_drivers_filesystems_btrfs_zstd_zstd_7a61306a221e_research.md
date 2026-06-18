# Group Research: ReactOS Btrfs Zstd Compression Subset A

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress.c

## Role

Main Zstandard compression implementation vendored into the ReactOS Btrfs filesystem driver. It implements compression contexts, parameter handling, dictionary support, block/frame compression, streaming compression, and compression level presets.

## Major Responsibilities

- Provides public and internal compression entry points:
  - `ZSTD_compress()`, `ZSTD_compressCCtx()`, `ZSTD_compress2()`
  - `ZSTD_compressBegin*()`, `ZSTD_compressContinue()`, `ZSTD_compressEnd()`
  - `ZSTD_compressStream*()`, `ZSTD_flushStream()`, `ZSTD_endStream()`
- Manages `ZSTD_CCtx`, `ZSTD_CStream`, and `ZSTD_CDict` allocation, reset, sizing, and freeing.
- Converts user-facing compression levels and advanced parameters into validated `ZSTD_compressionParameters`.
- Builds and maintains per-block match state, entropy state, literal buffers, sequence buffers, and streaming input/output buffers.
- Handles dictionary modes:
  - raw dictionary content
  - full zstd dictionary with entropy tables
  - copied CDict tables
  - attached dictionary match state
  - prefix dictionary
- Encodes full zstd frames:
  - frame header
  - compressed/raw/RLE blocks
  - optional checksum
  - final empty block when required

## Compression Flow

The central one-shot path is:

1. Initialize or reset a `ZSTD_CCtx`.
2. Resolve requested parameters into applied parameters with `ZSTD_getCParamsFromCCtxParams()`.
3. Allocate workspace and block buffers in `ZSTD_resetCCtx_internal()`.
4. Optionally load dictionary content or attach/copy a `ZSTD_CDict`.
5. Write frame header in `ZSTD_writeFrameHeader()`.
6. Split input into blocks in `ZSTD_compress_frameChunk()`.
7. For each block:
   - update window state
   - correct index overflow if needed
   - validate dictionary distance
   - build sequence store with selected matcher
   - compress literals and sequences
   - fall back to raw/RLE block if compression is not beneficial
8. Write epilogue/checksum in `ZSTD_writeEpilogue()`.

## Important Internal Mechanics

- `ZSTD_resetCCtx_internal()` is the main workspace allocator and state initializer. It computes block size, token space, match table space, LDM space, streaming buffers, entropy workspace, and sequence buffers.
- `ZSTD_selectBlockCompressor()` dispatches match finding by strategy and dictionary mode:
  - fast
  - double fast
  - greedy
  - lazy/lazy2
  - btlazy2
  - btopt/btultra/btultra2
- `ZSTD_compressSequences_internal()` compresses the literal section, writes sequence count headers, selects/builds FSE tables for literal lengths, offsets, and match lengths, then calls `ZSTD_encodeSequences()`.
- `ZSTD_compressBlock_internal()` handles normal block compression and RLE optimization.
- `ZSTD_compressBlock_targetCBlockSize()` routes through superblock compression when target compressed block sizing is requested.
- `ZSTD_overflowCorrectIfNeeded()` rescales match table indices before 32-bit index overflow.
- `ZSTD_writeFrameHeader()` implements zstd frame descriptor construction, dictionary ID fields, window descriptor, content size fields, and magicless format support.

## Dictionary Handling

Dictionary support is extensive and safety-sensitive.

- `ZSTD_compress_insertDictionary()` chooses raw vs full dictionary handling based on `ZSTD_dictContentType_e` and dictionary magic.
- `ZSTD_loadZstdDictionary()` parses full zstd dictionaries:
  - dictionary ID
  - HUF table
  - FSE offset/match-length/literal-length tables
  - repeat offsets
  - dictionary content
- `ZSTD_checkDictNCount()` rejects dictionaries whose normalized FSE distributions cannot encode required symbols.
- `ZSTD_shouldAttachDict()` decides whether to reference CDict match tables or copy them into the active context.
- Attached dictionaries are invalidated when the active input advances beyond the configured window.

## Streaming Behavior

`ZSTD_compressStream2()` provides transparent initialization. When the stream is still in `zcss_init`, it resolves parameters, initializes local dictionaries, and creates either a single-threaded stream state or, under `ZSTD_MULTITHREAD`, delegates to `ZSTDMT`.

Single-threaded streaming uses these stages:

- `zcss_load`: load input into the context input buffer or directly compress final input if output capacity is large enough.
- `zcss_flush`: flush compressed output from the internal output buffer.
- `zcss_init`: requires initialization before compression.

The stream resets session state when a frame ends.

## ReactOS/Btrfs Relevance

This file is compression-library code embedded under the ReactOS Btrfs driver. The filesystem-facing value is the availability of zstd frame/block compression for Btrfs compressed extents. The code itself is generic zstd compression logic, not Btrfs metadata logic.

## Risks and Notes

- This is vendored third-party code with broad API surface; local modifications should be minimized unless syncing with upstream zstd.
- External sequence support explicitly warns that sequences are not verified and invalid sequences may cause out-of-bounds access or data corruption.
- Static contexts cannot resize; many APIs reject static contexts when allocation would be required.
- Dictionary lifetime matters for by-reference dictionaries and attached CDicts.
- Streaming APIs have legacy behavior where pledged source size `0` is treated as unknown in several compatibility paths.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_internal.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_internal.h

## Role

Private compression header for zstd modules under `lib/compress`. It defines the core internal state structures, helper routines, match/window management primitives, sequence storage helpers, hashing functions, and private function prototypes used by the compression implementation files.

## Major Definitions

- Compression stages:
  - `ZSTDcs_created`
  - `ZSTDcs_init`
  - `ZSTDcs_ongoing`
  - `ZSTDcs_ending`
- Streaming stages:
  - `zcss_init`
  - `zcss_load`
  - `zcss_flush`
- Dictionary state:
  - `ZSTD_prefixDict`
  - `ZSTD_localDict`
  - `ZSTD_dictMode_e`
- Entropy state:
  - `ZSTD_hufCTables_t`
  - `ZSTD_fseCTables_t`
  - `ZSTD_entropyCTables_t`
  - `ZSTD_compressedBlockState_t`
- Match/window state:
  - `ZSTD_window_t`
  - `ZSTD_matchState_t`
  - `ZSTD_blockState_t`
- Long distance matching:
  - `ldmEntry_t`
  - `ldmState_t`
  - `ldmParams_t`
  - `rawSeq`
  - `rawSeqStore_t`
- Context parameter and runtime state:
  - `ZSTD_CCtx_params_s`
  - `ZSTD_CCtx_s`

## Important Helpers

- `ZSTD_LLcode()` and `ZSTD_MLcode()` map literal and match lengths to zstd entropy symbols.
- `ZSTD_updateRep()` updates repeat offsets after a sequence.
- `ZSTD_noCompressBlock()` writes raw block headers and payloads.
- `ZSTD_rleCompressBlock()` writes RLE block headers and one literal byte.
- `ZSTD_minGain()` computes the minimum gain required before compressed output is accepted.
- `ZSTD_disableLiteralsCompression()` implements literal-compression mode policy.
- `ZSTD_storeSeq()` copies literals and records one sequence in `seqStore_t`.
- `ZSTD_count()` and `ZSTD_count_2segments()` count match length in one or two memory segments.
- `ZSTD_hashPtr()` and related functions provide match hash functions for 4-8 byte match lengths.
- Rolling hash helpers support long distance matching.

## Window Management

The header contains the core rolling window logic used by all matchers:

- `ZSTD_window_init()` initializes a safe nonzero base/limit state.
- `ZSTD_window_update()` appends source ranges and switches non-contiguous prior input into external-dictionary mode.
- `ZSTD_window_clear()` drops prior match history.
- `ZSTD_window_hasExtDict()` detects external dictionary state.
- `ZSTD_matchState_dictMode()` chooses no-dict, ext-dict, or dict-match-state mode.
- `ZSTD_window_needOverflowCorrection()` and `ZSTD_window_correctOverflow()` protect 32-bit match indices from overflow.
- `ZSTD_window_enforceMaxDist()` enforces the maximum match distance and invalidates dictionaries when too far away.
- `ZSTD_checkDictValidity()` invalidates attached dictionaries for blocks beyond window range.
- `ZSTD_getLowestMatchIndex()` and `ZSTD_getLowestPrefixIndex()` compute match search lower bounds.

## Private API Surface

The header exposes private compression functions used across zstd compression modules:

- `ZSTD_selectBlockCompressor()`
- `ZSTD_loadCEntropy()`
- `ZSTD_reset_compressedBlockState()`
- `ZSTD_getCParamsFromCCtxParams()`
- `ZSTD_initCStream_internal()`
- `ZSTD_resetSeqStore()`
- `ZSTD_getCParamsFromCDict()`
- `ZSTD_compressBegin_advanced_internal()`
- `ZSTD_compress_advanced_internal()`
- `ZSTD_writeLastEmptyBlock()`
- `ZSTD_referenceExternalSequences()`
- `ZSTD_cycleLog()`

## ReactOS/Btrfs Relevance

This header is the structural backbone for the vendored zstd compressor. In the Btrfs driver context, it defines how compressed extent data is transformed into zstd frames/blocks and how compression memory is managed inside the driver’s zstd subsystem.

## Risks and Notes

- Most functions are `MEM_STATIC`/inline internal helpers, so behavioral changes here can affect every matcher and compressor path.
- `ZSTD_storeSeq()` assumes sequence store capacity and literal buffer limits were correctly allocated by the context reset path.
- Window/index correction logic is subtle and critical for long streams and reused contexts.
- Dictionary validity depends on correct maintenance of `loadedDictEnd`, `dictLimit`, and `lowLimit`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_literals.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_literals.c

## Role

Implements literal-section compression for zstd blocks. It decides whether literals should be stored raw, represented as RLE, compressed with Huffman coding, or emitted using a repeated Huffman table.

## Main Functions

- `ZSTD_noCompressLiterals()`
  - Writes a raw literals section.
  - Chooses a 1, 2, or 3 byte literal header depending on source size.
  - Copies literal bytes directly after the header.
- `ZSTD_compressRleLiteralsBlock()`
  - Writes an RLE literals section.
  - Stores only the repeated byte after the header.
- `ZSTD_compressLiterals()`
  - Main literal compression selector.
  - Copies prior Huffman state into the next Huffman state before attempting reuse.
  - Skips compression when disabled or when literals are too small.
  - Uses `HUF_compress1X_repeat()` for single stream mode and `HUF_compress4X_repeat()` otherwise.
  - Falls back to raw literals if compression fails, is not beneficial, or produces an error.
  - Emits RLE literals if the Huffman compressor reports single-byte output.
  - Writes compressed literal headers for 3, 4, or 5 byte header formats.

## Key Policy

- Small literals are left uncompressed for speed unless a valid repeat table makes compression cheap enough to try.
- `ZSTD_minGain()` is used to reject compressed literals that do not save enough space.
- Fast strategy with literal compression disabled by policy will emit raw literals.
- Reused Huffman tables are marked with `set_repeat`; newly built tables leave the next table in check mode.

## Dependencies

- Includes `zstd_compress_literals.h`.
- Relies on internal zstd definitions from `zstd_compress_internal.h`.
- Calls Huffman APIs from the zstd HUF implementation through included internal headers.

## ReactOS/Btrfs Relevance

Btrfs zstd compression emits block payloads where literals often dominate compressed size. This file implements the literal-section decisions used by the block compressor in `zstd_compress.c`.

## Risks and Notes

- The function intentionally falls back to raw literals in many cases, prioritizing valid output and speed over marginal compression wins.
- Header size and compressed literal size are packed into bit fields; off-by-one changes would break zstd format compatibility.
- The function preserves prior Huffman state on fallback, which is important for entropy repeat semantics across blocks.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_literals.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_literals.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_literals.h

## Role

Private header declaring literal compression helpers used by the zstd compression pipeline.

## Exposed Functions

- `ZSTD_noCompressLiterals()`
  - Emits raw literal sections.
- `ZSTD_compressRleLiteralsBlock()`
  - Emits RLE literal sections.
- `ZSTD_compressLiterals()`
  - Selects and emits raw, RLE, repeated-table, or Huffman-compressed literal sections.

## Dependencies

- Includes `zstd_compress_internal.h` for:
  - `ZSTD_hufCTables_t`
  - `ZSTD_minGain()`
  - zstd strategy and internal block-format types

## ReactOS/Btrfs Relevance

This header connects the main compressor to the literal-section encoder used for Btrfs zstd block/frame compression.

## Risks and Notes

- The API is internal, not a stable external interface.
- Callers must pass valid previous/next Huffman table state and an adequately sized entropy workspace.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_literals.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_sequences.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_sequences.c

## Role

Implements sequence entropy-table selection, FSE table construction, and final bitstream encoding for zstd match sequences. It is the sequence-side counterpart to literal compression.

## Main Components

- `kInverseProbabilityLog256`
  - Lookup table used for approximate entropy cost calculations.
- `ZSTD_fseBitCost()`
  - Estimates the cost of encoding symbols using an existing FSE table.
  - Rejects repeat tables that cannot represent required symbols.
- `ZSTD_crossEntropyCost()`
  - Estimates cost of encoding a distribution with default normalized counts.
- `ZSTD_selectEncodingType()`
  - Chooses among:
    - `set_basic`
    - `set_rle`
    - `set_repeat`
    - `set_compressed`
  - Uses fast heuristics for lower strategies and cost comparison for lazy/optimal strategies.
- `ZSTD_buildCTable()`
  - Builds or copies the FSE compression table according to selected encoding type.
  - Writes normalized count headers for compressed tables.
- `ZSTD_encodeSequences()`
  - Encodes literal length, match length, and offset code streams into a zstd bitstream.
  - Dispatches to a BMI2-specialized implementation when dynamic BMI2 support is enabled.

## Encoding Flow

1. The caller provides symbol code tables for literal lengths, match lengths, and offsets.
2. `ZSTD_selectEncodingType()` decides how each symbol stream should be represented.
3. `ZSTD_buildCTable()` prepares the FSE table and writes any required table description.
4. `ZSTD_encodeSequences_body()` initializes FSE states from the last sequence.
5. Sequences are encoded in reverse order.
6. Extra bits for literal length, match length, and offset are interleaved with FSE state transitions.
7. FSE states are flushed and the bitstream is closed.

## Long Offset Handling

When `longOffsets` is true, offset extra bits may exceed the safe stream accumulator budget. The encoder splits offset bits into an early flushed portion and a later portion to avoid accumulator overflow, especially on 32-bit builds.

## Dependencies

- Includes `zstd_compress_sequences.h`.
- Uses FSE APIs, BIT stream APIs, entropy constants, and zstd sequence definitions from internal zstd headers.

## ReactOS/Btrfs Relevance

This file emits the compressed sequence section for each zstd block. For Btrfs compressed extents, it is part of the path that converts LZ-style matches into format-compliant zstd block payloads.

## Risks and Notes

- Bitstream ordering is intentionally reverse-sequence order; changing this would break decoding.
- Cost estimation affects compression ratio and speed but must still preserve valid fallback behavior.
- Repeat-table validation is necessary because reused FSE tables may lack symbols required by the current block.
- 32-bit and long-offset flush decisions are format and portability sensitive.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_sequences.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_sequences.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_sequences.h

## Role

Private header declaring sequence compression helpers for FSE table selection, table construction, cost estimation, and sequence bitstream encoding.

## Exposed Types

- `ZSTD_defaultPolicy_e`
  - `ZSTD_defaultDisallowed`
  - `ZSTD_defaultAllowed`

This controls whether default zstd FSE tables may be selected for a given symbol stream.

## Exposed Functions

- `ZSTD_selectEncodingType()`
  - Chooses basic, RLE, repeated, or compressed FSE representation.
- `ZSTD_buildCTable()`
  - Builds/copies the selected FSE compression table and writes table metadata when needed.
- `ZSTD_encodeSequences()`
  - Encodes sequence symbols and extra bits into the final bitstream.
- `ZSTD_fseBitCost()`
  - Estimates repeat-table encoding cost.
- `ZSTD_crossEntropyCost()`
  - Estimates default-table encoding cost.

## Dependencies

- Includes `fse.h` for FSE table and repeat-mode types.
- Includes `zstd_internal.h` for symbol encoding types, strategy enums, sequence definitions, and shared constants.

## ReactOS/Btrfs Relevance

This header is used by `zstd_compress.c` to compress the sequence portion of each zstd block produced for Btrfs zstd compression.

## Risks and Notes

- Internal-only API; callers must pass symbol counts, max values, code tables, and entropy workspace consistent with the current block.
- The functions declared here are tightly coupled to zstd block format constants and FSE table layouts.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_sequences.h -->