# `sources/distributed-fs/ceph-client/drivers/hwmon/max77705-hwmon.c` Research

Purpose: this platform hwmon child driver exposes voltage and current telemetry from the MAX77705 PMIC through the parent MFD regmap. It reports two voltage channels and two current channels, including an average current attribute for `ISYS`.

Important APIs, types, and functions: `struct channel_desc` describes the raw register, optional average register, label, and nano-unit resolution. `current_channel_desc[]` covers `IIN_REG` and `ISYS_REG`; `voltage_channel_desc[]` covers `VBYP_REG` and `VSYS_REG`. `max77705_read_and_convert()` handles regmap reads, optional signed extension, and nano-to-milli conversion with `mult_frac()`. `max77705_is_visible()`, `max77705_read_string()`, and `max77705_read()` implement hwmon callbacks.

Control flow: probe obtains the parent regmap with `dev_get_regmap(pdev->dev.parent, NULL)` and registers a `max77705` hwmon device. Reads choose the channel descriptor by hwmon type and channel, then convert current as signed 16-bit values and voltage as unsigned values. Labels are returned from the descriptor tables.

State and persistence: the driver has no private mutable state beyond using the parent regmap as `drvdata`. Hardware registers provide current values, and no cache is maintained.

Dependencies and integration points: depends on `linux/mfd/max77705-private.h` register definitions, regmap, platform bus, and hwmon. It is bound by platform driver name `max77705-hwmon` and is expected to be instantiated by the MAX77705 MFD core.

Risks and test signals: there is a suspicious visibility/read-string mix-up: current label handling uses `hwmon_in_label` in places where `hwmon_curr_label` would be expected. Tests should verify generated sysfs labels for current channels, signed current conversion for negative values, absence of average on channel 0, parent-regmap missing probe failure, and correct millivolt/milliamp scaling.
