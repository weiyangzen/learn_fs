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
