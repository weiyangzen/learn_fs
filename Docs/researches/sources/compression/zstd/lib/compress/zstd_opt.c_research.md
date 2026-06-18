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
