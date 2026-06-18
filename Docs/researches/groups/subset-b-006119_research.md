<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_internal.h -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_internal.h

## Purpose
`zstd_compress_internal.h` is the private compression spine for this Zstd copy. It defines compressor context state, match/window state, sequence storage, entropy table metadata, hash helpers, repeat-offset helpers, block/raw encoders, and private function declarations used by the compressor implementation and nearby dictionary/benchmark code.

## Important APIs, Types, and Functions
Key types include `ZSTD_CCtx_s`, `ZSTD_CCtx_params_s`, `ZSTD_MatchState_t`, `ZSTD_window_t`, `SeqStore_t`, `SeqDef`, `rawSeq`, `RawSeqStore_t`, `ZSTD_compressedBlockState_t`, `ZSTD_entropyCTables_t`, `ZSTD_entropyCTablesMetadata_t`, `ldmState_t`, `ldmParams_t`, `optState_t`, and `ZSTD_blockSplitCtx`. Important helpers are `ZSTD_getSequenceLength()`, `ZSTD_LLcode()`, `ZSTD_MLcode()`, `ZSTD_noCompressBlock()`, `ZSTD_rleCompressBlock()`, `ZSTD_minGain()`, `ZSTD_literalsCompressionIsDisabled()`, `ZSTD_storeSeqOnly()`, `ZSTD_storeSeq()`, `ZSTD_updateRep()`, `ZSTD_newRep()`, `ZSTD_count()`, `ZSTD_count_2segments()`, `ZSTD_hashPtr()`, `ZSTD_hashPtrSalted()`, rolling-hash helpers, `ZSTD_window_*()` maintenance helpers, `ZSTD_matchState_dictMode()`, and short-cache helpers `ZSTD_writeTaggedIndex()`/`ZSTD_comparePackedTags()`.

## Control Flow
Compressor front ends select block compressors through `ZSTD_selectBlockCompressor()` and use the context fields declared here to hold requested/applied params, window state, block entropy states, sequence stores, temporary workspace, dictionaries, streaming buffers, and external sequence producer buffers. Matchfinders append matches with `ZSTD_storeSeq()`, which copies literals into `SeqStore_t`, records long literal or match lengths through `longLengthType`, and emits `offBase` values in the repeat-code/full-offset sum type. Entropy and block writers later consume the same sequence/literal/code arrays.

## State and Persistence
`ZSTD_CCtx_s` persists across calls and contains reusable workspace allocations, previous/next block entropy, repeat offsets, streaming positions, dictionary references, pledged/consumed/produced byte counts, checksum state, and table-backed match state. `ZSTD_window_t` persists pointer bases and 32-bit indices; overflow correction adjusts `base`, `dictBase`, `lowLimit`, and `dictLimit` while preserving hash/chain cycle bits. `ZSTD_MatchState_t` persists hash tables, chain tables, dictionary match state links, LDM input, row-cache fields, and parser behavior flags.

## Dependencies and Integration Points
This header depends on common Zstd internals, bits, workspace allocation, and block pre-splitting. It is included by fast/double-fast matchfinders, literal/sequence/superblock encoders, lazy/optimal paths outside this work item, and dictionary builder code. The declarations for `ZSTD_buildBlockEntropyStats()`, `ZSTD_loadCEntropy()`, streaming init, advanced compression, external sequences, and deprecated internal wrappers connect private compressor modules to the public API layer and optional multithreaded compression.

## Risks
The highest-risk areas are pointer/index arithmetic around `base`, `dictBase`, `lowLimit`, and `dictLimit`; repeat-code translation for zero-literal sequences; one-long-length representation in `SeqStore_t`; intentional unsigned underflow checks; and wildcopy literal copying near block ends. Overflow correction requires table users to apply the returned correction consistently. External sequences are explicitly unverified and can cause out-of-bounds access if invalid.

## Test Signals
Useful tests cover no-dict, prefix-dict, ext-dict, attached CDict, dictionary invalidation after window distance, index overflow correction, first-block determinism, raw/RLE block fallback, long literal and match lengths above 64 KiB, zero-literal repcode updates, external sequence validation/fallback behavior, 32-bit builds, fuzzing with frequent overflow correction, and ASAN/MSAN/UBSAN runs around wildcopy and two-segment matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_literals.c -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_literals.c

