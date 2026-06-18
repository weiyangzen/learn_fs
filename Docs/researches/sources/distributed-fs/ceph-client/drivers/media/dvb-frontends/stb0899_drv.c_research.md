<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_drv.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_drv.c

## Purpose
`stb0899_drv.c` is the main Linux DVB frontend driver for the STB0899 multistandard satellite demodulator. It owns attach/probe, low-level register I/O, init, custom search dispatch, status/metric callbacks, DiSEqC and LNB controls, I2C repeater control, postprocess GPIO events, and module metadata.

## Important APIs, Types, And Functions
The exported attach point is `stb0899_attach()`, which allocates `struct stb0899_state`, stores config/I2C, wakes clocks, reads device/core IDs, and returns an embedded frontend. Low-level I/O includes `stb0899_read_reg()`, `_stb0899_read_s2reg()`, `stb0899_write_s2reg()`, `stb0899_read_regs()`, `stb0899_write_regs()`, and `stb0899_write_reg()`, including the documented 0xf2xx/0xf6xx follow-up read workaround. `stb0899_init()` writes all configured init tables, calculates clocks/rolloff, and initializes DiSEqC. `stb0899_search()` reads DVB properties, selects delivery, configures tuner bandwidth/gain and master clock, then calls `stb0899_dvbs_algo()` or `stb0899_dvbs2_algo()`. Status and metric callbacks translate hardware status into DVB frontend flags, C/N, RF strength, and BER/PER. DiSEqC routines handle FIFO writes, RX replies, mini-bursts, and 22 kHz tone.

## Control Flow
Attach wakes the device, enables clocks, checks IDs, and leaves full initialization to DVB core `.init`. Init iterates config tables for device, S2 demod, S1 demod, S2 FEC, and test registers, then calculates master clock and AGC defaults. Search validates symbol rate, switches delivery-mode clocks/FEC/stream settings, opens the I2C repeater for tuner callbacks, sets tuner bandwidth, adjusts AGC and LDPC iteration settings, runs the selected acquisition algorithm, and sets `internal->lock`. Read callbacks use `state->delsys` and `internal->lock` to choose S1 or S2 status paths.

## State And Persistence
`struct stb0899_state` persists frontend config, current delivery system, cached requested params, `rx_freq`, a mutex field, and extensive `internal` demod state. Hardware register state includes init table values, clock gates, stream merger reset state, DiSEqC config, GPIO postproc state, and acquisition settings. The driver keeps board config by pointer, so config and callback lifetimes must outlive the frontend.

## Dependencies And Integration Points
The driver depends on DVB frontend core, Linux I2C, `stb0899_priv.h`, `stb0899_drv.h`, and `stb0899_reg.h`. It integrates board-specific tuner operations through function pointers in `struct stb0899_config` and exposes an I2C repeater for tuner drivers such as STB6000. Postproc GPIO entries allow board-specific power/lock signaling.

## Risks And Test Signals
Risks include S2 indirect register protocol errors, master-clock misconfiguration, stale `internal->srate` when choosing RF gain before assignment, inconsistent symbol-rate limits (`info` minimum is 5 Msps while search accepts 1 Msps), commented-out wakeup op despite attach using wake, and division by hardware-derived values. GPIO voltage control is board-specific and can be unsafe on mismatched designs. Test signals are attach ID/core logs, init table writes, locks for DVB-S/DSS/DVB-S2, correct I2C repeater toggling around tuner access, DiSEqC TX/RX and burst behavior, voltage/tone verification, plausible C/N/RF strength metrics, and regression tests across low and high symbol rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb0899_drv.c -->
