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
