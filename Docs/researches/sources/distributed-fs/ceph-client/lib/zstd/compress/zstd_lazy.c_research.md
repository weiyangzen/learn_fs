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
