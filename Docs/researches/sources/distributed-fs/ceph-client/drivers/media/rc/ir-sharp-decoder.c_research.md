# sources/distributed-fs/ceph-client/drivers/media/rc/ir-sharp-decoder.c

Purpose: generic raw decoder and encoder for Sharp IR, including paired first/echo frames and a Denon-compatible first-frame variant.

Important APIs, types, and functions: constants define 15-bit message length, 40 us base unit, 320 us pulses, 1/2 ms bit periods, 40 ms echo spacing, and trailer spacing. `ir_sharp_decode()` parses pulse/space periods, records pulse length for period classification, validates first-frame exp/chk bits, waits for echo space, parses second frame, validates command/ext/check inversion, reverses address/command bits, and emits `RC_PROTO_SHARP`. `ir_sharp_encode()` emits the first and second 15-bit frames through `ir_raw_gen_pd()`. `sharp_handler` registers decode/encode hooks and timeout.

Control flow: decoding begins directly on a bit pulse without a leader. After 15 bits and a trailer pulse, the decoder moves through `STATE_ECHO_SPACE` to parse the second 15-bit echo. Final trailer space validates the pair and emits a scancode. Encoder emits two generated pulse-distance sequences: original command with exp/check bits and inverted command echo.

State and persistence behavior: per-device state stores state, count, bits, and last pulse length. The paired message is held in `bits` until the second half arrives.

Dependencies and integration points: depends on bit reversal, rc-core raw pulse-distance helpers, and keydown APIs. It aligns with the ImgTec Sharp descriptor, though the hardware descriptor reports only the first half.

Risks and edge cases: Sharp has no leader, increasing false-start risk. The first-frame check accepts both standard `(exp,chk) == 1,0` and Denon-style both zero. Pair validation masks only the command/ext/check region with `0x3ff`. Echo space is long and timeout-sensitive.

Test signals: decode standard Sharp, Denon-style first frames, invalid echo checksum, encode/decode round trip, and timeout around 40 ms echo gap.
