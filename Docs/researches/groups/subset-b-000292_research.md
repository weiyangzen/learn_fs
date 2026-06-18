# Research Group: subset-b-000292

This grouped report covers the requested XZ/liblzma LZMA, range coder, simple filter, helper script, and build metadata files. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma_decoder.c -->
# sources/compression/xz/src/liblzma/lzma/lzma_decoder.c

## Purpose
Implements the raw LZMA1 decoder used through the LZ wrapper and by LZMA2 chunk decoding. It combines adaptive probability models, range decoding, dictionary copying, LZMA state transitions, LZMA1EXT uncompressed-size/EOPM handling, property parsing, and memory-usage reporting.

## Important APIs, Types, And Functions
- `lzma_length_decoder` stores probability trees for low/mid/high match lengths.
- `lzma_lzma1_decoder` is the full persistent decoder state: literal/match probability arrays, range decoder, LZMA state, four repeat distances, lc/lp/pb-derived masks, known uncompressed size, EOPM policy, and resumable partial-symbol fields.
- `lzma_decode()` is the core decode callback. It initializes the range coder, copies hot fields to locals, decodes literals, normal matches, repeated matches, distances, EOPM, and copies match bytes into `lzma_dict`.
- `lzma_decoder_reset()` initializes probabilities, state, repeat distances, masks, length decoders, and resumable sequence fields from `lzma_options_lzma`.
- `lzma_lzma_decoder_create()` wires the LZ callback table and dictionary settings.
- `lzma_decoder_init()` validates options, handles `LZMA_FILTER_LZMA1EXT` size/flag semantics, creates, resets, and configures EOPM behavior.
- Public helpers include `lzma_lzma_decoder_init()`, `lzma_lzma_lclppb_decode()`, `lzma_lzma_decoder_memusage[_nocheck]()`, and `lzma_lzma_props_decode()`.

## Control Flow
`lzma_decode()` first calls `rc_read_init()` to consume the 5-byte LZMA range-coder initialization. It then enters a switch-threaded loop that can resume at a saved `sequence`. In non-`HAVE_SMALL` builds, a fast path is used while at least `LZMA_IN_REQUIRED` bytes are available and output space is not exhausted. The fast path decodes literals with unrolled 8-bit bit trees, decodes normal match lengths and distances, decodes repeated matches, validates distances, and calls `dict_repeat()`. If input/output boundaries are tight or EOPM handling is needed, control jumps to the resumable slow path.

The slow path mirrors the same grammar but every range-coder operation uses `_safe` macros that can save `coder->sequence` and return when input is exhausted. It also handles known uncompressed-size completion: when the output limit reaches the expected size it normalizes the range coder, accepts clean range end, rejects forbidden EOPM, or allows one final EOPM if configured. On exit, local state is copied back, known-size remaining bytes are decremented, and finished streams reset range state for possible LZMA2 reuse.

## State And Persistence
All probability arrays are adaptive and persisted across calls until reset. The decoder also persists range `code/range/init_bytes_left`, the LZMA state, four repeat distances, uncompressed-size remaining count, EOPM policy, and partial decode variables (`probs`, `symbol`, `limit`, `offset`, `len`, `sequence`). The dictionary object is copied locally for speed but writes back `pos` and `full`; `dict.limit` is intentionally not copied back.

## Dependencies And Integration Points
Depends on `lz_decoder.h` for dictionary and LZ wrapper callbacks, `lzma_common.h` for LZMA constants/state transitions/literal helpers, and `range_decoder.h` for range-coder macros. It is called through `lzma_lz_decoder_init()` and must be the final filter in a raw chain. LZMA2 reuses `lzma_lzma_decoder_create()`, `reset`, and `set_uncompressed` to decode independent chunks.

## Risks
The fast and slow paths must stay semantically identical. Resumable sequence labels are fragile because missing a save point can corrupt streams across short input buffers. Distance decoding contains intentional pointer arithmetic to one element before the modeled subarray, which is documented but non-standard. EOPM and known uncompressed-size interactions are subtle, especially for LZMA1EXT versus LZMA2. Range-coder normalization assumptions depend on `LZMA_IN_REQUIRED`. Corrupt distance validation must happen before dictionary reads or repeats.

## Test Signals
Round-trip LZMA1 and LZMA2 tests should cover literals, matches, repeated matches, all distance classes, small output buffers, one-byte input feeding, known-size streams with and without EOPM, unknown-size streams requiring EOPM, corrupt first range byte, invalid properties, too-short props, and invalid distances. Fuzzing should target resumable boundaries and EOPM near exact output limits.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma_decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma_decoder.h -->
# sources/compression/xz/src/liblzma/lzma/lzma_decoder.h

## Purpose
Declares the internal LZMA decoder interface used by raw filter initialization, LZMA2, `.lzma`/lzip-style property parsing, and memory accounting.

## Important APIs, Types, And Functions
- `lzma_lzma_decoder_init()` initializes an LZMA decoder in a filter chain.
- `lzma_lzma_decoder_memusage()` and `_nocheck()` report memory requirements, with `_nocheck()` intended for callers that already validated lc/lp/pb or do not need them yet.
- `lzma_lzma_props_decode()` decodes 5-byte LZMA properties into `lzma_options_lzma`.
- `lzma_lzma_lclppb_decode()` decodes the compact lc/lp/pb property byte.
- When `LZMA_LZ_DECODER_H` is visible, `lzma_lzma_decoder_create()` allocates and configures only the LZ-level raw decoder callbacks.

## Control Flow
The header itself has no runtime flow. It gates `lzma_lzma_decoder_create()` behind the LZ decoder include guard so only lower-level LZ integration code sees the raw create helper.

## State And Persistence
No state is stored in this header. It forward-declares functions that allocate and manipulate `lzma_lzma1_decoder` state defined privately in `lzma_decoder.c`.

## Dependencies And Integration Points
Includes `common.h` for liblzma base types. It is consumed by LZMA1/LZMA2 decoder setup code and property decoders for container formats.

## Risks
The `_nocheck` memory-usage API relies on caller-side validation; misuse can report memory for invalid option structures. The conditional declaration pattern can hide APIs from translation units unless include order is correct.

## Test Signals
Compile coverage should ensure both public and `LZMA_LZ_DECODER_H` declaration modes work. ABI/API tests should verify property decode and memory-usage entry points remain available under decoder builds.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma_decoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma_encoder.c -->
# sources/compression/xz/src/liblzma/lzma/lzma_encoder.c

## Purpose
Implements the raw LZMA1 encoder and its integration with the LZ encoder layer. It emits literals, normal matches, repeated matches, lengths, distances, optional end-of-payload markers, property bytes, and memory usage.

## Important APIs, Types, And Functions
- `literal_matched()` and `literal()` encode literal bytes with or without match-byte context.
- `length_update_prices()` refreshes length price tables for optimal parsing.
- `length()`, `match()`, and `rep_match()` encode LZMA grammar elements and update probabilities/state/repeat distances.
- `encode_symbol()` dispatches literal, repeated match, and normal match encoding.
- `encode_init()` emits the required first literal unless a preset dictionary already initializes state.
- `encode_eopm()` writes the LZMA end marker as a special UINT32_MAX distance.
- `lzma_lzma_encode()` is the main encoding loop used by LZMA1 and LZMA2.
- `lzma_lzma_encoder_reset()`, `lzma_lzma_encoder_create()`, and `lzma_lzma_encoder_init()` create/reset/wire the encoder.
- Public helpers include `lzma_lzma_encoder_memusage()`, `lzma_lzma_lclppb_encode()`, `lzma_lzma_props_encode()`, and `lzma_mode_is_supported()`.

## Control Flow
The encoder initializes by encoding the first byte as a literal unless input is unavailable or a preset dictionary is active. `lzma_lzma_encode()` drains pending range-coder output, then loops while input and output/chunk limits allow. It asks either `lzma_lzma_optimum_fast()` or `lzma_lzma_optimum_normal()` for the next `(back,len)` decision, encodes that symbol, optionally simulates output with `rc_encode_dummy()` for `out_limit`, updates uncompressed size, and flushes range output. At end-of-stream it exposes the uncompressed size if requested, writes EOPM when configured, flushes the range coder, and handles partial flush output for plain LZMA1.

