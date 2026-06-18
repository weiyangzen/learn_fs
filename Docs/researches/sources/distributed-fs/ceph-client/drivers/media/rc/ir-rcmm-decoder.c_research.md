# sources/distributed-fs/ceph-client/drivers/media/rc/ir-rcmm-decoder.c

Purpose: generic raw decoder and encoder for RC-MM 12-, 24-, and 32-bit pulse-distance-like two-bit-symbol protocols.

Important APIs, types, and functions: timing constants define prefix and four symbol spaces. `rcmm_mode()` determines toggle interpretation for 32-bit mode. `rcmm_miscmode()` emits 12- or 24-bit scancodes when a non-symbol duration terminates shorter frames. `ir_rcmm_decode()` parses prefix, low/bump/value sequence, stores two bits per symbol, emits `RC_PROTO_RCMM32` with optional toggle or delegates shorter frames. `ir_rcmm_rawencoder()` and `ir_rcmm_encode()` produce raw events for each bit length. `rcmm_handler` registers all RC-MM protocol bits.

Control flow: decoder starts on prefix pulse plus low space, then alternates one-unit bump pulses with one of four value spaces. Count increments by two until 32 bits, or an unrecognized value duration triggers short-frame handling for 12/24 bits. Final pulse after 32 bits emits if RCMM32 is enabled.

State and persistence behavior: per-device state stores state, count, and accumulated bits. No persistent storage.

Dependencies and integration points: depends on rc-core private raw helpers, enabled protocol masks, and rc-core keydown APIs. It complements the ImgTec header's unsupported two-bit pulse-position code type; the ImgTec hardware path marks that code type broken.

Risks and edge cases: short-frame detection is based on a value-space miss, so noisy timings can choose between invalid and RCMM12/24 emission. `rcmm_mode()` changes whether bit 15 is treated as toggle. The decoder returns no events if none of the RCMM protocol bits are enabled.

Test signals: decode/encode RCMM12, RCMM24, RCMM32; toggle interpretation for mode frames; disabled-protocol no-op behavior; and symbol timing margins for each two-bit value.
