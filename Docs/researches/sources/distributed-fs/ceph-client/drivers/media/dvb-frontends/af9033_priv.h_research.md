# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/af9033_priv.h

## Purpose
This private header is the AF9033/AF9035/IT9135 device-data repository. It provides register table structs, clock/ADC lookup data, bandwidth coefficients, OFSM init tables, tuner init tables, and power-reference data for signal strength.

## Important APIs And Types
`struct reg_val`, `struct reg_val_mask`, `struct coeff`, `struct clock_adc`, and `struct val_snr` model register writes and lookup data. `clock_adc_lut` maps crystal clocks to ADC clocks. `coeff_lut` stores 36-byte coefficient sets. Init tables include `ofsm_init`, `ofsm_init_it9135_v1`, and `ofsm_init_it9135_v2`. Tuner tables include TUA9001, FC0011, FC0012, MXL5007T, TDA18218, FC2580, and IT9135 variants 38/51/52/60/61/62. `power_reference` gives NorDig reference levels indexed by modulation and code rate.

## Control Flow And Integration
`af9033.c` selects an OFSM table by tuner family, then selects a tuner init table by exact tuner ID. Tuning uses `clock_adc_lut` and `coeff_lut`. Signal-strength logic for IT9135 uses `power_reference` together with TPS registers.

## State And Persistence
All content is static const module data. Hardware register state is created by replaying these tables during init and tuning.

## Dependencies
The file depends on DVB frontend definitions, the public AF9033 header, math64, regmap, kernel helpers, and integer log support.

## Risks
Most hardware behavior is encoded as opaque register constants. Table mistakes can cause silent lock failures, wrong TS output, poor sensitivity, or bad metrics. The coefficient table in this tree contains entries only for 12 MHz in the visible data used by current probe constraints, so adding clocks requires synchronized table and probe work.

## Test Signals
Exercise every supported tuner ID through init. Validate coefficient selection for every accepted bandwidth and clock. Compare strength/CNR values against known-good hardware measurements where possible.
