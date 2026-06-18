# subset-b-000315 research

This grouped report covers the requested Zstd lazy, long-distance matching, optimal parsing, and pre-split compression files. Each source file has its own section with reconciliation markers so the guard can split or validate source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_lazy.c -->
# sources/compression/zstd/lib/compress/zstd_lazy.c

## Purpose
`zstd_lazy.c` implements the greedy, lazy, lazy2, and btlazy2 block compressors for Zstd. It provides several match-finder backends, including hash chains, binary trees, and SIMD/SWAR row-hash matching, then feeds selected matches into `SeqStore_t` with updated repcode history.

## Important APIs, Types, And Functions
Externally relevant functions include `ZSTD_insertAndFindFirstIndex()`, `ZSTD_row_update()`, `ZSTD_dedicatedDictSearch_lazy_loadDictionary()`, and all exported `ZSTD_compressBlock_*` wrappers for greedy/lazy/lazy2/btlazy2 in no-dictionary, dictionary-match-state, dedicated-dictionary-search, external-dictionary, and row-match variants. Core internals are `ZSTD_updateDUBT()`, `ZSTD_insertDUBT1()`, `ZSTD_DUBT_findBestMatch()`, `ZSTD_HcFindBestMatch()`, `ZSTD_RowFindBestMatch()`, `ZSTD_searchMax()`, `ZSTD_compressBlock_lazy_generic()`, and `ZSTD_compressBlock_lazy_extDict_generic()`.

## Control Flow
The wrapper selected by compression strategy calls a generic parser with a search method and lazy depth. The parser checks repcode candidates, calls `ZSTD_searchMax()` for the configured match finder, optionally looks one or two bytes ahead for a better match, rewinds the match start when possible, stores a sequence, then scans immediate repcode continuations. Hash-chain mode inserts pending positions into `hashTable` and `chainTable`. Binary-tree mode first catches up unsorted positions, then searches/sorts the DUBT tree. Row-hash mode uses salted hashes, tag rows, and vector masks to prefilter candidates before validating full byte matches. External-dictionary paths use two-segment counting and dictionary-window bounds.

## State And Persistence
All state is in the compression context: `ZSTD_MatchState_t` owns `hashTable`, `chainTable`, `tagTable`, `hashCache`, `nextToUpdate`, `lazySkipping`, window bases/limits, optional `dictMatchState`, and row-hash salt entropy. The caller-owned `rep` array is updated across blocks. The file writes no persistent storage; it produces in-memory sequences in `SeqStore_t`. Dedicated dictionary search temporarily repacks dictionary hash-table space into bucket caches plus chain pointers.

## Dependencies And Integration Points
The file depends on `zstd_compress_internal.h`, `zstd_lazy.h`, common bit helpers, match counting helpers, offset/repcode macros, and architecture feature macros for SSE2, NEON, RVV, and SWAR fallbacks. It is selected from the central block-compressor dispatch path and is used by mid-level strategies before entropy encoding. Dictionary loading uses `ZSTD_dedicatedDictSearch_lazy_loadDictionary()` and `ZSTD_row_update()` to prepare tables.

## Risks
The highest-risk areas are pointer arithmetic around prefix/ext-dictionary transitions, `nextToUpdate` invariants after match skipping, binary-tree consistency when matches reach `iend`, row-table alignment and circular row heads, architecture-specific mask generation, and offset validity when repcodes become invalid under a shrinking window. Lazy skipping improves speed on incompressible data but loses table density, so changes can shift compression ratio. Dedicated dictionary search assumes oversized hash tables and packed chain pointers fit the allocated tables.

## Test Signals
Useful signals include round-trip compression at greedy/lazy/lazy2/btlazy2 levels, dictionary and external-dictionary corpora, row-match enabled and disabled builds, sanitizer runs for boundary reads near block ends, cross-architecture tests for SSE2/NEON/RVV/SWAR paths, and ratio/speed regression tests on repetitive and incompressible inputs. Build configurations excluding individual block compressors should also compile because wrappers become `NULL` through the header.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_lazy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_lazy.h -->
# sources/compression/zstd/lib/compress/zstd_lazy.h

## Purpose
`zstd_lazy.h` declares the public-internal interface for Zstd's greedy, lazy, lazy2, and btlazy2 block compressor implementations and their dictionary-specific variants.

