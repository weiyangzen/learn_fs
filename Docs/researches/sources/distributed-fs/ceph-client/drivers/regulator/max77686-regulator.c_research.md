# sources/distributed-fs/ceph-client/drivers/regulator/max77686-regulator.c

Purpose: registers 26 LDOs and 9 buck regulators for the MAX77686 PMIC, including suspend opmodes, DVS ramp tables, and optional GPIO control for selected rails.

Important APIs/types/functions: `struct max77686_data` holds a GPIO-enabled bitmap and per-regulator `opmode` shadow. `max77686_get_opmode_shift()` handles rail-specific enable-bit placement; `max77686_map_normal_mode()` maps normal mode to GPIO-control where applicable; suspend helpers update PWRREQ/low-power modes; `max77686_of_parse_cb()` obtains optional `maxim,ena` GPIOs.

Control flow: platform probe obtains the parent MFD regmap, initializes every opmode to normal, and registers all descriptors. During OF parsing, eligible rails can be switched to GPIO-control mode and given a nonexclusive enable GPIO.

State and persistence: the opmode array is runtime shadow state used by enable and suspend paths. Register settings persist in PMIC hardware; GPIO descriptor lifecycle is mediated through regulator core config.

Dependencies and integration: depends on MAX77686 MFD headers, platform MFD child binding, OF regulator nodes named `voltage-regulators`, GPIO descriptors, and regulator mode/suspend callbacks.

Risks and test signals: only selected rails support GPIO-control remapping, and failed GPIO-control register writes discard the GPIO. BUCK5-9 suspend mode requests are ignored. Test all descriptor IDs, DVS ramp selection, suspend-disable versus suspend-mode behavior, GPIO-control rails, and registration failure cleanup.
