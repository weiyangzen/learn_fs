# sources/distributed-fs/ceph-client/drivers/media/rc/ir-sanyo-decoder.c

Purpose: generic raw decoder and encoder for Sanyo/Aiwa/Chinon pulse-distance IR, a NEC-timed 42-bit protocol with address and command inverse fields.

Important APIs, types, and functions: constants define 42-bit length and NEC-like timings. `ir_sanyo_decode()` parses header, bits, repeat space, trailer, reverses address/command bits, validates command inverse, and emits `RC_PROTO_SANYO`. `ir_sanyo_encode()` constructs raw fields with bit-reversed address, inverse address, command, and inverse command, then calls `ir_raw_gen_pd()`. `sanyo_handler` registers decode/encode hooks, 38 kHz carrier, and timeout.

Control flow: after header pulse/space, each bit pulse and bit space shifts data. A long repeat space with zero data count causes `rc_repeat()`. A complete 42-bit frame goes through trailer validation and checksum before keydown.

State and persistence behavior: per-device state stores current state, count, and bits. Repeat is emitted without local previous-key storage because rc-core owns last key state.

Dependencies and integration points: depends on bit reversal, rc-core raw pulse-distance helpers, and keydown/repeat APIs. The protocol has a sibling ImgTec hardware descriptor with matching validation.

Risks and edge cases: the decoder validates only command inverse; address inverse extraction is commented out, so address inverse corruption may not be caught here. Repeat spacing is very long relative to bit spaces. Encoding uses `~scancode` masks and bit reversal; field-width mistakes would corrupt inverse fields.

Test signals: decode valid Sanyo frames, invalid command inverse, repeat frames, encode/decode round trip, and noisy long-space behavior.