## Important APIs, Types, And Functions
The header defines `ZSTD_LAZY_DDSS_BUCKET_LOG` for dedicated dictionary search buckets and `ZSTD_ROW_HASH_TAG_BITS` for row-match tag filtering. Shared helpers include `ZSTD_insertAndFindFirstIndex()`, `ZSTD_row_update()`, `ZSTD_dedicatedDictSearch_lazy_loadDictionary()`, and `ZSTD_preserveUnsortedMark()`. It declares block compressor entry points for no dictionary, `dictMatchState`, dedicated dictionary search, external dictionary, and row-hash variants, then maps `ZSTD_COMPRESSBLOCK_*` macros either to real functions or `NULL` when excluded at build time.

## Control Flow
There is no runtime control flow. Compile-time `ZSTD_EXCLUDE_*_BLOCK_COMPRESSOR` guards determine which strategies are available. The central compressor selection layer can use the macros without separately testing every exclusion flag.

## State And Persistence
The header owns no state. Its declarations operate on caller-owned `ZSTD_MatchState_t`, `SeqStore_t`, and repcode arrays. Constants affect the shape of hash/tag tables allocated and maintained elsewhere.

## Dependencies And Integration Points
It includes `zstd_compress_internal.h` for match-state, sequence-store, repcode, and integer types. It integrates with `zstd_lazy.c`, dictionary loading code, match-state reduction logic, and block-compressor selection in the compression pipeline.

## Risks
Prototype or macro mismatches here break strategy dispatch broadly. The exclusion macros must stay synchronized with implementation guards, or a build can expose unavailable functions or hide available ones. Constants are table-layout contracts; changing them requires auditing allocation, row search, and dedicated dictionary search code.

## Test Signals
Compile-only matrix coverage with each `ZSTD_EXCLUDE_*` option is important. Runtime signals are that selected compression levels still resolve to the intended block compressor and that dictionary-loading paths can call the helper declarations without link failures.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_lazy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_ldm.c -->
# sources/compression/zstd/lib/compress/zstd_ldm.c

## Purpose
`zstd_ldm.c` implements long-distance matching (LDM). It finds content-defined split points with a gear rolling hash, hashes fixed-length anchors with XXH64, records long raw sequences, and either interleaves them with normal block compression or exposes them as candidates to the optimal parser.

## Important APIs, Types, And Functions
Public functions are `ZSTD_ldm_adjustParameters()`, `ZSTD_ldm_getTableSize()`, `ZSTD_ldm_getMaxNbSeq()`, `ZSTD_ldm_fillHashTable()`, `ZSTD_ldm_generateSequences()`, `ZSTD_ldm_skipSequences()`, `ZSTD_ldm_skipRawSeqStoreBytes()`, and `ZSTD_ldm_blockCompress()`. Internal helpers include `ldmRollingHashState_t`, `ZSTD_ldm_gear_init()`, `ZSTD_ldm_gear_reset()`, `ZSTD_ldm_gear_feed()`, `ZSTD_ldm_insertEntry()`, backward match counters, `ZSTD_ldm_fillFastTables()`, `ZSTD_ldm_generateSequences_internal()`, `ZSTD_ldm_reduceTable()`, and `maybeSplitSequence()`.

## Control Flow
Parameter adjustment fills defaults from normal compression parameters. Sequence generation processes input in up to 1 MiB chunks, performs overflow correction, enforces maximum distance, runs the rolling gear hash to collect split points, hashes each candidate window, prefetches buckets, scans bucket entries with checksum filtering, validates forward and backward matches, emits raw sequences, and inserts new entries. When a long match overlaps future hashed data, the rolling hash is reset and scanning skips ahead. Block compression then consumes raw sequences: optimal strategies receive LDM through `ms->ldmSeqStore`, while faster strategies compress literal gaps with the selected block compressor and explicitly store LDM matches.

## State And Persistence
`ldmState_t` stores the LDM window, hash table, circular bucket offsets, split/candidate scratch buffers, and `loadedDictEnd`. `RawSeqStore_t` persists generated raw sequences across block boundaries using `pos` and `posInSequence`. Normal match-state tables may be caught up before compressing literal regions. No filesystem persistence occurs.

## Dependencies And Integration Points
The file depends on `zstd_ldm.h`, `debug.h`, `xxhash.h`, `zstd_fast.h`, `zstd_double_fast.h`, and `zstd_ldm_geartab.h`. It integrates with `ZSTD_window_update()` invariants, window overflow correction, max-distance enforcement, fast/double-fast table filling, block-compressor selection, and optimal parsing via `ms->ldmSeqStore`.

