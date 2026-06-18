<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt200x.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt200x.h

## Purpose
`nxt200x.h` is the public attach/configuration header for NXT2002/NXT2004 VSB/QAM demodulators.

## Important APIs, Types, And Functions
`nxt_chip_type` enumerates `NXTUNDEFINED`, `NXT2002`, and `NXT2004`. `struct nxt200x_config` supplies the demodulator I2C address and optional `set_ts_params()` callback used to switch board DMA/TS parameters for punctured versus non-punctured clocks. `nxt200x_attach()` is exported when `CONFIG_DVB_NXT200X` is reachable, with a warning stub otherwise.

## Control Flow
The header contains only declarations and the disabled-driver stub. Runtime attach and detection are implemented in `nxt200x.c`.

## State And Persistence
It defines no persistent state. The config object is board-owned and referenced by the driver.

## Dependencies And Integration Points
It includes DVB frontend and firmware declarations. Board drivers integrate by creating a config, calling `nxt200x_attach()`, and wiring tuner operations into the returned frontend.

## Risks
An incorrect demod I2C address prevents chip detection. Missing `set_ts_params()` is tolerated but may break TS output on boards that require clock-mode changes for QAM/VSB.

## Test Signals
Build coverage for enabled/disabled Kconfig, attach with valid and invalid I2C addresses, and VSB/QAM board callback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt200x.h -->
