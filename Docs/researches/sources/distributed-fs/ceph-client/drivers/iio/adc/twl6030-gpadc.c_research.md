# sources/distributed-fs/ceph-client/drivers/iio/adc/twl6030-gpadc.c

Purpose: platform IIO driver for TWL6030/TWL6032 GPADC blocks, supporting calibrated raw/processed reads, different channel/register models per chip, conversion-completion IRQs, input routing setup, and suspend/resume module toggling.

Important APIs/types/functions: `struct twl6030_gpadc_platform_data` provides channel tables, ideal calibration data, start-conversion and channel-register functions, and calibration routine. `struct twl6030_gpadc_data` stores mutex, completion, calibration table, and platform data. `twl6030_calibration()` and `twl6032_calibration()` decode trim registers. `twl6030_gpadc_read_raw()` starts conversion, waits for completion, and returns raw or processed values.

Control flow: probe selects TWL6030 or TWL6032 match data, allocates calibration table, initializes completion/mutex, reads trim registers to calculate per-channel gain/gain-error/offset-error, requests threaded IRQ, unmasks GPADC EOC interrupts, enables the GPADC module, wires VBUS/ID/VBAT/backup/VAC measurement inputs through TWL modules, and registers IIO. Reads serialize on `lock`, start conversion using chip-specific register writes, wait up to 5 seconds for IRQ completion, then read the result register and apply calibration/voltage conversion for processed channels.

State and persistence: calibration coefficients are computed at probe from PMIC trim registers and stored in memory. Hardware module enable/routing persists until suspend/remove or PMIC reset. Completion state is reused for conversions; no disk persistence.

Dependencies and integration: TWL MFD I2C helpers, platform IRQ, TWL interrupt mask helpers, IIO direct mode, OF match data, PM sleep ops.

Risks: calibration lookup assumes ideal table entries align with exposed channels; some channels intentionally lack calibration and return raw code; timeout is long and interrupt-dependent; remove disables IRQ and unregisters but module routing is mostly left to PMIC state. Test signals include trim decoding for both chip families, processed voltage math, raw uncalibrated channels, IRQ timeout, suspend/resume GPADC toggle, and USB/input routing writes.