## Purpose
`zstd_compress_literals.c` writes the literals section of a compressed block. It handles raw literals, RLE literals, and Huffman-compressed literals while deciding when compression is not worth the cost.

## Important APIs, Types, and Functions
Exported functions are `ZSTD_noCompressLiterals()`, `ZSTD_compressRleLiteralsBlock()`, and `ZSTD_compressLiterals()`. Internal helpers are debug-only `showHexa()`, `allBytesIdentical()`, and `ZSTD_minLiteralsToCompress()`. The code updates `ZSTD_hufCTables_t` repeat mode and CTable state supplied by the caller.

## Control Flow
`ZSTD_compressLiterals()` starts by copying `prevHuf` into `nextHuf`, then immediately emits raw literals when literal compression is disabled or below the strategy-dependent threshold. Otherwise it chooses one-stream Huffman for small input or valid small repeated tables, four-stream Huffman for larger input, sets HUF flags from BMI2/strategy/uncompressible suspicion, and calls `HUF_compress1X_repeat()` or `HUF_compress4X_repeat()`. If the result is zero, an error, or does not beat `ZSTD_minGain()`, the function restores `nextHuf` and emits raw literals. A one-byte HUF result is converted to an RLE literal block when the input really has a single symbol. Successful new-table compression marks `nextHuf->repeatMode = HUF_repeat_check` and writes the literal-section header.

## State and Persistence
The file itself has no persistent global state. It mutates caller-owned entropy state by copying/reusing/refreshing HUF tables and repeat mode. Output persistence is the byte format in `dst`: a variable-width literal section header followed by raw bytes, one RLE byte, or Huffman payload.

## Dependencies and Integration Points
The implementation depends on `zstd_compress_literals.h`, which brings in compression internals, HUF tables, `ZSTD_minGain()`, block constants, `MEM_writeLE*()`, and error macros. It is used by regular block compression and the superblock path; `zstd_compress_superblock.c` also calls the raw and RLE helpers directly when building subblocks from precomputed entropy.

## Risks
Header-size selection is sensitive to literal and compressed sizes. `ZSTD_compressRleLiteralsBlock()` asserts that all bytes are identical and `dstCapacity >= 4`, so callers must honor the contract. The HUF return value `1` has overloaded meaning and requires the explicit identical-byte check. Incorrect repeat-mode restoration on fallback would corrupt later blocks.

## Test Signals
Tests should exercise empty/small/large literals, disabled literal compression, fast-strategy target-length auto-disable behavior, RLE single-symbol blocks, HUF repeat reuse, new HUF table emission, compressed output that expands and falls back to raw, suspect-uncompressible mode, BMI2 and non-BMI2 paths, and destination-too-small errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_literals.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_literals.h -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_literals.h

## Purpose
`zstd_compress_literals.h` declares the private literals-section encoder API used by block and superblock compression code.

## Important APIs, Types, and Functions
It exposes `ZSTD_noCompressLiterals()`, `ZSTD_compressRleLiteralsBlock()`, and `ZSTD_compressLiterals()`. The declarations depend on `ZSTD_hufCTables_t`, `ZSTD_strategy`, `HUF_WORKSPACE_SIZE`, and shared compression constants from `zstd_compress_internal.h`.

## Control Flow
Callers choose between raw/RLE helpers for known special cases or call `ZSTD_compressLiterals()` with source bytes, destination capacity, aligned entropy workspace, previous and next HUF table state, strategy, literal-compression controls, uncompressible-input hint, and BMI2 flag.

## State and Persistence
The header owns no state. Its API makes state movement explicit through `prevHuf` and `nextHuf`, allowing block encoders to preserve repeatable Huffman tables across blocks and roll back when compression falls back to raw literals.

## Dependencies and Integration Points
This header is included by `zstd_compress_literals.c` and `zstd_compress_superblock.c`. It bridges literal payload encoding with the entropy state defined in the internal compressor header.

## Risks
The contracts documented here are important: the entropy workspace must be 4-byte aligned and at least `HUF_WORKSPACE_SIZE`, RLE input must contain one repeated byte, and RLE destination capacity must be at least four bytes. Violating these assumptions is mostly guarded by assertions, not robust runtime checks.

