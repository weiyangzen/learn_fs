# subset-b-006120 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_lazy.c -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_lazy.c

## Purpose

`zstd_lazy.c` implements the Zstd block compressors used by the greedy, lazy, lazy2, and btlazy2 strategies for Ceph's in-kernel Zstd client copy. It is responsible for finding repeated byte ranges in the current block and storing Zstd sequences into `SeqStore_t`, while updating the mutable `ZSTD_MatchState_t` tables that make future searches fast. The file supports normal prefix mode, external-dictionary mode, dictionary match state mode, and dedicated dictionary search mode, with both classic hash-chain/binary-tree matchfinders and the newer row-based matchfinder.

## Important APIs, Types, and Functions

The public functions are the compressor entry points declared in `zstd_lazy.h`: `ZSTD_compressBlock_greedy*()`, `ZSTD_compressBlock_lazy*()`, `ZSTD_compressBlock_lazy2*()`, and `ZSTD_compressBlock_btlazy2*()`. The suffixes select dictionary mode and row hash mode. `ZSTD_insertAndFindFirstIndex()` updates hash-chain state for dictionary loading and related table preparation. `ZSTD_row_update()` populates row-matchfinder tables while processing dictionaries. `ZSTD_dedicatedDictSearch_lazy_loadDictionary()` builds the dedicated dictionary search structure used by `ZSTD_dedicatedDictSearch` mode.

Internally, the file defines three matchfinder families. `ZSTD_HcFindBestMatch()` is the hash-chain finder. `ZSTD_BtFindBestMatch()` and helpers such as `ZSTD_updateDUBT()`, `ZSTD_insertDUBT1()`, and `ZSTD_DUBT_findBestMatch()` maintain a deferred-update binary tree. `ZSTD_RowFindBestMatch()` is the row-based finder that stores salted hash tags in `tagTable` rows and scans tag matches with SSE2, NEON, or SWAR helpers. `ZSTD_searchMax()` dispatches between generated specializations keyed by search method, dictionary mode, `minMatch`, and row size without using an indirect function pointer.

## Control Flow

All non-external-dictionary block entry points call `ZSTD_compressBlock_lazy_generic()`. It initializes the current block pointers, clamps `minMatch` and row size, validates repcodes against the active window, optionally primes the row hash cache, then loops over input until the safe match limit. At each position it tries a repcode match, then calls `ZSTD_searchMax()` for the selected matchfinder. If no match is found it advances by an adaptive skip amount and may enter `ms->lazySkipping`, which reduces table insertions during long incompressible runs. If a match is found, depth 0 stores it immediately, depth 1 and depth 2 look ahead one or two positions and compare approximate gains to pick a better parse.

After selecting a match, the loop rewinds the start while preceding bytes still match, stores the sequence with `ZSTD_storeSeq()`, updates `rep[0]` and `rep[1]`, disables lazy skipping after a successful match, and then emits any immediate repeat-code runs with zero literal length. The external-dictionary wrapper, `ZSTD_compressBlock_lazy_extDict_generic()`, mirrors this flow but checks repcode validity against `ZSTD_getLowestMatchIndex()`, uses `dictBase`/`dictEnd` with `ZSTD_count_2segments()`, and rewinds across the dictionary/prefix boundary.

The binary-tree path first inserts unsorted positions as a chain using `ZSTD_updateDUBT()`. `ZSTD_DUBT_findBestMatch()` walks unsorted candidates, sorts them with `ZSTD_insertDUBT1()`, then searches the tree while maintaining common-prefix lengths for smaller and larger branches. It skips repetitive regions by advancing `ms->nextToUpdate` to `matchEndIdx - 8`. The hash-chain path catches up `nextToUpdate` via `ZSTD_insertAndFindFirstIndex_internal()` and follows `chainTable` until search attempts, max distance, or chain bounds stop it. The row path prefetches rows, compares compact hash tags, collects candidate indexes, inserts the current position into the circular row, and checks only candidates whose tags match.

## State and Persistence Behavior