## Risks
Important risks are raw-sequence capacity exhaustion, off-by-one errors around `minMatchLength`, offset validity after chunk splitting, overflow correction invalidating dictionaries, split matches that cross block boundaries, and external-dictionary backward matching across two segments. LDM can strongly affect ratio and speed, so parameter defaults and gear-mask behavior are regression-sensitive.

## Test Signals
Signals include large-window round trips, multithreaded large-input compression, small and huge chunk boundaries, LDM with dictionaries and external dictionaries, capacity-limit error tests from `ZSTD_ldm_getMaxNbSeq()`, sanitizer tests for two-segment counting, and ratio/speed tracking on sparse repeated data where LDM should help.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_ldm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_ldm.h -->
# sources/compression/zstd/lib/compress/zstd_ldm.h

## Purpose
`zstd_ldm.h` declares the long-distance matching interface used by the compressor context, block-compressor pipeline, and parameter initialization code.

## Important APIs, Types, And Functions
The header defines `ZSTD_LDM_DEFAULT_WINDOW_LOG` and declares table initialization, sequence generation, raw-sequence skipping, block compression with predefined LDM sequences, memory sizing, maximum sequence estimation, and parameter adjustment APIs. The key data types are imported from internal headers: `ldmState_t`, `ldmParams_t`, `RawSeqStore_t`, `ZSTD_MatchState_t`, `SeqStore_t`, and `ZSTD_ParamSwitch_e`.

## Control Flow
There is no direct runtime flow. The documented contract requires callers to update the LDM window before sequence generation, allocate enough raw-sequence space, call skip helpers for data not passed to `ZSTD_ldm_blockCompress()`, and adjust parameters before sizing or running LDM.

## State And Persistence
The header owns no storage. It describes operations over LDM hash state, raw sequence stores, normal match state, and repcode arrays. Generated raw sequences persist in memory until consumed or skipped.

## Dependencies And Integration Points
It includes `zstd_compress_internal.h` and public `zstd.h`. It is included by `zstd_ldm.c` and by compression-context code that sizes LDM tables, fills dictionary tables, generates sequences, or routes blocks through LDM-aware compression.

## Risks
The API has strict ordering requirements: stale windows or insufficient raw sequence capacity produce invalid offsets or errors. `ZSTD_ldm_blockCompress()` accepts sequences longer than a block and mutates the raw sequence store, so callers must not assume one sequence maps to one block.

## Test Signals
Header-level signals are successful compilation across LDM-enabled and disabled parameter paths, plus integration tests that verify adjusted defaults, memory sizing, and raw-sequence consumption over multiple blocks.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_ldm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_ldm_geartab.h -->
# sources/compression/zstd/lib/compress/zstd_ldm_geartab.h

## Purpose
`zstd_ldm_geartab.h` provides the 256-entry 64-bit gear table used by LDM's rolling hash to create content-defined split points.

## Important APIs, Types, And Functions
The file defines one internal object, `static UNUSED_ATTR const U64 ZSTD_ldm_gearTab[256]`. Each byte value indexes a precomputed 64-bit constant used in `hash = (hash << 1) + table[input_byte]`.

## Control Flow
There is no control flow. `zstd_ldm.c` includes the table and reads it from the gear hash reset/feed loops.

## State And Persistence
The table is immutable static data. It creates no runtime state and writes no persistent data.

## Dependencies And Integration Points
It includes common compiler and memory headers for `UNUSED_ATTR` and `U64`. Its only direct consumer in this subset is `ZSTD_ldm_gear_reset()` and `ZSTD_ldm_gear_feed()` in `zstd_ldm.c`.

## Risks
Changing table values changes split-point distribution, which can significantly alter LDM compression ratio and speed. Because it is a header-defined `static` table, inclusion in many translation units would duplicate data, though current usage is narrow and `UNUSED_ATTR` suppresses unused warnings.

## Test Signals
There are no direct unit tests. Strong indirect signals are stable LDM ratio/speed benchmarks, deterministic compression output for fixed parameters, and fuzz/round-trip coverage of large inputs with LDM enabled.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_ldm_geartab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_opt.c -->
# sources/compression/zstd/lib/compress/zstd_opt.c

## Purpose
`zstd_opt.c` implements Zstd's binary-tree optimal parsers for `btopt`, `btultra`, and `btultra2`. It prices literals, literal lengths, offsets, and match lengths using adaptive statistics, finds match candidates, and runs a shortest-path search to choose the lowest-cost sequence stream for a block.

