# sources/distributed-fs/ceph-client/drivers/hwmon/wm8350-hwmon.c

## Purpose
This platform hwmon driver exposes WM8350 PMIC AUXADC voltage channels for USB, battery, and line inputs, with labels.

## Important APIs, Types, And Functions
- `input_names[]` maps WM8350 AUXADC channel IDs to labels.
- `show_voltage()` calls `wm8350_read_auxadc()`, multiplies by `WM8350_AUX_COEFF`, and reports millivolts.
- `show_label()` prints the static channel label.
- `wm8350_hwmon_probe()` gets the MFD-provided `struct wm8350` from platform data and registers the hwmon group.

## Control Flow
Probe is invoked for the `wm8350-hwmon` platform device. It registers a static sysfs group with three voltage inputs and three labels. Sysfs reads perform direct AUXADC conversions through the WM8350 MFD/comparator API.

## State And Persistence
The driver has no local cache or persistent settings. All values are live readings from PMIC ADC hardware, and labels are compile-time constants.

## Dependencies And Integration Points
It depends on WM8350 MFD core/comparator headers, platform-device binding `wm8350-hwmon`, hwmon sysfs groups, and devm hwmon registration.

## Risks
- `show_voltage()` does not check for negative error returns before multiplying by `WM8350_AUX_COEFF`, so lower-level ADC errors may be converted into misleading values if the helper can fail with negative codes.
- Board-specific scaling beyond the PMIC coefficient is not represented.
- No cache may make rapid sysfs polling expensive.

## Test Signals
Validate platform data retrieval, voltage conversion for known raw ADC codes, negative ADC error behavior, label mapping, and devm hwmon group cleanup.
