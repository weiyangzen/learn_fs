# subset-b-000314 Research

Grouped research for zstd compression internals. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_compress_internal.h -->
# sources/compression/zstd/lib/compress/zstd_compress_internal.h

## Purpose
Defines the private compression-side ABI shared by `lib/compress` modules in zstd. It centralizes context state, match state, entropy table state, sequence storage, repeat-code conventions, workspace sizing constants, hash helpers, window/index maintenance, and private entry points used by streaming, dictionary, block, long-distance, and sequence-producer paths.

## Important APIs, Types, And Functions
Core state types include `ZSTD_CCtx_s`, `ZSTD_CCtx_params_s`, `ZSTD_MatchState_t`, `ZSTD_window_t`, `ZSTD_blockState_t`, `ZSTD_compressedBlockState_t`, `SeqStore_t`, `SeqDef`, `rawSeq`, `RawSeqStore_t`, `optState_t`, `ldmState_t`, `ldmParams_t`, and entropy table metadata/containers (`ZSTD_hufCTables_t`, `ZSTD_fseCTables_t`, `ZSTD_entropyCTables_t`, `ZSTD_entropyCTablesMetadata_t`). `ZSTD_BlockCompressor_f` defines the common block compressor signature, and `ZSTD_selectBlockCompressor()` is the dispatcher hook used by the main compressor to pick fast, double-fast, lazy, btlazy, optimal, or row-based implementations.

Sequence helpers encode zstd's sequence representation: `ZSTD_getSequenceLength()` expands `SeqDef` plus the single long-length side channel in `SeqStore_t`; `ZSTD_storeSeqOnly()` and `ZSTD_storeSeq()` append a match sequence and copy literals; `ZSTD_LLcode()` and `ZSTD_MLcode()` map raw lengths to entropy symbol codes. Repeat-code utilities define the offBase sum type: `REPCODE*_TO_OFFBASE`, `OFFSET_TO_OFFBASE()`, `OFFBASE_IS_OFFSET()`, `OFFBASE_TO_OFFSET()`, `OFFBASE_TO_REPCODE()`, `ZSTD_updateRep()`, and `ZSTD_newRep()`.

Window and index helpers are a large part of the file: `ZSTD_window_init()`, `ZSTD_window_update()`, `ZSTD_window_clear()`, `ZSTD_window_hasExtDict()`, `ZSTD_matchState_dictMode()`, `ZSTD_window_needOverflowCorrection()`, `ZSTD_window_correctOverflow()`, `ZSTD_window_enforceMaxDist()`, `ZSTD_checkDictValidity()`, `ZSTD_getLowestMatchIndex()`, `ZSTD_getLowestPrefixIndex()`, and `ZSTD_index_overlap_check()`. Hash helpers include fixed-size hashes for 3-8 byte match lengths, salted row-matchfinder hashes, rolling hashes for long-distance matching, and short-cache tag helpers `ZSTD_writeTaggedIndex()` and `ZSTD_comparePackedTags()`.

Private/public-internal declarations include entropy loading/reset (`ZSTD_loadCEntropy()`, `ZSTD_reset_compressedBlockState()`), sequence conversion/summary APIs, parameter derivation (`ZSTD_getCParamsFromCCtxParams()`, `ZSTD_getCParamsFromCDict()`), streaming/init entry points, deprecated internal wrappers, external sequence registration (`ZSTD_referenceExternalSequences()`), and tracing.

## Control Flow
This header does not own a full compression pipeline by itself, but its inline helpers run throughout every block compression call. A context is initialized with parameters, workspace, block state, sequence store, match state, optional dictionary/prefix, optional LDM state, and streaming buffers. The caller selects a block compressor via `ZSTD_selectBlockCompressor()`, the compressor fills `SeqStore_t` by calling `ZSTD_storeSeq()`, the entropy pipeline consumes the stored sequences and literals, and the repeat offsets and entropy tables are carried forward through `prevCBlock`/`nextCBlock`.

Window flow is index-based rather than pointer-persistent. `ZSTD_window_update()` appends a contiguous source segment or converts the previous prefix into an external dictionary when the source is non-contiguous. Before block compression, `ZSTD_window_enforceMaxDist()` or `ZSTD_checkDictValidity()` invalidates history outside the allowed window and drops attached dictionaries when they can no longer be referenced. When 32-bit indices approach `ZSTD_CURRENT_MAX`, `ZSTD_window_correctOverflow()` shifts `base`, `dictBase`, `lowLimit`, and `dictLimit` by a correction that preserves the low cycle bits used by hash/chain tables.

Sequence flow uses compact `SeqDef` fields and a single long-length escape in `SeqStore_t`. Literal bytes are copied into the literal buffer, while match lengths are stored as `mlBase = matchLength - MINMATCH`. Repeat-code updates follow zstd's special rules for zero-literal repeat matches via `ll0`.

