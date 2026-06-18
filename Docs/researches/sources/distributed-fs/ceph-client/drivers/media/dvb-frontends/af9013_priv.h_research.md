# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/af9013_priv.h

## Purpose
This private header supplies AF9013 implementation data: firmware name, helper structs, bandwidth coefficients, demodulator initialization registers, and tuner-specific initialization tables.

## Important APIs And Types
`AF9013_FIRMWARE` is `"dvb-fe-af9013.fw"`. `struct af9013_reg_mask_val` represents masked register updates, and `struct af9013_coeff` maps clock/bandwidth pairs to 24-byte CFOE coefficient values. `coeff_lut` covers 28.8, 20.48, 28, and 25 MHz clocks for 6/7/8 MHz bandwidths. `demod_init_tab` is the core demod table. Tuner tables include `tuner_init_tab_env77h11d5`, `mt2060`, `mt2060_2`, `mxl5003d`, `mxl5005`, `qt1010`, `mc44s803`, `unknown`, and `tda18271`.

## Control Flow And Integration
`af9013.c` includes this header directly. During `af9013_init()`, it writes `demod_init_tab` first, then selects one tuner table based on `state->tuner`. During `af9013_set_frontend()`, it selects a `coeff_lut` entry based on `state->clk` and requested bandwidth. Metrics code also depends on `<linux/int_log.h>` included here for CNR calculations.

## State And Persistence
The file is static read-only data compiled into the module. It does not allocate runtime state. Hardware state changes happen when the tables are replayed into registers.

## Dependencies
The header is private to the AF9013 driver and depends on DVB frontend definitions, firmware loader, I2C mux, math64, regmap, and public AF9013 platform definitions.

## Risks
Unsupported clock/bandwidth combinations fail tuning. The register tables are opaque vendor/device data; table corruption can break tuning, AGC, metrics, or TS output without compiler warnings. Some tuner tables enable signal-strength calibration registers; missing calibration makes strength unavailable or inaccurate.

## Test Signals
Table coverage should be tested through targeted init for each supported tuner ID and tune across 6/7/8 MHz for each supported clock. Static review should ensure table names remain aligned with public tuner constants.
