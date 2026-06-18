<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65218.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65218.c

Purpose: exposes three TPS65218 PMIC GPO lines, enforcing PMIC-specific open-drain and sequencer restrictions.

Important APIs, types, and functions: `struct tps65218_gpio` stores parent PMIC data and gpiochip. GPIO callbacks are request, direction_output, get, set, and set_config. Register writes use protected `tps65218_set_bits()` and `tps65218_clear_bits()` with `TPS65218_PROTECT_L1`.

Control flow: probe gets parent MFD data, copies a three-line template, sets the device parent, and registers the gpiochip. Request validates electrical mode: GPO1 and GPO3 must be open-drain, open-source is rejected for all lines, sequencer functions are disabled for GPO1/GPO3, and mux bits are cleared. Set/output update enable bits in `TPS65218_REG_ENABLE2`; set_config supports fixed open-drain on GPO1/GPO3 and push-pull/open-drain selection on GPO2.

State and persistence behavior: no private cache; PMIC registers hold line state, muxing, buffer mode, and sequencer state.

Dependencies and integration points: depends on parent TPS65218 MFD, regmap-backed protected update helpers, gpiolib line open-drain/open-source flags, OF/platform IDs, and pinconf drive parameters.

Risks and test signals: request-time policy depends on consumers declaring open-drain where required; missing flags cause request failure. Protected writes can fail and must be surfaced. Test all three request paths, sequencer disable, GPO2 drive mode toggling, enable-bit get/set, and invalid offset handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65218.c -->
