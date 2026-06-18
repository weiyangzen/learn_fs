# sources/distributed-fs/ceph-client/drivers/media/rc/ir-xmp-decoder.c

Purpose: raw decoder for the XMP IR protocol. It decodes two half-frames of variable nibble-duration data into a 32-bit scancode and treats nonzero toggle frames as repeats.

Important APIs, types, and functions: constants define 136 us unit, leader pulse, nibble prefix, half-frame space, and trailer space. `enum xmp_state` tracks inactive, leader pulse, and nibble-space states. `ir_xmp_decode()` stores 16 nibble durations, derives a divider from nibble 3, converts durations to nibble values, validates two checksum sums, verifies repeated subaddress, warns on unexpected OEM, constructs `addr << 24 | subaddr << 16 | obc1 << 8 | obc2`, and emits `rc_keydown()` for toggle 0 or `rc_repeat()` otherwise. `xmp_handler` registers a decode-only raw handler.

Control flow: a leader pulse starts collection. Each nibble is represented by a space duration after a leader. A half-frame space moves back to leader-pulse state and expects the second half. A trailer space finalizes exactly 16 collected nibbles. A 16-count half-frame is treated as a likely final key-up frame and rewinds to count 8 so the trailer can still be found.

State and persistence behavior: per-device state stores state, count, and duration/nibble array in `dev->raw->xmp`. No persistent storage and no encoder.

Dependencies and integration points: depends on rc-core private raw helpers and keydown/repeat APIs. It registers only `RC_PROTO_BIT_XMP`.

Risks and edge cases: divider derivation subtracts a fixed compensation and rejects values below 50, so receiver timing variation can affect decode. Toggle 9 frames are intentionally not distinguished in this implementation despite protocol comments. There is no encode path. OEM mismatch only logs a warning, not a rejection.

Test signals: decode known XMP full frames, repeat/toggle frames, checksum failures, subaddress mismatches, final half-frame behavior, and noisy divider values.
