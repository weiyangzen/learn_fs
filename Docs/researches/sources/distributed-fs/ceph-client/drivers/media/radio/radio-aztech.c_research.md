# Research: sources/distributed-fs/ceph-client/drivers/media/radio/radio-aztech.c

Purpose: ISA V4L2 radio driver for Aztech/Packard Bell radio cards, implemented through `radio-isa` plus the LM7000 tuner helper.

Important details: `struct aztech` extends the generic card with `curvol`. Callbacks implement allocation, mute/volume, frequency setting, stereo/mono status, and signal status. Ports are module-configurable, with valid values `0x350` and `0x358`; region size is 8.

Control flow: the `radio-isa` framework handles probe/registration. Frequency setting bit-bangs the LM7000 with `aztech_set_pins`, mixing current two-bit volume with tuner CE/CLK/DATA bits. Mute maps to volume zero; volume is encoded into bits 0 and 2. Status reads `AZTECH_BIT_MONO` and `AZTECH_BIT_NOT_TUNED`.

State and persistence: runtime `curvol` is mirrored to I/O bits and reused while clocking tuner data. The framework stores frequency and stereo choice. No persistent state.

Dependencies and integration: ISA I/O, `radio-isa`, V4L2 tuner API, `lm7000`. Risks are minimal volume granularity, no hardware probe callback, and read-bit polarity assumptions. Test signals are valid-port handling, tuner programming, mute/volume controls, mono/stereo reporting, and signal status under tuned/untuned stations.