## State And Persistence
Persistent state is stored in `lzma_lzma1_encoder`: range encoder, uncompressed byte count, optional output limit, LZMA state, four repeat distances, match arrays, mode flag, initialization/flushed flags, EOPM flag, lc/lp/pb masks, adaptive probabilities, length encoders, price tables, price counters, and optimum-path arrays. `lzma_lzma_encoder_reset()` reinitializes probability models and price counters while `create()` configures mode-specific dimensions.

## Dependencies And Integration Points
Depends on `lzma2_encoder.h`, `lzma_encoder_private.h`, `fastpos.h`, range encoder helpers, match finder APIs through `lz_encoder.h`, and LZMA constants. It plugs into `lzma_lz_encoder_init()` as a filter-chain coder and into LZMA2 via raw create/reset/encode helpers. Properties interoperate with decoder property parsing and `.lzma` headers.

## Risks
Output-size limiting uses `rc_forget()` to discard the newest symbol, so range-coder pending state must be intact and `rc->pos == 0`. Plain LZMA does not support sync flush. First-byte initialization assumes position zero and no preset dictionary. Distance table size calculation must avoid overflow for huge dictionaries. Fast and normal optimum decisions must keep `mf->read_ahead` consistent with emitted `len`.

## Test Signals
Round-trip tests should cover fast/normal modes, all presets, preset dictionaries, empty input, one-byte input, LZMA1 with partial output buffer flushes, LZMA2 chunk limits, out-limit encoding, property encode/decode symmetry, invalid options, unsupported sync flush, and EOPM presence/absence.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma_encoder.h -->
# sources/compression/xz/src/liblzma/lzma/lzma_encoder.h

## Purpose
Declares internal and semi-public LZMA encoder entry points for filter-chain setup, property encoding, memory usage, and LZMA2 raw encoder reuse.

## Important APIs, Types, And Functions
- Forward declaration `lzma_lzma1_encoder`.
- `lzma_lzma_encoder_init()` initializes an LZMA encoder filter.
- `lzma_lzma_encoder_memusage()` reports required memory.
- `lzma_lzma_props_encode()` emits 5-byte LZMA properties.
- `lzma_lzma_lclppb_encode()` encodes lc/lp/pb to one byte.
- Under `LZMA_LZ_ENCODER_H`, raw helpers `lzma_lzma_encoder_create()`, `lzma_lzma_encoder_reset()`, and `lzma_lzma_encode()` are visible for LZMA2.

## Control Flow
No runtime flow is defined. Conditional declarations separate public internal filter APIs from lower-level raw LZ encoder integration.

## State And Persistence
The header hides the concrete encoder struct, enforcing state access through private implementation and raw helper functions.

## Dependencies And Integration Points
Includes `common.h`. Consumed by `lzma_encoder_private.h`, LZMA2 encoder code, and filter initialization tables.

## Risks
Compile-time visibility depends on include order and feature macros. Callers of raw helpers must satisfy LZ-layer contracts around match finder state, output limits, and reset sequencing.

## Test Signals
Build configurations with encoder-only, LZMA2, and property support should all compile. Property encode and raw LZMA2 chunk encoding tests exercise these declarations.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma_encoder_optimum_fast.c -->
# sources/compression/xz/src/liblzma/lzma/lzma_encoder_optimum_fast.c

## Purpose
Implements the fast greedy-ish match selector for LZMA encoder fast mode. It trades compression ratio for speed by using heuristics over current and next matches instead of full dynamic programming.

## Important APIs, Types, And Functions
- `change_pair()` compares whether a longer-distance candidate is worthwhile relative to a smaller distance.
- `lzma_lzma_optimum_fast()` returns the next `back_res` and `len_res` symbol decision, using match finder results, repeat distances, and lookahead.

## Control Flow
The function obtains current matches with `mf_find()` unless one byte of lookahead is already cached. It rejects matches when fewer than two bytes are available. It checks the four repeat distances first; any repeat match reaching `nice_len` is emitted immediately. A normal match reaching `nice_len` is also emitted immediately. Otherwise it trims suspicious two-byte or distance-expensive matches, prefers repeat matches when close enough to the normal match length, and may encode a literal if the next position has a better match or if a repeat at the next byte would be better. If no heuristic rejects the current normal match, it emits it and skips the remaining matched bytes.

## State And Persistence
Uses and updates match-finder lookahead via `mf_find()`/`mf_skip()`. It stores `coder->longest_match_length` and `coder->matches_count` when it probes the next byte and returns a literal. It reads `coder->reps` but repeat-distance ordering is updated later by `encode_symbol()`.

## Dependencies And Integration Points
Depends on `lzma_encoder_private.h`, `memcmplen.h`, match finder APIs, and `not_equal_16()`. Called only from `lzma_lzma_encode()` when `coder->fast_mode` is true.

## Risks
Heuristic thresholds influence compression ratio and speed. Incorrect `mf_skip()` counts desynchronize `read_ahead`. The cached next-byte match path assumes dictionary buffers are stable between `mf_find()` calls. Two-byte match rejection is distance-sensitive and can affect compatibility only through compression ratio, not decompression correctness.

## Test Signals
Fast-mode round trips at levels 0-3, tiny buffers, inputs with repeated short distances, long-distance two-byte matches, and one-byte lookahead paths should be covered. Compression-ratio benchmarks are useful regression signals for heuristic changes.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma_encoder_optimum_fast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma_encoder_optimum_normal.c -->
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
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma_encoder_optimum_normal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma_encoder_presets.c -->
# sources/compression/xz/src/liblzma/lzma/lzma_encoder_presets.c

## Purpose
Maps user preset levels and the extreme flag to concrete `lzma_options_lzma` values for dictionary size, mode, match finder, nice length, and search depth.

## Important APIs, Types, And Functions
- `lzma_lzma_preset()` is the only function. It validates preset level/flags and fills `lzma_options_lzma`.

## Control Flow
The function masks the level and flags, rejects levels above 9 or unsupported flags, clears preset dictionary fields, sets default lc/lp/pb, chooses dictionary size from `dict_pow2`, then selects fast mode for levels 0-3 and normal mode for 4-9. With `LZMA_PRESET_EXTREME`, it forces normal mode/BT4 and overrides nice length/depth based on level.

## State And Persistence
No global mutable state. It writes the caller-provided options struct.

## Dependencies And Integration Points
Includes `common.h` for API types and constants. Used by higher-level preset configuration paths in applications and internal tests. `xz` needs it even in decode-only builds per file note.

## Risks
Preset choices are user-visible performance/ratio policy. Changing them can affect memory usage, compression ratio, speed, and compatibility expectations. Unsupported flag validation must reject unknown bits.

## Test Signals
Tests should verify all levels 0-9 and extreme combinations produce expected options, invalid levels/flags fail, and resulting options pass encoder validation and round-trip.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma_encoder_presets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma_encoder_private.h -->
# sources/compression/xz/src/liblzma/lzma/lzma_encoder_private.h

## Purpose
Defines private LZMA encoder data structures, constants, helper macros, and optimum-parser prototypes shared by encoder implementation files.

## Important APIs, Types, And Functions
- `not_equal_16()` compares the first two candidate bytes using unaligned reads when available.
- `OPTS` defines the optimal parser window size as 4096 entries.
- `lzma_length_encoder` stores length probabilities plus price tables and counters.
- `lzma_optimal` stores one node in the optimal parse graph.
- `struct lzma_lzma1_encoder_s` contains range encoder, size/out-limit state, LZMA state/reps, match candidates, mode flags, adaptive probabilities, price tables, and optimum arrays.
- Prototypes declare `lzma_lzma_optimum_fast()` and `lzma_lzma_optimum_normal()`.

## Control Flow
The header has no direct control flow but its structs define the state layout used by the encoder loop and parser functions.

## State And Persistence
All persistent LZMA encoder state is defined here. It spans compression progress (`uncomp_size`), output-limit behavior, adaptive probabilities, match finder lookahead caches, and normal parser graph state.

## Dependencies And Integration Points
Includes `lz_encoder.h`, `range_encoder.h`, `lzma_common.h`, and `lzma_encoder.h`. It is the private bridge between the main encoder, fast optimum parser, and normal optimum parser.