The function mutates `ZSTD_MatchState_t` heavily: `hashTable`, `chainTable`, `tagTable`, `hashCache`, `nextToUpdate`, `lazySkipping`, `hashSaltEntropy`, and dictionary-related pointers are part of the persistent match state across calls. The block compressors also update caller-owned repeat offsets in `rep[]` so later blocks inherit the same repcode history. Row mode uses salted hashes and accumulates `hashSaltEntropy` so table collisions vary across context resets. Dedicated dictionary loading temporarily repurposes oversized hash-table storage to build a compact bucket-and-chain structure, then leaves the dictionary match state ready for fast dictionary probes.

## Dependencies and Integration Points

The implementation depends on `zstd_compress_internal.h` for core types, window helpers, hash functions, sequence storage, and repcode utilities; `zstd_lazy.h` for declarations and constants; and `../common/bits.h` for trailing-zero scans. It is selected by `ZSTD_selectBlockCompressor()` through the function-like macros in `zstd_lazy.h`. Dictionary modes integrate with `ZSTD_MatchState_t::dictMatchState`, external dictionary windows, and dedicated dictionary search structures loaded during dictionary preparation. The row path relies on architecture feature macros for SSE2 and NEON but has a SWAR fallback.

## Risks

The code has high pointer arithmetic density and relies on tight preconditions such as `ip <= iend - 8`, valid `nextToUpdate`, and correct window limits. Regressions can silently corrupt compression output if binary-tree ordering or unsorted markers are mishandled. Dedicated dictionary search is memory-layout sensitive because it uses extra hash-table capacity as temporary chain storage. Row mode is architecture-sensitive: tag rotation, endian handling, row alignment, and the slot zero sentinel must remain consistent. Lazy skipping improves speed but can affect ratio if the cache refill or `nextToUpdate` updates are wrong. Repcodes crossing dictionary boundaries are another high-risk area.

## Test Signals

Useful tests include round-trip compression/decompression for every exported greedy/lazy/lazy2/btlazy2 variant, with and without row matching, external dictionaries, dictionary match states, and dedicated dictionary search. Boundary cases should cover tiny blocks, blocks at `iend - 8`, repeated single-byte data, long incompressible runs that trigger `lazySkipping`, dictionary/prefix boundary matches, repcode validity near window expiration, and row sizes 16/32/64. Kernel builds on x86 with SSE2, ARM64 with NEON, and a portable fallback configuration provide coverage for SIMD-specific paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_lazy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_lazy.h -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_lazy.h

## Purpose

`zstd_lazy.h` is the internal header for the greedy/lazy family of Zstd block compressors. It publishes the block-compressor functions implemented in `zstd_lazy.c`, exposes dictionary/table update helpers used while loading dictionaries, and maps excluded compressor families to `NULL` so the central compressor selector can compile against one stable interface.

## Important APIs, Types, and Functions

The header defines `ZSTD_LAZY_DDSS_BUCKET_LOG`, the bucket multiplier for the dedicated dictionary search structure, and `ZSTD_ROW_HASH_TAG_BITS`, the number of tag bits used by row hashing. When any greedy/lazy/btlazy compressor family is enabled, it declares `ZSTD_insertAndFindFirstIndex()`, `ZSTD_row_update()`, `ZSTD_dedicatedDictSearch_lazy_loadDictionary()`, and `ZSTD_preserveUnsortedMark()`.

The main exported surface is grouped by strategy. The greedy group declares normal, row, dictionary match state, dedicated dictionary search, and external dictionary variants. The lazy and lazy2 groups declare the same broad set. The btlazy2 group declares normal, dictionary match state, and external dictionary variants because btlazy2 does not have the full dedicated dictionary/row suffix matrix here. Each group also defines `ZSTD_COMPRESSBLOCK_*` macros that resolve to the real function when enabled or `NULL` when a `ZSTD_EXCLUDE_*` build flag removes it.

## Control Flow

This header does not implement runtime control flow, but it controls compile-time dispatch. `ZSTD_selectBlockCompressor()` can use the `ZSTD_COMPRESSBLOCK_*` macros without scattering preprocessor conditionals through the compressor selection table. When a family is excluded, the macro becomes `NULL`, which preserves the selector layout while preventing references to missing functions.

## State and Persistence Behavior

All declared functions operate on caller-owned state. `ZSTD_MatchState_t` owns the persistent hash, chain, row, dictionary, and window tables. `SeqStore_t` receives generated sequences for the current block. `rep[ZSTD_REP_NUM]` stores the repeat-offset history across blocks. The header itself stores no state, but its macros determine which strategy functions may appear in dispatch state.

