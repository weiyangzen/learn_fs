# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bsbe1-d01a.h

Purpose: Provides static board-support data for the ALPS BSBE1-D01A satellite frontend variant using an STV0288 demodulator and STB6000 tuner.

Important APIs/types/functions: `stv0288_bsbe1_d01a_inittab` is a register/value initialization table terminated by `0xff, 0xff`. `stv0288_bsbe1_d01a_config` is a `struct stv0288_config` with demod address `0x68`, `min_delay_ms = 100`, and the initialization table pointer.

Control flow: The header has no functions. Board drivers include it and pass `&stv0288_bsbe1_d01a_config` to `stv0288_attach()`, after which the STV0288 driver consumes the inittab during demod initialization.

State and persistence: No mutable runtime state is owned here. The static table encodes volatile hardware reset/programming defaults for the demodulator.

Dependencies/integration: Includes `stb6000.h` and `stv0288.h`. Used by budget-ci style PCI DVB-S board setup for ALPS BSBE1-D01A hardware.

Risks and test signals: Validate that the inittab remains terminated, register pairs stay aligned, and the demod address/delay match the board wiring. Because this is a header with non-const static data, every including translation unit gets its own copy; changes should be limited to board-support contexts.