## Risks
Struct layout changes affect memory usage and all encoder code. `not_equal_16()` depends on safe buffer availability for two bytes. `OPTS` must remain consistent with `LOOP_INPUT_MAX` in `lzma_encoder.c`. Price arrays are large and tied to LZMA constants.

## Test Signals
Compile and round-trip all encoder modes after any change. Memory-usage tests should track `sizeof(lzma_lzma1_encoder)`. Parser boundary tests should cover `OPTS` sizing.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma_encoder_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/rangecoder/Makefile.inc -->
# sources/compression/xz/src/liblzma/rangecoder/Makefile.inc

## Purpose
Automake fragment that adds range-coder source/header files to liblzma builds depending on encoder/decoder feature conditions.

## Important APIs, Types, And Functions
No C APIs. Build variables used:
- `EXTRA_DIST` includes `rangecoder/price_tablegen.c`.
- `liblzma_la_SOURCES` always includes `range_common.h`.
- `COND_ENCODER_LZMA1` adds `range_encoder.h`, `price.h`, and `price_table.c`.
- `COND_DECODER_LZMA1` adds `range_decoder.h`.

## Control Flow
Build-time conditional inclusion controls which headers/tables are distributed and compiled into liblzma.

## State And Persistence
No runtime state. It persists build metadata in Automake variables.

## Dependencies And Integration Points
Included from the larger liblzma Automake setup. Coordinates with LZMA1 encoder/decoder feature toggles.

## Risks
Incorrect conditionals can omit headers or price table objects needed by encoder builds. `price_tablegen.c` must remain distributed even though generated table output is committed.

## Test Signals
Autotools builds with encoder-only, decoder-only, both, and minimal configurations should succeed. `make distcheck` should include the generator.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/rangecoder/Makefile.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/rangecoder/price.h -->
# sources/compression/xz/src/liblzma/rangecoder/price.h

## Purpose
Provides inline probability price calculations used by LZMA optimal parsing and price-table refresh logic.

## Important APIs, Types, And Functions
- Constants: `RC_MOVE_REDUCING_BITS`, `RC_BIT_PRICE_SHIFT_BITS`, `RC_PRICE_TABLE_SIZE`, and `RC_INFINITY_PRICE`.
- External table `lzma_rc_prices`.
- `rc_bit_price()`, `rc_bit_0_price()`, and `rc_bit_1_price()` map probabilities/bits to fixed-point prices.
- `rc_bittree_price()` and `rc_bittree_reverse_price()` compute prices for normal and reverse bit trees.
- `rc_direct_price()` prices unmodeled direct bits.

## Control Flow
All functions are inline arithmetic over probability tables. Bit-tree price functions walk from symbol to root or from root to leaves, summing individual bit prices.

## State And Persistence
No mutable state. Uses the generated immutable `lzma_rc_prices` table.

## Dependencies And Integration Points
Requires range-coder constants and `probability` from `range_common.h`; included by `range_encoder.h` and optimal parser code.

## Risks
Price scale constants must match `price_table.c` generation and parser assumptions. Incorrect indexing can bias optimal parsing. `RC_INFINITY_PRICE` must be safely above realistic path costs without overflowing additions.

## Test Signals
Price-table generation comparison, parser round trips, compression-ratio benchmarks, and unit checks for bit-tree price symmetry are useful.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/rangecoder/price.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/rangecoder/price_table.c -->
# sources/compression/xz/src/liblzma/rangecoder/price_table.c

## Purpose
Defines the generated lookup table used by `price.h` to approximate range-coder bit prices quickly.

## Important APIs, Types, And Functions
- `const uint8_t lzma_rc_prices[RC_PRICE_TABLE_SIZE]` is the only exported object, hidden by declaration attributes in `price.h`.

## Control Flow
No runtime control flow beyond table lookup by callers.

## State And Persistence
Immutable process-wide table.

## Dependencies And Integration Points
Includes `range_encoder.h`, which pulls in price and range constants. Used by LZMA encoder optimal parser and length/distance price refreshes.

## Risks
The table must match `price_tablegen.c`, `RC_MOVE_REDUCING_BITS`, and `RC_BIT_PRICE_SHIFT_BITS`. Manual edits can silently degrade compression decisions.

## Test Signals
Regenerate with `price_tablegen.c` and compare byte-for-byte. Compression-ratio tests can catch table corruption indirectly.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/rangecoder/price_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/rangecoder/price_tablegen.c -->
# sources/compression/xz/src/liblzma/rangecoder/price_tablegen.c

## Purpose
Standalone C generator for `price_table.c`.

## Important APIs, Types, And Functions
- `init_price_table()` computes prices for each reduced probability bucket.
- `print_price_table()` emits the C source containing `lzma_rc_prices`.
- `main()` initializes and prints the table.

## Control Flow
The generator defines `BUILDING_PRICE_TABLEGEN` to avoid normal liblzma dependencies, includes `range_common.h` and `price.h`, computes the table with repeated squaring/bit counting, and prints formatted C source with a split SPDX string.

## State And Persistence
Uses a local static `rc_prices` array during generation. Output is persisted by redirecting stdout when regenerating the committed table.

## Dependencies And Integration Points
Depends only on standard `<inttypes.h>`, `<stdio.h>`, and range/price constants. Listed in `EXTRA_DIST`.

## Risks
Generator and committed table can drift. The generator relies on constants from headers; changing price constants requires regenerating and reviewing output. Since it includes `price.h`, declaration of `lzma_rc_prices` is made harmless by stub visibility macros.

## Test Signals
Build and run generator, compare output against `price_table.c`, and compile generated output. Dist checks should include this source.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/rangecoder/price_tablegen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/rangecoder/range_common.h -->
# sources/compression/xz/src/liblzma/rangecoder/range_common.h

## Purpose
Defines common constants, reset macros, and the `probability` type shared by range encoder and decoder implementations.

## Important APIs, Types, And Functions
- Constants: `RC_SHIFT_BITS`, `RC_TOP_BITS`, `RC_TOP_VALUE`, `RC_BIT_MODEL_TOTAL_BITS`, `RC_BIT_MODEL_TOTAL`, and `RC_MOVE_BITS`.
- Macros: `bit_reset(prob)` and `bittree_reset(probs, bit_levels)`.
- `typedef uint16_t probability`.

## Control Flow
Only reset macros perform loops/assignments at call sites. `bittree_reset` iterates through all modeled tree nodes.

## State And Persistence
No stored state. Defines the representation for adaptive probability arrays used across encoder and decoder structs.

## Dependencies And Integration Points
Includes `common.h` unless `BUILDING_PRICE_TABLEGEN` is defined. Used by `range_encoder.h`, `range_decoder.h`, `price.h`, and LZMA model structs.

## Risks
Changing probability width or range constants affects ABI-internal memory layout, performance, generated price tables, and inline assembly assumptions. Comments note 2024 branchless C/x86-64 assembly assumes `uint16_t`.

## Test Signals
Full encoder/decoder round trips, generated price table comparison, x86-64 assembly builds, and memory-usage regression tests.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/rangecoder/range_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/rangecoder/range_decoder.h -->
# sources/compression/xz/src/liblzma/rangecoder/range_decoder.h

## Purpose
Defines the range decoder state and a macro library for safe/resumable and fast LZMA bit decoding, with optional branchless C and x86-64 inline assembly variants.

## Important APIs, Types, And Functions
- `LZMA_RANGE_DECODER_CONFIG` selects optimized variants.
- `RC_BIT_MODEL_OFFSET` supports branchless probability updates.
- `lzma_range_decoder` stores `range`, `code`, and initialization bytes left.
- `rc_read_init()`, `rc_to_local()`, `rc_from_local()`, `rc_reset()`, and `rc_is_finished()`.
- Core macros: `rc_normalize[_safe]`, `rc_if_0[_safe]`, `rc_update_0`, `rc_update_1`, `rc_bit[_safe]`, `rc_bittree3/6/8`, `rc_bittree_rev4`, `rc_bit_add_if_1`, `rc_matched_literal`, and `rc_direct[_safe]`.