## State And Persistence
All state is in-memory and context-scoped. `ZSTD_CCtx_s` persists requested/applied parameters, workspace ownership, source/destination byte counts, checksum state, block entropy state, repeat offsets, sequence buffers, match tables, LDM data, optional local dictionary buffers, streaming input/output buffers, and external sequence buffers across calls as required by simple or streaming APIs. `ZSTD_MatchState_t` persists hash/chain tables, row-matchfinder caches, dictionary match-state references, `nextToUpdate`, lazy-skipping settings, and dictionary validity boundaries. `ZSTD_window_t` persists the base referential and low/dictionary limits that make stored U32 indices meaningful.

The file also defines persistence rules for reusable entropy: `prevCBlock` and `nextCBlock` carry Huffman/FSE tables and repeat offsets across blocks; literal/FSE repeat modes determine whether new tables, default tables, or previous tables are used.

## Dependencies And Integration Points
The header depends on common zstd internals (`zstd_internal.h`, `bits.h`, `mem.h` through transitive includes), the compression workspace allocator (`zstd_cwksp.h`), optional multithreaded compression (`zstdmt_compress.h`), and block splitting workspace sizing (`zstd_preSplit.h`). It is included by the concrete compressors, literal/sequence/superblock encoders, dictionary builder paths, and some benchmark/decode-corpus utilities that need sequence conversion.

Integration is broad: fast and double-fast compressors use hash, count, repeat, sequence, and window helpers; entropy encoders use `SeqStore_t` and entropy table types; superblock code uses entropy metadata and `ZSTD_getSequenceLength()`; main compression code owns the declared private entry points.

## Risks And Edge Cases
The main risks are invariant drift and undefined behavior around pointer/index arithmetic. Many helpers intentionally allow pointer overflow attributes and depend on U32 index correction, power-of-two distances, and contiguous/non-contiguous source detection. Sequence storage assumes the caller allocated enough literal and sequence capacity and that at most one long literal or match length needs the side channel. Repeat-code handling is subtle when a zero-literal match changes the repcode interpretation.

Dictionary validity is another high-risk area: `loadedDictEnd`, `dictLimit`, `lowLimit`, and `dictMatchState` must be invalidated together or stale dictionary references can survive beyond the window. Short-cache tagged indices pack tag bits into hash table entries and require index high bits to be clear. Inline assembly in `ZSTD_selectAddr()` is x86-64-specific and relies on fallback behavior elsewhere.

## Test Signals
Useful tests include compression/decompression round trips across simple, streaming, dictionary, prefix, ext-dict, attached CDict, and external-sequence modes; fuzzing with `ZSTD_WINDOW_OVERFLOW_CORRECT_FREQUENTLY`; ASAN/UBSAN/MSAN runs for sequence/literal buffers and workspace reuse; tests that force non-contiguous input segments and dictionary invalidation; tests with very long literal or match lengths; and corpus comparisons that verify compressed output remains decodable and ratio-sensitive after changes to match or repeat-code logic.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_compress_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_compress_literals.c -->
# sources/compression/zstd/lib/compress/zstd_compress_literals.c

## Purpose
Implements zstd literals-section encoding for raw, RLE, compressed, and repeat-Huffman modes. It decides when literal compression is worthwhile, builds the literals-section header, invokes Huffman compression with repeat-table support, and falls back to raw literals when compression is disabled, too small, unprofitable, or fails.

## Important APIs, Types, And Functions
`ZSTD_noCompressLiterals()` writes a raw literals block with a 1, 2, or 3 byte literals header and copies the source bytes. `ZSTD_compressRleLiteralsBlock()` writes an RLE literals block when all literals are identical. `ZSTD_compressLiterals()` is the main exported function for block compression and accepts destination capacity, source literals, entropy workspace, previous/next Huffman tables, compression strategy, literal-compression disabling, incompressibility suspicion, and BMI2 flags.

Internal helpers include `allBytesIdentical()` and `ZSTD_minLiteralsToCompress()`. Debug builds can log a hexadecimal literal listing through `showHexa()`.

## Control Flow
`ZSTD_compressLiterals()` first copies `prevHuf` into `nextHuf` on the assumption that the previous Huffman table may be reused. If literal compression is disabled, or if the source size is below a strategy- and repeat-mode-dependent threshold, it emits raw literals. Otherwise it reserves the literals header size, configures Huffman flags (`HUF_flags_bmi2`, repeat preference for low strategies, optimal depth for high strategies, and suspect-uncompressible sampling), and calls either `HUF_compress1X_repeat()` for small/single-stream cases or `HUF_compress4X_repeat()`.

After Huffman compression it checks minimum gain with `ZSTD_minGain()`. Failed compression, zero output, errors, or insufficient gain cause the function to restore `nextHuf` from `prevHuf` and emit raw literals. A one-byte Huffman result is treated as a possible single-symbol alphabet; when confirmed, it emits an RLE literals block. Successful new-table compression marks `nextHuf->repeatMode = HUF_repeat_check`; repeat mode writes a `set_repeat` header. The final header encodes type, one-stream/four-stream selector, decompressed literal size, and compressed literal size using 3, 4, or 5 bytes.

## State And Persistence
The persistent state is the Huffman repeat table. `prevHuf` is read, `nextHuf` is tentatively initialized from it, and `nextHuf` either remains a reused table, becomes a freshly built table pending repeat validation, or is restored on fallback. No file/global state is mutated. The entropy workspace must be 4-byte aligned and large enough for `HUF_WORKSPACE_SIZE`.

