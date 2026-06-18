# sources/distributed-fs/ceph-client/drivers/regulator/bq257xx-regulator.c

Purpose: This compact driver exposes the OTG VBUS output of TI BQ257xx charger MFD devices as a regulator. It supports VBUS voltage selection, current-limit programming, register-backed enable, and optional external GPIO assertion for OTG enable.

Important APIs, types, and functions: `struct bq257xx_reg_data` stores the registered regulator, optional `otg_en_gpio`, and a mutable copy of the descriptor. `bq25703_vbus_get_cur_limit()` reads `BQ25703_OTG_CURRENT` and extracts the current field with `FIELD_GET`. `bq25703_vbus_set_cur_limit()` validates min/max values, rounds max current to register steps, rejects rounding below the requested minimum, and writes the field with `FIELD_PREP`. `bq25703_vbus_enable()` and `_disable()` drive the optional GPIO before delegating to regmap enable helpers. `bq257xx_reg_dt_parse_gpio()` descends into `regulators/vbus` to fetch `enable-gpios`.

Control flow: Probe sets the child OF node from the parent device, allocates private data, copies `bq25703_vbus_desc`, stores driver data, parses the optional GPIO, fills `regulator_config` with the platform device, original OF node, parent regmap, and driver data, then registers one regulator. Missing parent regmap aborts probe; GPIO `-ENOENT` is treated as register-only operation while other GPIO errors are logged and leave the pointer as an error object.

State and persistence behavior: Voltage selection, current limit, and OTG enable are stored in charger registers. The optional GPIO is driven low by default when acquired and is set high or low around regulator enable/disable. There is no suspend/resume or interrupt state. Descriptor state is copied into private memory before registration, allowing future per-device mutation.

Dependencies and integration points: The file depends on `linux/mfd/bq257xx.h` for register definitions and field masks, regulator core regmap helpers, OF regulator child nodes, GPIO descriptors, regmap, and platform-device creation by the charger MFD. It registers as `"bq257xx-regulator"`.

Risks: `bq257xx_reg_dt_parse_gpio()` logs non-ENOENT GPIO errors but does not clear `otg_en_gpio`; enable/disable later treat any non-null error pointer as a valid GPIO and may dereference an error pointer. Current-limit validation checks `max_uA < 0` but not `min_uA < 0`, relying on rounding logic to reject problematic values. The current register write uses `regmap_write()` instead of update-bits, so unrelated bits in `BQ25703_OTG_CURRENT` would be overwritten if any exist.

Test signals: Test register-only mode, valid GPIO mode, non-ENOENT GPIO error handling, voltage selector get/set through regmap helpers, current limit boundaries and rounding rejection, max over range, negative inputs, GPIO sequencing on enable/disable, parent regmap absence, and DT traversal when `regulators` or `vbus` child nodes are missing.