## Dependencies and Integration Points

The header includes `zstd_compress_internal.h`, so it is tightly coupled to internal compression types rather than the public Zstd API. It is consumed by `zstd_lazy.c` and by central compression code that selects block compressors. Dictionary-loading code uses `ZSTD_row_update()` and `ZSTD_dedicatedDictSearch_lazy_loadDictionary()` to prebuild matchfinder tables before block compression.

## Risks

The primary risks are interface drift and build-configuration mismatches. If an implementation is renamed or excluded without updating the macro matrix, compressor selection may call the wrong function or dereference `NULL`. The header also declares `ZSTD_preserveUnsortedMark()` even though its implementation is outside this file group; callers depend on that function to preserve binary-tree unsorted markers during index reduction. Constants such as `ZSTD_LAZY_DDSS_BUCKET_LOG` must remain synchronized with memory sizing and dedicated dictionary loading assumptions.

## Test Signals

Build tests should cover all combinations of `ZSTD_EXCLUDE_GREEDY_BLOCK_COMPRESSOR`, `ZSTD_EXCLUDE_LAZY_BLOCK_COMPRESSOR`, `ZSTD_EXCLUDE_LAZY2_BLOCK_COMPRESSOR`, and `ZSTD_EXCLUDE_BTLAZY2_BLOCK_COMPRESSOR`. Runtime tests should verify that strategy selection returns non-`NULL` functions only for enabled families and that dictionary-loading paths can call the helper declarations successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_lazy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_ldm.c -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_ldm.c

## Purpose

`zstd_ldm.c` implements Zstd long distance matching. It scans input with a content-defined rolling gear hash, records candidate anchor points in a separate LDM hash table, generates `rawSeq` long-match sequences, and then integrates those sequences with normal block compression. The goal is to recover matches that are too distant or too costly for the regular per-block matchfinders to find efficiently.

## Important APIs, Types, and Functions

The public functions are `ZSTD_ldm_adjustParameters()`, `ZSTD_ldm_getTableSize()`, `ZSTD_ldm_getMaxNbSeq()`, `ZSTD_ldm_fillHashTable()`, `ZSTD_ldm_generateSequences()`, `ZSTD_ldm_skipSequences()`, `ZSTD_ldm_skipRawSeqStoreBytes()`, and `ZSTD_ldm_blockCompress()`. Internal state is built around `ldmRollingHashState_t`, which holds the current gear hash and stop mask, and around `ldmState_t`, whose table entries and bucket offsets persist across chunks.

Important helpers include `ZSTD_ldm_gear_init()`, `ZSTD_ldm_gear_reset()`, and `ZSTD_ldm_gear_feed()` for split-point discovery; `ZSTD_ldm_insertEntry()` and `ZSTD_ldm_getBucket()` for ring-bucket table maintenance; `ZSTD_ldm_countBackwardsMatch()` and `_2segments()` for extending matches backwards; `ZSTD_ldm_reduceTable()` for overflow correction; and `maybeSplitSequence()` for clipping raw sequences to a block boundary.

## Control Flow

Parameter setup starts with `ZSTD_ldm_adjustParameters()`, which derives `windowLog`, `hashRateLog`, `hashLog`, `minMatchLength`, and `bucketSizeLog` from the normal compression parameters when fields are unset. `ZSTD_ldm_fillHashTable()` can preseed the LDM table from dictionary data: it feeds bytes through the gear hash, converts split points into `xxh64()` fingerprints over `minMatchLength` bytes, and stores `offset` plus upper checksum bits in the selected bucket.

`ZSTD_ldm_generateSequences()` processes large input in 1 MiB chunks. Before each chunk it applies window overflow correction if needed, reduces stored offsets by the correction value, invalidates dictionaries on correction, and enforces max distance at the chunk end. It then delegates to `ZSTD_ldm_generateSequences_internal()`, which primes the rolling hash with `minMatchLength` bytes, batches split points into `splitIndices`, prefetches candidate buckets, and searches each bucket for checksum-compatible entries. For each candidate it measures a forward match and a backward extension, chooses the best total match, emits a `rawSeq` with literal length, match length, and offset, inserts the current entry, and advances the anchor. Overlapping/repeating patterns reset the gear hash and skip over covered bytes to avoid pathological insertion cost.

