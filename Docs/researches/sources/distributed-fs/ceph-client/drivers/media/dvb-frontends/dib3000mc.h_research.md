# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib3000mc.h

## Purpose
Declares the board configuration and public API for the DiBcom DiB3000MC/P demodulator driver.

## Important APIs, Types, And Functions
`struct dib3000mc_config` provides AGC configuration, phase and impulse noise modes, PWM3 inversion/use/value, max timing and low-noise ADC levels, AGC command bits, mobile-mode flag, and MPEG2 188-byte output preference. Default I2C addresses are `DEFAULT_DIB3000MC_I2C_ADDRESS` 16 and `DEFAULT_DIB3000P_I2C_ADDRESS` 24.

When `CONFIG_DVB_DIB3000MC` is reachable, the header declares `dib3000mc_attach()`, `dib3000mc_i2c_enumeration()`, and `dib3000mc_get_tuner_i2c_master()`. Disabled stubs warn and return `NULL` or `-ENODEV`. Regardless of Kconfig block, it declares exported helpers `dib3000mc_pid_control()`, `dib3000mc_pid_parse()`, and `dib3000mc_set_config()`.

## Control Flow
Bridge drivers call enumeration for multi-demod address assignment when needed, call attach for each demodulator, then use the returned frontend and optional tuner I2C master. PID helper calls control demodulator-side TS filtering.

## State And Persistence
The header owns no state. The implementation stores a pointer to the config rather than copying it, so the config and nested `agc` object must persist for the frontend lifetime unless intentionally replaced through `dib3000mc_set_config()`.

## Dependencies And Integration Points
It includes `dibx000_common.h` for AGC config and I2C master interfaces. Integration is with DiB bridge drivers, tuner drivers behind the demodulator I2C gate, and DVB frontend registration.

## Risks
The PID helper declarations remain visible even when the main driver is disabled; callers need proper Kconfig/link dependencies. Bitfield config values are compact but not self-validating, so invalid board data can program nonsensical AGC/PWM registers. The config pointer lifetime contract is implicit.

## Test Signals
Compile users with the demodulator enabled and disabled. Runtime validation should confirm default address handling, enumeration address reassignment, stable config storage, and availability of the tuner I2C master after attach.
