<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt200x.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt200x.c

## Purpose
`nxt200x.c` supports Nextwave NXT2002 and NXT2004 ATSC 8VSB / ITU J.83 Annex B QAM demodulators. It detects the chip variant, loads external firmware, controls the demod microcontroller, configures tuner and demod registers for VSB/QAM, exposes DVB frontend status/statistics, and provides the `nxt200x_attach()` API for board drivers.

## Important APIs, Types, And Functions
`struct nxt200x_state` holds the I2C adapter, board config, frontend, detected chip type, and initialization flag. I2C helpers are `i2c_writebytes()`, `i2c_readbytes()`, `nxt200x_writebytes()`, and `nxt200x_readbytes()`. Multi-register helpers `nxt200x_writereg_multibyte()` and `nxt200x_readreg_multibyte()` abstract variant-specific indirect register access. Firmware helpers are `nxt200x_crc()`, `nxt2002_load_firmware()`, `nxt2004_load_firmware()`, `nxt2002_init()`, and `nxt2004_init()`. Tuning uses `nxt200x_setup_frontend_parameters()`, `nxt200x_writetuner()`, `nxt200x_agc_reset()`, and microcontroller start/stop helpers. Public export is `nxt200x_attach()`.

## Control Flow
Attach allocates state, reads five ID bytes from the demod, selects NXT2002 or NXT2004, verifies known IDs, copies `nxt200x_ops`, and returns the frontend. First `init` requests the matching firmware file, downloads it with the chip-specific loader, then runs a long register initialization sequence. NXT2002 firmware is chunked with CRCs and RAM-base selection; NXT2004 firmware uses a fixed RAM base, whole-image CRC, and 255-byte writes.

Tuning stops the microcontroller, performs NXT2004 digital-mode setup, asks board code to set punctured TS clock for QAM or non-punctured for VSB, obtains tuner register bytes through `tuner_ops.calc_regs`, writes them either directly or through the demod depending on chip type, resets AGC, programs target power, SDM, accumulators, AGC controls, modulation-specific values, and restarts the microcontroller. Status reads register `0x31` and maps bit `0x20` to full DVB lock. BER, signal strength, SNR, and uncorrected block reads come from indirect registers around `0xA6` and `0xE6`.

## State And Persistence
`initialised` prevents repeated firmware loads. `demod_chip` selects firmware, register sequences, multireg protocol, and tuner write path. Hardware retains firmware and register configuration until reset. No persistent kernel metadata is stored.

## Dependencies And Integration Points
The driver depends on Linux firmware loading, I2C, DVB frontend APIs, tuner operations (`calc_regs`), and the board callback `set_ts_params()` from `nxt200x_config`. Firmware files are `dvb-fe-nxt2002.fw` and `dvb-fe-nxt2004.fw`.

## Risks
The code is built around undocumented register sequences with many comments marked unknown. Several helper calls ignore return values, so I2C failures can be masked. `nxt200x_writereg_multibyte()` logs an error but still returns 0 after failed completion polling. Firmware download and CRC handling are variant-specific and can silently misconfigure if the wrong firmware is supplied. Statistics scaling is approximate and old DVBv3 style.

## Test Signals
Hardware attach for NXT2002 and NXT2004 cards, missing/wrong firmware tests, VSB/QAM tuning with tuner `calc_regs`, TS puncture callback verification, lock acquisition and statistic reads, I2C failure injection during firmware and multireg access, and repeated init/tune/sleep cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/nxt200x.c -->