## Dependencies And Integration Points
This file includes `zstd_compress_literals.h`, which brings in compression internals and Huffman table types. It depends on common helpers for little-endian writes, bounded errors, debug logging, `ZSTD_minGain()`, and Huffman APIs from the common entropy layer. It is used by the regular block compressor and by superblock sub-block compression for literal sections.

## Risks And Edge Cases
Header sizing is sensitive to literal and compressed sizes; wrong thresholds corrupt the literals section. The RLE path asserts that all bytes are identical and that `dstCapacity >= 4`, so callers must satisfy the documented preconditions. The `cLitSize == 1` ambiguity is deliberately handled because it can mean either single-symbol alphabet or a legitimate one-byte compressed stream for tiny inputs. Fallback must restore `nextHuf`, or later repeat-mode decisions can reference a table that was never emitted.

## Test Signals
Round-trip tests should cover raw, RLE, compressed, and repeat literals; tiny inputs below threshold; exactly 31/32, 4095/4096, 1 KB, and 16 KB header boundary sizes; disabled literal compression; incompressible data; single-symbol data; and dictionary/repeat-table reuse across adjacent blocks. Differential tests should compare BMI2 and non-BMI2 outputs for decodability.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_compress_literals.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_compress_literals.h -->
# sources/compression/zstd/lib/compress/zstd_compress_literals.h

## Purpose
Declares the private literal-section compression API used inside zstd's compression library. It exposes raw, RLE, and Huffman/repeat literal compression entry points to block and superblock encoders.

## Important APIs, Types, And Functions
The header declares `ZSTD_noCompressLiterals()`, `ZSTD_compressRleLiteralsBlock()`, and `ZSTD_compressLiterals()`. The full compression API accepts previous and next `ZSTD_hufCTables_t`, a `ZSTD_strategy`, an entropy workspace, literal compression mode controls, a suspect-uncompressible hint, and a BMI2 flag. The comments document key preconditions: RLE input must contain one repeated byte and the entropy workspace must be 4-byte aligned and at least `HUF_WORKSPACE_SIZE`.

## Control Flow
The header is declarative. Callers choose the raw helper when literals must be stored uncompressed, the RLE helper when a single repeated byte is known, or `ZSTD_compressLiterals()` when the implementation should choose compressed, repeat, RLE, or raw output based on strategy and profitability.

## State And Persistence
No state is stored in the header. The API makes Huffman-table persistence explicit through `prevHuf` and `nextHuf`, allowing block-to-block repeat-mode reuse.

## Dependencies And Integration Points
It includes `zstd_compress_internal.h` for `ZSTD_hufCTables_t`, `ZSTD_minGain()`, `ZSTD_strategy`, and shared error/types. It is consumed by normal block compression and `zstd_compress_superblock.c`.

## Risks And Edge Cases
The risk is caller misuse of preconditions: insufficient destination capacity for RLE/raw headers, misaligned or undersized workspaces, or incorrect `prevHuf`/`nextHuf` lifetime. Because this is a private header, ABI stability is less important than keeping all internal callers synchronized with the implementation.

## Test Signals
Compile coverage across modules is the first signal. Runtime tests should exercise each declared function through block compression, including raw fallback, RLE literals, compressed literals, and repeat-Huffman reuse.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_compress_literals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_compress_sequences.c -->
# sources/compression/zstd/lib/compress/zstd_compress_sequences.c

## Purpose
Implements FSE table selection, FSE table construction, entropy cost estimation, and bitstream encoding for zstd sequence sections. It decides whether literal-length, match-length, and offset-code streams should use RLE, default, repeat, or newly compressed FSE tables, then encodes sequences in reverse order into a bitstream.

## Important APIs, Types, And Functions
`ZSTD_selectEncodingType()` selects `set_rle`, `set_basic`, `set_repeat`, or `set_compressed` for a symbol stream using frequency counts, prior repeat mode, default distributions, sequence count, strategy, and estimated costs. `ZSTD_buildCTable()` materializes the selected FSE table and writes any required normalized-count header bytes. `ZSTD_encodeSequences()` is the public sequence body encoder with optional dynamic BMI2 dispatch.

Cost helpers include `ZSTD_fseBitCost()`, `ZSTD_crossEntropyCost()`, `ZSTD_NCountCost()`, `ZSTD_entropyCost()`, `ZSTD_getFSEMaxSymbolValue()`, and `ZSTD_useLowProbCount()`. `ZSTD_BuildCTableWksp` overlays the entropy workspace for normalization and table building.

## Control Flow
Encoding-type selection first handles the all-one-symbol case as RLE, with a small special case favoring default tables for two or fewer symbols when allowed. For strategies below `ZSTD_lazy`, it uses heuristics to prefer repeat or default tables for small/cheap streams. For lazy and stronger strategies, it estimates basic, repeat, and newly compressed costs and chooses the cheapest valid mode. A compressed-table choice moves repeat mode to `FSE_repeat_check`.