## Control Flow
The decoder initializes by reading five bytes, requiring the first to be zero. Fast macros assume the caller has guaranteed enough input and directly advance `rc_in_ptr`. Safe macros check input exhaustion and jump to `out` after saving the caller-provided sequence. Optional branchless C macro replacements remove some branches for selected operations. On x86-64 GCC/Clang builds, the default config selects inline assembly for normal bit trees, reverse bit trees, variable reverse bits, matched literals, and direct bits.

## State And Persistence
The persistent state is `lzma_range_decoder`, but performance macros copy it and input position into locals with `rc_to_local()` and store them back with `rc_from_local()`. Probability arrays are mutated by the update macros at each decoded bit.

## Dependencies And Integration Points
Includes `range_common.h`. Used heavily by `lzma_decoder.c`, whose local variable names and labels are part of the macro contract. Optimized variants depend on compiler, architecture, and `LZMA_RANGE_DECODER_CONFIG`.

## Risks
This header is macro-heavy and relies on caller variables such as `rc`, `rc_bound`, `rc_in_ptr`, `symbol`, `coder`, and `out`. Safe macros use `goto out`, making integration fragile. Inline assembly has portability and compiler-constraint risk. Fast macros require sufficient input; wrong `LZMA_IN_REQUIRED` assumptions can overread. Probability update math must remain bit-exact with encoder.

## Test Signals
Decoder round trips under default, `HAVE_SMALL`, branchless C, and disabled-assembly configurations. One-byte input fuzzing exercises safe macros. Cross-compiler and non-x86 builds are important. Corrupt stream tests should verify first-byte and `rc_is_finished()` checks.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/rangecoder/range_decoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/rangecoder/range_encoder.h -->
# sources/compression/xz/src/liblzma/rangecoder/range_encoder.h

## Purpose
Defines the range encoder state and inline helpers used by LZMA encoding to queue modeled/direct bits, emit bytes, simulate output limits, and flush streams.

## Important APIs, Types, And Functions
- `RC_SYMBOLS_MAX` bounds queued symbols between `rc_encode()` calls.
- `lzma_range_encoder` stores `low`, `cache_size`, `range`, `cache`, output total, queue position/count, symbol kinds, and probability pointers.
- Queueing helpers: `rc_bit()`, `rc_bittree()`, `rc_bittree_reverse()`, `rc_direct()`, and `rc_flush()`.
- Output helpers: `rc_shift_low()`, `rc_encode()`, `rc_encode_dummy()`, `rc_forget()`, `rc_pending()`, and `rc_reset()`.

## Control Flow
Encoding is staged: LZMA code queues up to `RC_SYMBOLS_MAX` symbols and calls `rc_encode()` to consume the queue. `rc_encode()` normalizes range, processes each queued bit/direct/flush symbol, updates probability models for modeled bits, and writes bytes through `rc_shift_low()`. If output fills, it returns true and resumes later using `pos`. Flush symbols emit five final bytes and reset the range encoder. `rc_encode_dummy()` clones range state and simulates whether an eventual flush would exceed a whole-stream output limit.

## State And Persistence
The encoder persists range interval state, delayed carry cache, total bytes emitted, and partially processed queued symbols. Probability arrays are mutated only when `rc_encode()` actually encodes queued modeled bits; `rc_encode_dummy()` does not mutate probabilities.

## Dependencies And Integration Points
Includes `range_common.h` and `price.h`. Used by `lzma_encoder.c` and price calculation code. `rc_pending()` is used by LZMA2 chunk-size limiting.

## Risks
Queue bound must cover the largest symbol burst; comments say 48+5 is sufficient for LZMA. `rc_forget()` is valid only when `pos == 0`. Partial output handling for plain LZMA1 depends on `pos/count` correctness. Dummy simulation must mirror real output length closely for output-limited encoding.

## Test Signals
Round-trip tests with very small output buffers, output-limit tests, flush boundary tests, EOPM emission, and assertions for `RC_SYMBOLS_MAX`. Compare dummy and real encoded sizes near limits.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/rangecoder/range_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/Makefile.inc -->
# sources/compression/xz/src/liblzma/simple/Makefile.inc

## Purpose
Automake fragment that includes the common simple filter wrapper and conditionally includes encoder/decoder/property and architecture-specific BCJ filter sources.

## Important APIs, Types, And Functions
No C APIs. Build variables:
- Always adds `simple_coder.c`, `simple_coder.h`, and `simple_private.h`.
- `COND_ENCODER_SIMPLE` adds `simple_encoder.c/.h`.
- `COND_DECODER_SIMPLE` adds `simple_decoder.c/.h`.
- Per-filter conditions add `x86.c`, `powerpc.c`, `ia64.c`, `arm.c`, `armthumb.c`, `arm64.c`, `sparc.c`, and `riscv.c`.

## Control Flow
Build-time conditionals select feature-specific sources.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Included by liblzma build setup. Conditions must match configured filter support and public filter IDs.

## Risks
Mismatched conditions can expose filter IDs without implementations or compile unused code. Common wrapper must always be included when any simple filter is enabled.

## Test Signals
Autotools matrix builds for individual BCJ filters, encoder-only, decoder-only, and all-filters configurations.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/Makefile.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/arm.c -->
# sources/compression/xz/src/liblzma/simple/arm.c

## Purpose
Implements the ARM BCJ simple filter for 32-bit ARM branch-with-link instructions.

## Important APIs, Types, And Functions
- `arm_code()` converts 24-bit branch immediates between relative and absolute form.
- `arm_coder_init()` wires the filter through `lzma_simple_coder_init()`.
- Conditional exports `lzma_simple_arm_encoder_init()` and `lzma_simple_arm_decoder_init()`.

## Control Flow
The filter rounds size down to a 4-byte boundary, scans each instruction, and detects BL by `buffer[i+3] == 0xEB`. It reconstructs the 24-bit immediate, shifts by two, adds or subtracts `now_pos + i + 8` depending on encode/decode, shifts back, and writes the immediate bytes.

## State And Persistence
No filter-specific persistent state. Position comes from the wrapper's `now_pos`.

## Dependencies And Integration Points
Includes `simple_private.h`. Uses common simple wrapper with `unfiltered_max=4` and `alignment=4`.

## Risks
False positives in non-code data are possible. Correctness depends on 4-byte alignment and ARM PC bias of 8. It ignores incomplete trailing bytes by returning the filtered boundary.

## Test Signals
Encode/decode inverse tests for aligned ARM BL instructions, arbitrary-data bijection tests, start offset handling, and trailing 1-3 byte buffers.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/arm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/arm64.c -->
# sources/compression/xz/src/liblzma/simple/arm64.c

## Purpose
Implements ARM64 BCJ filtering for BL and ADRP instructions and exposes standalone buffer encode/decode APIs when enabled.

## Important APIs, Types, And Functions
- `arm64_code()` converts BL and selected ADRP immediates.
- `arm64_coder_init()` wires wrapper settings.
- Conditional filter-chain exports `lzma_simple_arm64_encoder_init()` and decoder init.
- Standalone APIs `lzma_bcj_arm64_encode()` and `lzma_bcj_arm64_decode()`.

## Control Flow
The function rounds size to 4 bytes and scans 32-bit little-endian instructions. BL is detected by top opcode bits and converted by adding/subtracting `pc >> 2` to the 26-bit immediate. ADRP is detected with mask `0x9F000000`, extracts immediate pieces, skips values outside a +/-512 MiB compromise range, clears immediate fields, adds/subtracts page PC, and writes the transformed immediate back. Standalone APIs mask start offset to a 4-byte boundary.

## State And Persistence
No persistent filter-specific state. Wrapper tracks `now_pos`.

## Dependencies And Integration Points
Uses `read32le()`/`write32le()` from common headers through `simple_private.h`. The wrapper uses `unfiltered_max=4` and `alignment=4`.

## Risks
BL uses only six opcode bits, so false positives in non-code data are a known ratio tradeoff. ADRP conversion assumes useful range and may depend on section alignment. Auto-vectorization is explicitly disabled for Clang due to code size/performance risk.

## Test Signals
Inverse tests for BL and ADRP, standalone API tests, start-offset masking, random-data bijection checks, and benchmark coverage for Clang/GCC builds.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/arm64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/armthumb.c -->
# sources/compression/xz/src/liblzma/simple/armthumb.c

