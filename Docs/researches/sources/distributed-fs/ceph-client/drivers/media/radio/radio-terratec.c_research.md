# sources/distributed-fs/ceph-client/drivers/media/radio/radio-terratec.c

Purpose: implements board-specific support for the TerraTec ActiveRadio ISA card using the shared `radio-isa` V4L2 framework.

Important APIs and functions: module lifecycle is `terratec_init` and `terratec_exit`. Hooks are `terratec_alloc`, `terratec_s_mute_volume`, `terratec_s_frequency`, and `terratec_g_signal`, collected in `terratec_ops`.

Control flow: the radio-ISA framework probes the single supported port `0x590`, reserves two I/O bytes, registers the radio device, and calls this file's hooks for operations. Frequency setting converts V4L2 units to a legacy tuner value with 10.7 MHz IF adjustment, fills a 25-bit buffer by repeated subtraction, and clocks bits through write-enable/data/clock port toggles. Volume/mute writes an 8-bit digital volume pattern to `io + 1`; mute forces volume zero. Signal reads bit 1 at the base port, where set means no signal.

State and persistence: per-card state is the generic `radio_isa_card`; this file has only module parameters and static driver metadata. Hardware state is volatile and set through ISA I/O.

Dependencies and integration points: depends on `radio-isa.h`, ISA registration, direct I/O, and V4L2 behavior supplied by the shared framework. It advertises stereo and maximum volume 10.

Risks: only one I/O port is supported despite historical uncertainty. Frequency conversion is opaque and comment-marked as poorly understood. Volume programming writes only data bits without explicit visible clocking in this driver, relying on card behavior. There is no RDS support despite hardware notes mentioning SAA6588.

Test signals: probe at 0x590, `v4l2-compliance`, frequency tuning at low/mid/high FM values, mute/volume behavior on speaker output, signal bit readings, and unload releasing the requested region.
