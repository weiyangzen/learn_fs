# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bsbe1.h

Purpose: Provides board-support data and tuner helper routines for the ALPS BSBE1 DVB-S frontend using an STV0299 demodulator and simple I2C PLL tuner.

Important APIs/types/functions: `alps_bsbe1_inittab` is the STV0299 initialization register table. `alps_bsbe1_set_symbol_rate()` selects ACLK/BCLK values from symbol-rate bands and writes ratio registers `0x1f` to `0x21`. `alps_bsbe1_tuner_set_params()` programs a four-byte tuner message at address `0x61` for 950 to 2150 MHz. `alps_bsbe1_config` fills `struct stv0299_config` with demod address `0x68`, `mclk = 88 MHz`, inversion, delay, and symbol-rate callback.

Control flow: Board drivers include this header, attach STV0299 with `alps_bsbe1_config`, and generally install `alps_bsbe1_tuner_set_params()` as the tuner callback. Tuning validates frequency, opens the frontend I2C gate if present, sends the PLL divider bytes, and leaves gate closure to surrounding frontend conventions.

State and persistence: No owned runtime state; the frequency divider bytes and STV0299 registers are volatile hardware state. `fe->tuner_priv` is expected to point to the I2C adapter.

Dependencies/integration: Requires STV0299 helper declarations and DVB/I2C types supplied by including board code. Used by TTPci budget/budget-ci board setup.

Risks and test signals: Test symbol-rate boundary bands, ratio byte programming, frequency limit rejection, I2C gate handling, and tuner I2C failure propagation. The tuner helper opens the gate but does not explicitly close it, so integration behavior depends on caller/demod conventions.