`ZSTD_buildCTable()` then follows the selected mode: RLE builds an RLE table and writes one symbol byte, repeat copies the previous table, basic builds from default norms without output bytes, and compressed normalizes counts, writes an NCount header, and builds a new table. The compressed path may reduce the last symbol count by one to match zstd's sequence coding convention.

`ZSTD_encodeSequences_body()` initializes FSE states from the last sequence, writes raw extra bits for that last sequence, then walks sequences backward. For each sequence it FSE-encodes offset/match/literal symbols and writes literal-length, match-length, and offset extra bits with careful flush scheduling for 32-bit and 64-bit bit accumulators. Long offsets are split so the bit accumulator never overflows. Finally it flushes the three FSE states and closes the bitstream.

## State And Persistence
The file mutates FSE repeat modes passed by pointer and writes `nextCTable` instances that persist into the next block's entropy state. `ZSTD_buildCTable()` may copy `prevCTable` for repeat mode. The code tables (`llCodeTable`, `mlCodeTable`, `ofCodeTable`) are read from the sequence store and not owned here. The entropy workspace is temporary and reused by callers.

## Dependencies And Integration Points
It includes `zstd_compress_sequences.h`, which brings in FSE and compression internals. It depends on common FSE bit-cost, normalized-count, bitstream, and default distribution tables (`LL_defaultNorm`, `ML_defaultNorm`, `OF_defaultNorm`, `LL_bits`, `ML_bits`). It integrates with entropy-stat building in other compression files and with `zstd_compress_superblock.c` for sub-block sequence emission.

## Risks And Edge Cases
The encoder depends on reverse-order sequence emission and exact bit flush thresholds; changes can break decoder compatibility. Repeat table reuse must be rejected when a previous CTable cannot represent a counted symbol or has zero probability for a used symbol. `ZSTD_crossEntropyCost()` assumes `accuracyLog <= 8` and valid non-zero norm values. The compressed-table path mutates `count` by decrementing the last symbol in some cases, so callers must provide a mutable count buffer and expect that adjustment.

Long offsets are sensitive on 32-bit accumulators and when `windowLog > STREAM_ACCUMULATOR_MIN`. The intentional unsigned-underflow loop over `size_t n=nbSeq-2; n<nbSeq; n--` requires `nbSeq > 0`, which callers ensure by writing a separate zero-sequence header path.

## Test Signals
Round-trip coverage should include zero, one, and many sequences; RLE/default/repeat/compressed table modes for LL/ML/OF; repeat-table reuse after dictionaries; high-window long offsets; 32-bit builds; dynamic BMI2 and non-BMI2 paths; and fuzz cases around tiny destination capacities. Compatibility tests should include older decoder guard cases through the superblock path.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_compress_sequences.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_compress_sequences.h -->
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
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_compress_sequences.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_compress_superblock.c -->
# sources/compression/zstd/lib/compress/zstd_compress_superblock.c

## Purpose
Implements target-compressed-block-size support by compressing one logical zstd block as a superblock split into multiple zstd sub-blocks. It reuses a single set of entropy statistics across sub-blocks, writes entropy tables once, emits later sub-blocks in repeat mode, and falls back to uncompressed output when splitting cannot satisfy compression or compatibility constraints.

## Important APIs, Types, And Functions
The public entry point is `ZSTD_compressSuperBlock()`. Internal literal and sequence emitters are `ZSTD_compressSubBlock_literal()` and `ZSTD_compressSubBlock_sequences()`. `ZSTD_compressSubBlock()` assembles one compressed zstd block from literal and sequence sections and writes the block header. `ZSTD_compressSubBlock_multi()` estimates split points, compresses sub-blocks, writes a raw tail when needed, and maintains entropy/repcodes.

Sizing helpers include `ZSTD_seqDecompressedSize()`, `ZSTD_estimateSubBlockSize_literal()`, `ZSTD_estimateSubBlockSize_symbolType()`, `ZSTD_estimateSubBlockSize_sequences()`, `ZSTD_estimateSubBlockSize()`, `ZSTD_needSequenceEntropyTables()`, `countLiterals()`, and `sizeBlockSequences()`. `EstimatedBlockSize` holds estimated literal and full block sizes.

## Control Flow
`ZSTD_compressSuperBlock()` first calls `ZSTD_buildBlockEntropyStats()` over the full sequence store to produce next entropy tables and metadata. It then delegates to `ZSTD_compressSubBlock_multi()`.

`ZSTD_compressSubBlock_multi()` estimates the full compressed size. If the full estimate is larger than the source size, it bails out with 0 so the caller can emit a raw block. Otherwise it derives average literal and sequence costs, estimates the number of sub-blocks, and repeatedly chooses sequence counts with `sizeBlockSequences()`. Each non-final sub-block is compressed only if its compressed size is non-zero and smaller than its decompressed size; otherwise the candidate is coalesced with following data. The final sub-block is compressed similarly with the caller's `lastBlock` flag.

Literal entropy is written only when the superblock's Huffman metadata requires a new table. Sequence entropy starts as required for the first compressed sub-block, and later sub-blocks use `set_repeat`. If required entropy was never actually written, the function restores previous Huffman state or returns 0 to force raw output. If some source remains after compressed sub-blocks, it writes that suffix with `ZSTD_noCompressBlock()` and recomputes repeat offsets for the subset of sequences actually emitted.

