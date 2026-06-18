# sources/distributed-fs/ceph-client/drivers/iio/adc/rohm-bd79124.c

## Purpose
This is the I2C IIO ADC and GPIO-output driver for the ROHM BD79124, an 8-channel 12-bit ADC whose pins can be muxed between ADC inputs and GPO outputs. It supports direct raw voltage reads, scale reporting from the `vdd` regulator, optional threshold events when an IRQ is wired, and GPIO registration for channels not claimed as ADC channels in firmware.

## Important APIs, types, and functions
The central state is `struct bd79124_data`, which owns the regmap, regulator-derived full-scale voltage, cached threshold limits, event monitor/suppression bitmaps, a delayed work item, mutex, and `gpio_chip`. The regmap uses 16-bit register addresses, 8-bit values, Maple cache, volatile result/status registers, and precious event flag registers. IIO entry points are `bd79124_read_raw()`, event config/value callbacks, and the `bd79124_info` table. GPIO integration is via `bd79124gpo_chip`, `bd79124gpo_set()`, `bd79124gpo_set_multiple()`, and `bd79124_init_valid_mask()`.

## Control flow
`bd79124_probe()` allocates the IIO device, initializes regmap and regulators, chooses event-capable or no-IRQ channel templates, allocates firmware-described channel specs with `devm_iio_adc_device_alloc_chaninfo_se()`, initializes hardware defaults, requests a threaded threshold IRQ when available, registers IIO, then registers any unused pins as GPOs. Raw reads lock the device, force auto-conversion mode, replace the auto-channel sequencer with a single channel, wait the documented conversion time, read the recent-result register pair, and restore the previous sequencer mask.

## State and persistence
Hardware state is mostly volatile but mirrored in regmap cache. Threshold values are cached in `alarm_r_limit[]` and `alarm_f_limit[]` because disabling one direction is implemented by writing an extreme threshold rather than a hardware enable bit. `alarm_monitored[]` tracks enabled event directions and `alarm_suppressed[]` tracks one-second rate-limit suppression. GPIO valid pins are captured once from the ADC channel allocation.

## Dependencies and integration points
The driver depends on I2C, regmap, regulator supplies `vdd` and `iovdd`, generic IIO ADC channel firmware helpers, IIO events, optional IRQ, and gpiolib. Firmware channel children decide which pins are ADCs; all remaining pins become GPIO outputs. IIO events are pushed with `iio_push_event()` from the threaded IRQ path.

## Risks
Event logic is subtle because the chip keeps IRQ asserted while a threshold condition persists, so suppression rewrites limits and delayed work later restores them. A notable risk is in `bd79124_enable_event()`: the rising-direction branch selects `data->alarm_f_limit[channel]` instead of the rising-limit cache before writing the high-limit register, which looks like a copy/paste bug. `bd79124gpo_set_multiple()` compares `all_gpos ^ *mask`, which rejects masks that are not exactly equal to the PINCFG state rather than checking only requested bits; this is intentional per the comment but should be regression-tested with partial masks. Raw reads temporarily disturb the auto-channel set, so restore failure can disable alarm monitoring.

## Test signals
Useful tests are probe with and without IRQ, firmware channel subsets that leave no GPIOs, all GPIOs, and mixed ADC/GPO pins, direct raw reads while alarms are enabled, threshold enable/disable and hysteresis sysfs paths, repeated threshold IRQ storm suppression and re-enable timing, regulator scale reporting, and `set_multiple()` with valid and invalid GPIO masks.
