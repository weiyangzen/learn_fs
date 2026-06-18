# sources/distributed-fs/ceph-client/drivers/media/radio/radio-zoltrix.c

Purpose: implements the Zoltrix Radio Plus ISA card using the shared `radio-isa` framework, including custom frequency programming, volume/mute, stereo forcing, signal, and rx-subchannel detection.

Important APIs and functions: module lifecycle is `zoltrix_init`/`zoltrix_exit`. Board hooks are `zoltrix_alloc`, `zoltrix_s_mute_volume`, `zoltrix_s_frequency`, `zoltrix_g_rxsubchans`, `zoltrix_g_signal`, and `zoltrix_s_stereo`.

Control flow: the framework probes ports `0x20c` and `0x30c`. Volume/mute writes zero twice and reads a confirmation port when muted, or writes `vol - 1`, sleeps, and reads another port when unmuted. Frequency setting rejects zero, computes an encoded value from V4L2 frequency, merges it and stereo mode into a 64-bit bitmask, sends a reset/prepare sequence, clocks 45 bits through port patterns with microsecond delays, sends a termination sequence, then reapplies cached mute/volume. Stereo changes retune the current frequency to update the programmed bit. Signal and stereo-detect reads compare two samples after volume writes.

State and persistence: `struct zoltrix` embeds the framework card and tracks current volume and mute state for reapplication after frequency changes. Framework state holds frequency and stereo. Hardware state is volatile.

Dependencies and integration points: depends on `radio-isa.h`, direct port I/O, delays, and V4L2 behavior from the shared radio-ISA layer. It is explicitly for the original Zoltrix Radio Plus, not later 108/Windows variants.

Risks: signal/stereo detection is documented as inconsistent and relies on magic values (`0xcf`, `0xdf`, `0xef`). Frequency programming is bitmask-heavy and timing-sensitive. Retuning to apply stereo can fail if cached frequency is invalid. Low volume behavior is known to be non-linear.

Test signals: probe at both ports, full-band tuning compared with real stations, mute/volume reapplication after tuning, stereo force and detection behavior, signal stability, zero-frequency rejection, and `v4l2-compliance`.
