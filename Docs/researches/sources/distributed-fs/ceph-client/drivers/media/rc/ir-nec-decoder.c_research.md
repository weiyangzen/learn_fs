# sources/distributed-fs/ceph-client/drivers/media/rc/ir-nec-decoder.c

Purpose: generic rc-core raw decoder and encoder for normal NEC, NECX, and NEC32 pulse-distance IR protocols, including standard and NECX repeat handling.

Important APIs, types, and functions: constants define NEC timing and bit count. `enum nec_state` models header, bit, and trailer states. `ir_nec_decode()` parses timing events, distinguishes NEC and NECX header pulses, recognizes repeat spaces, accumulates 32 bits, converts bytes through `ir_nec_bytes_to_scancode()`, and emits `rc_keydown()` or `rc_repeat()`. `ir_nec_scancode_to_raw()` converts rc-core scancodes back to raw 32-bit NEC data. `ir_nec_encode()` uses `ir_raw_gen_pd()`. `nec_handler` registers all NEC-family protocol bits, 38 kHz carrier, and timeout.

Control flow: a header pulse transitions to header space. A repeat-length space jumps to trailer-pulse handling without reading 32 bits. Full frames shift bits MSB-first as durations are classified as zero or one spaces. Trailer space finalizes either a full scancode or a repeat. For NECX, one-bit repeat detection is tracked by `necx_repeat`.

State and persistence behavior: per-device NEC decoder state stores state, bit count, bits, NECX flag, and NECX repeat flag. No persistent storage beyond raw decoder state.

Dependencies and integration points: depends on bit reversal, `rc-core-priv.h`, `ir_nec_bytes_to_scancode()` from rc-core private helpers, raw pulse-distance generation, and rc-core keydown/repeat.

Risks and edge cases: NECX repeat logic differs from normal repeat and uses `NECX_REPEAT_BITS`. Inverse-byte interpretation is delegated to rc-core helper. Timing margins are protocol-specific and can reject noisy receivers. Encoder must honor the protocol enum to avoid ambiguous scancode interpretation.

Test signals: decode/encode NEC, NECX, NEC32; repeat frames for normal NEC and NECX; invalid timings; overflow reset; and transmit carrier defaults.
