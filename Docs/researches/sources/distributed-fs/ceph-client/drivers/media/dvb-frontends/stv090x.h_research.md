# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv090x.h

## Purpose
`stv090x.h` is the public board-driver contract for the STV0900/STV0903 DVB frontend driver. It defines the device, demodulator, clock, transport-stream, I2C repeater, ADC-range, and configuration types consumed by `stv090x.c`, plus the exported `stv090x_attach()` entry point when the driver is enabled.

## Important APIs And Types
The public enums identify demodulator path (`STV090x_DEMODULATOR_0` and `_1`), chip variant (`STV0903`, `STV0900`), LDPC/demod mode (`STV090x_DUAL`, `STV090x_SINGLE`), TS mode (`SERIAL_PUNCTURED`, `SERIAL_CONTINUOUS`, `PARALLEL_PUNCTURED`, `DVBCI`), input clock mode (`CLK_INT`, `CLK_EXT`), I2C repeater level from 256 down to 2, and ADC range (`2Vpp` or `1Vpp`).

`struct stv090x_config` is the key integration object. Board code supplies chip identity, demod mode/path, crystal frequency and I2C address, TS output modes and optional TS clocks, TEI-update bits, repeater level, tuner baseband gain, ADC ranges, DiSEqC envelope selection, and tuner callback functions. It also includes callback slots populated by the demod driver: `set_gpio` and `get_dvb_frontend`.

`stv090x_attach()` returns a `struct dvb_frontend *` for legacy attach users when `CONFIG_DVB_STV090x` is reachable. The disabled inline fallback logs a Kconfig warning and returns `NULL`.

## Control Flow And Integration
Board or bridge drivers construct `struct stv090x_config`, set tuner callbacks, and either instantiate the I2C driver with platform data or call `stv090x_attach(config, i2c, demod)`. The implementation copies the config pointer into each `struct stv090x_state` and uses it throughout setup, tuning, TS-path configuration, tuner gate operations, and power management. The demod driver mutates the config only to publish `set_gpio` and `get_dvb_frontend` helper callbacks.

## State And Persistence Behavior
This header defines configuration memory owned by the caller; the driver stores the pointer, not a deep copy. Callback pointers and scalar fields therefore must remain valid for the frontend lifetime. The default comments document expected defaults for `xtal`, `address`, `tuner_bbgain`, and ADC ranges, but the header does not enforce them; enforcement is partial and happens in the implementation.

## Dependencies
The file refers to `struct dvb_frontend`, `struct i2c_adapter`, `struct i2c_client`, `u8`, `u32`, `bool`, and `enum tuner_mode`, which are supplied by the surrounding Linux media/kernel include context and by the implementation’s tuner header. It is included by board drivers and by `stv090x.c`.

## Risks And Edge Cases
Because the config is pointer-retained, stack-allocated or short-lived config objects are unsafe. The `address` and `xtal` comments state defaults, but attach/probe expects useful values for reliable I2C and clock programming. Optional tuner callbacks are checked in the implementation, but a missing callback can remove important hardware setup or status validation. The public enum values are programmed directly into register fields, so board code should use only the declared constants.

## Test Signals
Compile coverage should verify both enabled and disabled Kconfig branches. Runtime validation should confirm a board config can attach through both legacy attach and I2C probe paths, callback pointers are invoked in the expected order, TS mode and TS clock fields produce valid transport output, ADC range settings map to the expected tuner input mode, and `get_dvb_frontend`/`set_gpio` are populated after successful setup.