## Test Signals
Compile coverage should include all users of the header. Runtime tests should verify the documented preconditions through normal block encoding, superblock subblock encoding, raw fallback, RLE literals, and repeated HUF table reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_literals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_sequences.c -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_sequences.c

## Purpose
`zstd_compress_sequences.c` selects FSE encoding modes for sequence symbol streams, builds FSE compression tables, estimates repeat/default/compressed costs, and encodes sequences into the Zstd bitstream.

## Important APIs, Types, and Functions
Public-internal APIs are `ZSTD_selectEncodingType()`, `ZSTD_buildCTable()`, `ZSTD_encodeSequences()`, `ZSTD_fseBitCost()`, and `ZSTD_crossEntropyCost()`. Important helpers include `ZSTD_getFSEMaxSymbolValue()`, `ZSTD_useLowProbCount()`, `ZSTD_NCountCost()`, `ZSTD_entropyCost()`, `ZSTD_encodeSequences_body()`, `ZSTD_encodeSequences_default()`, and the optional BMI2 wrapper. `ZSTD_BuildCTableWksp` provides normalized-count and FSE build workspace.

## Control Flow
`ZSTD_selectEncodingType()` first handles RLE/basic single-symbol cases, then for fast strategies uses heuristics favoring repeat or default tables, and for lazy-or-better strategies estimates bit costs for default, repeat, and freshly compressed FSE tables. `ZSTD_buildCTable()` materializes the selected type: RLE writes one symbol byte, repeat copies the previous CTable, basic builds from default norms, and compressed normalizes counts, writes an NCount header, and builds a new CTable. `ZSTD_encodeSequences()` dispatches to BMI2 or default encoding, initializes final FSE states from the last sequence, writes extra bits and FSE symbols in reverse sequence order, then flushes the three states.

## State and Persistence
The file keeps only static lookup data for inverse probability costs. It mutates caller-owned FSE CTables and count arrays. Encoded persistence is the sequences section body: optional FSE table descriptions followed by a reverse-order bitstream whose interpretation depends on LL/ML/OF code tables and repeat/default state selected earlier.

## Dependencies and Integration Points
The file depends on `zstd_compress_sequences.h`, FSE APIs, bitstream APIs, default normalized distributions, LL/ML extra-bit tables, `SeqDef`, and CPU feature macros. It is used by block entropy construction and by `zstd_compress_superblock.c` to write each subblock's sequence section.

## Risks
The reverse bitstream has tight 32-bit vs 64-bit flush requirements. Long offsets require special splitting so the bit accumulator is not overfilled. Repeat-table use must reject tables that cannot represent active symbols or assign zero probability to used symbols. `ZSTD_buildCTable()` deliberately decrements the final symbol count in compressed mode when possible; mistakes there affect normalization and decoder compatibility.

## Test Signals
Tests should cover set_basic, set_rle, set_repeat, and set_compressed choices for LL/ML/OF streams; repeat table rejection; default table allowed/disallowed paths; low and high sequence counts around the low-probability heuristic; long offsets with large window logs; BMI2/non-BMI2 encoding; small destination buffers; and decode round trips for blocks with one, two, many, and maximum-code symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_sequences.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_sequences.h -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_sequences.h

## Purpose
`zstd_compress_sequences.h` declares the private sequence entropy and bitstream encoding API for Zstd compression.

## Important APIs, Types, and Functions
It defines `ZSTD_DefaultPolicy_e` and declares `ZSTD_selectEncodingType()`, `ZSTD_buildCTable()`, `ZSTD_encodeSequences()`, `ZSTD_fseBitCost()`, and `ZSTD_crossEntropyCost()`.

## Control Flow
Callers count LL/ML/OF code frequencies, ask `ZSTD_selectEncodingType()` which encoding mode to use, call `ZSTD_buildCTable()` to write table metadata and prepare CTables, then call `ZSTD_encodeSequences()` with CTables, code arrays, sequence array, long-offset mode, and BMI2 mode.

## State and Persistence
The header owns no state. Its APIs operate on caller-provided FSE repeat modes, CTables, code tables, count arrays, and entropy workspaces. The resulting state persists in the next block's entropy tables and in the emitted sequence-section bytes.

## Dependencies and Integration Points
It includes `zstd_compress_internal.h` for `SeqDef`, `fse.h` for FSE tables/repeat modes, and `zstd_internal.h` for symbol encoding types and strategy. The header is consumed by sequence compression, block entropy building, and superblock compression.