## State And Persistence
The function consumes `zc->seqStore`, `zc->blockState.prevCBlock`, `zc->blockState.nextCBlock`, `zc->appliedParams`, `zc->tmpWorkspace`, and `zc->bmi2`. It mutates `nextCBlock->entropy` during entropy-stat building and may restore `nextCBlock->entropy.huf` from the previous block if literal entropy was not emitted. It updates `nextCBlock->rep` when skipped sequences require repeat-code repair. The workspace is temporary.

## Dependencies And Integration Points
This file depends on common zstd block format helpers, `hist.h`, `zstd_compress_internal.h`, `zstd_compress_sequences.h`, and `zstd_compress_literals.h`. It integrates with the main compression path when `targetCBlockSize` is set. The output is a sequence of valid zstd blocks representing the input range, with only the last sub-block carrying the frame's last-block marker.

## Risks And Edge Cases
The highest-risk logic is entropy table emission across split sub-blocks. If a new table is selected but no compressed sub-block writes it, later repeat-mode blocks would be invalid, so the implementation forces fallback. Compatibility guards avoid old decoder bugs when sequence headers/bodies are too small. Literal header size is guessed before final compressed size is known; expansion beyond the guessed header width triggers raw literal fallback.

Split estimates are heuristic and can choose sub-blocks that do not compress; the code handles this by coalescing, but ratio and target size can vary. Recomputing repcodes after skipped sequences is subtle and must match `ZSTD_updateRep()` semantics. `ZSTD_seqDecompressedSize()` asserts literal accounting, so long-length handling through `ZSTD_getSequenceLength()` is required.

## Test Signals
Tests should enable `targetCBlockSize` across compressible, incompressible, mixed, and dictionary inputs; validate round trips; inspect that produced block sizes roughly follow target constraints; cover first-sub-block entropy, repeat-mode later sub-blocks, zero-sequence sub-blocks, raw tail fallback, and old-decoder compatibility guards. State tests should verify repeat offsets after partially compressed superblocks.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_compress_superblock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_compress_superblock.h -->
# sources/compression/zstd/lib/compress/zstd_compress_superblock.h

## Purpose
Declares the private superblock compression entry point used when zstd tries to target a compressed block size. It is the interface between the main compressor and the multi-sub-block implementation.

## Important APIs, Types, And Functions
The header declares `ZSTD_compressSuperBlock(ZSTD_CCtx* zc, void* dst, size_t dstCapacity, void const* src, size_t srcSize, unsigned lastBlock)`. The comment documents that it compresses a given block into multiple sub-blocks around `targetCBlockSize`.

## Control Flow
The header is declarative. A caller with a populated `ZSTD_CCtx`, sequence store, and block state invokes this function instead of the normal single-block emission path when target compressed block sizing is active.

## State And Persistence
State is owned by `ZSTD_CCtx`; the API passes the context directly so the implementation can access sequence store, entropy state, parameters, BMI2 status, and scratch workspace.

## Dependencies And Integration Points
It includes public `zstd.h` for `ZSTD_CCtx`. The implementation also integrates with literal and sequence encoders, but those details are intentionally hidden from this header.

## Risks And Edge Cases
Because the function receives the full context, changes to `ZSTD_CCtx_s` internals can affect the implementation without signature changes. Callers must only use it after sequence generation and entropy workspace initialization.

## Test Signals
Compile coverage plus target-block-size compression/decompression tests are the main validation signals.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_compress_superblock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_cwksp.h -->
# sources/compression/zstd/lib/compress/zstd_cwksp.h

## Purpose
Implements zstd's compression workspace arena. The workspace packs context objects, entropy workspaces, hash/chain tables, aligned buffers, init-once buffers, and unaligned buffers into one contiguous allocation or caller-provided static buffer while supporting reuse across compressions and parameter changes.

## Important APIs, Types, And Functions
`ZSTD_cwksp` tracks `workspace`, `workspaceEnd`, `objectEnd`, `tableEnd`, `tableValidEnd`, `allocStart`, `initOnceStart`, allocation failure, oversized duration, current phase, and static/dynamic ownership. Allocation phases are `ZSTD_cwksp_alloc_objects`, `ZSTD_cwksp_alloc_aligned_init_once`, `ZSTD_cwksp_alloc_aligned`, and `ZSTD_cwksp_alloc_buffers`; ownership mode is `ZSTD_cwksp_dynamic_alloc` or `ZSTD_cwksp_static_alloc`.

Sizing/alignment helpers include `ZSTD_cwksp_align()`, `ZSTD_cwksp_alloc_size()`, `ZSTD_cwksp_aligned_alloc_size()`, `ZSTD_cwksp_aligned64_alloc_size()`, `ZSTD_cwksp_slack_space_required()`, and `ZSTD_cwksp_bytes_to_align_ptr()`. Reservation APIs include `ZSTD_cwksp_reserve_object()`, `ZSTD_cwksp_reserve_object_aligned()`, `ZSTD_cwksp_reserve_table()`, `ZSTD_cwksp_reserve_aligned_init_once()`, `ZSTD_cwksp_reserve_aligned64()`, and `ZSTD_cwksp_reserve_buffer()`.