## Purpose
Implements BCJ filtering for ARM-Thumb BL instruction pairs.

## Important APIs, Types, And Functions
- `armthumb_code()` converts two-halfword Thumb branch immediates.
- `armthumb_coder_init()` wires the simple wrapper.
- Conditional exports `lzma_simple_armthumb_encoder_init()` and decoder init.

## Control Flow
If fewer than four bytes are available it filters nothing. Otherwise it scans every two bytes through `size - 4`, detects the high-halfword/low-halfword BL pattern, reconstructs the immediate, converts with `now_pos + i + 4` on encode or subtracts on decode, writes updated halfwords, and skips the second half of the matched instruction.

## State And Persistence
No filter-specific state. `now_pos` is maintained by the wrapper.

## Dependencies And Integration Points
Uses `simple_private.h` and wrapper parameters `unfiltered_max=4`, `alignment=2`.

## Risks
Detection may match non-code data. Offsets depend on Thumb PC bias of 4 and halfword alignment. The loop leaves trailing bytes for the wrapper when an incomplete instruction remains.

## Test Signals
Encode/decode inverse tests for Thumb BL, unaligned start-offset rejection through wrapper, trailing byte behavior, and random-data bijection checks.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/armthumb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/ia64.c -->
# sources/compression/xz/src/liblzma/simple/ia64.c

## Purpose
Implements BCJ filtering for IA-64/Itanium bundle branch slots.

## Important APIs, Types, And Functions
- `BRANCH_TABLE` maps 5-bit instruction templates to branch slot masks.
- `ia64_code()` scans 16-byte bundles and converts matching branch immediate fields.
- `ia64_coder_init()` wires wrapper settings.
- Conditional encoder/decoder init exports.

## Control Flow
The filter rounds size to a 16-byte boundary. For each bundle it reads the template, checks branch-capable slots using `BRANCH_TABLE`, extracts the 41-bit slot instruction across up to six bytes, checks branch opcode fields, extracts and converts a 21-bit shifted immediate relative to `now_pos + i`, clears/reinserts fields, and writes back the touched bytes.

## State And Persistence
No persistent filter state. Wrapper tracks `now_pos`.

## Dependencies And Integration Points
Includes `simple_private.h`; wrapper uses `unfiltered_max=16` and `alignment=16`.

## Risks
Bitfield extraction across byte boundaries is complex and easy to break. Correct template masks are essential. False positives in non-code bundles are possible. Only complete 16-byte bundles are processed.

## Test Signals
Known IA-64 branch instruction vectors, encode/decode inverse tests, every branch table template, trailing bundle fragments, and random-data bijection.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/ia64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/powerpc.c -->
# sources/compression/xz/src/liblzma/simple/powerpc.c

## Purpose
Implements BCJ filtering for big-endian PowerPC branch instructions.

## Important APIs, Types, And Functions
- `powerpc_code()` detects and converts PowerPC branch immediates.
- `powerpc_coder_init()` wires the wrapper.
- Conditional encoder/decoder init exports.

## Control Flow
The filter rounds size to 4 bytes, scans instructions, detects branch opcode `0x48`-class with link/absolute bit condition, reconstructs a 26-bit aligned source offset, adds/subtracts `now_pos + i`, and writes the destination bits while preserving low flag bits.

## State And Persistence
No filter-specific persistent state.

## Dependencies And Integration Points
Uses `simple_private.h` with wrapper `unfiltered_max=4`, `alignment=4`.

## Risks
Endian handling is manual. Detection choices affect false positives. Preserving low instruction bits is required for reversibility.

## Test Signals
Known PowerPC branch vectors, inverse encode/decode, random-data bijection, and trailing-byte handling.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/powerpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/riscv.c -->
# sources/compression/xz/src/liblzma/simple/riscv.c

## Purpose
Implements RISC-V BCJ filtering for RV32/RV64 instruction streams, covering JAL and sequential AUIPC+instruction pairs, with separate encode and decode paths plus standalone buffer APIs.

## Important APIs, Types, And Functions
- Macros `NOT_AUIPC_PAIR()` and `NOT_SPECIAL_AUIPC()` validate AUIPC pair and special-format conditions compactly.
- `riscv_encode()` converts JAL and AUIPC+inst2 to compression-friendly absolute-address forms.
- `riscv_decode()` reverses real and fake transformed forms.
- Conditional exports `lzma_simple_riscv_encoder_init()`/decoder init and standalone `lzma_bcj_riscv_encode()`/decode.

## Control Flow
The encoder requires at least 8 bytes and scans every two bytes because compressed 16-bit instructions can appear. JAL with rd x1 or x5 is converted by rearranging the 20-bit immediate into big-endian address-like bytes after adding PC. AUIPC with rd not x0/x2 is checked against the following 32-bit instruction; if it is not a pair, the scanner skips enough bytes to avoid decoder desynchronization on false AUIPC+AUIPC patterns. Valid pairs are encoded into a special AUIPC rd=x2 format that stores low bits of inst2 in the first word and the absolute address in big-endian order in the second word. AUIPC with rd x0 or x2 is skipped or fake-decoded if it already matches the special format so the transform remains bijective on arbitrary data.

The decoder mirrors this. It decodes JAL big-endian address bytes back to J-type immediate bits. For AUIPC, ordinary-looking pairs are fake-encoded into the special form, while special-form pairs are decoded by reading the big-endian absolute address, subtracting PC, reconstructing inst2, and rebuilding AUIPC with sign-extension compensation.

## State And Persistence
No filter-specific heap state. The wrapper tracks `now_pos`; standalone APIs mask start offset to an even boundary. Transform state is entirely local to each buffer scan.

## Dependencies And Integration Points
Includes `simple_private.h`, uses endian helpers, and is included only under RISC-V filter feature macros. Wrapper parameters are `unfiltered_max=8` and `alignment=2`.

## Risks
This is the most complex simple filter. It intentionally accepts relaxed AUIPC pairs for speed/size, so false positives and future compiler codegen patterns are central risks. The fake conversion is required for bijection on arbitrary byte streams; skipping distances are part of decoder synchronization. Big-endian storage is used inside an otherwise little-endian instruction stream for compression ratio. C-extension scanning by 2 bytes and the `size < 8` rule mean last-six-byte JALs are intentionally not converted.

## Test Signals
Golden vectors for JAL, AUIPC+JALR, AUIPC+ADDI, loads/stores, rd x0/x2 cases, fake special-format bytes, and non-pair AUIPC+AUIPC. Random-data encode/decode bijection tests are critical. Real RISC-V binaries from GCC/Clang should be benchmarked for ratio and tested under chunked buffer boundaries.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/riscv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/simple_coder.c -->
# sources/compression/xz/src/liblzma/simple/simple_coder.c

## Purpose
Implements the common wrapper for BCJ/simple filters, handling filter-chain integration, buffering of unfiltered tails, start offsets, finish behavior, and memory ownership.

## Important APIs, Types, And Functions
- `copy_or_code()` either copies input directly or calls the next filter to provide data.
- `call_filter()` invokes the architecture-specific filter and advances `now_pos`.
- `simple_code()` is the main filter-chain callback.
- `simple_coder_end()` frees next coder, filter-specific state, and wrapper.
- `simple_coder_update()` forwards unsupported updates to the next filter.
- `lzma_simple_coder_init()` allocates/configures the wrapper and initializes the next filter.

## Control Flow
`simple_code()` rejects `LZMA_SYNC_FLUSH`. It first flushes already filtered bytes from the internal buffer. If output has enough room, it copies any buffered tail to output, gets more data from input or the next coder, filters the new output range in place, and copies any unfiltered tail back into the internal buffer. If buffered data remains, it compacts/fills the internal buffer, filters as much as possible, treats all remaining data as filtered at end-of-stream, and flushes to output. It returns `LZMA_STREAM_END` only after the next/end condition is reached and all buffered data is emitted.

## State And Persistence
Persistent wrapper state includes next coder, `end_was_reached`, direction flag, filter callback, optional filter-specific state, `now_pos`, allocated buffer size, buffer flush position, filtered boundary, current buffer size, and flexible buffer contents. Tail bytes that cannot yet be filtered are persisted across calls.

