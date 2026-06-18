# sources/distributed-fs/ceph-client/drivers/clk/clk-si570.c

Purpose: I2C CCF driver for Silicon Labs Si570/Si571 programmable XO/VCXO and Si598/Si599 devices. It computes factory crystal frequency from DT-supplied factory output and programs RFREQ/N1/HSDIV for requested output rates.

Important APIs/types/functions: `struct clk_si570_info` records max frequency and whether temperature-stability variants need a divider-register offset. `struct clk_si570` holds regmap, divider offset, factory crystal frequency, cached divider values, current frequency, and I2C client. Core helpers include `si570_get_divs()`, `si570_get_defaults()`, `si570_update_rfreq()`, `si570_calc_divs()`, `si570_set_frequency()`, and `si570_set_frequency_small()`. CCF ops are `si570_recalc_rate`, `si570_determine_rate`, and `si570_set_rate`.

Control flow: probe allocates state, selects device info from match data, optionally reads `temperature-stability` and applies the 7 ppm register offset, names the clock, requires `factory-fout`, reads optional `silabs,skip-recall`, initializes regmap, recalls NVM unless skipped, computes factory `fxtal`, registers the clock/provider, optionally applies DT `clock-frequency`, then logs the current frequency. Runtime set_rate rejects out-of-range requests; changes below 3500 ppm update RFREQ under freeze-M, while larger changes recalculate dividers, freeze DCO, update HSDIV/N1/RFREQ, unfreeze, assert NEWFREQ, and wait.

State and persistence: cached `fxtal`, `n1`, `hs_div`, `rfreq`, and `frequency` mirror hardware after defaults and set_rate. Hardware state persists in divider/RFREQ/control registers; regmap marks control volatile and limits writable ranges. Optional NVM recall changes RAM register contents at probe.

Dependencies and integration: depends on I2C, regmap, CCF, DT properties `factory-fout`, optional `temperature-stability`, optional `silabs,skip-recall`, and optional `clock-frequency`. Uses fixed compatible data for Si570/571 and Si598/599 max-frequency differences.

Risks: `si570_determine_rate()` computes candidate dividers but never writes `req->rate` to the rounded achievable value on success, so callers may not see rounding information. Missing required DT properties fail probe. Recalc returns cached frequency after read failure, potentially masking hardware errors. Probe may modify hardware by recalling NVM and applying `clock-frequency`. Large rate changes are timing-sensitive and assume fixed wait ranges.

Test signals: cover factory-fout parsing, 7 ppm offset, skip-recall behavior, small versus large frequency changes, divider search boundaries, max-frequency variants, recalc from raw registers, and initial `clock-frequency` programming. No direct tests are present.
