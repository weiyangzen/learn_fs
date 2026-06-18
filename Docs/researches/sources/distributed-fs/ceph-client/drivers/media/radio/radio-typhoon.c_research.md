# sources/distributed-fs/ceph-client/drivers/media/radio/radio-typhoon.c

Purpose: supports Typhoon/EcoRadio ISA cards through the shared `radio-isa` framework, implementing the card's non-linear frequency programming and coarse speaker-volume mute behavior.

Important APIs and functions: module lifecycle is `typhoon_init` and `typhoon_exit`. Board hooks are `typhoon_alloc`, `typhoon_s_frequency`, and `typhoon_s_mute_volume` in `typhoon_ops`.

Control flow: initialization validates the `mutefreq` module parameter in kHz, then registers an ISA driver for ports `0x316` and `0x336`. Frequency setting approximates the hardware transfer curve with a third-order polynomial and writes the resulting bits to offsets `io + 4`, `io + 6`, and `io + 8`. Mute/volume maps a 16-bit framework volume to two hardware bits. When volume reaches zero, the driver marks the card muted and tunes to a configured noise frequency; when volume becomes nonzero, it retunes to the cached station.

State and persistence: `struct typhoon` embeds the generic ISA card and a `muted` flag. The framework stores cached frequency and volume. Hardware state is transient and controlled only through port writes.

Dependencies and integration points: depends on `radio-isa.h`, ISA bus registration, direct port I/O, and V4L2 behavior from the framework. It advertises stereo and maximum volume 3, though hardware notes say stereo behavior is uncertain.

Risks: muting by detuning can produce noise rather than silence and can surprise users watching frequency-sensitive hardware. The polynomial tuning approximation is empirical. The line output has no mute/volume support despite V4L2 controls. The I/O region size is 8 while writes use `io + 8`, which is at the first byte beyond an 8-byte region if size semantics are exclusive.

Test signals: module parameter validation, requested-region coverage for all offsets, frequency tuning accuracy across band, mute/unmute retuning to `mutefreq` and back, volume step mapping, and `v4l2-compliance` on hardware.