## Dependencies And Integration Points
Includes `simple_private.h`. Called by every architecture-specific simple filter init with its callback, private-state size, maximum unfiltered tail, required alignment, and direction.

## Risks
Buffer pointer arithmetic must avoid undefined behavior when `out == NULL`; the code includes explicit checks. `unfiltered <= allocated/2` depends on filter callbacks returning conservative filtered sizes. No sync flush support may surprise filter-chain users. Allocation of `simple` after wrapper allocation can leak wrapper if not cleaned by caller on error unless higher-level init handles it. Alignment validation uses start offsets from options.

## Test Signals
Streaming tests with tiny input/output buffers, no next coder, next coder returning `STREAM_END`, finish behavior, unsupported sync flush, nonzero start offsets, invalid alignment, and filters with unfiltered tails. Leak tests around allocation failures are useful.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/simple_coder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/simple_coder.h -->
# sources/compression/xz/src/liblzma/simple/simple_coder.h

## Purpose
Declares encoder and decoder initialization entry points for all simple/BCJ filters.

## Important APIs, Types, And Functions
Declares paired init functions for x86, PowerPC, IA-64, ARM, ARM-Thumb, ARM64, SPARC, and RISC-V encoders and decoders.

## Control Flow
No runtime flow. This header centralizes init prototypes for filter registration code.

## State And Persistence
No state.

## Dependencies And Integration Points
Includes `common.h` for liblzma core types. Used by simple encoder/decoder property code, architecture filter files, and filter initialization tables.

## Risks
Prototype availability must match feature macro builds and implementation files. Missing declarations can break filter registration or cause conditional build drift.

## Test Signals
Build all filter combinations and verify each enabled filter can initialize both encoder and decoder chains.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/simple_coder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/simple_decoder.c -->
# sources/compression/xz/src/liblzma/simple/simple_decoder.c

## Purpose
Decodes serialized BCJ/simple filter properties into `lzma_options_bcj`.

## Important APIs, Types, And Functions
- `lzma_simple_props_decode()` parses zero-byte or four-byte properties.

## Control Flow
If `props_size` is zero, defaults are used and it returns OK. If size is not four, it returns `LZMA_OPTIONS_ERROR`. For four bytes it allocates `lzma_options_bcj`, reads little-endian `start_offset`, frees the allocation if the offset is zero, otherwise stores it through `options`.

## State And Persistence
Allocates an options struct only for non-default start offsets. Caller owns the resulting options through liblzma allocator conventions.

## Dependencies And Integration Points
Includes `simple_decoder.h`, uses `read32le()` and allocator helpers. Used by raw/container filter property decoding for BCJ filters.

## Risks
The function assumes `*options` already represents default NULL when props are empty or offset zero; callers must initialize it appropriately. Allocation failure returns `LZMA_MEM_ERROR`.

## Test Signals
Decode empty props, four zero bytes, nonzero start offset, invalid prop lengths, and allocation-failure paths.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/simple_decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/simple_decoder.h -->
# sources/compression/xz/src/liblzma/simple/simple_decoder.h

## Purpose
Declares property decoding for simple/BCJ filters.

## Important APIs, Types, And Functions
- `lzma_simple_props_decode()`.

## Control Flow
No runtime flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Includes `simple_coder.h` so filter init prototypes and common types are visible to decoder property users.

## Risks
Minimal; declaration must stay in sync with implementation.

## Test Signals
Decoder build configurations and property decode tests.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/simple_decoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/simple_encoder.c -->
# sources/compression/xz/src/liblzma/simple/simple_encoder.c

## Purpose
Encodes serialized BCJ/simple filter properties and reports their encoded size.

## Important APIs, Types, And Functions
- `lzma_simple_props_size()` returns 0 for default/no options or 4 for nonzero start offset.
- `lzma_simple_props_encode()` writes little-endian start offset when nonzero.

## Control Flow
Both functions inspect `options` as `lzma_options_bcj`. Default NULL or zero offset produces no property bytes. Nonzero offset writes four bytes.

## State And Persistence
No persistent state. Writes caller-provided output buffer.

## Dependencies And Integration Points
Includes `simple_encoder.h`, uses `write32le()`. Used by filter property serialization.

## Risks
Callers must provide a large enough `out` buffer when size is 4. Start offset alignment is validated later by `lzma_simple_coder_init()`, not here.

## Test Signals
Property size/encode tests for NULL, zero, and nonzero offsets; decode symmetry with `simple_decoder.c`.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/simple_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/simple_encoder.h -->
# sources/compression/xz/src/liblzma/simple/simple_encoder.h

## Purpose
Declares property size and encode helpers for simple/BCJ filters.

## Important APIs, Types, And Functions
- `lzma_simple_props_size()`.
- `lzma_simple_props_encode()`.

## Control Flow
No runtime flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Includes `simple_coder.h`. Used by filter property encoding paths.

## Risks
Minimal; prototypes must match implementation and conditional build usage.

## Test Signals
Encoder property build and symmetry tests.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/simple_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/simple_private.h -->
# sources/compression/xz/src/liblzma/simple/simple_private.h

## Purpose
Defines the private wrapper state for simple/BCJ filters and declares the common initializer used by architecture filters.

## Important APIs, Types, And Functions
- `lzma_simple_coder` stores next coder, end flag, direction flag, filter callback, optional filter-specific state, current position, buffer allocation/positions, and flexible buffer.
- `lzma_simple_coder_init()` declaration accepts filter callback, private-state size, maximum unfiltered tail, alignment, and direction.

## Control Flow
No direct control flow; describes the callback signature that architecture filters implement.

## State And Persistence
Defines all persistent state used by `simple_coder.c`, including unflushed filtered bytes and unfiltered tail bytes.

## Dependencies And Integration Points
Includes `simple_coder.h`. Used by all architecture-specific simple filter implementations.

## Risks
Flexible-array allocation size must match `allocated`. Callback contract requires returning the number of bytes safely filtered and leaving incomplete instruction tails unfiltered.

## Test Signals
Wrapper streaming tests for every filter and struct allocation/free tests under sanitizers.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/simple_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/sparc.c -->
# sources/compression/xz/src/liblzma/simple/sparc.c

## Purpose
Implements BCJ filtering for SPARC branch/call-like instructions.

## Important APIs, Types, And Functions
- `sparc_code()` detects SPARC branch encodings and converts addresses.
- `sparc_coder_init()` wires wrapper settings.
- Conditional encoder/decoder init exports.

## Control Flow
The filter rounds size to 4 bytes and scans words. It detects instructions whose first bytes match SPARC call/branch patterns, builds a big-endian 32-bit source, shifts by two, adds/subtracts `now_pos + i`, shifts back, reconstructs sign/format bits, and writes the word.

## State And Persistence
No filter-specific state.

## Dependencies And Integration Points
Uses `simple_private.h` with `unfiltered_max=4`, `alignment=4`.

## Risks
Manual sign and bit reconstruction is delicate. False positives in non-code data can hurt compression. Only full aligned words are transformed.

## Test Signals
Known SPARC vectors, encode/decode inverse tests, random-data bijection, and trailing-byte tests.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/sparc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/x86.c -->
# sources/compression/xz/src/liblzma/simple/x86.c

## Purpose
Implements the x86 BCJ filter for CALL/JMP rel32 instructions, including state needed to avoid unsafe conversions around overlapping branch bytes.

## Important APIs, Types, And Functions
- `Test86MSByte()` checks whether the high address byte is 0x00 or 0xFF.
- `lzma_simple_x86` stores `prev_mask` and `prev_pos`.
- `x86_code()` converts E8/E9 relative addresses to/from absolute-like values.
- `x86_coder_init()` initializes wrapper and x86-specific state.
- Conditional filter-chain init exports and standalone `lzma_bcj_x86_encode()`/decode.

## Control Flow
The filter requires at least five bytes. It adjusts previous-position state, scans until `size - 5`, and only processes opcodes E8/E9. It updates `prev_mask` based on distance from previous branch candidate, checks high-byte plausibility and mask constraints, reads the rel32 source, repeatedly converts and checks masked high bytes until stable, writes transformed bytes, and advances past the instruction. Non-converted candidates update the mask and advance one byte.

