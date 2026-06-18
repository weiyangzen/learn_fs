# sources/distributed-fs/ceph-client/drivers/media/radio/radio-trust.c

Purpose: implements support for the Trust FM Radio ISA card through the shared `radio-isa` framework, including bit-banged I2C programming of the tuner and audio processor.

Important APIs and functions: module lifecycle is `trust_init`/`trust_exit`. Board hooks include `trust_alloc`, `trust_initialize`, `trust_s_mute_volume`, `trust_s_frequency`, `trust_s_stereo`, `trust_g_signal`, and `trust_s_ctrl`. `write_i2c` implements a simple variadic bit-banged I2C write over the ISA port.

Control flow: the framework probes configured or known ports `0x350` and `0x358`, allocates `struct trust`, and registers a V4L2 radio node. Initialization sets output latch defaults, configures TDA7318 speaker attenuation/input gain, and adds bass/treble controls. Frequency setting converts V4L2 frequency to 10 kHz plus 10.7 MHz IF and writes a five-byte TSA6060T sequence. Mute/volume changes update a latch bit and write TDA7318 volume. Stereo changes update another latch bit. Signal reads the port 100 times and reports no signal if bit 0 was ever seen set.

State and persistence: `struct trust` embeds `radio_isa_card` and keeps the current output latch byte `ioval`. The shared framework tracks frequency, mute, stereo, and controls. Hardware state is volatile.

Dependencies and integration points: depends on `radio-isa.h`, direct port I/O, V4L2 controls supplied by the framework, and the TDA7318/TSA6060T serial protocols implemented by bit-banged writes.

Risks: `write_i2c` does not sample or enforce ACKs; it just clocks an acknowledge bit. Signal detection ORs repeated reads, so transient noise can force no-signal. Bass/treble table mapping is non-linear and hardware-specific. Variadic I2C writes are easy to misuse if byte count and arguments diverge.

Test signals: probe both jumper-selected ports, initialization programming on a logic analyzer, volume/mute/stereo/bass/treble controls, frequency conversion against known stations, signal reporting stability, and `v4l2-compliance`.