`ZSTD_ldm_blockCompress()` consumes generated sequences during normal block compression. For strategies at or above `ZSTD_btopt`, it exposes the raw sequence store through `ms->ldmSeqStore` so the optimal parser can treat LDM matches as candidates. For lower strategies, it walks the raw sequences itself, compresses literal spans with the selected block compressor, updates repcodes, stores the LDM match with `ZSTD_storeSeq()`, and finally compresses the last literal tail.

## State and Persistence Behavior

The LDM table and bucket offsets persist in `ldmState_t` across chunks and can include dictionary entries. `ZSTD_ldm_generateSequences()` updates `ldmState->window`, `loadedDictEnd`, and table offsets during overflow correction and max-distance enforcement. `RawSeqStore_t` persists generated sequences through `size`, `capacity`, `pos`, and `posInSequence`, and skip helpers mutate those fields when data is omitted or consumed. `ZSTD_ldm_blockCompress()` also mutates the normal match state tables by invoking the selected block compressor and updates `rep[]` as LDM matches are emitted.

## Dependencies and Integration Points

The file includes `zstd_ldm.h`, kernel `xxhash`, `zstd_fast.h`, `zstd_double_fast.h`, and `zstd_ldm_geartab.h`. It relies on `ZSTD_window_*` helpers, `ZSTD_count*()` match counters, `ZSTD_selectBlockCompressor()`, and `ZSTD_storeSeq()` from internal compression code. The normal fast and double-fast tables are proactively filled through `ZSTD_ldm_fillFastTables()` when LDM has skipped long spans before calling a secondary compressor.

## Risks

LDM is sensitive to offset validity over long inputs. Overflow correction must reduce table offsets consistently or stale offsets can point outside the current window. Sequence splitting is subtle because offsets must remain valid at the end of a split sequence, not only at its start. Raw sequence store capacity is a hard limit: sequence generation returns `dstSize_tooSmall` if it fills. Gear hash stop masks affect both speed and ratio, and degenerate `hashRateLog` values need bounds protection. External dictionary backward extension crosses segment boundaries and must not underflow pointers.

## Test Signals

Tests should include round trips with LDM enabled across multi-megabyte inputs, repeated-byte data, inputs with distant repeats beyond normal block windows, external dictionaries, and dictionary preloading. Error tests should force small raw sequence capacity. Streaming tests should skip bytes with both `ZSTD_ldm_skipSequences()` and `ZSTD_ldm_skipRawSeqStoreBytes()`, split sequences across block boundaries, and exercise overflow correction by feeding high logical offsets. Strategy coverage should include fast/dfast direct LDM consumption and btopt/btultra candidate integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_ldm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_ldm.h -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_ldm.h

## Purpose

`zstd_ldm.h` declares the internal long-distance matching interface. It exposes the functions needed to size LDM workspaces, adjust LDM parameters, prefill long-match hash tables, generate raw long-match sequences, skip unused sequence ranges, and combine LDM sequences with normal block compression.

## Important APIs, Types, and Functions

`ZSTD_LDM_DEFAULT_WINDOW_LOG` maps the LDM default window to `ZSTD_WINDOWLOG_LIMIT_DEFAULT`. `ZSTD_ldm_fillHashTable()` seeds an `ldmState_t` table from `[ip, iend)`. `ZSTD_ldm_generateSequences()` populates a `RawSeqStore_t` with long-range matches for a source range. `ZSTD_ldm_blockCompress()` consumes those predefined sequences while running a selected secondary compressor. `ZSTD_ldm_skipSequences()` and `ZSTD_ldm_skipRawSeqStoreBytes()` advance sequence-store cursors for data that will not be compressed through the LDM path. `ZSTD_ldm_getTableSize()` and `ZSTD_ldm_getMaxNbSeq()` are workspace sizing helpers. `ZSTD_ldm_adjustParameters()` derives unset LDM parameters from normal compression parameters.

## Control Flow

Callers normally adjust parameters, allocate table and raw sequence capacity from the sizing helpers, update the LDM window for the incoming source, generate sequences, then either call `ZSTD_ldm_blockCompress()` for each block or skip the corresponding sequence bytes when data is handled elsewhere. The header documents that `ZSTD_window_update()` must be called for all available input before `ZSTD_ldm_generateSequences()` and that the generated sequence store must have enough capacity.

