# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ascot2e.c

## Purpose
`ascot2e.c` implements a Sony ASCOT2E terrestrial/cable tuner driver that attaches tuner operations to an existing DVB frontend.

## Important APIs, Types, And Functions
`struct ascot2e_priv` stores current frequency, 7-bit I2C address, adapter, power state, and optional active-tuner callback. Internal enums describe power state and TV system variants for DVB-T, DVB-T2, DVB-C Annex A, and DVB-C2-like table entries. Core functions are I2C helpers, power-save transitions, `ascot2e_get_tv_system()`, `ascot2e_set_params()`, `ascot2e_get_frequency()`, and exported `ascot2e_attach()`.

## Control Flow
Attach allocates private state, opens the demod I2C gate if available, writes boot/PLL/RSSI/default power-save registers, closes the gate, installs `dvb_tuner_ops`, and stores `fe->tuner_priv`. Set-params maps delivery system and bandwidth to a table entry, optionally notifies parent tuner selection, leaves power save, rounds frequency to 25 kHz, programs IF/AGC/filter/LNA settings, writes frequency and bandwidth registers, waits for VCO calibration, returns CPU/logic to sleep, records frequency, and returns.

## State And Persistence
The driver tracks only current tuned frequency and sleep/active state in memory. Hardware registers hold the actual tuner configuration until power loss or reprogramming.

## Dependencies And Integration Points
It depends on DVB frontend core, Linux I2C, and the demod frontend's optional `i2c_gate_ctrl`. `ascot2e_attach()` is exported and guarded by a Kconfig stub in the header.

## Risks
`config->xtal_freq_mhz` is documented but attach writes a fixed 16 MHz value, so non-16 MHz boards may not work. Many I2C writes ignore return values in attach and tune sequences, which can hide partial programming. Unsupported delivery systems return `-EINVAL`. The I2C address is shifted right by one, assuming callers pass an 8-bit address.

## Test Signals
Hardware tune tests should cover DVB-T/T2/C bandwidths and sleep/resume transitions. Fault injection should validate I2C failure propagation in helpers and expose ignored errors. Confirm parent active-tuner callback sequencing when multiple tuners share resources.
