# sources/distributed-fs/ceph-client/include/sound/opl4.h

Source read summary: 19 lines, OPL4 wavetable add-on constructor.

Purpose: declares creation of a Yamaha OPL4 component paired with an existing OPL3/FM device.

Important APIs, types, and functions: `struct snd_opl4` is forward-declared and `snd_opl4_create()` accepts a card, left/right ports, optional FM OPL3 pointer, hardware value, integrated flag, and output pointer.

Control flow: a legacy card driver creates OPL3 first when present, then calls `snd_opl4_create()` to register wavetable functionality on the adjacent ports.

State and persistence behavior: no state is defined here; OPL4 device state is owned by the implementation and hardware registers.

Dependencies and integration points: includes `opl3.h` and integrates OPL4 wavetable hardware with ALSA card setup.

Risks and edge cases: port pairing and integrated flags must match hardware; incorrect OPL3 association can break FM/wavetable coexistence.

Test signals: OPL4 creation with/without OPL3 pointer, port resource conflicts, integrated-card variants, and playback/sequencer registration.
