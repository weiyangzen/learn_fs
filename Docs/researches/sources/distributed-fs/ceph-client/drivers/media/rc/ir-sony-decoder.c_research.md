# sources/distributed-fs/ceph-client/drivers/media/rc/ir-sony-decoder.c

Purpose: generic raw decoder and encoder for Sony SIRC 12-, 15-, and 20-bit pulse-length protocols.

Important APIs, types, and functions: constants define 600 us unit, 2.4 ms header pulse, pulse lengths for zero/one, and trailer space. `ir_sony_decode()` parses header, pulse-length bits, infers completion from remaining space, validates enabled protocol bits based on count, extracts device/subdevice/function with `bitrev8()`, and emits the correct Sony protocol. `ir_sony_encode()` converts rc-core scancodes back to raw bit layouts for each Sony variant and calls `ir_raw_gen_pl()`. `sony_handler` registers all Sony protocol bits, 40 kHz carrier, and timeout.

Control flow: after header pulse/space, bit pulses carry data value and bit spaces separate symbols. The decoder can enter finished state when the remaining space is longer than another bit. The final trailer chooses protocol by bit count and enabled-protocol mask.

State and persistence behavior: per-device state stores state, count, and bits. No persistent storage.

Dependencies and integration points: depends on bit reversal, rc-core raw pulse-length generator, enabled protocol masks, and keydown APIs. It shares scancode layout expectations with the ImgTec Sony descriptor.

Risks and edge cases: Sony variants are length-disambiguated, so enabled protocol masks can cause otherwise valid frames to be silently dropped. Completion detection relies on trailer space duration after subtracting bit spaces. Encoding assumes any non-12/non-15 protocol passed is Sony20.

Test signals: decode and encode Sony12/15/20, disabled protocol masks, noisy trailer spaces, scancode field extraction, and 40 kHz transmit carrier behavior.