## Risks
The API assumes frequency counts, max symbols, default norms, previous CTables, and workspace sizes are consistent. Passing a default table when defaults are disallowed, or a previous CTable that cannot encode the current symbol range, will lead to fallback/error paths in the implementation.

## Test Signals
Compile and runtime coverage should verify all declared paths through normal block compression, dictionary repeat-table reuse, superblock subblocks, long-offset blocks, and destination-capacity failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_sequences.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_superblock.c -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_superblock.c

## Purpose
`zstd_compress_superblock.c` implements target-compressed-block-size support. It takes one compressor block's sequence store and entropy statistics, splits it into several compressed Zstd subblocks around `targetCBlockSize`, and falls back to raw blocks when subblock compression is not beneficial or would violate entropy/header contracts.

## Important APIs, Types, and Functions
The exported entry point is `ZSTD_compressSuperBlock()`. Key internal functions include `ZSTD_compressSubBlock_literal()`, `ZSTD_seqDecompressedSize()`, `ZSTD_compressSubBlock_sequences()`, `ZSTD_compressSubBlock()`, `ZSTD_estimateSubBlockSize_literal()`, `ZSTD_estimateSubBlockSize_sequences()`, `ZSTD_estimateSubBlockSize()`, `ZSTD_needSequenceEntropyTables()`, `countLiterals()`, `sizeBlockSequences()`, and `ZSTD_compressSubBlock_multi()`. `EstimatedBlockSize` carries estimated literal and total block sizes.

## Control Flow
`ZSTD_compressSuperBlock()` first calls `ZSTD_buildBlockEntropyStats()` over the whole block, producing next entropy tables plus metadata. `ZSTD_compressSubBlock_multi()` estimates full-block compressed size, computes average literal and sequence costs, derives a subblock count from `targetCBlockSize`, and chooses sequence ranges with `sizeBlockSequences()`. Each subblock writes a Zstd block header, literal section, and sequence section through `ZSTD_compressSubBlock()`. Literal entropy is written only once when needed, and following subblocks use repeat/treeless forms. Sequence entropy is written on the first successful compressed subblock, then repeat mode is used. Failed or non-beneficial subblocks are coalesced or, at the end, emitted raw.

## State and Persistence
The function mutates `zc->blockState.nextCBlock->entropy` and possibly its repeat offsets. It consumes `zc->seqStore` arrays but does not own them. It tracks local pointers into literals, sequences, LL/ML/OF code tables, input, and output so partial compressed and raw subblocks still cover the original block in order.

## Dependencies and Integration Points
The file depends on common block constants, histogram counting, sequence cost helpers, literal helpers, and internal context structures. It is used when `ZSTD_CCtx_params.targetCBlockSize` requests bounded compressed block sizes. It integrates with old-decoder compatibility checks for small FSE NCount/bitstream combinations and tiny repeat-mode sequence bodies.

## Risks
The split heuristic is estimate-driven and can coalesce or raw-fallback when estimates are wrong. It must preserve entropy table contracts: if table metadata says new sequence entropy must be emitted but no subblock writes it, compression must fail back to raw. Literal header sizing can be guessed too small when entropy is included. If some input tail is raw-emitted after skipped sequences, repeat offsets must be regenerated from committed sequences to keep the next block correct.

## Test Signals
Tests should cover target sizes below, near, and above normal block compressed sizes; no-sequence blocks; many-sequence blocks; first/last subblock boundaries; entropy tables written once then repeated; raw fallback for incompressible data; decoder compatibility guards; repcode regeneration after partial raw tail; destination-too-small errors; and round trips with dictionaries and large windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_superblock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_superblock.h -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_superblock.h

## Purpose
`zstd_compress_superblock.h` declares the private advanced compression entry point for target compressed block sizing.

## Important APIs, Types, and Functions
It includes `<linux/zstd.h>` for `ZSTD_CCtx` and declares `ZSTD_compressSuperBlock(ZSTD_CCtx* zc, void* dst, size_t dstCapacity, void const* src, size_t srcSize, unsigned lastBlock)`.

## Control Flow
Callers invoke `ZSTD_compressSuperBlock()` after matchfinding has populated the context sequence store. The function compresses the provided source block into one or more Zstd blocks sized around the context target, setting the final block marker according to `lastBlock`.

