
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad3552r-common.c

## Purpose
`ad3552r-common.c` provides shared model metadata and helper routines for the AD3541R/AD3542R/AD3551R/AD3552R DAC family. It is used by both the standard SPI driver and the high-speed IIO backend driver.

## Important APIs, types, and functions
- Exports `ad3541r_model_data`, `ad3542r_model_data`, `ad3551r_model_data`, and `ad3552r_model_data` in namespace `IIO_AD3552R`.
- `ad3552r_calc_custom_gain()` packs gain scaling and offset polarity/bit fields into the channel gain register value.
- `ad3552r_calc_gain_and_offset()` computes IIO scale and offset for standard or custom output ranges.
- `ad3552r_get_ref_voltage()` selects internal floating, internal 2.5 V output, or external vref input based on regulator/property state.
- `ad3552r_get_drive_strength()` validates `adi,sdo-drive-strength`.
- `ad3552r_get_custom_gain()` parses `custom-output-range-config` child node fields.
- `ad3552r_get_output_range()` parses and validates `adi,output-range-microvolt`.

## Control flow
Consumer drivers select model data by device match, then call common property helpers during setup. Output range parsing returns `-ENOENT` when optional range is missing, allowing consumers to choose custom-gain fallback where appropriate. Scale/offset computation derives IIO values from either model range tables or custom gain formulas.

## State and persistence behavior
The file itself is stateless except for constant model/range tables. It fills caller-owned `struct ad3552r_ch_data` and output parameters. It can enable/read a `vref` regulator through devm helper, so regulator lifetime is tied to the device.

## Dependencies and integration points
Depends on bitfield helpers, device property/fwnode APIs, regulator consumer APIs, and `ad3552r.h`. Exports are consumed by `ad3552r.c` and `ad3552r-hs.c`, both importing namespace `IIO_AD3552R`.

## Risks and edge cases
- `ad3552r_calc_custom_gain()` uses `FIELD_PREP(AD3552R_MASK_CH_OFFSET_BIT_8, abs(goffs))`; because the mask is a single bit, only the low packed bit selected by the mask is represented here while the low offset bits must be written separately by consumers.
- `ad3552r_get_custom_gain()` reads `adi,gain-offset` as `u32` then assigns to `s16`; negative firmware values require correct fwnode interpretation and range validation is absent.
- `ad3552r_get_drive_strength()` returns the raw property-read error for missing property, leaving callers to treat missing as optional.
- External vref tolerance is hard-coded to 2.5 V +/- 100 mV.

## Test signals
Property parsing tests should cover all legal output ranges for AD3542 and AD3552 tables, missing optional range, missing custom-gain child, invalid drive strength, external vref out of tolerance, and scale/offset calculations for bipolar/unipolar/custom ranges.
