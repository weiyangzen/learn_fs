# sources/distributed-fs/ceph-client/drivers/media/rc/ir-rc5-decoder.c

Purpose: generic raw decoder and encoder for RC5, RC5X-20, and RC5 StreamZap Manchester-coded protocols.

Important APIs, types, and functions: constants define bit counts, 889 us unit, RC5X gap, and trailer. `ir_rc5_decode()` implements a Manchester state machine with special RC5X gap detection after eight bits, decodes protocol variants based on bit count and gap, extracts toggle/system/command/xdata fields, and emits `rc_keydown()`. Timing descriptors `ir_rc5_timings`, `ir_rc5x_timings`, and `ir_rc5_sz_timings` feed `ir_raw_gen_manchester()`. `ir_rc5_encode()` handles each protocol variant and returns `-EINVAL` for unsupported protocol enums. `rc5_handler` registers all three protocol bits.

Control flow: decoding starts on a pulse, consumes bit start/end units, checks for a trailer space, and at `STATE_FINISHED` selects RC5, RC5X, or RC5_SZ based on `is_rc5x` and `count`. Disabled protocol bits cause silent reset without keydown. Encoding splits RC5X into pre-gap and post-gap Manchester segments.

State and persistence behavior: per-device state includes state, count, bits, and `is_rc5x`. Toggle is emitted from frame bits. No persistent storage.

Dependencies and integration points: depends on rc-core raw Manchester helpers, enabled protocol masks, and keydown APIs. It complements the ImgTec hardware RC5 descriptor, which only supports standard RC5.

Risks and edge cases: RC5X detection after exactly `CHECK_RC5X_NBITS` is timing-sensitive. RC5 command extension bit handling inverts command bit semantics. Disabled protocol masks intentionally drop otherwise valid frames. StreamZap scancode is treated as raw enough for encoding.

Test signals: decode and encode RC5, RC5X-20, and RC5_SZ; verify toggle handling; test disabled enabled-protocol masks; and inject RC5X gap timing variations.