## State and Persistence
The header has no state. The declared function uses and updates state inside `ZSTD_CCtx`, especially sequence storage, entropy tables, block state, temporary workspace, BMI2 flag, and applied compression parameters.

## Dependencies and Integration Points
This header is used by the main compressor when `targetCBlockSize` is active. It intentionally exposes only the single superblock function rather than the subblock helpers.

## Risks
The API relies on an initialized `ZSTD_CCtx` with a valid sequence store and temporary workspace. Calling it outside the normal block-compression flow would violate hidden invariants from `zstd_compress_internal.h`.

## Test Signals
Compile coverage should ensure the main compressor can include this header in kernel-style builds. Runtime tests should enable target compressed block size and verify last-block handling, size targeting, fallback behavior, and decompression round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_superblock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_cwksp.h -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_cwksp.h

## Purpose
`zstd_cwksp.h` implements Zstd's private compression workspace arena. It packs static objects, reusable fixed objects, matchfinder tables, aligned buffers, init-once buffers, and general buffers into one caller-owned or allocated contiguous region.

## Important APIs, Types, and Functions
Key types are `ZSTD_cwksp`, `ZSTD_cwksp_alloc_phase_e`, and `ZSTD_cwksp_static_alloc_e`. Important helpers include `ZSTD_cwksp_init()`, `ZSTD_cwksp_create()`, `ZSTD_cwksp_free()`, `ZSTD_cwksp_move()`, `ZSTD_cwksp_reserve_object()`, `ZSTD_cwksp_reserve_object_aligned()`, `ZSTD_cwksp_reserve_table()`, `ZSTD_cwksp_reserve_aligned_init_once()`, `ZSTD_cwksp_reserve_aligned64()`, `ZSTD_cwksp_reserve_buffer()`, `ZSTD_cwksp_clean_tables()`, `ZSTD_cwksp_mark_tables_dirty()`, `ZSTD_cwksp_mark_tables_clean()`, `ZSTD_cwksp_clear_tables()`, `ZSTD_cwksp_clear()`, `ZSTD_cwksp_available_space()`, `ZSTD_cwksp_used()`, `ZSTD_cwksp_sizeof()`, and oversized-workspace checks.

## Control Flow
Workspace allocation proceeds in strict phases: objects first, then init-once/tables, then aligned/tables, then buffers/tables. Objects and tables grow upward from the beginning of the workspace, while aligned/buffer allocations grow downward from an aligned end pointer. Advancing into table allocation aligns the table start to 64 bytes. Table validity is tracked separately from table reservation so reused tables can avoid clearing when their values are already bounded.

## State and Persistence
`ZSTD_cwksp` persists the workspace bounds, object/table ends, valid-table end, downward allocation start, init-once boundary, allocation failure flag, static/dynamic ownership mode, phase, and oversized duration counter. Object allocations survive `ZSTD_cwksp_clear()`, while tables and temporary buffers are invalidated between parameter sets or compression runs as needed. Init-once buffers are zeroed only the first time a region becomes exposed to memory checkers.

## Dependencies and Integration Points
The allocator depends on custom allocation hooks, Zstd internals, compiler helpers, and portability macros. `ZSTD_CCtx_s` embeds a `ZSTD_cwksp`; reset and dictionary creation code use it to allocate block states, entropy workspaces, match tables, sequence buffers, LDM state, and temporary block-split buffers.

## Risks
The main risks are out-of-order allocations, alignment mistakes, stale table values after table/temporary overlap, and misuse of init-once buffers that may contain prior data. Assertions enforce many invariants, but release builds rely on callers obeying phase and size contracts. Static allocation ownership must be correct so custom free does not double-free or leak.

## Test Signals
Tests should cover dynamic and static workspaces, repeated context resets with changing compression parameters, table reuse without memset, dirty/clean table transitions, allocation failure paths, oversized-duration shrink decisions, ASAN/MSAN behavior around init-once memory, alignment of 64-byte buffers/tables, and custom allocator failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_cwksp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_double_fast.c -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_double_fast.c

## Purpose
`zstd_double_fast.c` implements the double-fast block matchfinder. It keeps both a long-match hash table and a small-match hash table, favoring speed while finding better matches than the single fast parser.

