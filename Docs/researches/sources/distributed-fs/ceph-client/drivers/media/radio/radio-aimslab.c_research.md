# Research: sources/distributed-fs/ceph-client/drivers/media/radio/radio-aimslab.c

Purpose: ISA driver for AIMSlab RadioTrack/RadioReveal FM cards using the `radio-isa` framework and LM7000 tuner helper.

Important types/APIs: `struct rtrack` extends `radio_isa_card` with current analog volume. It implements `alloc`, `init`, `s_mute_volume`, `s_frequency`, and `g_signal` callbacks. Module parameters are `io[]` and `radio_nr[]`; accepted ports are `0x20f` and `0x30f`.

Control flow: module init registers an ISA driver with max two instances. The common framework allocates the card, claims I/O, registers V4L2 controls/device, then calls `rtrack_initialize`, initial frequency/stereo setup, and video registration. Frequency programming calls `lm7000_set_freq` with `rtrack_set_pins`, which maps LM7000 bits to card I/O pins while preserving volume/mute bits. Volume uses timed up/down pulses and a cached `curvol`; mute writes a fixed off pattern.

State and persistence: current volume is runtime memory; hardware volume is analog and changed by timed pulses. Frequency and stereo state are tracked by `radio-isa`.

Dependencies and integration: `radio-isa`, `lm7000`, ISA I/O ports, V4L2 controls. Risks include timed analog volume drift, long initialization delay, and no autodetect probe callback. Test signals include `v4l2-compliance`, tune/mute/volume controls, signal bit reading, and unload muting by `radio-isa`.