## State and Persistence Behavior

The declared API mutates `ldmState_t`, `RawSeqStore_t`, `ZSTD_MatchState_t`, `SeqStore_t`, and `rep[]`, but the header itself stores no state. `RawSeqStore_t::pos` and `posInSequence` are explicitly part of the consumption protocol. `ZSTD_ldm_blockCompress()` may split a raw sequence between blocks and update the store accordingly.

## Dependencies and Integration Points

The header includes `zstd_compress_internal.h` for internal compression types such as `ldmParams_t`, `ldmState_t`, `RawSeqStore_t`, `SeqStore_t`, and `ZSTD_MatchState_t`, plus `<linux/zstd.h>` for public context types and `size_t`. It is used by the compressor context setup and by `zstd_ldm.c`. Optimal parsing integrates with the same raw sequence store through `ms->ldmSeqStore`.

## Risks

The most important contract risk is cursor misuse: `ZSTD_ldm_skipSequences()` and `ZSTD_ldm_skipRawSeqStoreBytes()` are documented as not interchangeable. Mixing them can desynchronize `pos` and `posInSequence`. The header comment also states that `ZSTD_ldm_blockCompress()` does not return errors, while `ZSTD_ldm_generateSequences()` can; callers must handle generation errors before compression. The closing include guard comment says `ZSTD_FAST_H`, which is harmless but misleading.

## Test Signals