## Important APIs, Types, and Functions
When not excluded by `ZSTD_EXCLUDE_DFAST_BLOCK_COMPRESSOR`, exported functions are `ZSTD_fillDoubleHashTable()`, `ZSTD_compressBlock_doubleFast()`, `ZSTD_compressBlock_doubleFast_dictMatchState()`, and `ZSTD_compressBlock_doubleFast_extDict()`. Internal variants include CDict/CCtx table fillers and generic no-dict, dictMatchState, and extDict compressors specialized by minimum match length through `ZSTD_GEN_DFAST_FN`.

## Control Flow
Fill functions populate `ms->hashTable` as the long table and `ms->chainTable` as the small table, using tagged short-cache entries for CDicts and normal indices for CCtx tables. The no-dict compressor probes repcode at `ip+1`, then long matches, then small matches, and for a small hit checks whether a long match at `ip+1` is better. After storing a sequence it performs complementary insertions near the match end and greedily consumes immediate repcode matches. DictMatchState mode probes prefix tables and attached dictionary tables with tag checks. ExtDict mode maps indices to either `base` or `dictBase` and counts matches across the dictionary/prefix boundary with `ZSTD_count_2segments()`.

## State and Persistence
The function updates match tables in `ZSTD_MatchState_t`, appends sequences and literals to `SeqStore_t`, and updates the caller's `rep[0..1]` history for the next block. Dictionary variants read but do not mutate attached dictionary match tables. It has no file-static mutable state.

## Dependencies and Integration Points
It depends on `zstd_compress_internal.h` for hashing, sequence storage, repeat-code handling, window boundaries, short-cache helpers, and match counting. It is selected by the block-compressor dispatcher for the `ZSTD_dfast` strategy unless excluded at compile time. The header maps the function pointers to `NULL` when excluded, allowing dispatch tables to omit the strategy implementation.

## Risks
The code relies on intentional pointer arithmetic near `iend - HASH_READ_SIZE`, unsigned index comparisons, dummy reads for branchless safety, and correct base selection for extDict. Short/long table synchronization and complementary insertions are performance-critical and correctness-sensitive. Repcode disabling/restoration must preserve history when offsets fall outside the current prefix.

## Test Signals
Tests should cover no-dict, extDict, and dictMatchState compression at minMatch 4 through 7; CDict table prefill and short-cache tags; excluded-build compilation; repeated immediate repcodes; long-vs-small match preference; window boundary invalidation; 32-bit and 64-bit builds; ASAN/fuzzer runs for end-of-block probes; and round trips for data crossing dictionary/prefix boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_double_fast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_double_fast.h -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_double_fast.h

## Purpose
`zstd_double_fast.h` declares the double-fast matchfinder API and compile-time exclusion shims.

## Important APIs, Types, and Functions
It declares `ZSTD_fillDoubleHashTable()`, `ZSTD_compressBlock_doubleFast()`, `ZSTD_compressBlock_doubleFast_dictMatchState()`, and `ZSTD_compressBlock_doubleFast_extDict()` when `ZSTD_EXCLUDE_DFAST_BLOCK_COMPRESSOR` is not defined. It also defines `ZSTD_COMPRESSBLOCK_DOUBLEFAST*` macros to either the real functions or `NULL`.

## Control Flow
The compressor dispatcher includes this header and uses the macros to install function pointers for no-dict, attached-dictionary, and extDict double-fast compression. Table loading calls `ZSTD_fillDoubleHashTable()` with dictionary table load and table fill purpose modes.

## State and Persistence
The header owns no state. The functions it declares mutate `ZSTD_MatchState_t` tables, `SeqStore_t` output, and repeat offsets through caller-provided pointers.

## Dependencies and Integration Points
It includes common memory types and `zstd_compress_internal.h`. It is the interface between strategy dispatch and `zstd_double_fast.c`, and its `NULL` macros support builds that remove the double-fast compressor.

## Risks
Callers must handle `NULL` macro values when the implementation is excluded. Passing a match state without both long and small tables sized for double-fast would corrupt memory in the implementation.

## Test Signals
Compile tests should cover both normal and `ZSTD_EXCLUDE_DFAST_BLOCK_COMPRESSOR` builds. Runtime tests should verify dispatch to no-dict, dictMatchState, and extDict functions for the `dfast` strategy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_double_fast.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_fast.c -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_fast.c