Lifecycle and validation helpers include `ZSTD_cwksp_init()`, `ZSTD_cwksp_create()`, `ZSTD_cwksp_free()`, `ZSTD_cwksp_move()`, `ZSTD_cwksp_clear()`, `ZSTD_cwksp_clear_tables()`, `ZSTD_cwksp_clean_tables()`, `ZSTD_cwksp_mark_tables_dirty()`, `ZSTD_cwksp_mark_tables_clean()`, `ZSTD_cwksp_assert_internal_consistency()`, `ZSTD_cwksp_sizeof()`, `ZSTD_cwksp_used()`, `ZSTD_cwksp_available_space()`, and waste checks for oversized workspaces.

## Control Flow
Workspace layout grows objects/tables forward from the beginning and buffers/aligned allocations backward from the end: `[objects][tables ->] free [<- buffers][<- aligned][<- init once]`. Allocation must proceed by phase. Moving into the table/init-once phase aligns the start of tables to 64 bytes and sets initial validity markers. Object allocations are only valid in the first phase. Tables are forward allocations with 64-byte alignment and U32-sized byte counts. Aligned and buffer allocations reserve space from the high end and may reduce `tableValidEnd` if they overlap previously valid table space.

Clearing invalidates tables and high-end allocations but preserves object allocations; table cleaning zeros only the portion between `tableValidEnd` and `tableEnd`; dirty/clean markers let match tables be reused without full clearing when their values remain bounded.

## State And Persistence
The workspace persists for the lifetime of a compression context or CDict. Static objects and some init-once buffers can carry data across compressions by design. Table memory can be considered valid, dirty, or cleared based on `tableValidEnd`. `workspaceOversizedDuration` persists to help callers decide when a workspace is wastefully large. ASAN/MSAN hooks poison and unpoison regions to make misuse visible under sanitizers.

## Dependencies And Integration Points
The file depends on zstd custom allocation wrappers, common internals, portability/compiler macros, and power-of-two checks. `ZSTD_CCtx` and `ZSTD_CDict` allocation/reset code use it to allocate all compression-side data structures. Match finders rely on the table-validity contract to avoid unnecessary clears, and entropy/literal/sequence code relies on aligned scratch buffers.

## Risks And Edge Cases
Phase ordering is strict; reserving the wrong category after advancing too far fails. Pointer comparisons and alignment assumptions are central to internal consistency. Under ASAN, allocation sizes include redzones and dynamic workspaces are poisoned/unpoisoned; static workspaces cannot always be poisoned at teardown. Init-once memory intentionally may contain prior data, so users must avoid leaking or semantically depending on old contents.

Integer overflow and underflow in size estimation are risks when calculating workspace requirements. Table allocations are not redzoned, and they require byte counts to be multiples of both `sizeof(U32)` and 64. `ZSTD_cwksp_free()` clears the descriptor before freeing the captured pointer, so ownership must be initialized correctly.

## Test Signals
Sanitizer builds are especially valuable: ASAN for redzones, MSAN for uninitialized reads, and fuzzing with repeated context reuse and parameter changes. Unit-style tests should cover static and dynamic workspaces, allocation phase violations, table dirty/clean transitions, clear versus clear_tables behavior, workspace move/free, estimated-space bounds, and oversized-duration tracking.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_cwksp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_double_fast.c -->
# sources/compression/zstd/lib/compress/zstd_double_fast.c

## Purpose
Implements zstd's double-fast block compressor. It uses two hash tables, a long 8-byte hash and a shorter min-match hash, to find better matches than the single-table fast compressor while keeping a speed-oriented parse. It provides no-dictionary, attached dictionary match-state, and external-dictionary variants, plus dictionary table-fill helpers.

## Important APIs, Types, And Functions
Exported functions are `ZSTD_fillDoubleHashTable()`, `ZSTD_compressBlock_doubleFast()`, `ZSTD_compressBlock_doubleFast_dictMatchState()`, and `ZSTD_compressBlock_doubleFast_extDict()`. Static fill helpers specialize CDict table filling with short-cache tagged indices and CCtx table filling with plain indices. Generic compressors are specialized by macro for min-match lengths 4, 5, 6, and 7.

The main implementations are `ZSTD_compressBlock_doubleFast_noDict_generic()`, `ZSTD_compressBlock_doubleFast_dictMatchState_generic()`, and `ZSTD_compressBlock_doubleFast_extDict_generic()`. They use shared helpers from `zstd_compress_internal.h`: `ZSTD_hashPtr()`, `ZSTD_selectAddr()`, `ZSTD_count()`, `ZSTD_count_2segments()`, `ZSTD_storeSeq()`, `ZSTD_getLowestPrefixIndex()`, `ZSTD_getLowestMatchIndex()`, `ZSTD_index_overlap_check()`, and short-cache tag helpers.