Interface tests should validate table size is zero when LDM is disabled, max sequence estimates are nonzero only when enabled, generated sequences can be consumed block by block, and skipped input leaves the raw store cursor at the expected sequence and in-sequence position. Build tests should catch signature drift with `zstd_ldm.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_ldm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_ldm_geartab.h -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_ldm_geartab.h

## Purpose

`zstd_ldm_geartab.h` provides the fixed 256-entry gear hash table used by long distance matching. Each byte value maps to a 64-bit pseudo-random constant. `zstd_ldm.c` combines these constants with a left-shift rolling hash to find content-defined split points.

## Important APIs, Types, and Functions

The header exports one internal object: `static UNUSED_ATTR const U64 ZSTD_ldm_gearTab[256]`. It includes `compiler.h` for `UNUSED_ATTR` and `mem.h` for `U64`. There are no functions and no public runtime API.

## Control Flow

This file contributes data to the control flow in `ZSTD_ldm_gear_reset()` and `ZSTD_ldm_gear_feed()`. For each input byte, those functions update `hash = (hash << 1) + ZSTD_ldm_gearTab[inputByte]`. A stop mask derived from `hashRateLog` and `minMatchLength` determines when a rolling hash value is accepted as a split point.

## State and Persistence Behavior

The table is immutable and file-local because it is declared `static const`. Every translation unit that includes this header gets its own internal copy unless the compiler/linker folds constants. It does not persist dynamic state, but changing any constant changes LDM split-point distribution and therefore compression behavior.

## Dependencies and Integration Points

The only observed consumer in this subset is `zstd_ldm.c`. The table is part of the LDM algorithm contract: `ZSTD_ldm_gear_init()` chooses high-weight mask bits based on assumptions about how gear hash bits depend on recent bytes. The `UNUSED_ATTR` annotation allows the header to be included in configurations where LDM helpers are compiled out or optimized away.

## Risks

The constants must remain deterministic across builds and platforms. Any accidental edit can alter compression ratio, speed, and reproducibility. Because the table is a header-local `static` object, including it broadly can add object size. Endianness is not a direct risk for the table values because indexing is byte-based, but `U64` width and literal parsing must remain stable.

## Test Signals

Useful tests are mostly indirect: LDM split-rate tests for selected `hashRateLog` values, round-trip compression with LDM enabled, and reproducibility checks that the same input and parameters produce the same sequence decisions. Static checks can verify the table has exactly 256 entries and compiles in kernel mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_ldm_geartab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_opt.c -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_opt.c

## Purpose

`zstd_opt.c` implements Zstd's optimal parsing block compressors: btopt, btultra, and btultra2. These strategies collect candidate matches with a binary-tree matchfinder, price literals, literal lengths, match lengths, and offsets using adaptive entropy statistics, and run a bounded dynamic-programming search to choose lower-cost sequences than the greedy/lazy parsers.

## Important APIs, Types, and Functions

The exported compressor entry points are `ZSTD_compressBlock_btopt()`, `ZSTD_compressBlock_btopt_dictMatchState()`, `ZSTD_compressBlock_btopt_extDict()`, `ZSTD_compressBlock_btultra()`, `ZSTD_compressBlock_btultra_dictMatchState()`, `ZSTD_compressBlock_btultra_extDict()`, and `ZSTD_compressBlock_btultra2()`. `ZSTD_updateTree()` is exported for dictionary loading.

Important internal pricing functions include `ZSTD_bitWeight()`, `ZSTD_fracWeight()`, `ZSTD_rescaleFreqs()`, `ZSTD_rawLiteralsCost()`, `ZSTD_litLengthPrice()`, `ZSTD_getMatchPrice()`, and `ZSTD_updateStats()`. Match collection is handled by `ZSTD_insertBt1()`, `ZSTD_updateTree_internal()`, `ZSTD_insertBtAndGetAllMatches()`, generated `ZSTD_btGetAllMatches_*()` specializations, and `ZSTD_selectBtGetAllMatches()`. LDM candidate integration is handled by `ZSTD_optLdm_t` and helpers such as `ZSTD_optLdm_processMatchCandidate()`.

## Control Flow

`ZSTD_compressBlock_opt_generic()` is the central parser. It selects a match collector for the current dictionary mode and `minMatch`, initializes or rescales symbol statistics, initializes LDM candidate state from `ms->ldmSeqStore`, and loops over the block until `iend - 8`. At each anchor it calls `getAllMatches()` to find matches and injects any applicable LDM candidate. If no match exists, it advances one byte.

When matches exist, the parser initializes `opt[0]` with the current literal run and then prices all initial match lengths. Large matches beyond `sufficient_len` are emitted immediately. Otherwise, it iterates relative positions in the bounded `ZSTD_OPT_NUM` window. For each position it considers extending the previous path by one literal, updates repcode history when a path ends in a match, optionally skips unpromising positions in opt level 0, gathers further matches at that position, and prices each feasible match length. The table stores "stretches" during the forward pass: a match followed by literals. When the search reaches a terminal large match, end of the window, or the best known path, it walks backward, converts stretches into normal sequences, calls `ZSTD_updateStats()` for each chosen sequence, emits with `ZSTD_storeSeq()`, and refreshes base prices for the next parse segment.

The match collector first checks repcodes, then optionally probes a 3-byte hash table when `minMatch == 3`, then inserts the current position into the binary tree and records strictly improving match lengths. It also searches a dictionary match state binary tree when active. `ZSTD_updateTree_internal()` can insert skipped positions ahead of a search so tree state remains consistent.

## State and Persistence Behavior

Optimal parsing persists adaptive frequencies in `ms->opt`: literal frequencies, literal-length frequencies, match-length frequencies, offset-code frequencies, sums, base prices, price tables, and match tables. These statistics are initialized from a dictionary entropy table when available, from source literals and base distributions on the first block, or downscaled between later blocks. `ZSTD_compressBlock_btultra2()` can run a first pass on the first block to seed stats, then resets the sequence store and rewinds window bookkeeping so the second pass compresses as if starting fresh. Matchfinder state persists in `ms->hashTable`, `hashTable3`, `chainTable`, and `nextToUpdate`. The parser updates the caller's `rep[]` according to the selected path.

## Dependencies and Integration Points

The file includes `zstd_compress_internal.h`, `hist.h`, and `zstd_opt.h`. It depends on HUF and FSE cost-table helpers from the internal symbol-cost state, on histogram counting for first-block literal stats, on window helpers for external dictionaries, on `ZSTD_newRep()` and `ZSTD_storeSeq()` for sequence semantics, and on `RawSeqStore_t` generated by LDM. It is selected by central compressor dispatch through macros in `zstd_opt.h`.

## Risks

The dynamic-programming logic is correctness-sensitive because it stores one representation during the forward pass and rewrites it into another representation during reverse traversal. Incorrect repcode updates, literal length price deltas, or `opt[]` bounds can generate invalid sequences. The binary tree has the same pointer and ordering risks as lazy btlazy2. Statistics must be downscaled without reaching zero for required symbols, or costs become unstable. `btultra2` deliberately mutates window base and limits after a dry run; that narrow contract assumes first block, no dictionary, no prefix, and no LDM. LDM candidate cursor handling can desynchronize if block positions overshoot candidate ends.

## Test Signals

Round-trip tests should cover btopt, btultra, and btultra2 with no dictionary, external dictionary, and dictionary match state where supported. Add corpus tests comparing compression ratio stability for first block, later blocks, small blocks under `ZSTD_PREDEF_THRESHOLD`, and `minMatch == 3`. Stress repeated data, incompressible data, long offsets, LDM-enabled optimal parsing, and repcode-heavy inputs. Assertions should be exercised in debug builds for `ZSTD_OPT_NUM` boundaries, tree update bounds, and btultra2 first-pass preconditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_opt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_opt.h -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_opt.h

## Purpose

`zstd_opt.h` is the internal declaration header for the optimal-parser block compressors. It provides the enabled/disabled macro surface used by compressor dispatch and declares `ZSTD_updateTree()` for dictionary-table preparation.

## Important APIs, Types, and Functions

When bt/lazy or optimal families are enabled, `ZSTD_updateTree()` is declared for `ZSTD_loadDictionaryContent()` and related setup code. The btopt group declares normal, dictionary match state, and external dictionary variants and maps `ZSTD_COMPRESSBLOCK_BTOPT*` macros to those functions or `NULL`. The btultra group declares normal, dictionary match state, external dictionary, and btultra2 variants and maps `ZSTD_COMPRESSBLOCK_BTULTRA*` macros similarly.

## Control Flow

The header has compile-time control flow only. It centralizes `ZSTD_EXCLUDE_BTOPT_BLOCK_COMPRESSOR`, `ZSTD_EXCLUDE_BTULTRA_BLOCK_COMPRESSOR`, and `ZSTD_EXCLUDE_BTLAZY2_BLOCK_COMPRESSOR` conditionals so the compressor selector can use one macro name for each strategy slot. It also documents that btultra2 has no extDict or dictMatchState variant because it is intended only for the first block without dictionaries or prefix history.

## State and Persistence Behavior

The declared functions mutate `ZSTD_MatchState_t`, `SeqStore_t`, and `rep[]`, but the header stores no runtime state. Macro values affect dispatch-table state by making disabled compressor slots `NULL`.

## Dependencies and Integration Points

The header includes `zstd_compress_internal.h` for internal type definitions. It is consumed by `zstd_opt.c`, dictionary-loading code that needs `ZSTD_updateTree()`, and central block-compressor selection. It must remain synchronized with `zstd_opt.c` exports and with the strategy enum support in compressor parameters.

## Risks

The main risks are build matrix drift and unsupported dispatch. If macros are wrong, a strategy can become selectable while its implementation is excluded, or a valid implementation can be hidden as `NULL`. The comment indentation around btultra2 is harmless but makes the special-case contract easy to miss.

## Test Signals

Build tests should compile with btopt excluded, btultra excluded, and both enabled. Runtime selection tests should verify that `ZSTD_btopt`, `ZSTD_btultra`, and `ZSTD_btultra2` map to non-`NULL` functions only when compiled in, and that dictionary modes never request a btultra2 variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_opt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_preSplit.c -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_preSplit.c

## Purpose

`zstd_preSplit.c` implements a heuristic for pre-splitting full 128 KiB blocks when the beginning and end of a block appear statistically different. The split point can improve compression when a block contains two different data distributions by allowing later compression stages to process more homogeneous pieces.

## Important APIs, Types, and Functions

The single public function is `ZSTD_splitBlock()`. Internal data structures are `Fingerprint`, which stores event counts and a total event count, and `FPStats`, which holds past and new fingerprints. `hash2()` hashes one or two bytes depending on hash-table size. `recordFingerprint_generic()` and generated `ZSTD_recordFingerprint_*()` functions sample events at different rates. `fpDistance()` computes a normalized absolute difference between fingerprints, and `compareFingerprints()` checks that distance against a threshold. `ZSTD_splitBlock_byChunks()` scans 8 KiB chunks, while `ZSTD_splitBlock_fromBorders()` performs the cheaper border/middle heuristic.

## Control Flow

`ZSTD_splitBlock()` accepts a level from 0 to 4. Level 0 calls `ZSTD_splitBlock_fromBorders()`. That path records byte histograms for the first and last 512 bytes, returns no split if they are not sufficiently different, then samples the middle 512 bytes and chooses 32 KiB, 64 KiB, or 96 KiB based on which side the middle resembles. Levels 1 through 4 call `ZSTD_splitBlock_byChunks()` with increasingly dense sampling. The chunk path records the first 8 KiB as the reference, then compares each subsequent 8 KiB chunk to accumulated past events. If the new chunk differs enough, its offset is returned as the split point; otherwise events are merged and the penalty threshold is gradually relaxed.

## State and Persistence Behavior

All state is temporary and stored in caller-provided workspace. The functions assert that the workspace is aligned and large enough for `FPStats`. `ZSTD_splitBlock_fromBorders()` also uses an additional `Fingerprint` carved out of the same workspace at `512 * sizeof(unsigned)`. No persistent compressor state is modified.

## Dependencies and Integration Points

The file includes common compiler, memory, dependency, and internal headers, plus `hist.h` and `zstd_preSplit.h`. It depends on `HIST_add()` for byte histograms in the fast border mode and uses `ZSTD_SLIPBLOCK_WORKSPACESIZE` from the header to assert workspace capacity. The intended caller is a higher-level compressor path that can split only full 128 KiB blocks.

## Risks

The function currently asserts `blockSize == 128 KiB`; using it on smaller blocks is outside contract. `addEvents_generic()` assumes `srcSize >= HASHLENGTH`; callers satisfy this through fixed chunk sizes. The workspace overlay for `middleEvents` depends on `ZSTD_SLIPBLOCK_WORKSPACESIZE` being large enough and on alignment. The heuristic can choose suboptimal split points because it uses sampled fingerprints rather than full compression estimates. `flushEvents()` and `removeEvents()` are unused, which is intentional but can confuse maintainers.

## Test Signals

Tests should cover level 0 through 4 on 128 KiB synthetic blocks: uniform data should return `blockSize`, sharply different halves should split near the transition, and border/middle cases should produce 32 KiB, 64 KiB, or 96 KiB as designed. Debug builds should assert on invalid level, undersized workspace, and non-128 KiB blocks. Compression integration tests should verify that a returned split still round-trips after both pieces are compressed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_preSplit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_preSplit.h -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_preSplit.h

## Purpose

`zstd_preSplit.h` declares the block pre-splitting helper and its workspace size. It documents that the helper is currently restricted to full 128 KiB blocks and provides the single internal entry point used by compression code that wants a cheap split heuristic.

## Important APIs, Types, and Functions

`ZSTD_SLIPBLOCK_WORKSPACESIZE` is defined as `8208`, large enough for the fingerprint workspace used by `zstd_preSplit.c`. `ZSTD_splitBlock()` takes a block pointer, block size, heuristic level, workspace pointer, and workspace size, and returns either a split offset or `blockSize` when no split is advised.

## Control Flow

The header does not implement control flow. Its comments define the caller contract: level must be 0 through 4, higher levels spend more effort on boundary detection, the workspace must be aligned for `size_t`, `wkspSize` must be at least `ZSTD_SLIPBLOCK_WORKSPACESIZE`, and `blockSize` must currently be exactly 128 KiB.

## State and Persistence Behavior

The API is stateless from the caller's perspective aside from temporary writes into the provided workspace. No compression tables, windows, or sequence stores are passed to the function.

## Dependencies and Integration Points

The header includes `<linux/types.h>` for `size_t`. It is implemented by `zstd_preSplit.c` and is intended for higher-level block compression logic that can split 128 KiB blocks before entropy or sequence compression. The naming of `ZSTD_SLIPBLOCK_WORKSPACESIZE` appears to use "SLIP" rather than "SPLIT"; consumers must use the exact macro name.

## Risks

The main risk is contract misuse. Passing smaller blocks, unaligned workspace, or a too-small workspace will trigger assertions in debug builds and may be unsafe in non-debug contexts. The fixed workspace macro must remain synchronized with the implementation's layout assumptions.

## Test Signals

Compile tests should include this header in kernel mode and verify the signature matches `zstd_preSplit.c`. Runtime tests should allocate exactly `ZSTD_SLIPBLOCK_WORKSPACESIZE`, pass aligned storage, and validate all heuristic levels on full 128 KiB blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_preSplit.h -->
