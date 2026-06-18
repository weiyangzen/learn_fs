# sources/distributed-fs/ceph-client/drivers/hwmon/wm831x-hwmon.c

## Purpose
This platform hwmon driver exposes auxiliary ADC readings from WM831x PMIC devices. It reports four generic AUX voltages, named system/USB/battery/wall/backup-battery voltages, PMIC chip temperature, and battery temperature as a voltage.

## Important APIs, Types, And Functions
- `input_names[]` maps WM831x AUXADC channel IDs to label strings.
- `show_voltage()` calls `wm831x_auxadc_read_uv()` and reports millivolts.
- `show_chip_temp()` calls `wm831x_auxadc_read()` and converts raw ADC code to millidegrees Celsius using the formula in the comment.
- `show_label()` prints channel labels.
- `wm831x_hwmon_probe()` gets the parent MFD `struct wm831x` and registers devm hwmon groups.

## Control Flow
The platform device is created by the WM831x MFD layer. Probe fetches the parent driver data and registers a fixed attribute group with `devm_hwmon_device_register_with_groups()`. Sysfs reads call into the PMIC AUXADC helpers directly; no driver-local cache is maintained.

## State And Persistence
The driver has no mutable runtime state beyond the hwmon registration. Values are live ADC reads. Labels are static. Any ADC calibration or power sequencing is delegated to the WM831x MFD/AUXADC layer.

## Dependencies And Integration Points
It depends on the WM831x MFD core and AUXADC APIs, platform-device binding `wm831x-hwmon`, hwmon sysfs groups, and standard sensor attribute helpers.

## Risks
- The chip temperature conversion is hard-coded; wrong raw-unit assumptions in the lower AUXADC helper would produce wrong millidegree output.
- Battery temperature is intentionally reported as voltage because external components determine conversion, so userspace must know board-specific thermistor scaling.
- No cache means frequent reads can trigger frequent ADC conversions.

## Test Signals
Validate MFD child probing, each AUXADC channel read path, label mapping, negative error propagation from AUXADC helpers, PMIC temperature conversion with known raw values, and hwmon group registration/teardown.
