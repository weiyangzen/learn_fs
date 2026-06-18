# sources/distributed-fs/ceph-client/drivers/media/rc/ir-jvc-decoder.c

Purpose: generic rc-core raw decoder and encoder for the JVC pulse-distance IR protocol, including repeat detection.

Important APIs, types, and functions: constants define 16 bits, 525 us units, header, bit, trailer, and repeat spacing. `enum jvc_state` covers header, bit pulse/space, trailer, and repeat-check states. `ir_jvc_decode()` parses raw events, reverses byte bits with `bitrev8()`, emits `RC_PROTO_JVC` keydown on the first full frame, and treats later matching headerless frames as repeats. `ir_jvc_encode()` uses `ir_raw_gen_pd()` with `ir_jvc_timings`. `jvc_handler` registers decode/encode hooks, 38 kHz carrier, and timeout.

Control flow: the decoder requires an initial header pulse/space to start. It shifts 16 bits MSB-first, checks trailer pulse/space, emits the first scancode, stores `old_bits`, then moves to `STATE_CHECK_REPEAT`. A later event either resets on a new header or continues into another bit pulse sequence for repeat validation.

State and persistence behavior: per-device state includes count, bits, old bits, first-frame flag, toggle, and state. No persistent storage. Toggle is flipped at each new header.

Dependencies and integration points: depends on `rc-core-priv.h`, raw pulse-distance generator helpers, bit reversal, and rc-core keydown/repeat APIs.

Risks and edge cases: repeat validation requires repeated bits matching `old_bits`; mismatches reset as invalid. The source contains a visibly odd indentation before an `else`, but behavior is the standard header/no-header repeat branch. Timeout values must be long enough for JVC trailer spacing.

Test signals: decode a first JVC frame, repeated held-key frames, invalid repeat data, encode known scancodes, and verify carrier/min-timeout with transmit-capable devices.
