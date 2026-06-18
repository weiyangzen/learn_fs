# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt3306a.h

## Purpose
`lgdt3306a.h` is the public board-driver interface for the LGDT3306A ATSC/QAM demodulator. It describes transport-stream output options, IF frequencies, I2C repeater policy, crystal selection, and the attach API.

## Important APIs, Types, and Functions
The header defines `enum lgdt3306a_mpeg_mode`, `enum lgdt3306a_tp_clock_edge`, and `enum lgdt3306a_tp_valid_polarity`. `struct lgdt3306a_config` carries the demod I2C address, QAM/VSB IF frequencies in kHz, repeater-deny and spectral-inversion flags, MPEG/TS polarity settings, supported `xtalMHz` values, and output pointers for the created frontend and muxed tuner adapter. `lgdt3306a_attach()` is declared when `CONFIG_DVB_LGDT3306A` is reachable and replaced with a warning stub otherwise.

## Control Flow
Legacy callers fill this config and call `lgdt3306a_attach()`. I2C-client users provide the same structure as platform data; probe copies it, fills `i2c_addr` from the client, and writes back `fe` and `i2c_adapter` after mux creation.

## State and Persistence
The header itself owns no state. Its config fields determine volatile demodulator register programming at init and tune time, especially IF/NCO setup, TS bus shape, and I2C repeater behavior.

## Dependencies and Integration Points
It depends on `<linux/i2c.h>` and `<media/dvb_frontend.h>`. Integration is with board/card drivers that instantiate the demodulator and downstream tuner on a possibly muxed I2C bus.

## Risks and Edge Cases
Only 24 MHz and 25 MHz crystals are handled by the implementation. The `spectral_inversion` bit is present but the C file mostly applies modulation-specific defaults, so callers should verify board behavior rather than assuming the field fully controls inversion. The `fe` and `i2c_adapter` output pointers must be valid for I2C-client probe mode.

## Test Signals
Compile coverage should include enabled and disabled Kconfig paths. Runtime tests should validate the caller's IF frequencies, TS polarity/mode choices, repeater-deny setting, and returned frontend/tuner adapter pointers.