## Control Flow
Table fill inserts positions every three bytes. The CDict variant stores packed index/tag entries in both hash tables and may fill additional positions for full loading; the CCtx variant stores plain indices. The long table hashes with match length 8, while the small table hashes with the configured `minMatch`.

The no-dictionary compressor loops from the current anchor. At each candidate it updates both hash tables, checks a repcode at `ip+1`, checks an 8-byte long match, checks a short match, and if a short match is found probes a long match at `ip+1` to prefer the longer parse. It stores sequences, performs complementary insertion around the match end, then consumes immediate repeat-code matches.

The dict-match-state variant checks current-prefix long/short candidates and CDict long/short candidates using packed tags to avoid unnecessary dictionary reads. It translates dictionary indices into the current referential with `dictIndexDelta` and counts matches across dictionary and prefix with `ZSTD_count_2segments()`. The ext-dict variant performs similar two-segment counting against `window.dictBase` and falls back to the no-dict variant when the external dictionary is invalidated by distance.

## State And Persistence
The compressor mutates `ms->hashTable` for long hashes, `ms->chainTable` for small hashes, `seqStore`, and the caller's repeat offsets. It reads match window state, compression parameters, optional `dictMatchState`, and prefetch settings. The final return value is the trailing literal byte count not represented by a sequence; callers later encode those literals. Dictionary tables in CDict mode persist and can use short-cache tags.

## Dependencies And Integration Points
This file is compiled unless `ZSTD_EXCLUDE_DFAST_BLOCK_COMPRESSOR` is defined. It includes `zstd_double_fast.h` and internal compression helpers. The block compressor dispatcher selects these functions for `ZSTD_dfast` strategy modes. It integrates with workspace allocation because `hashTable` and `chainTable` are allocated in `ZSTD_cwksp`, and with entropy encoding through `SeqStore_t`.

## Risks And Edge Cases
The code relies on careful pointer bounds and hash-table update order. Repcode checks at `ip+1` require offset validity and overlap checks, especially for dictionary references. No-dict mode temporarily invalidates repeat offsets outside the prefix and restores saved offsets during cleanup. Dict-match-state mode asserts repcodes are representable and does not support zero-disabling the same way as some no-dict paths.

Choosing between short and long matches affects compression ratio and must preserve decoder-equivalent sequence semantics. Tagged dictionary table entries require correct packing/unpacking and index high bits. Ext-dict mode must count across two segments and choose the correct lower bound for backward extension.

## Test Signals
Round-trip tests should cover `ZSTD_dfast` with minMatch 4-7, no dictionary, prefix, attached CDict, and external dictionary inputs; repeated blocks to validate table reuse and repcode persistence; small blocks near `HASH_READ_SIZE`; long matches versus short-match-at-current plus long-match-at-next decisions; and sanitizer/fuzzer runs for window boundary and non-contiguous input cases.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_double_fast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_double_fast.h -->
# sources/compression/zstd/lib/compress/zstd_double_fast.h

## Purpose
Declares the private double-fast compressor interface and provides null macros when the double-fast block compressor is excluded at build time.

## Important APIs, Types, And Functions
When enabled, the header declares `ZSTD_fillDoubleHashTable()`, `ZSTD_compressBlock_doubleFast()`, `ZSTD_compressBlock_doubleFast_dictMatchState()`, and `ZSTD_compressBlock_doubleFast_extDict()`. It also defines dispatcher macros `ZSTD_COMPRESSBLOCK_DOUBLEFAST`, `ZSTD_COMPRESSBLOCK_DOUBLEFAST_DICTMATCHSTATE`, and `ZSTD_COMPRESSBLOCK_DOUBLEFAST_EXTDICT`, which become `NULL` if `ZSTD_EXCLUDE_DFAST_BLOCK_COMPRESSOR` is set.

## Control Flow
The header is declarative. Compressor selection code can use the macros without conditionalizing every call site on build exclusion.

## State And Persistence
No state is owned here. The declared functions operate on `ZSTD_MatchState_t`, `SeqStore_t`, and repeat-code arrays owned by the caller.

## Dependencies And Integration Points
It includes common memory types and `zstd_compress_internal.h` for match-state and sequence-store definitions. It integrates with the block compressor selector and with CDict/CCtx table-loading code.

## Risks And Edge Cases
Build configurations excluding double-fast must handle the `NULL` macros and avoid selecting those compressors. Signature drift between this header and the implementation would break private compressor dispatch.

## Test Signals
Compile tests with and without `ZSTD_EXCLUDE_DFAST_BLOCK_COMPRESSOR`, plus compression tests that select double-fast in all dictionary modes, validate the header contract.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_double_fast.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_fast.c -->
# sources/compression/zstd/lib/compress/zstd_fast.c

## Purpose
Implements zstd's fastest single-hash-table block compressor. It provides table-filling and block parsing for no dictionary, attached dictionary match-state, and external dictionary modes. The parser prioritizes speed through pipelined hash/table/match operations, adaptive skipping, and specialized min-match variants.

