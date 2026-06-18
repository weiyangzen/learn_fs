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
