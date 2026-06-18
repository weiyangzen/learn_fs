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
