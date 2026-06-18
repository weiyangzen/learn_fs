# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgs8gl5.c

## Purpose
`lgs8gl5.c` implements a simple Legend Silicon LGS-8GL5 DMB-TH/DTMB OFDM demodulator frontend.

## Important APIs, Types, and Functions
`struct lgs8gl5_state` holds the I2C adapter, config, and DVB frontend. Register helpers are `lgs8gl5_write_reg()`, `lgs8gl5_read_reg()`, `lgs8gl5_update_reg()`, and `lgs8gl5_update_alt_reg()` for an alternate I2C address at `demod_address + 2`. Runtime operations include `lgs8gl5_soft_reset()`, `lgs8gl5_start_demod()`, `lgs8gl5_init()`, `lgs8gl5_set_frontend()`, `lgs8gl5_get_frontend()`, status and metric readers, and `lgs8gl5_attach()`.

## Control Flow
Attach allocates state, saves the config and I2C adapter, checks register `REG_RESET`, installs `lgs8gl5_ops`, and returns the frontend. Init writes a fixed demod setup sequence. Set-frontend accepts only 8 MHz bandwidth, calls tuner `set_params()`, closes any I2C gate, and starts demodulation. Start-demod writes the alternate device, resets, programs OFDM registers, waits for carrier for up to roughly 40 ms, then waits for lock for up to roughly 240 ms and copies register `REG_A2` into `REG_7D` before final reset.

## State and Persistence
Software state is only the allocated frontend wrapper. Hardware register state is rebuilt by init and set-frontend. BER and uncorrected-block metrics are stubbed to zero; signal strength and SNR reuse the register strength level.

## Dependencies and Integration Points
The file depends on I2C and DVB frontend core, is exported by `lgs8gl5_attach()`, and advertises `SYS_DTMB`. It expects an external tuner through standard DVB tuner ops.

## Risks and Edge Cases
`lgs8gl5_update_reg()` reads but ignores the old value and blindly writes the new value. The alternate I2C device is marked with a TODO, so board compatibility depends on undocumented hardware. I2C helpers return `-1` for many failures rather than errno-specific values. Only 8 MHz channels are accepted despite the ops advertising bandwidth auto capability.

## Test Signals
Validate attach at the demod I2C address, init sequence completion, tuner programming, rejection of non-8 MHz bandwidth, carrier/lock polling behavior, FE_HAS_SIGNAL/CARRIER/SYNC/LOCK mapping, and strength/SNR scaling from `REG_STRENGTH`.