## Important APIs, Types, And Functions
Exported functions are `ZSTD_fillHashTable()`, `ZSTD_compressBlock_fast()`, `ZSTD_compressBlock_fast_dictMatchState()`, and `ZSTD_compressBlock_fast_extDict()`. Static fill helpers distinguish CDict tagged-index tables from CCtx plain-index tables. `ZSTD_match4Found_cmov()` and `ZSTD_match4Found_branch()` provide two candidate validation strategies; no-dict mode selects cmov for smaller windows where candidate-in-range is less predictable.

Main generic parsers are `ZSTD_compressBlock_fast_noDict_generic()`, `ZSTD_compressBlock_fast_dictMatchState_generic()`, and `ZSTD_compressBlock_fast_extDict_generic()`. Macro-generated wrappers specialize min-match lengths 4-7 and cmov/branch variants.

## Control Flow
`ZSTD_fillHashTable()` inserts positions every three bytes from `nextToUpdate` to the requested end. CDict filling uses short-cache tag packing and full loading; CCtx filling uses plain hashes and currently asserts fast loading.

The no-dict compressor uses a deliberately pipelined loop over adjacent and stepped positions (`ip0`..`ip3`). It interleaves repcode checks, hash computation, table lookup, table writeback, and match comparison to reduce dependency stalls. When a repcode or normal match is found, it optionally extends backward, counts forward match length, stores a sequence, inserts complementary positions, consumes immediate repeat-code matches, and restarts. It returns the final literal tail size.

The dict-match-state compressor checks current-prefix matches and attached dictionary matches. Dictionary hash entries carry short-cache tags, and dictionary matches are only used in one path when the normal prefix match is invalid to mirror ext-dict parsing behavior. The ext-dict compressor resolves each index against `dictBase` or `base`, counts matches across dictionary and prefix, and falls back to no-dict mode if the external dictionary has been invalidated.

## State And Persistence
The function mutates `ms->hashTable`, `seqStore`, and repeat offsets. It reads `ms->window`, `cParams`, `dictMatchState`, and `prefetchCDictTables`. It updates only the first two repeat offsets directly; the broader repeat-code convention is completed by the shared sequence encoding path. Saved invalid rep offsets are restored during cleanup so cross-block history remains correct even when a repcode cannot be used in the current prefix.

## Dependencies And Integration Points
It includes `zstd_compress_internal.h` and `zstd_fast.h`. The block compressor selector chooses these functions for `ZSTD_fast` strategy modes. It integrates with the workspace-managed hash table, dictionary table loading, window/dictionary validity logic, and later entropy encoding via `SeqStore_t`.

## Risks And Edge Cases
This code is highly performance-tuned and sensitive to instruction ordering. Comments note places where boolean expressions, inline assembly barriers, or writeback order are chosen to influence branch generation and safety. Bounds are guarded by `ilimit = iend - HASH_READ_SIZE`, but many reads intentionally rely on that invariant. Repcode invalidation/restoration at prefix boundaries is subtle. Dict-match-state asserts that repcodes are within dictionary+prefix length and does not support zero-disabled repcodes in the same way as no-dict mode.

Non-contiguous input and ext-dict overlap require correct `prefixStartIndex`, `dictStartIndex`, and `lowLimit` calculations. Short-cache tagged CDict entries must be compared before dictionary memory reads to avoid expensive misses without dropping valid matches.

## Test Signals
Round-trip tests should force `ZSTD_fast` with minMatch 4-7, small and large windows, cmov and branch variants, no dictionary, prefix dictionaries, attached CDicts, external dictionaries, non-contiguous streaming segments, and immediate repeat-code chains. Performance regression tests are also important because many transformations that preserve correctness can hurt the intended fast path.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_fast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_fast.h -->
# sources/compression/zstd/lib/compress/zstd_fast.h

## Purpose
Declares the private fast block compressor API for zstd. It exposes hash-table filling and the three fast compressor variants used by the block compressor dispatcher.

## Important APIs, Types, And Functions
The header declares `ZSTD_fillHashTable()`, `ZSTD_compressBlock_fast()`, `ZSTD_compressBlock_fast_dictMatchState()`, and `ZSTD_compressBlock_fast_extDict()`. All compression functions share the `ZSTD_BlockCompressor_f`-style signature with `ZSTD_MatchState_t`, `SeqStore_t`, repeat offsets, source pointer, and source size.

## Control Flow
The header is declarative. Callers fill tables for a CCtx or CDict with `ZSTD_fillHashTable()`, then select the appropriate compression variant based on dictionary mode: no dictionary, attached dictionary match-state, or external dictionary.

## State And Persistence
No state is stored in the header. The declared functions mutate caller-owned match-state tables, sequence store, and repeat-code history.

## Dependencies And Integration Points
It includes common `mem.h` for `U32` and `zstd_compress_internal.h` for compression-private types. It is used by compressor selection and dictionary/table initialization code.

## Risks And Edge Cases
The private signature assumes callers have already initialized window state, hash-table memory, compression parameters, and repeat offsets. Selecting the wrong variant for the active dictionary mode can produce invalid references.

## Test Signals
Compile coverage plus compression round trips for all fast dictionary modes validate the interface. Dispatcher tests should confirm `ZSTD_fast` selects these functions under the expected parameter combinations.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_fast.h -->
