# sources/distributed-fs/ceph-client/drivers/media/radio/radio-rtrack2.c

Purpose: implements the AIMSlab RadioTrack II ISA card using the shared `radio-isa` framework. It supplies board-specific port programming for frequency, mute, and signal detection.

Important APIs and functions: module entry/exit are `rtrack2_init` and `rtrack2_exit`, registering an `isa_driver`. Board hooks are `rtrack2_alloc`, `rtrack2_s_frequency`, `rtrack2_g_signal`, and `rtrack2_s_mute_volume`, collected in `radio_isa_ops`.

Control flow: the shared framework probes configured or known ports `0x20f` and `0x30f`, allocates a `radio_isa_card`, and exposes standard V4L2 radio operations. Setting frequency converts V4L2 units to the card's serial programming value, sends a reset/preamble sequence, clocks ten zero bits, then clocks 15 frequency bits using `zero` and `one` port waveforms. Mute writes the mute value to the base I/O port, and signal reads bit 1 where set means no signal.

State and persistence: per-card state is the generic `radio_isa_card` allocated by the framework. Frequency, mute, and stereo bookkeeping are primarily framework state; hardware registers are programmed through ISA I/O and do not persist across unload.

Dependencies and integration points: depends on `radio-isa.h`, ISA driver registration, request-region ownership via the framework, low-level `outb_p/inb`, and V4L2 ioctls implemented by the shared radio-ISA layer.

Risks: hardware timing is implicit in `outb_p`; faster or virtualized systems may not match original bus timing. Only two I/O addresses are supported. Signal polarity is board-specific. There is no explicit hardware detection beyond what the framework and port list provide.

Test signals: `v4l2-compliance` on real RadioTrack II hardware, probe at both possible ports, frequency-programming validation across the FM band, mute state retention through frequency changes, and signal bit behavior with/without antenna input.