## Important APIs, Types, And Functions
Public entry points include `ZSTD_updateTree()`, `ZSTD_compressBlock_btopt()`, `ZSTD_compressBlock_btopt_dictMatchState()`, `ZSTD_compressBlock_btopt_extDict()`, `ZSTD_compressBlock_btultra()`, `ZSTD_compressBlock_btultra_dictMatchState()`, `ZSTD_compressBlock_btultra_extDict()`, and `ZSTD_compressBlock_btultra2()`. Key internals include price/stat helpers (`ZSTD_rescaleFreqs()`, `ZSTD_rawLiteralsCost()`, `ZSTD_litLengthPrice()`, `ZSTD_getMatchPrice()`, `ZSTD_updateStats()`), match finders (`ZSTD_insertBt1()`, `ZSTD_updateTree_internal()`, `ZSTD_insertBtAndGetAllMatches()`), LDM candidate helpers (`ZSTD_optLdm_t`, `ZSTD_optLdm_processMatchCandidate()`), and `ZSTD_compressBlock_opt_generic()`.

## Control Flow
At block start, the parser rescales or initializes frequency statistics, optionally from dictionary entropy tables. It selects a generated get-all-matches function for the current dictionary mode and minimum match length. For each input position, it finds repcode, hash3, binary-tree, dictionary, and optional LDM matches. It initializes a price table, expands possible literal and match transitions, updates repcode histories at match endpoints, and stops early for sufficiently long matches. The selected path is then walked backward, converted from stretches into sequences, emitted to `SeqStore_t`, and used to update adaptive statistics. `btultra2` may run a first no-output pass on the first block to seed statistics, then rewinds history and compresses again.

## State And Persistence
`ms->opt` stores price tables, match tables, literal/LL/ML/offset frequencies, sums, base prices, price type, and entropy cost references. `ms->hashTable`, `hashTable3`, `chainTable`, `nextToUpdate`, and window state hold match-finder history. `ms->ldmSeqStore` can feed long-distance candidates. The repcode array is updated for the caller. No persistent storage is written.

## Dependencies And Integration Points
The file depends on `zstd_compress_internal.h`, `hist.h`, and `zstd_opt.h`, plus FSE/HUF cost tables and match-counting/window helpers from the compression internals. It integrates with dictionary entropy tables, LDM, binary-tree dictionary loading through `ZSTD_updateTree()`, and central strategy dispatch for optimal compression levels.

## Risks
This file is sensitive to integer overflow in price calculations, path-table bounds (`ZSTD_OPT_NUM`/`ZSTD_OPT_SIZE`), match ordering, and repcode history semantics when literal length is zero. Dictionary and external-dictionary matches require careful two-segment counting and offset translation. The first-pass `btultra2` history rewind has a narrow contract: first block only, no dictionary, no prefix, and no LDM. Small changes can alter compression ratio, speed, or deterministic output.

## Test Signals
Important signals include round-trip tests at high compression levels, dictionary and external-dictionary tests, LDM plus optimal-parser tests, `minMatch == 3` coverage for hash3, sanitizer runs near block ends, deterministic-output checks, and benchmark tracking for ratio/speed on first-block and dictionary-heavy corpora.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_opt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_opt.h -->
# sources/compression/zstd/lib/compress/zstd_opt.h

## Purpose
`zstd_opt.h` declares the internal interface for Zstd optimal binary-tree compressors and dictionary tree loading.

## Important APIs, Types, And Functions
The header declares `ZSTD_updateTree()` when any binary-tree strategy requires dictionary content loading. It declares `btopt`, `btultra`, and `btultra2` block compressors, including dictionary-match-state and external-dictionary variants where supported. It maps `ZSTD_COMPRESSBLOCK_BTOPT`, `ZSTD_COMPRESSBLOCK_BTULTRA`, and related macros to real functions or `NULL` under build exclusion flags.

## Control Flow
There is no runtime control flow. Preprocessor guards define the available optimal-parser surface. `btultra2` is intentionally only declared for no-dictionary mode because its two-pass first-block optimization is not meant for dictionaries.

## State And Persistence
The header owns no state. Its functions operate on `ZSTD_MatchState_t`, `SeqStore_t`, and caller-provided repcode arrays, mutating in-memory match and parser state in the implementation.