## State And Persistence
`prev_mask` and `prev_pos` persist across streaming calls in the filter-specific state. Standalone APIs create fresh state with `prev_pos = -5`.

## Dependencies And Integration Points
Uses `simple_private.h`; wrapper uses `simple_size=sizeof(lzma_simple_x86)`, `unfiltered_max=5`, `alignment=1`. Standalone APIs expose buffer transforms outside filter chains.

## Risks
State handling is essential for bijection and avoiding false conversions. The mask logic is inherited from classic BCJ filters and is hard to reason about. It scans arbitrary bytes, so false positives are a compression risk. Buffer tails shorter than five bytes must remain unfiltered.

## Test Signals
Known x86 CALL/JMP vectors, streaming boundaries across a 5-byte instruction, repeated branch candidates, standalone API tests, random-data bijection, and start offset variations.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/simple/x86.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/validate_map.sh -->
# sources/compression/xz/src/liblzma/validate_map.sh

## Purpose
Shell validation script for liblzma symbol version map files. It detects missing exported API symbols, obsolete alpha/beta version names, duplicate map lines, and divergence between generic and Linux maps.

## Important APIs, Types, And Functions
No functions are defined. Important variables:
- `SYMS` lists API symbols from `api/lzma/*.h` that are absent from `liblzma_generic.map`.
- `VER` and `NAMES` check alpha/beta version naming.
- `DUPS` identifies duplicate map lines.
- `IN_SYNC` flags mismatch between `liblzma_linux.map` and `liblzma_generic.map` after deleting fixed compatibility lines.
- `STATUS` is final exit status.

## Control Flow
The script sets `LC_ALL=C`, changes to its own directory, derives missing symbols with `sed`, `sort`, and `grep`, obtains package version via `build-aux/version.sh`, checks old alpha/beta names for non-development releases, finds duplicate map lines, compares Linux and generic maps with a fixed line deletion, prints grouped diagnostics if anything is wrong, and exits 1 on problems or 0 otherwise.

## State And Persistence
No persistent state. It reads source headers and map files and writes diagnostics to stdout.

## Dependencies And Integration Points
Depends on POSIX shell, `sed`, `sort`, `grep`, `cmp`, and `build-aux/version.sh`. Intended for maintainer/build validation around `liblzma_generic.map` and `liblzma_linux.map`.

## Risks
Line-number deletion `sed '111,125d'` is brittle if the Linux compatibility block moves. Symbol extraction regex only matches a specific `extern LZMA_API(...) name(` pattern. Map parsing ignores lines containing `{}`, `:`, or `*`, so formatting changes can affect results.

## Test Signals
Run in CI/maintainer checks. Mutating maps to remove a symbol, add duplicate lines, or desynchronize Linux/generic maps should produce expected failures.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/validate_map.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/lzmainfo/Makefile.am -->
# sources/compression/xz/src/lzmainfo/Makefile.am

## Purpose
Automake rules for building, linking, installing, and uninstalling the `lzmainfo` compatibility tool and its man pages.

## Important APIs, Types, And Functions
Build variables:
- `bin_PROGRAMS = lzmainfo`.
- `lzmainfo_SOURCES` includes `lzmainfo.c` and common tuklib helpers.
- Conditional `lzmainfo_w32res.rc` for Windows.
- `lzmainfo_CPPFLAGS` includes locale/common/liblzma API paths.
- `lzmainfo_LDADD` links liblzma, optional gnulib, and intl.
- `dist_man_MANS = lzmainfo.1`.
- Hooks install/uninstall translated man pages.

## Control Flow
Automake builds the binary, compiles Windows resources when needed, and custom install hooks iterate translated man directories, invoking `install-man` with overridden man variables. Uninstall hook removes translated man pages.

## State And Persistence
No runtime state. Installation creates binary and man page artifacts.

## Dependencies And Integration Points
Integrates with top-level gettext/NLS, gnulib, liblzma, Windows resource compiler, and po4a translated man page layout.

## Risks
Install hooks rely on Automake internals and shell loops. Translated man installation depends on directory presence. Link order places `LTLIBINTL` after libgnu as needed.

## Test Signals
`make`, `make install DESTDIR=...`, `make uninstall`, Windows resource builds, and NLS enabled/disabled builds.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/lzmainfo/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/lzmainfo/lzmainfo.c -->
# sources/compression/xz/src/lzmainfo/lzmainfo.c

## Purpose
Implements the `lzmainfo` command-line tool for compatibility with LZMA Utils, printing metadata from the 13-byte `.lzma` header.

## Important APIs, Types, And Functions
- `help()` prints localized usage and exits.
- `version()` prints package version and exits.
- `parse_args()` handles `--help` and `--version`.
- `my_log2()` computes a simple base-2 exponent for dictionary display.
- `lzmainfo()` reads and parses one file's header, prints uncompressed size, dictionary size, lc, lp, and pb.
- `main()` initializes program name/gettext, sets binary stdin on DOS-like systems, dispatches stdin/files, and exits via tuklib.

## Control Flow
`main()` parses options, then either reads stdin or loops over operands. For each file, `lzmainfo()` reads 13 bytes, decodes first five bytes with `lzma_properties_decode()` for LZMA1, interprets the next eight bytes as little-endian uncompressed size, prints fields in LZMA Utils-compatible text, frees decoded options, and reports errors without aborting the whole file loop except for memory/internal errors.

## State And Persistence
No persistent state besides process exit status. Each file allocates and frees `filter.options`.

## Dependencies And Integration Points
Depends on liblzma API, getopt, gettext/tuklib wrappers for program name, nonprint masking, wrapping, and exit. Built by `src/lzmainfo/Makefile.am`.

## Risks
It opens files with `"r"` rather than `"rb"` except stdin is set binary on DOS-like systems; platform C runtime behavior may matter. `my_log2()` assumes meaningful dictionary sizes from decoded properties. Output format is intentionally not translated in the data fields to preserve script compatibility.

## Test Signals
Run against valid `.lzma` headers with known/unknown uncompressed sizes, invalid property byte, too-short file, stdin, `-` operand, multiple files, nonprint filenames, and `--help`/`--version`.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/lzmainfo/lzmainfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/scripts/Makefile.am -->
# sources/compression/xz/src/scripts/Makefile.am

## Purpose
Automake rules for installing shell wrapper scripts (`xzdiff`, `xzgrep`, `xzmore`, `xzless`), compatibility symlinks, and translated man page symlinks.

## Important APIs, Types, And Functions
Build variables:
- `nodist_bin_SCRIPTS = xzdiff xzgrep xzmore xzless`.
- `dist_man_MANS` lists four man pages.
- `links` maps target-link pairs for xzcmp/xzegrep/xzfgrep and optional LZMA-compatible names.
- `install-exec-hook`, `install-data-hook`, and `uninstall-hook`.

## Control Flow
Install hooks create executable symlinks in bindir, install translated man pages if available, and create man-page symlinks matching executable aliases. Uninstall hooks remove symlinks and man-page aliases.

## State And Persistence
Installation mutates bindir and mandir contents through symlinks and installed man pages.

## Dependencies And Integration Points
Uses Automake transforms, `LN_S`, gettext/po4a man directories, and `COND_LZMALINKS`.

## Risks
Shell quoting around transformed names and directories must remain portable. Man-page symlinks are only made when target man page exists. Hooks rely on Automake internals for translated man installation.

## Test Signals
`make install/uninstall DESTDIR=...` with and without `COND_LZMALINKS`, with NLS translated man directories, and with program name transforms.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/scripts/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/scripts/xzdiff.in -->
# sources/compression/xz/src/scripts/xzdiff.in

## Purpose
Template for `xzdiff`/`xzcmp`, comparing uncompressed contents of compressed files or a compressed file against its uncompressed counterpart.

## Important APIs, Types, And Functions
Shell variables:
- `xz='@xz@ --format=auto'` with `XZ_OPT` preserved for limits/threads.
- `prog` and `cmp` selected by executable name and environment (`DIFF`/`CMP`).
- `escape` sed script quotes user options for later `eval`.
- `xz1`, `xz2` choose decompressor commands by suffix.
- `xz_status` captures decompressor exit statuses through extra file descriptors.

