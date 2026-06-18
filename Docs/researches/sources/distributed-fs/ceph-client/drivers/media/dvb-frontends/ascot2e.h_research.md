# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ascot2e.h

## Purpose
This public header declares configuration and attach API for the Sony ASCOT2E tuner driver.

## Important APIs And Types
`struct ascot2e_config` includes `i2c_address`, `xtal_freq_mhz`, optional callback private data, and `set_tuner_callback`. `ascot2e_attach()` attaches tuner ops to a supplied DVB frontend when `CONFIG_DVB_ASCOT2E` is reachable; otherwise an inline stub logs that the driver is disabled and returns NULL.

## Control Flow And Integration
Demod/bridge drivers call `ascot2e_attach(fe, config, i2c)` after creating the demod frontend. The tuner driver then populates `fe->ops.tuner_ops` and uses optional demod `i2c_gate_ctrl` during attach.

## State And Persistence
The header holds configuration only. Private runtime state is allocated by `ascot2e.c`.

## Dependencies
It includes DVB frontend and I2C headers. Kconfig requires DVB core and I2C.

## Risks
The implementation currently uses a fixed 16 MHz setup despite the `xtal_freq_mhz` field, so the public contract and implementation may diverge. Callers must understand whether `i2c_address` is 8-bit or 7-bit formatted because implementation shifts it.

## Test Signals
Compile both enabled and disabled Kconfig cases. Runtime attach should return the original frontend on success, set tuner ops, and log the attached address.