## Dependencies And Integration Points
It includes `zstd_compress_internal.h` and is consumed by compressor-selection and dictionary-loading code. It is implemented by `zstd_opt.c` and coordinates with compile-time compressor exclusion settings.

## Risks
Mismatched guards can lead to unresolved symbols or missing strategy dispatch. Adding dictionary variants for `btultra2` would violate the implementation contract unless the two-pass state rewind is redesigned.

## Test Signals
Compile matrix tests with `ZSTD_EXCLUDE_BTOPT_BLOCK_COMPRESSOR` and `ZSTD_EXCLUDE_BTULTRA_BLOCK_COMPRESSOR` are primary. Runtime tests should confirm high compression levels select the intended function pointers and dictionary loading still invokes `ZSTD_updateTree()` when needed.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_opt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_preSplit.c -->
# sources/compression/zstd/lib/compress/zstd_preSplit.c

## Purpose
`zstd_preSplit.c` implements a heuristic for splitting a full 128 KiB block when the beginning and end appear statistically different. It is a pre-compression block boundary detector, not a compressor.

## Important APIs, Types, And Functions
The exported function is `ZSTD_splitBlock()`. Internal types are `Fingerprint` and `FPStats`, which store sampled hash-event histograms. Important helpers are `hash2()`, `initStats()`, generated `ZSTD_recordFingerprint_*()` functions for different sampling rates, `fpDistance()`, `compareFingerprints()`, `mergeEvents()`, `ZSTD_splitBlock_byChunks()`, and `ZSTD_splitBlock_fromBorders()`.

## Control Flow
Level 0 compares byte histograms from both block borders and a middle segment, returning no split, 32 KiB, 64 KiB, or 96 KiB. Levels 1-4 scan 8 KiB chunks with progressively denser fingerprint sampling and larger hash tables. The scanner accumulates past events, compares the next chunk to the accumulated fingerprint with a decreasing penalty, and returns the first statistically different chunk boundary; otherwise it returns the original block size.

## State And Persistence
The caller provides an aligned workspace of at least `ZSTD_SLIPBLOCK_WORKSPACESIZE`. All histograms live in that workspace for the duration of one call. No persistent state or global mutable state is used.

## Dependencies And Integration Points
The file depends on common compiler/memory/dependency/internal headers, `hist.h`, and `zstd_preSplit.h`. It integrates with higher-level compression code that can decide to split 128 KiB blocks before normal block compression.

## Risks
The function currently asserts a full 128 KiB block and aligned workspace; calling it for smaller blocks or unaligned scratch is invalid. The heuristics are ratio/speed-sensitive and can over-split or miss useful boundaries. Workspace layout is manual in `ZSTD_splitBlock_fromBorders()`, so the header size contract must remain correct if `FPStats` changes.

## Test Signals
Signals include direct tests for all levels on homogeneous data, sharply changing data, and borderline distributions; asserts or error handling for invalid block sizes in debug builds; workspace-alignment tests; and compression-ratio benchmarks to confirm that split decisions improve or at least do not regress target corpora.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_preSplit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_preSplit.h -->
# sources/compression/zstd/lib/compress/zstd_preSplit.h

## Purpose
`zstd_preSplit.h` exposes the small pre-split API for deciding whether a 128 KiB block should be split before compression.

## Important APIs, Types, And Functions
The header defines `ZSTD_SLIPBLOCK_WORKSPACESIZE` as 8208 bytes and declares `ZSTD_splitBlock(const void* blockStart, size_t blockSize, int level, void* workspace, size_t wkspSize)`.

## Control Flow
There is no header control flow. The documented contract says `level` must be 0 through 4, `workspace` must be `size_t` aligned and large enough, and current implementation expects `blockSize == 128 KB`.

## State And Persistence
No state is owned by the header. The implementation uses only caller-provided workspace and returns the selected split position or the original block size.

## Dependencies And Integration Points
It includes `<stddef.h>` for `size_t` and is implemented by `zstd_preSplit.c`. Higher-level compression code can include it to invoke the pre-split heuristic before normal block compression.

## Risks
The fixed workspace size is an ABI-like contract with the implementation. If the implementation's histogram structs grow beyond this size, callers can corrupt memory. The 128 KiB-only limitation must be respected by all callers.

## Test Signals
Compile coverage plus direct calls at all legal levels are the basic signals. Integration tests should verify callers allocate aligned workspace of at least the advertised size and never pass partial blocks unless the implementation is extended.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstd_preSplit.h -->
