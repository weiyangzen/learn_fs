# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ves1x93.c

Purpose: Implements VLSI VES1893/VES1993 DVB-S QPSK demodulators. It identifies chip revision, loads the matching register initialization table, configures inversion/FEC/symbol rate/LNB voltage, exposes an I2C gate for tuner access, and reports lock/statistics through DVB frontend ops.

Important APIs/types/functions: `struct ves1x93_state` owns I2C/config/frontend state, selected init/write tables, demod type, cached inversion, and last tuned frequency. `ves1x93_writereg()`/`ves1x93_readreg()` are I2C register helpers. `ves1x93_set_inversion()`, `ves1x93_set_fec()`, `ves1x93_get_fec()`, and `ves1x93_set_symbolrate()` encode the main tuning parameters. `ves1x93_i2c_gate_ctrl()` toggles reg0 between tuner-gate open and normal states. `ves1x93_attach()` is exported and `ves1x93_ops` supplies the DVB-S frontend methods.

Control flow: Attach allocates state, reads identity register `0x1e`, selects VES1893 tables for `0xdc`/`0xdd` or VES1993 tables for `0xde`, then returns an initialized frontend. Init iterates the chip-specific write table and writes only marked registers, optionally ORing `invert_pwm` into AGC register `0x05`. Tuning calls the external tuner, closes the I2C gate, writes inversion, FEC, and symbol-rate registers, stores cache values, and for VES1893 pulses the clear bit because VES1993 loses lock if that sequence is used. Status reads retry up to ten times when VES1893 reports inconsistent low sync bits and high lock bits.

State and persistence: No persistent storage exists. State persists only while the frontend is attached: selected chip tables, cached inversion for auto-inversion reporting, and last frequency for AFC-corrected `get_frontend()`. Hardware state is volatile register programming.

Dependencies/integration: Depends on Linux I2C, delays, DVB frontend APIs, and `ves1x93.h`. Integrates with external tuner ops through `set_params`, with board LNB control through `set_voltage`, and with tuner drivers through `i2c_gate_ctrl`.

Risks and test signals: Test identity handling for all supported revisions and unknown IDs, VES1893 versus VES1993 symbol-rate behavior, inversion auto/on/off including the documented I/Q swap, FEC rejection outside 1/2..8/9, voltage writes for 13/18/off, I2C gate open/close, status retry loop, AFC frequency correction, and uncorrected-block reset. `ves1x93_readreg()` returns the negative I2C transfer count in an unsigned byte path on read failure, which can look like a valid register value to callers.
