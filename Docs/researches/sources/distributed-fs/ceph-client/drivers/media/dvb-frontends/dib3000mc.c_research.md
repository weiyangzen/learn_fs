# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib3000mc.c

## Purpose
Implements the DiBcom DiB3000MC/P DVB-T COFDM demodulator frontend. It supports identification of 3000MC and 3000P devices, board-configured AGC/PWM setup, bandwidth/timing programming, output-mode control, autosearch, final tune, status/statistic reads, PID parsing/filtering helpers, tuner I2C master access, and multi-demodulator I2C address enumeration.

## Important APIs, Types, And Functions
`struct dib3000mc_state` embeds a `dvb_frontend`, points to `struct dib3000mc_config`, stores 8-bit wire I2C address, adapter, `dibx000_i2c_master`, timing frequency cache, current bandwidth, device ID, and SFN workaround flag. Register access is through `dib3000mc_read_word()` and `dib3000mc_write_word()`, which allocate a 4-byte buffer per transfer.

Public/exported APIs are `dib3000mc_attach()`, `dib3000mc_i2c_enumeration()`, `dib3000mc_get_tuner_i2c_master()`, `dib3000mc_pid_control()`, `dib3000mc_pid_parse()`, and `dib3000mc_set_config()`. Frontend ops cover init, sleep, set/get frontend, tune settings, status, BER, signal strength, SNR placeholder, uncorrected blocks, and release.

## Control Flow
Attach allocates state, stores config/I2C/address, copies ops, verifies vendor ID `0x01b3` and device ID `0x3001` or `0x3002`, initializes a `dibx000_i2c_master` for tuner access, writes a clock config register, and returns the embedded frontend. Init performs a demod restart, power/mobility setup, clock setup, phase-noise and AGC programming from `cfg->agc`, timing/lock/search/default bandwidth setup, spurious/FEC/diversity/impulse-noise/output setup, and closes the tuner I2C gate.

Set-frontend disables output, records bandwidth, applies bandwidth tables, enables the optional SFN workaround, lets the tuner tune, performs autosearch when transmission/guard/modulation/FEC are auto, reads back TPS on success, and then calls `dib3000mc_tune()`. The final tune path programs channel config, optional SFN registers, adaptive config based on modulation, 2K/8K timing coefficients, timing-offset correction if indicated by lock register bit `0x80`, and then enables MPEG2 FIFO output. Status maps bits from register 509 to DVB lock flags.

## State And Persistence
Driver state persists the current bandwidth, cached timing frequency `timf`, selected config pointer, device ID, and SFN workaround state. `dib3000mc_set_config()` can replace the config pointer after attach, so config lifetime and synchronization are caller responsibilities. Hardware state persists output mode, PID parser/filter registers, I2C gate/master behavior, AGC/PWM settings, timing, and demodulator lock state.

## Dependencies And Integration Points
The file depends on Linux I2C/slab/kernel APIs, DVB frontend APIs, `dib3000mc.h`, and `dibx000_common.h` through the header. Board integration is via `struct dib3000mc_config`, especially AGC config, phase/impulse noise modes, PWM3 settings, max-time/ADC levels, AGC command bits, mobile mode, and MPEG2 packet-size preference. It integrates with tuners through `dib3000mc_get_tuner_i2c_master()` and with bridges through PID parser/control exports.

## Risks
I2C read/write allocate memory on every transfer, so memory pressure can turn reads into zero and writes into `-ENOMEM`; many callers do not propagate read failures distinctly. The config pointer is not copied and may be replaced at runtime, so dangling or concurrently changed configs can corrupt register programming. Several channel-config expressions appear hardcoded or suspicious, such as `switch (HIERARCHY_1)` and `(ch->hierarchy == 0 || 1 == 1)`, meaning hierarchy handling is effectively fixed. Autosearch returns success/failure by register polling but a not-found path returns 0 rather than an error. The module parameter `buggy_sfn_workaround` affects global behavior for all instances.

## Test Signals
Build with `CONFIG_DVB_DIB3000MC`. Runtime tests should cover attach to both MC and P IDs, I2C enumeration of multi-demod boards, init/sleep, tuner I2C master gated and ungated access, fixed and auto DVB-T tuning, 5/6/7/8 MHz bandwidths, SFN workaround on/off, output modes, PID parser/filter writes, and status/BER/uncorrected/strength reads after lock. Memory-failure or fault-injection tests around I2C buffer allocation would expose weak error propagation.
