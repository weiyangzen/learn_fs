# sources/compression/xz/src/liblzma/lzma/lzma_encoder_optimum_normal.c

## Purpose
Implements normal-mode optimal parsing for the LZMA encoder. It computes bit-price costs for literals, repeated matches, and normal matches over a bounded lookahead window, then backtracks the least-cost path.

## Important APIs, Types, And Functions
- Price helpers: `get_literal_price()`, `get_len_price()`, `get_short_rep_price()`, `get_pure_rep_price()`, `get_rep_price()`, and `get_dist_len_price()`.
- Price-table refreshers: `fill_dist_prices()` and `fill_align_prices()`.
- Optimum helpers: `make_literal()`, `make_short_rep()`, `backward()`, `helper1()`, and `helper2()`.
- `lzma_lzma_optimum_normal()` is the exported parser entry point used by `lzma_lzma_encode()`.

## Control Flow
If a previous optimal path still has pending symbols, `lzma_lzma_optimum_normal()` returns the next path segment immediately. Otherwise it refreshes distance/alignment prices when counters cross thresholds and no readahead is pending. `helper1()` seeds the optimum graph from the current position: it gathers matches, computes repeat lengths, handles immediate nice-length cases, prices the literal and short-rep alternatives, initializes prices for lengths through `len_end`, and adds repeat and normal match candidates. The main loop advances `cur`, obtains new matches for each lookahead position, stops early on a nice match, and calls `helper2()` to reconstruct state/reps for that node and extend the graph with literal, short-rep, rep, rep+literal+rep, normal match, and match+literal+rep candidates. `backward()` reverses predecessor links and returns the first symbol.

## State And Persistence
Uses `coder->opts[OPTS]` as the dynamic-programming table. Each `lzma_optimal` records price, state, predecessor, match kind, previous literal flags, and repeat-distance snapshots. Persistent price tables live in `coder->dist_slot_prices`, `dist_prices`, `align_prices`, and length encoder price arrays. `opts_end_index`/`opts_current_index` persist a chosen path across calls. Match finder readahead and cached longest match are also part of the parser state.

## Dependencies And Integration Points
Depends on `lzma_encoder_private.h`, `fastpos.h`, `memcmplen.h`, range price helpers, LZMA state updates, and match finder APIs. Its output is consumed by `encode_symbol()`, which must match the parser's `(back,len)` encoding convention.

## Risks
This file is algorithmically dense and sensitive to off-by-one errors in `cur + len`, `OPTS` bounds, `mf_avail()`, and `read_ahead`. Reconstructing `state` and `reps` in `helper2()` must match actual encoder state transitions exactly or price decisions become invalid. The special `prev_1_is_literal`/`prev_2` path encoding is fragile. Price refresh thresholds influence compression ratio and performance. The code currently has TODO cleanup comments, so future refactors need strong regression testing.

## Test Signals
Normal-mode round trips across levels 4-9 and extreme presets are required. Regression tests should include tiny inputs, high repetition, alternating literal/match patterns, long-distance matches, matches near `OPTS` boundaries, preset dictionaries, and fuzzed inputs for encoder/decompressor round-trip. Compression-ratio benchmarks should flag parser cost regressions.