## Purpose
`zstd_fast.c` implements the single-hash-table fast block matchfinder. It prioritizes throughput using pipelined hash lookups, simple skip acceleration, and greedy repcode handling.

## Important APIs, Types, and Functions
Exported functions are `ZSTD_fillHashTable()`, `ZSTD_compressBlock_fast()`, `ZSTD_compressBlock_fast_dictMatchState()`, and `ZSTD_compressBlock_fast_extDict()`. Internal helpers include CDict/CCtx hash table fillers, `ZSTD_match4Found_cmov()`, `ZSTD_match4Found_branch()`, and generic no-dict/dictMatchState/extDict compressors specialized by minimum match length and branch/cmov mode through `ZSTD_GEN_FAST_FN`.

## Control Flow
Hash-table fill inserts every third position and optionally fills empty intermediate positions; CDict mode stores packed short-cache tags, while CCtx mode stores plain indices. The no-dict compressor pipelines hash, table lookup, match load, and compare across adjacent candidate positions, periodically increasing step size for incompressible regions. It first checks repcode candidates, then hash candidates, counts backward and forward match length, stores sequences, inserts near match boundaries, and consumes immediate repeat matches. DictMatchState mode probes local and attached-dictionary tables, using dictionary tags to avoid many remote loads. ExtDict mode resolves candidates against `dictBase` or `base`, falls back to no-dict when the dictionary is invalidated, and uses two-segment counting for cross-boundary matches.

## State and Persistence
The function mutates `ms->hashTable`, appends to `SeqStore_t`, and updates `rep[0]`/`rep[1]` for subsequent blocks. It reads `ZSTD_MatchState_t.window`, `cParams`, `dictMatchState`, and prefetch settings. It has no persistent global state.

## Dependencies and Integration Points
It depends on internal hash functions, `ZSTD_storeSeq()`, `ZSTD_count()`, `ZSTD_count_2segments()`, repcode macros, window low-index helpers, short-cache tag helpers, and CPU/prefetch macros. It is selected for the `ZSTD_fast` strategy by the compressor dispatcher and supports prefix, external dictionary, and attached CDict modes.

## Risks
The implementation is built around deliberate speculative reads guarded by index checks or dummy addresses, so boundary conditions are high risk. Cmov vs branch selection changes generated code and performance. Repcode invalidation/restoration is subtle when old offsets are outside the current prefix. DictMatchState tries to mimic extDict parse behavior by preferring dictionary matches only when local matches are invalid; changing this can alter compressed output and ratio.

## Test Signals
Tests should cover minMatch 4 through 7, small blocks near `HASH_READ_SIZE`, incompressible skip acceleration, repcode-only matches, prefix and non-contiguous extDict windows, attached CDicts with short-cache tags and prefetching, invalidated dictionaries, branch/cmov behavior on different window logs, ASAN/fuzzer boundary checks, and round-trip determinism for repeated context reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_fast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_fast.h -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_fast.h

## Purpose
`zstd_fast.h` declares the fast matchfinder API used by compression strategy dispatch and dictionary table loading.

## Important APIs, Types, and Functions
It declares `ZSTD_fillHashTable()`, `ZSTD_compressBlock_fast()`, `ZSTD_compressBlock_fast_dictMatchState()`, and `ZSTD_compressBlock_fast_extDict()`.

## Control Flow
Callers fill the hash table for a CCtx or CDict with `ZSTD_fillHashTable()`, then dispatch one of the block compressors depending on dictionary mode. All compressors receive `ZSTD_MatchState_t`, `SeqStore_t`, repeat-code history, source pointer, and source size.

## State and Persistence
The header owns no state. The declared implementation updates the match state's hash table, sequence store contents, and caller-held repeat offsets.

## Dependencies and Integration Points
It includes common memory types and `zstd_compress_internal.h`. It is consumed by the main block-compressor selector and other compression internals that need to prefill or run the fast parser.

## Risks
The API assumes `ms->hashTable`, window fields, and compression parameters are initialized for fast parsing. Calling the wrong variant for the active dictionary mode can produce invalid offsets.

## Test Signals
Compile tests should verify inclusion in kernel-style builds. Runtime coverage should exercise the no-dict, dictMatchState, and extDict functions via the `ZSTD_fast` strategy and verify round-trip correctness with reused contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_fast.h -->