## Control Flow
The script parses `--help`, `--version`, `--`, and cmp/diff options, validating input files. For one operand, it derives the uncompressed filename from recognized suffixes and compares decompressed input to that file. For two operands, it chooses decompressor commands based on each suffix and handles compressed-compressed, stdin-stdin, `/dev/fd` capable systems, and fallback temporary directory comparison. It then reconciles decompressor statuses, ignoring successful decompression and SIGPIPE, and exits with the diff/cmp status or 2 on decompression/setup errors.

## State And Persistence
May create a temporary directory in fallback two-compressed-file mode and removes it via traps. No persistent state otherwise.

## Dependencies And Integration Points
Configured by Autotools placeholders for shell, xz path, package metadata, and optional path setup. Integrates with gzip, bzip2, lzop, zstd, lz4 when suffixes indicate those formats. Installed via `scripts/Makefile.am`.

## Risks
Uses `eval` to run user-selected diff/cmp and quoted options; escaping is central to safety. Suffix inference is broad and can misclassify names. `/dev/fd` probing handles old shell bugs. Temporary directory fallback must be secure and cleaned on signals. Preserving `XZ_OPT` is intentional but changes resource behavior.

## Test Signals
Tests for one/two operands, stdin, xz/gz/bz2/lzo/zstd/lz4 suffixes, files with quotes/spaces/newlines where possible, diff and cmp modes, decompressor failures, SIGPIPE from early cmp/diff exit, mktemp fallback, and `--help`/`--version`.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/scripts/xzdiff.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/scripts/xzgrep.in -->
# sources/compression/xz/src/scripts/xzgrep.in

## Purpose
Template for `xzgrep`, `xzegrep`, and `xzfgrep`, running grep variants over decompressed input.

## Important APIs, Types, And Functions
Shell variables:
- `xz='@xz@ --format=auto'`.
- `prog`/`grep` selected from executable name and `GREP`.
- `escape` quotes options/patterns for `eval`.
- Flags track pattern presence and filename/list modes.
- `grep_supports_label` detects support for `grep -H --label`.
- Per-file `uncompress`, `xz_status`, and result accumulator `res`.

## Control Flow
The script parses grep options, rejects recursive/directory/null-data options that cannot be supported, handles `--help`/`--version`, identifies options requiring arguments, and ensures a pattern via `-e` if needed. It defaults files to stdin. For each input, it chooses a decompressor by suffix or xz autodetection, pipes decompressed data into grep, handles `-l`/`-L`, filename prefixing via `--label` or a sed fallback, captures decompressor status separately, ignores SIGPIPE when grep exits early, and accumulates grep-like exit status semantics.

## State And Persistence
No persistent filesystem state. Result state is process-local across file loop.

## Dependencies And Integration Points
Autotools placeholders configure shell/xz/package/path. Depends on grep, sed, expr, gzip/bzip2/lzop/zstd/lz4 as needed. Installed by scripts Automake rules and invoked through symlink aliases.

## Risks
Complex POSIX shell parsing and `eval` require careful escaping. Option support intentionally excludes recursive/directory/null-data behavior. Filename prefix sed fallback must escape metacharacters and newlines. Different grep implementations have different `--label` support and binary-file behavior. Exit status handling around signals differs across shells.

## Test Signals
Pattern with/without `-e`, option clusters, grep modes (`-H`, `-h`, `-l`, `-L`), unsupported options, stdin, all supported suffixes, decompressor errors, SIGPIPE from `grep -q`, filenames with special characters, and grep implementations without `--label`.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/scripts/xzgrep.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/scripts/xzless.in -->
# sources/compression/xz/src/scripts/xzless.in

## Purpose
Template for `xzless`, using `less` with `LESSOPEN` to view decompressed xz-compatible files.

## Important APIs, Types, And Functions
Variables:
- `xz='@xz@ --format=auto'`.
- `LESSMETACHARS` workaround for old less versions.
- `VER` parsed from `less -V`.
- `LESSOPEN` configured differently by less version.
- `SHOW_PREPROC_ERRORS` enabled for less >= 632.

## Control Flow
The script handles `--help` and `--version`, initializes `LESSMETACHARS` if absent, parses the major less version, selects `LESSOPEN` prefix form (`||-`, `|-`, or `|`) based on version capabilities, optionally enables `--show-preproc-errors`, exports variables, and execs `less`.

## State And Persistence
Exports environment variables for the executed `less` process only.

## Dependencies And Integration Points
Configured shell/xz/package placeholders. Depends on `less` behavior and xz autodetection. Installed with script aliases by Automake.

## Risks
Version parsing assumes `less -V` output format and numeric version. `exec less $SHOW_PREPROC_ERRORS "$@"` intentionally allows the optional flag to split but depends on it being empty or one option. Preserving `XZ_OPT` can affect resource limits.

## Test Signals
Run with less versions below 429, 429-450, 451+, and 632+ if available or mocked. Test empty compressed files, stdin, file arguments, `--help`, `--version`, and inherited `LESSMETACHARS`.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/scripts/xzless.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/scripts/xzmore.in -->
# sources/compression/xz/src/scripts/xzmore.in

## Purpose
Template for `xzmore`, viewing decompressed files through `more` or `$PAGER` with interactive prompts between files.

## Important APIs, Types, And Functions
Variables:
- `xz='@xz@ --format=auto'`.
- `oldtty`, `cb`, and `ncb` manage terminal mode.
- `FIRST`, `FILE`, and `ANS` implement multi-file prompting.

## Control Flow
The script handles `--help` and `--version`, saves terminal settings, sets traps to restore terminal mode, and either reads stdin or iterates files. With no args and tty stdin it prints usage and exits 1; otherwise it pipes decompressed stdin to `${PAGER:-more}`. For multiple files it prompts before subsequent files, lets `e`/`q` exit and `s` skip, prints a file banner, and pipes `xz -cdfqQ -- "$FILE"` to the pager.

## State And Persistence
Temporarily changes terminal mode and restores it via traps. No persistent filesystem state.

## Dependencies And Integration Points
Configured shell/xz/package placeholders. Depends on `stty`, `dd`, `more`/`PAGER`, and xz. Installed via scripts Automake rules.

## Risks
Uses `eval "${PAGER:-more}"`, so pager environment content is executed as shell code by design. Terminal restoration must work across signals. File readability check uses `true < "$FILE"`. `XZ_OPT` is preserved.

## Test Signals
No-arg tty and pipe modes, single and multiple files, prompt responses `q/e/s/other`, terminal restore on signals, custom `PAGER`, unreadable file, and `--help`/`--version`.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/scripts/xzmore.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/Makefile.am -->
# sources/compression/xz/src/xz/Makefile.am

## Purpose
Automake rules for building and installing the main `xz` command, optional list-mode sources, compatibility symlinks, Windows resources, and translated man-page aliases.

## Important APIs, Types, And Functions
Build variables:
- `bin_PROGRAMS = xz`.
- `xz_SOURCES` lists command modules, headers, and common tuklib helpers.
- `COND_MAIN_DECODER` adds `list.c/.h`.
- `COND_W32` adds resource file.
- `xz_CPPFLAGS` include locale/common/liblzma API paths.
- `xz_LDADD` links liblzma, optional gnulib, and intl.
- `xzlinks` includes `unxz`, `xzcat`, and optional LZMA Utils names.
- Install/uninstall hooks create/remove executable and man-page symlinks.

## Control Flow
Automake compiles the main program, conditionally includes decoder list support and Windows resource compilation, links libraries in the required order, installs `xz.1`, and creates symlinks for executable aliases and man-page aliases. Uninstall removes those aliases and man pages.

## State And Persistence
Installation mutates bindir and mandir through files/symlinks. No runtime state.

## Dependencies And Integration Points
Integrates with liblzma, common tuklib code, gnulib, gettext/NLS, Windows resource compiler, and po4a translated man directories.

## Risks
Source list must stay synchronized with actual command modules. Link order around `libgnu.a` and `LTLIBINTL` matters. Install hooks rely on shell portability and Automake internals. Optional alias support changes installed surface area.

## Test Signals
`make`, `make check`, `make install/uninstall DESTDIR=...`, builds with/without main decoder, with/without LZMA links, NLS translated man pages, program-name transforms, and Windows resource builds.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/Makefile.am -->
